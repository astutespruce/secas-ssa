from pathlib import Path

import numpy as np

from analysis.constants import DATASETS
from analysis.lib.raster import extract_count_in_geometry


src_dir = Path("../secas-blueprint/data/inputs/indicators/base")


def extract_indicator_by_mask(id, shape_mask, window, cellsize):
    """Calculate the area of overlap by value in the indicator dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    id : str
        ID of indicator dataset
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window
        for extracting area of shape_mask from raster
    cellsize : float
        area of each pixel

    Returns
    -------
    list
        acres in each indicator value, in the order they occur in the list of values
        in the DATASETS structure
    """

    indicator = DATASETS[id]
    filename = src_dir / indicator["filename"]

    values = [e["value"] for e in indicator["values"]]
    bins = np.arange(0, max(values) + 1)
    counts = extract_count_in_geometry(
        filename, shape_mask, window, bins, boundless=True
    )

    # Some indicators exclude 0 values, remove them from counts
    min_value = min(values)
    if min_value > 0:
        counts = counts[min_value:]

    return counts * cellsize
