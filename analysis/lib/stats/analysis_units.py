import geopandas as gp
import pandas as pd
import shapely

from analysis.constants import M2_ACRES, SECAS_STATES
from analysis.lib.stats.inundation_frequency import (
    summarize_nlcd_inundation_frequency_in_aoi,
)
from analysis.lib.stats.landfire import summarize_landfire_evt_in_aoi
from analysis.lib.stats.nlcd import summarize_nlcd_impervious_in_aoi, summarize_nlcd_landcover_in_aoi
from analysis.lib.stats.protected_areas import extract_protected_area_stats
from analysis.lib.stats.rasterized_geometry import RasterizedGeometry
from analysis.lib.stats.sarp import extract_sarp_huc12_stats
from analysis.lib.stats.se_blueprint_indicators import summarize_indicator_in_aoi
from analysis.lib.stats.slr import extract_slr_proj_in_analysis_areas, summarize_slr_in_aoi
from analysis.lib.stats.urban import summarize_urban_in_aoi
from api.settings import SHARED_DATA_DIR

data_dir = SHARED_DATA_DIR / "inputs"
bnd_dir = data_dir / "boundaries"
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
    left, right = shapely.STRtree(states.geometry.values).query(df.geometry.values, predicate="intersects")
    state_join = (
        pd.DataFrame({"state": states.state.values.take(right)}, index=df.index.values.take(left))
        .groupby(level=0)
        .state.unique()
        .apply(sorted)
        .apply(lambda x: ", ".join(x))
        .rename("states")
    )

    df = df.join(state_join)
    df["count"] = shapely.get_num_geometries(df.geometry.values)
    df["acres"] = shapely.area(df.geometry.values) * M2_ACRES
    df["bounds"] = shapely.bounds(df.geometry.values).tolist()

    results = []

    count = 0

    for index, row in df.iterrows():
        rasterized_geometry = RasterizedGeometry(row.geometry)

        result = {
            "pixels": rasterized_geometry.pixels,
            "rasterized_acres": rasterized_geometry.acres,
        }

        # short-circuit if there are no rasterized pixels
        if rasterized_geometry.acres == 0:
            results.append(result)

            if progress_callback is not None:
                await progress_callback(100 * count / len(df))

            count += 1
            continue

        # Extract SLR
        if "slr_depth" in datasets or "slr_proj" in datasets:
            result["slr_depth"] = summarize_slr_in_aoi(rasterized_geometry)

        # Extract urban
        if "urban" in datasets:
            result["urban"] = summarize_urban_in_aoi(rasterized_geometry)

        # Extract NLCD
        if "nlcd_landcover" in datasets:
            result["nlcd_landcover"] = summarize_nlcd_landcover_in_aoi(rasterized_geometry)

        if "nlcd_impervious" in datasets:
            result["nlcd_impervious"] = summarize_nlcd_impervious_in_aoi(rasterized_geometry)

        # Extract LANDFIRE EVT
        if "landfire_evt" in datasets:
            result["landfire_evt"] = summarize_landfire_evt_in_aoi(rasterized_geometry)

        # Extract SE Blueprint indicators
        se_blueprint_indicators = [dataset for dataset in datasets if dataset.startswith("se_blueprint")]
        for dataset in se_blueprint_indicators:
            result[dataset] = summarize_indicator_in_aoi(dataset, rasterized_geometry)

        # Extract inundation frequency
        if "nlcd_inundation_freq" in datasets:
            result["nlcd_inundation_freq"] = summarize_nlcd_inundation_frequency_in_aoi(rasterized_geometry)

        results.append(result)

        if progress_callback is not None:
            await progress_callback(100 * count / len(df))

        count += 1

    out = df[["states", "count", "acres"]].join(pd.DataFrame(results, index=df.index))

    if len(set(["sarp_aquatic_barriers", "sarp_aquatic_network_alteration"]).intersection(datasets)) > 0:
        sarp_huc12_stats = extract_sarp_huc12_stats(df)
        if sarp_huc12_stats is not None:
            out = out.join(sarp_huc12_stats)

    if "protected_areas" in datasets:
        protected_area_stats = extract_protected_area_stats(df)
        if protected_area_stats is not None:
            out = out.join(protected_area_stats)

    if "slr_proj" in datasets:
        slr_proj = extract_slr_proj_in_analysis_areas(df)
        if slr_proj is not None:
            out = out.join(slr_proj)

    return out
