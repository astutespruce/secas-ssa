import geopandas as gp
import numpy as np
import pandas as pd
import rasterio
import shapely

from analysis.constants import (
    SLR_DEPTH_VALUES,
    SLR_NODATA_VALUES,
    SLR_PROJ_COLUMNS,
    SLR_PROJ_SCENARIOS,
    SLR_YEARS,
)
from api.settings import SHARED_DATA_DIR

SLR_BINS = [v["value"] for v in SLR_DEPTH_VALUES + SLR_NODATA_VALUES]


src_dir = SHARED_DATA_DIR / "inputs/threats/slr"
slr_mask_filename = src_dir / "slr_mask.tif"
depth_filename = src_dir / "slr.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"


def summarize_slr_in_aoi(rasterized_geometry):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    ndarray
        [area for 0ft inundation, area for 1ft, ..., area for 10f, area for nodata cols...]
    """

    with rasterio.open(depth_filename) as src:
        acres = rasterized_geometry.get_acres_by_bin(src, bins=SLR_BINS)

    # accumulate values for depths 0-10ft
    acres[:11] = np.cumsum(acres[:11])

    return acres


def extract_slr_proj_in_analysis_areas(df: gp.GeoDataFrame) -> pd.DataFrame:
    """Extract SLR projections by decade and scenario, using area-weighted
    average per analysis unit with each overlapping SLR projection cell

    Parameters
    ----------
    df : GeoDataFrame
        uses index to aggregate results

    Returns
    -------
    DataFrame
        indexed on same index as df, returns list of dicts of scenario and values
        by decade (in order of SLR_YEARS)
    """
    index_name = df.index.name or "index"
    tmp = df.explode(ignore_index=False, index_parts=False)
    out_name = "slr_proj"

    slr_proj = gp.read_feather(proj_filename)
    left, right = shapely.STRtree(slr_proj.geometry.values).query(tmp.geometry.values, predicate="intersects")

    # no intersections
    if len(left) == 0:
        return None

    pairs = gp.GeoDataFrame(
        {
            "geometry": tmp.geometry.values.take(left),
            "index_right": slr_proj.index.values.take(right),
            "geometry_right": slr_proj.geometry.values.take(right),
        },
        index=pd.Index(tmp.index.values.take(left), name=index_name),
        geometry="geometry",
        crs=df.crs,
    )
    shapely.prepare(pairs.geometry.values)
    shapely.prepare(pairs.geometry_right.values)

    # if left completely contains right, the right geometry is the intersection
    left_contains = shapely.contains_properly(pairs.geometry.values, pairs.geometry_right.values)
    pairs.loc[left_contains, "geometry"] = pairs.loc[left_contains].geometry_right.values

    # if right completely contains the left, the left (geometry) are the intersection
    right_contains = ~left_contains & shapely.contains_properly(pairs.geometry.values, pairs.geometry_right.values)

    # any that aren't contained in either direction must be intersected
    ix = ~(left_contains | right_contains)
    pairs.loc[ix, "geometry"] = shapely.intersection(pairs.loc[ix].geometry.values, pairs.loc[ix].geometry_right.values)

    # explode and only keep polygons
    pairs = pairs.drop(columns=["geometry_right"]).explode(ignore_index=False, index_parts=False)
    pairs = pairs.loc[shapely.get_type_id(pairs.geometry.values) == 3]

    if len(pairs) == 0:
        return None

    # calculate area-weighted average per year and scenario across any overlapping cells
    # NOTE: we don't calculate acres, we only need area ratio
    pairs["area"] = shapely.area(pairs.geometry.values)
    pairs = pairs.loc[pairs["area"] > 0].copy()
    total_area = pairs.groupby(level=0)["area"].sum().rename("total_area")
    pairs = pairs.join(total_area)
    pairs["area_factor"] = pairs["area"] / pairs.total_area

    pairs = pairs.drop(columns=["area", "geometry"]).join(slr_proj[SLR_PROJ_COLUMNS], on="index_right")
    pairs[SLR_PROJ_COLUMNS] = pairs[SLR_PROJ_COLUMNS].multiply(pairs.area_factor, axis=0)

    # restructure into one row per scenario, with columns for years and aggregate
    # back to original index
    projections = (
        pairs[SLR_PROJ_COLUMNS]
        .reset_index()
        .melt(id_vars=[index_name])
        .groupby([index_name, "variable"])
        .value.sum()
        .reset_index(level=-1)
    )
    projections[["year", "scenario"]] = projections.variable.str.split("_", expand=True)
    projections = (
        projections.set_index("scenario", append=True).pivot(columns=["year"], values=["value"]).reset_index(-1)
    )
    projections.columns = ["scenario"] + projections.columns.get_level_values(-1)[1:].astype("int64").to_list()

    # sort by same order as SLR_PROJ_SCENARIOS
    projections["sort_order"] = projections.scenario.map({k: i for i, k in enumerate(SLR_PROJ_SCENARIOS)})
    projections = projections.sort_values(by="sort_order")

    # transform in to dict of list of year values
    projections["values"] = projections[SLR_YEARS].apply(list, axis=1)
    projections[out_name] = projections[["scenario", "values"]].to_dict(orient="records")

    out = df[[]].join(projections.groupby(level=0)[out_name].apply(np.array))
    # fill with empty arrays
    out.loc[out[out_name].isnull(), out_name] = out[out_name].apply(lambda x: np.array([]))

    return out[out_name]
