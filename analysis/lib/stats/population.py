from pathlib import Path

import pandas as pd
import pygeos as pg

import rasterio

from analysis.constants import (
    M2_ACRES,
)
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import boundless_raster_geometry_mask
from analysis.lib.stats import (
    extract_urban_by_geometry,
    extract_slr_by_geometry,
)


data_dir = Path("data/inputs")
bnd_dir = data_dir / "boundaries"
extent_filename = bnd_dir / "nonmarine_mask.tif"
# boundary_filename = data_dir / "boundaries/se_boundary.feather"
# county_filename = data_dir / "boundaries/counties.feather"
# ownership_filename = data_dir / "boundaries/ownership.feather"


# TODO: param for progress callback
def get_results(df, progress_callback=None):
    # convert to plain DataFrame with just pygeos geometries
    df = pd.DataFrame(df)
    df["geometry"] = df.geometry.values.data
    df["acres"] = pg.area(df.geometry.values) * M2_ACRES
    df["__geo__"] = to_dict_all(df.geometry.values)
    df["bounds"] = pg.bounds(df.geometry.values).tolist()

    # TODO: prefilter polygons to those that overlap boundary

    results = []

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

            result["shape_mask"] = (~shape_mask).sum() * cellsize

            data = extent_raster.read(1, window=window, boundless=True)
            mask = (data == nodata) | shape_mask

            # slice out flattened array of values that are not masked
            result["overlap"] = data[~mask].sum() * cellsize
            if result["overlap"] == 0:
                results.append(result)

                if progress_callback is not None:
                    progress_callback(100 * count / len(df))

                count += 1
                continue

            # Extract SLR
            slr = extract_slr_by_geometry(row.geometry, shapes, row.bounds)
            result["has_slr"] = slr is not None
            if slr is not None:
                result["slr_depth"] = slr["depth"]
                result["slr_proj"] = slr["projections"]
                result["slr_shape_mask"] = slr["shape_mask"]

            # Extract urban
            urban = extract_urban_by_geometry(shapes, row.bounds)
            result["has_urban"] = urban is not None
            if urban is not None:
                result["urban"] = urban["urban"]
                result["urban_proj"] = urban["projections"]

            # Extract NLCD
            # TODO:

            results.append(result)

            if progress_callback is not None:
                progress_callback(100 * count / len(df))

            count += 1

        return df[["acres"]].join(pd.DataFrame(results, index=df.index))
