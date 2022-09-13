from pathlib import Path

import numpy as np

from analysis.constants import NLCD_YEARS, NLCD_INDEXES
from analysis.lib.raster import extract_count_in_geometry


src_dir = Path("data/inputs/nlcd")

PERCENTS = np.arange(0, 1.01, 0.01)


def extract_nlcd_landcover_by_mask(shape_mask, window, cellsize):
    """Calculate the area of overlap between shapes and NLCD indexes (not codes)
    for each available year.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window for extracting area of shape_mask from raster
    cellsize : area of each pixel

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
            filename, shape_mask, window, bins, boundless=True
        )

        areas.append(counts * cellsize)

    # Transpose and convert to dict, only keep those that have areas
    areas = np.array(areas).T

    results = {
        NLCD_INDEXES[i]["label"]: areas[i].tolist()
        for i in NLCD_INDEXES
        if areas[i].sum()
    }

    return results


def extract_nlcd_impervious_by_mask(shape_mask, window, cellsize):
    """Calculate total amount of impervious surface within shape_mask based on
    count per percent (0-100) * percent

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window for extracting area of shape_mask from raster
    cellsize : area of each pixel

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
            filename, shape_mask, window, bins, boundless=True
        )

        areas.append((PERCENTS * counts * cellsize).sum())

    # Transpose
    return np.array(areas).T.tolist()
