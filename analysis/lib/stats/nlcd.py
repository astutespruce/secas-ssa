import numpy as np
import rasterio

from analysis.constants import NLCD_YEARS, NLCD_INDEXES
from api.settings import SHARED_DATA_DIR

src_dir = SHARED_DATA_DIR / "inputs/nlcd"
landcover_filename = str(src_dir / "landcover_{year}.tif")
impervious_filename = str(src_dir / "impervious_{year}.tif")

PERCENTS = np.arange(0, 1.01, 0.01)


def summarize_nlcd_landcover_in_aoi(rasterized_geometry):
    """Calculate the area of overlap between shapes and NLCD indexes (not codes)
    for each available year.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    dict
        {<NLCD index>: [<acres 2020>, <acres 2030>, ..., <acres 2100>], ...}
    """

    bins = list(NLCD_INDEXES.keys())
    areas = []

    for year in NLCD_YEARS:
        with rasterio.open(landcover_filename.format(year=year)) as src:
            acres = rasterized_geometry.get_acres_by_bin(src, bins)

        areas.append(acres)

    # Transpose and convert to dict, only keep those that have areas
    areas = np.array(areas).T

    results = {
        NLCD_INDEXES[i]["label"]: areas[i].tolist()
        for i in NLCD_INDEXES
        if areas[i].sum()
    }

    return results


def summarize_nlcd_impervious_in_aoi(rasterized_geometry):
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
        with rasterio.open(impervious_filename.format(year=year)) as src:
            acres = rasterized_geometry.get_acres_by_bin(src, bins)

        areas.append((PERCENTS * acres).sum())

    # Transpose
    return np.array(areas).T.tolist()
