from collections import defaultdict

from analysis.constants import NLCD_INUNDATION_FREQUENCY, NLCD_INDEXES
from analysis.lib.raster import extract_count_in_geometry
from api.settings import DATA_DIR

BINS = list(NLCD_INUNDATION_FREQUENCY.keys())

inundation_frequency_dir = DATA_DIR / "inputs/inundation_frequency"
inundation_frequency_filename = (
    inundation_frequency_dir / "nlcd_inundation_frequency.tif"
)


def extract_nlcd_inundation_frequency_by_mask(mask_config):
    """Calculate the area of overlap between shapes and inundation frequency
    by NLCD 2021 land cover class.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window for extracting area of shape_mask from raster
    cellsize : area of each pixel

    Returns
    -------

    dict

        {<NLCD index>: [<inundation freq bin 0 acres>,...], ...}
    """

    acres = (
        extract_count_in_geometry(
            inundation_frequency_filename, mask_config, bins=BINS, boundless=True
        )
        * mask_config.cellsize
    ).round(2)

    results = defaultdict(list)
    for key, entry in NLCD_INUNDATION_FREQUENCY.items():
        results[NLCD_INDEXES[entry["nlcd"]]["label"]].append(acres[key])

    # drop any that are not present
    results = {k: v for k, v in results.items() if sum(v) > 0}

    return results
