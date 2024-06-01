import numpy as np
import rasterio

from analysis.constants import DATASETS
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/indicators"


def summarize_indicator_in_aoi(id, rasterized_geometry):
    """Calculate the area of overlap by value in the indicator dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
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

    with rasterio.open(src_dir / indicator["filename"]) as src:
        acres = rasterized_geometry.get_acres_by_bin(src, bins)

    # Some indicators exclude 0 values, remove them from results
    min_value = min(values)
    if min_value > 0:
        acres = acres[min_value:]

    return acres
