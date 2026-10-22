import pandas as pd
import shapely
from pyogrio import read_dataframe

from api.settings import DATA_DIR

huc12_filename = DATA_DIR / "inputs/sarp_huc12_stats.fgb"


def extract_sarp_huc12_stats(df):
    """Extract SARP HUC12 statistics at HUC12 level

    Parameters
    ----------
    df : GeoDataFrame
        contains geometries that define the analysis units.

    Returns
    -------
    DataFrame
        contains a record with statistics for each record in df
    """

    tmp = df.explode(ignore_index=False, index_parts=False)
    # use union of individual area bounding boxes to read features
    read_mask = shapely.union_all(shapely.envelope(tmp.geometry.values))
    # NOTE: pyogrio does not currently work properly for use_arrow=True if the
    # mask does not overlap and returns no features, so we can't use it here.
    huc12 = read_dataframe(
        huc12_filename, columns=["HUC12", "dams", "crossings", "altered_miles", "total_miles"], mask=read_mask
    )

    left, right = shapely.STRtree(huc12.geometry.values).query(df.geometry.values, predicate="intersects")

    if len(df) == 0:
        return None

    # calculate stats by record in input df
    stats = (
        pd.DataFrame(
            {"index_right": huc12.index.values.take(right)},
            index=df.index.values.take(left),
        )
        .join(
            huc12[["HUC12", "dams", "crossings", "altered_miles", "total_miles"]],
            on="index_right",
        )
        .drop(columns=["index_right"])
        .groupby(level=0)
        .agg(
            {
                "dams": "sum",
                "crossings": "sum",
                "altered_miles": "sum",
                "total_miles": "sum",
                "HUC12": "count",
            }
        )
        .fillna(0)
        .rename(columns={"HUC12": "subwatersheds"})
    )

    # stored as a proportion due to percent formatting in XLSX
    stats["pct_altered"] = stats.altered_miles / stats.total_miles

    return stats
