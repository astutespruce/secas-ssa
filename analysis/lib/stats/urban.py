import rasterio

from analysis.constants import (
    URBAN_YEARS,
    URBAN_PROBABILITIES,
    URBAN_BINS,
    URBAN_THRESHOLD,
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

    high = []
    low = []

    for year in URBAN_YEARS:
        with rasterio.open(urban_filename.format(year=year)) as src:
            acres = rasterized_geometry.get_acres_by_bin(src, URBAN_BINS)

        if year == 2030:
            # extract area already urban (in index 51) and add to front of list
            already_urban = acres[51]
            high.append(already_urban)
            low.append(already_urban)

        # high urbanization is sum of pixel counts * probability for all
        # urbanized pixels
        high.append((acres * URBAN_PROBABILITIES).sum())

        # low urbanization is sum of pixel counts * probability for
        # probabilities >= 50% (25 of 50 runs)
        low.append(
            (acres[URBAN_THRESHOLD:] * URBAN_PROBABILITIES[URBAN_THRESHOLD:]).sum()
        )

    return {"high": high, "low": low}
