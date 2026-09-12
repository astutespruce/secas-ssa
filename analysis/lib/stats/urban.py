import numpy as np
import rasterio

from analysis.constants import (
    URBAN_BINS,
    URBAN_PROBABILITIES,
    URBAN_THRESHOLD,
    URBAN_YEARS,
)
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/threats/urban"
urban_filename = str(src_dir / "urban_{year}.tif")


def summarize_urban_in_aoi(rasterized_geometry):
    """Calculate the area of overlap between shapes and urbanization
    for each decade from 2030 to 2100.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    dict
        {
            'urban': <acres already urban>,
            "high": [<acres 2030>, ..., <acres 2100>],
            "low": [<acres 2030>, ..., <acres 2100>],
        }
    """

    high_urban_acres = np.zeros((len(URBAN_YEARS) + 3,))
    low_urban_acres = np.zeros((len(URBAN_YEARS) + 3,))

    for year_index, year in enumerate(URBAN_YEARS):
        with rasterio.open(urban_filename.format(year=year)) as src:
            urban_prob_acres = rasterized_geometry.get_acres_by_bin(src, URBAN_BINS)

        # high urbanization is sum of acres by probability bin * probability
        high_urban_acres[year_index + 1] = (urban_prob_acres * URBAN_PROBABILITIES).sum()

        # low urbanization is sum of pixel counts * probability for
        # probabilities >= 50% (25 of 50 runs)
        low_urban_acres[year_index + 1] = (
            urban_prob_acres[URBAN_THRESHOLD:] * URBAN_PROBABILITIES[URBAN_THRESHOLD:]
        ).sum()

        if year == 2030:
            # extract area already urban (in index 51) and add to front of list
            high_urban_acres[0] = urban_prob_acres[51]
            low_urban_acres[0] = urban_prob_acres[51]

        elif year == 2100:
            # important: we calculate nodata area based on all pixels that had >= 0 probability;
            # for most other layer we just sum their acres to calculate this
            urban_nodata = rasterized_geometry.acres - rasterized_geometry.outside_extent_acres - urban_prob_acres.sum()

            high_noturban_2100 = urban_prob_acres.sum() - high_urban_acres[year_index + 1]
            if high_noturban_2100 < 1e-6:
                high_noturban_2100 = 0.0
            high_urban_acres[-2] = high_noturban_2100

            low_noturban_2100 = urban_prob_acres.sum() - low_urban_acres[year_index + 1]
            if low_noturban_2100 < 1e-6:
                low_noturban_2100 = 0.0
            low_urban_acres[-2] = low_noturban_2100

            if urban_nodata < 1e-6:
                urban_nodata = 0.0
            high_urban_acres[-1] = urban_nodata
            low_urban_acres[-1] = urban_nodata

    return {"high": high_urban_acres, "low": low_urban_acres}
