from collections import defaultdict

import rasterio

from analysis.constants import NLCD_INUNDATION_FREQUENCY, NLCD_INDEXES
from api.settings import DATA_DIR

BINS = list(NLCD_INUNDATION_FREQUENCY.keys())

inundation_frequency_dir = DATA_DIR / "inputs/inundation_frequency"

inundation_frequency_filename = (
    inundation_frequency_dir / "nlcd_inundation_frequency.tif"
)


def summarize_nlcd_inundation_frequency_in_aoi(rasterized_geometry):
    """Calculate the area of overlap between shapes and inundation frequency
    by NLCD 2021 land cover class.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------

    dict

        {<NLCD index>: [<inundation freq bin 0 acres>,...], ...}
    """

    with rasterio.open(inundation_frequency_filename) as src:
        acres = rasterized_geometry.get_acres_by_bin(src, BINS).round(2)

    results = defaultdict(list)
    for key, entry in NLCD_INUNDATION_FREQUENCY.items():
        results[NLCD_INDEXES[entry["nlcd"]]["label"]].append(acres[key])

    # drop any that are not present
    results = {k: v for k, v in results.items() if sum(v) > 0}

    return results
