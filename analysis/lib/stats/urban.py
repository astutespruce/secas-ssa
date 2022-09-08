from pathlib import Path

from analysis.constants import (
    URBAN_YEARS,
    URBAN_PROBABILITIES,
    URBAN_BINS,
    URBAN_THRESHOLD,
)
from analysis.lib.raster import extract_count_in_geometry


src_dir = Path("data/inputs/threats/urban")


def extract_urban_by_mask(shape_mask, window, cellsize):
    """Calculate the area of overlap between shapes and urbanization
    for each decade from 2020 to 2100.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window for extracting area of shape_mask from raster
    cellsize : area of each pixel

    Returns
    -------
    dict
        {
            'urban': <acres already urban>,
            "high": [<acres 2020>, <acres 2030>, ..., <acres 2100>],
            "low": [<acres 2020>, <acres 2030>, ..., <acres 2100>],
        }
    """

    high = []
    low = []

    for year in URBAN_YEARS:
        filename = src_dir / f"urban_{year}.tif"
        counts = extract_count_in_geometry(
            filename, shape_mask, window, URBAN_BINS, boundless=True
        )

        if year == 2020:
            # extract area already urban (in index 51) and add to front of list
            already_urban = counts[51] * cellsize
            high.append(already_urban)
            low.append(already_urban)

        # high urbanization is sum of pixel counts * probability for all urbanized pixels
        high.append(((counts * URBAN_PROBABILITIES).sum() * cellsize))

        # low urbanization is sum of pixel counts * probability for probabilities >= 50% (25 of 50 runs)
        low.append(
            (
                (counts[URBAN_THRESHOLD:] * URBAN_PROBABILITIES[URBAN_THRESHOLD:]).sum()
                * cellsize
            )
        )

    return {"high": high, "low": low}
