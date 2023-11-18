from analysis.constants import (
    URBAN_YEARS,
    URBAN_PROBABILITIES,
    URBAN_BINS,
    URBAN_THRESHOLD,
)
from analysis.lib.raster import extract_count_in_geometry
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/threats/urban"


def extract_urban_by_mask(mask_config):
    """Calculate the area of overlap between shapes and urbanization
    for each decade from 2030 to 2100.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    mask_config : AOIMaskConfig

    Returns
    -------
    dict
        {
            'urban': <acres already urban>,
            "high": [<acres 2030>, ..., <acres 2100>],
            "low": [<acres 2030>, ..., <acres 2100>],
        }
    """

    cellsize = mask_config.cellsize

    high = []
    low = []

    for year in URBAN_YEARS:
        filename = src_dir / f"urban_{year}.tif"
        counts = extract_count_in_geometry(
            filename, mask_config, URBAN_BINS, boundless=True
        )

        if year == 2030:
            # extract area already urban (in index 51) and add to front of list
            already_urban = counts[51] * cellsize
            high.append(already_urban)
            low.append(already_urban)

        # high urbanization is sum of pixel counts * probability for all
        # urbanized pixels
        high.append(((counts * URBAN_PROBABILITIES).sum() * cellsize))

        # low urbanization is sum of pixel counts * probability for
        # probabilities >= 50% (25 of 50 runs)
        low.append(
            (
                (counts[URBAN_THRESHOLD:] * URBAN_PROBABILITIES[URBAN_THRESHOLD:]).sum()
                * cellsize
            )
        )

    return {"high": high, "low": low}
