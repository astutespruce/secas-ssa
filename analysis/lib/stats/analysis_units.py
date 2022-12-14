from pathlib import Path

import geopandas as gp
import pandas as pd
import shapely

import rasterio

from analysis.constants import M2_ACRES, SECAS_STATES
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import boundless_raster_geometry_mask
from analysis.lib.stats.sarp import extract_sarp_huc12_stats
from analysis.lib.stats.slr import (
    extract_slr_depth_by_mask,
    extract_slr_projections_by_geometry,
)
from analysis.lib.stats.urban import extract_urban_by_mask
from analysis.lib.stats.nlcd import (
    extract_nlcd_landcover_by_mask,
    extract_nlcd_impervious_by_mask,
)
from analysis.lib.stats.se_blueprint_indicators import extract_indicator_by_mask
from api.settings import SHARED_DATA_DIR


data_dir = SHARED_DATA_DIR / "inputs"
bnd_dir = data_dir / "boundaries"
extent_filename = bnd_dir / "nonmarine_mask.tif"
states_filename = bnd_dir / "states.feather"


async def get_analysis_unit_results(df, datasets, progress_callback=None):
    """Calculate statistics for each analysis unit

    Parameters
    ----------
    df : GeoDataFrame
        each row is a separate analysis unit
    datasets : list-like
        list of dataset IDs to query
    progress_callback : function, optional (default: None)
        function to call each after each analysis unit is processed

    Returns
    -------
    DataFrame
    """

    states = gp.read_feather(states_filename, columns=["state", "id", "geometry"])
    states = states.loc[states.id.isin(SECAS_STATES)]
    tree = shapely.STRtree(df.geometry.values)
    left, right = tree.query(states.geometry.values, predicate="intersects")
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

    # convert to plain DataFrame with just shapely geometries
    df = pd.DataFrame(df).join(state_join)
    df["count"] = shapely.get_num_geometries(df.geometry.values)
    df["geometry"] = df.geometry.values
    df["acres"] = shapely.area(df.geometry.values) * M2_ACRES
    df["__geo__"] = to_dict_all(df.geometry.values)
    df["bounds"] = shapely.bounds(df.geometry.values).tolist()

    results = []

    # TODO: prefilter polygons to those that overlap boundary

    sarp_huc12_stats = None
    if (
        "sarp_aquatic_barriers" in datasets
        or "sarp_aquatic_network_alteration" in datasets
    ):
        sarp_huc12_stats = extract_sarp_huc12_stats(df)

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
            shape_mask, _, window = boundless_raster_geometry_mask(
                extent_raster, shapes, row.bounds, all_touched=False
            )

            result["pixels"] = (~shape_mask).sum()
            result["rasterized_acres"] = result["pixels"] * cellsize

            data = extent_raster.read(1, window=window, boundless=True)
            mask = (data == nodata) | shape_mask

            # slice out flattened array of values that are not masked
            result["overlap"] = data[~mask].sum() * cellsize
            result["outside_se"] = result["rasterized_acres"] - result["overlap"]
            if result["overlap"] == 0:
                results.append(result)

                if progress_callback is not None:
                    await progress_callback(100 * count / len(df))

                count += 1
                continue

            # Extract SLR
            if "slr_depth" in datasets or "slr_proj" in datasets:
                result["slr_depth"] = extract_slr_depth_by_mask(
                    shape_mask,
                    window,
                    cellsize,
                    result["rasterized_acres"],
                    result["outside_se"],
                )

            if "slr_proj" in datasets:
                result["slr_proj"] = extract_slr_projections_by_geometry(row.geometry)

            # Extract urban
            if "urban" in datasets:
                result["urban"] = extract_urban_by_mask(shape_mask, window, cellsize)

            # Extract NLCD
            if "nlcd_landcover" in datasets:
                result["nlcd_landcover"] = extract_nlcd_landcover_by_mask(
                    shape_mask, window, cellsize
                )

            if "nlcd_impervious" in datasets:
                result["nlcd_impervious"] = extract_nlcd_impervious_by_mask(
                    shape_mask, window, cellsize
                )

            # Extract SE Blueprint indicators
            se_blueprint_indicators = [
                dataset for dataset in datasets if dataset.startswith("se_blueprint")
            ]
            for dataset in se_blueprint_indicators:
                result[dataset] = extract_indicator_by_mask(
                    dataset, shape_mask, window, cellsize
                )

            results.append(result)

            if progress_callback is not None:
                await progress_callback(100 * count / len(df))

            count += 1

        df = df[["states", "count", "acres"]].join(
            pd.DataFrame(results, index=df.index)
        )

        if sarp_huc12_stats is not None:
            df = df.join(sarp_huc12_stats)

        return df
