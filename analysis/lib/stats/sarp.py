import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp

from analysis.constants import GEO_CRS
from analysis.lib.io import read_feather_by_bounds
from api.settings import DATA_DIR

huc12_filename = DATA_DIR / "inputs/sarp_huc12_stats.feather"


def extract_sarp_huc12_stats(df):
    """Extract SARP HUC12 statistics at HUC12 level

    Parameters
    ----------
    df : GeoDataFrame
        contains ceometries that define the analysis units.

    Returns
    -------
    DataFrame
        contains a record with statistics for each record in df

    """

    huc12 = read_feather_by_bounds(
        huc12_filename,
        pg.bounds(df.geometry.values.data),
        columns=[
            "geometry",
            "HUC12",
            "dams",
            "crossings",
            "altered_miles",
            "total_miles",
        ],
    )
    tree = pg.STRtree(huc12.geometry.values.data)
    left, right = tree.query_bulk(df.geometry.values.data, predicate="intersects")

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
