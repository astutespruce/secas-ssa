import numpy as np

from analysis.constants import NLCD_YEARS, NLCD_INDEXES
from analysis.lib.raster import extract_count_in_geometry
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/nlcd"

PERCENTS = np.arange(0, 1.01, 0.01)


def extract_nlcd_landcover_by_mask(mask_config):
    """Calculate the area of overlap between shapes and NLCD indexes (not codes)
    for each available year.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    mask_config : AOIMaskConfig

    Returns
    -------
    dict
        {<NLCD index>: [<acres 2020>, <acres 2030>, ..., <acres 2100>], ...}
    """

    bins = list(NLCD_INDEXES.keys())
    areas = []

    for year in NLCD_YEARS:
        filename = src_dir / f"landcover_{year}.tif"
        counts = extract_count_in_geometry(
            filename, mask_config, bins, boundless=True
        )

        areas.append(counts * mask_config.cellsize)

    # Transpose and convert to dict, only keep those that have areas
    areas = np.array(areas).T

    results = {
        NLCD_INDEXES[i]["label"]: areas[i].tolist()
        for i in NLCD_INDEXES
        if areas[i].sum()
    }

    return results


def extract_nlcd_impervious_by_mask(mask_config):
    """Calculate total amount of impervious surface within shape_mask based on
    count per percent (0-100) * percent

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    mask_config : AOIMaskConfig

    Returns
    -------
    list
        [<acres 2020>, <acres 2030>, ..., <acres 2100>]
    """

    bins = PERCENTS.tolist()
    areas = []

    for year in NLCD_YEARS:
        filename = src_dir / f"impervious_{year}.tif"
        counts = extract_count_in_geometry(
            filename, mask_config, bins, boundless=True
        )

        areas.append((PERCENTS * counts * mask_config.cellsize).sum())

    # Transpose
    return np.array(areas).T.tolist()
