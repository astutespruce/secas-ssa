import geopandas as gp
import pandas as pd
from pyogrio import read_dataframe
import shapely

from analysis.constants import M2_ACRES
from api.settings import DATA_DIR

protected_areas_filename = (
    DATA_DIR / "inputs/protected_areas/protected_areas_with_gap_status.fgb"
)
columns = ["name", "owner", "gap_status"]


def extract_protected_area_stats(df):
    """Extract intersection of areas of interest with protected areas data

        Parameters
        ----------
    df : GeoDataFrame
        area of interest

        Returns
        -------
        DataFrame
            one row per original row with list of protected area info [{"name": <>, "owner": <>, "gap_status": <>, "acres": <>}, ...]

    """

    index_name = df.index.name or "index"

    protected_areas = read_dataframe(
        protected_areas_filename,
        columns=columns + ["geometry"],
        # FIXME: use geometry mask or this reads too many features
        bbox=tuple(df.total_bounds),
        use_arrow=True,
    )

    if len(protected_areas) == 0:
        return None

    # find all protected areas polygons that intersect any part of the AOI
    tmp = df.explode(ignore_index=False, index_parts=False)
    left, right = shapely.STRtree(protected_areas.geometry.values).query(
        tmp.geometry.values, predicate="intersects"
    )

    # no intersections
    if len(left) == 0:
        return None

    pairs = gp.GeoDataFrame(
        {
            # index_name: tmp.index.values.take(left),
            "geometry": tmp.geometry.values.take(left),
            "index_right": protected_areas.index.values.take(right),
            "geometry_right": protected_areas.geometry.values.take(right),
        },
        index=pd.Index(tmp.index.values.take(left), name=index_name),
        geometry="geometry",
        crs=df.crs,
    )
    shapely.prepare(pairs.geometry.values)
    shapely.prepare(pairs.geometry_right.values)

    # if left completely contains right, the right geometry is the intersection
    left_contains = shapely.contains_properly(
        pairs.geometry.values, pairs.geometry_right.values
    )
    pairs.loc[left_contains, "geometry"] = pairs.loc[
        left_contains
    ].geometry_right.values

    # if right completely contains the left, the left (geometry) are the intersection
    right_contains = ~left_contains & shapely.contains_properly(
        pairs.geometry.values, pairs.geometry_right.values
    )

    # any that aren't contained in either direction must be intersected
    ix = ~(left_contains | right_contains)
    pairs.loc[ix, "geometry"] = shapely.intersection(
        pairs.loc[ix].geometry.values, pairs.loc[ix].geometry_right.values
    )

    # explode and only keep polygons
    pairs = pairs.drop(columns=["geometry_right"]).explode(
        ignore_index=False, index_parts=False
    )
    pairs = pairs.loc[shapely.get_type_id(pairs.geometry.values) == 3]

    if len(pairs) == 0:
        return None

    # aggregate to multipolygons based on protected areas columns
    protected_areas = gp.GeoDataFrame(
        pairs.join(protected_areas[columns], on="index_right")
        .groupby([index_name] + columns)
        .agg({"geometry": shapely.multipolygons})
        .reset_index()
        .set_index(index_name),
        geometry="geometry",
        crs=df.crs,
    )

    protected_areas["acres"] = shapely.area(protected_areas.geometry.values) * M2_ACRES

    # transform to dict per original row
    protected_areas["protected_areas"] = protected_areas[columns + ["acres"]].to_dict(
        orient="records"
    )
    protected_areas = protected_areas["protected_areas"].groupby(index_name).apply(list)

    out = df.join(protected_areas)
    # fill with empty lists
    ix = out.protected_areas.isnull()
    out.loc[ix, "protected_areas"] = out.protected_areas.apply(lambda x: [])

    return out[["protected_areas"]]
