import numpy as np
import rasterio

from analysis.constants import NUM_LANDFIRE_VALUES
from api.settings import DATA_DIR

src_dir = DATA_DIR / "inputs/landfire"
filename = src_dir / "landfire_evt.tif"


def summarize_landfire_evt_in_aoi(rasterized_geometry):
    """Calculate the area of overlap by value in the LANDFIRE EVT dataset

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    list
        {<LANDFIRE index>: <acres>, }
    """

    bins = np.arange(NUM_LANDFIRE_VALUES).tolist()

    with rasterio.open(filename) as src:
        acres = rasterized_geometry.get_acres_by_bin(src, bins)

    # Transpose and convert to dict, only keep those that have areas
    acres = acres.T

    results = {i: acres[i].tolist() for i in bins if acres[i].sum()}

    return results
