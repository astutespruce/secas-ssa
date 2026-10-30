import numpy as np
import rasterio

from analysis.constants import DATASETS, NUM_LANDFIRE_VALUES
from api.settings import DATA_DIR

src_dir = DATA_DIR / "inputs"

mask_filename = src_dir / DATASETS["landfire_evt"]["filename"].replace(".tif", "_mask.tif")


def open_rasters(datasets):
    """Open raster file for each dataset included in dataset_ids

    Parameters
    ----------
    dataset_ids : list of str
        list of dataset IDs

    Returns
    -------
    dict
        {<dataset_id>: <rasterio file handle>, ...}
    """
    if "landfire_evt" in datasets:
        return {"landfire_evt": rasterio.open(src_dir / DATASETS["landfire_evt"]["filename"])}

    return {}


def summarize_landfire_evt_in_aoi(src, rasterized_geometry):
    """Calculate the area of overlap by value in the LANDFIRE EVT dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    src : rasterio reader
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    list
        {<LANDFIRE index>: <acres>, }
    """

    bins = np.arange(NUM_LANDFIRE_VALUES).tolist()

    acres = rasterized_geometry.get_acres_by_bin(src, bins)

    # Transpose and convert to dict, only keep those that have areas
    acres = acres.T

    results = {i: acres[i].tolist() for i in bins if acres[i].sum()}

    return results
