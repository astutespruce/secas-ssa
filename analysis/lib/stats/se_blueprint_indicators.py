import numpy as np

from analysis.constants import DATASETS
from analysis.lib.raster import extract_count_in_geometry
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/indicators"


def extract_indicator_by_mask(id, mask_config):
    """Calculate the area of overlap by value in the indicator dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    id : str
        ID of indicator dataset
    mask_config : AOIMaskConfig

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
        filename, mask_config, bins, boundless=True
    )

    # Some indicators exclude 0 values, remove them from counts
    min_value = min(values)
    if min_value > 0:
        counts = counts[min_value:]

    return counts * mask_config.cellsize
