import numpy as np
import rasterio

from analysis.constants import DATASETS
from api.settings import SOUTHEAST_BLUEPRINT_DATA_DIR

src_dir = SOUTHEAST_BLUEPRINT_DATA_DIR / "inputs"


def open_rasters(dataset_ids):
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
    return {
        dataset_id: rasterio.open(src_dir / DATASETS[dataset_id]["filename"])
        for dataset_id in dataset_ids
        if dataset_id.startswith("se_blueprint")
    }


def summarize_indicator_in_aoi(src, id, rasterized_geometry):
    """Calculate the area of overlap by value in the indicator dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    src : rasterio reader
    id : str
        ID of indicator dataset
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    list
        acres in each indicator value, in the order they occur in the list of values
        in the DATASETS structure
    """

    indicator = DATASETS[id]

    values = [e["value"] for e in indicator["values"]]
    bins = np.arange(0, max(values) + 1)
    acres = rasterized_geometry.get_acres_by_bin(src, bins)

    # Some indicators exclude 0 values, remove them from results
    min_value = min(values)
    if min_value > 0:
        acres = acres[min_value:]

    return acres
