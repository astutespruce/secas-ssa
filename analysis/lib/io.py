import json

import geopandas as gp
import numpy as np
from pyarrow.dataset import dataset
import shapely


def read_feather_by_bounds(path, bounds, columns=None):
    """Read a GeoDataFrame using a cheap spatial index on bounds to avoid
    reading all features.

    Parameters
    ----------
    path : str or Path
    bounds : ndarray of floats with shape (4, n)
        bounds of features used to query features from dataset
    columns : list-like
        columns to read from dataset

    Returns
    -------
    GeoDataFrame
        all features from dataset that have bounding boxes that intersect the
        passed in bounds
    """

    ds = dataset(path, format="feather")
    table = ds.to_table(columns=["minx", "miny", "maxx", "maxy"])
    src_bounds = (
        table["minx"].to_numpy(),
        table["miny"].to_numpy(),
        table["maxx"].to_numpy(),
        table["maxy"].to_numpy(),
    )
    boxes = shapely.box(*np.vstack(src_bounds))
    tree = shapely.STRtree(boxes)

    query_boxes = shapely.box(*bounds.T)
    right = tree.query(query_boxes)[1]
    ix = np.sort(np.unique(right))

    df = ds.take(ix, columns=columns).to_pandas()
    df["geometry"] = shapely.from_wkb(df.geometry.values)

    meta = json.loads(ds.schema.metadata[b"geo"])
    crs = meta["columns"][meta["primary_column"]]["crs"]
    df = gp.GeoDataFrame(df, crs=crs)

    return df
