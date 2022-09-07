from pathlib import Path

import geopandas as gp
import pandas as pd
import pygeos as pg

import rasterio

from analysis.constants import AREA_PRECISION, M2_ACRES, SECAS_STATES
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import boundless_raster_geometry_mask
from analysis.lib.stats.slr import extract_slr_by_geometry
from analysis.lib.stats.urban import extract_urban_by_mask
from analysis.lib.stats.nlcd import extract_nlcd_by_mask


data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
extent_filename = bnd_dir / "nonmarine_mask.tif"
states_filename = bnd_dir / "states.feather"
# boundary_filename = data_dir / "boundaries/se_boundary.feather"
# county_filename = data_dir / "boundaries/counties.feather"
# ownership_filename = data_dir / "boundaries/ownership.feather"


def get_population_results(df, progress_callback=None):
    states = gp.read_feather(states_filename, columns=["state", "id", "geometry"])
    states = states.loc[states.id.isin(SECAS_STATES)]
    tree = pg.STRtree(df.geometry.values.data)
    left, right = tree.query_bulk(states.geometry.values.data, predicate="intersects")
    state_join = (
        pd.DataFrame(
            {"state": states.state.values.take(left)}, index=df.index.values.take(right)
        )
        .groupby(level=0)
        .state.unique()
        .apply(sorted)
        .apply(lambda x: ", ".join(x))
        .rename("states")
    )

    # convert to plain DataFrame with just pygeos geometries
    df = pd.DataFrame(df).join(state_join)
    df["count"] = pg.get_num_geometries(df.geometry.values.data)
    df["geometry"] = df.geometry.values.data
    df["acres"] = (pg.area(df.geometry.values) * M2_ACRES).round(AREA_PRECISION)
    df["__geo__"] = to_dict_all(df.geometry.values)
    df["bounds"] = pg.bounds(df.geometry.values).tolist()

    results = []

    # TODO: prefilter polygons to those that overlap boundary

    count = 0
    with rasterio.open(extent_filename) as extent_raster:
        # square meters to acres
        cellsize = extent_raster.res[0] * extent_raster.res[1] * M2_ACRES
        nodata = int(extent_raster.nodata)

        for index, row in df.iterrows():
            print(f"Processing {index}")
            result = {}
            shapes = [row.__geo__]

            # calculate main mask; if 0 bail out
            shape_mask, transform, window = boundless_raster_geometry_mask(
                extent_raster, shapes, row.bounds, all_touched=False
            )

            result["shape_mask"] = ((~shape_mask).sum() * cellsize).round(
                AREA_PRECISION
            )

            data = extent_raster.read(1, window=window, boundless=True)
            mask = (data == nodata) | shape_mask

            # slice out flattened array of values that are not masked
            result["overlap"] = (data[~mask].sum() * cellsize).round(AREA_PRECISION)
            result["outside_se"] = result["shape_mask"] - result["overlap"]
            if result["overlap"] == 0:
                results.append(result)

                if progress_callback is not None:
                    progress_callback(100 * count / len(df))

                count += 1
                continue

            # Extract SLR
            result["slr"] = extract_slr_by_geometry(row.geometry, shapes, row.bounds)

            # Extract urban
            result["urban"] = extract_urban_by_mask(shape_mask, window, cellsize)

            # Extract NLCD
            result["nlcd"] = extract_nlcd_by_mask(shape_mask, window, cellsize)

            results.append(result)

            if progress_callback is not None:
                progress_callback(100 * count / len(df))

            count += 1

        return df[["states", "count", "acres"]].join(
            pd.DataFrame(results, index=df.index)
        )
