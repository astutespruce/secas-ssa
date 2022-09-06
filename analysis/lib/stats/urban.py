from pathlib import Path

import numpy as np
import rasterio

from analysis.constants import (
    URBAN_YEARS,
    URBAN_PROBABILITIES,
    URBAN_BINS,
    URBAN_THRESHOLD,
    ACRES_PRECISION,
    M2_ACRES,
)
from analysis.lib.raster import (
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
    detect_data,
)


src_dir = Path("data/inputs/threats/urban")


# TODO: pass mask and window
def extract_by_geometry(shapes, bounds):
    """Calculate the area of overlap between shapes and urbanization
    for each decade from 2020 to 2100.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        {
            'shape_mask': <acres>,
            'urban': <acres already urban>,
            'projections': [<acres 2020>, <acres 2030>, ..., <acres 2100>]
        }
    """

    results = {}

    # prescreen to make sure data are present
    with rasterio.open(src_dir / "urban_mask.tif") as src:
        if not detect_data(src, shapes, bounds):
            return None

    # create mask and window
    with rasterio.open(src_dir / "urban_2020.tif") as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, shapes, bounds, all_touched=False
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(ACRES_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    projections = {"High": [], "Low": []}

    for year in URBAN_YEARS:
        filename = src_dir / f"urban_{year}.tif"
        counts = extract_count_in_geometry(
            filename, shape_mask, window, URBAN_BINS, boundless=True
        )

        if year == 2020:
            # extract area already urban (in index 51)
            results["urban"] = (
                (counts[51] * cellsize).round(ACRES_PRECISION).astype("float32")
            )

        # high urbanization is sum of pixel counts * probability for all urbanized pixels
        projections["High"].append(
            ((counts * URBAN_PROBABILITIES).sum() * cellsize).round(ACRES_PRECISION)
        )

        # low urbanization is sum of pixel counts * probability for probabilities >= 50% (25 of 50 runs)
        projections["Low"].append(
            (
                (counts[URBAN_THRESHOLD:] * URBAN_PROBABILITIES[URBAN_THRESHOLD:]).sum()
                * cellsize
            ).round(ACRES_PRECISION)
        )

    results["projections"] = projections

    return results
