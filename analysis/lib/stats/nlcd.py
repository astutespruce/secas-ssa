import numpy as np
import rasterio

from analysis.constants import DATASETS, NLCD_INDEXES, NLCD_YEARS
from api.settings import DATA_DIR

src_dir = DATA_DIR / "inputs"

landcover_mask_filename = src_dir / DATASETS["nlcd_landcover"]["filename"].format(year="mask")
impervious_mask_filename = src_dir / DATASETS["nlcd_impervious"]["filename"].format(year="mask")


def open_rasters(dataset_ids):
    """Open raster file for each nlcd dataset included in dataset_ids

    Parameters
    ----------
    dataset_ids : list of str
        list of dataset IDs

    Returns
    -------
    dict
        {<dataset_id>_<year>: <rasterio file handle>, ...}
    """
    out = {}
    if "nlcd_landcover" in dataset_ids:
        filename = DATASETS["nlcd_landcover"]["filename"]
        out.update(
            {f"nlcd_landcover_{year}": rasterio.open(src_dir / filename.format(year=year)) for year in NLCD_YEARS}
        )
    if "nlcd_impervious" in dataset_ids:
        filename = DATASETS["nlcd_impervious"]["filename"]
        out.update(
            {f"nlcd_impervious_{year}": rasterio.open(src_dir / filename.format(year=year)) for year in NLCD_YEARS}
        )

    return out


def summarize_nlcd_landcover_in_aoi(files, rasterized_geometry):
    """Calculate the area of overlap between shapes and NLCD indexes (not codes)
    for each available year.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    files : dict
            lookup of nlcd_nlcd_{year} to open raster file
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    dict
        {<NLCD label>: [<acres 2020>, <acres 2030>, ..., <acres 2100>], ...}
    """

    bins = list(NLCD_INDEXES.keys())
    areas = []

    for year in NLCD_YEARS:
        acres = rasterized_geometry.get_acres_by_bin(files[f"nlcd_landcover_{year}"], bins)
        areas.append(acres)

    # Transpose and convert to dict, only keep those that have areas
    areas = np.array(areas).T

    results = {NLCD_INDEXES[i]["label"]: areas[i].tolist() for i in NLCD_INDEXES if areas[i].sum()}

    return results


def summarize_nlcd_impervious_in_aoi(files, rasterized_geometry):
    """Calculate total amount of impervious surface within shape_mask based on
    count per percent (0-100) * percent

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    files : dict
        lookup of nlcd_impervious_{year} to open raster file
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    list
        [<acres 2020>, <acres 2030>, ..., <acres 2100>, <NODATA acres>]
    """

    percent_values = np.arange(0, 1.01, 0.01)

    bins = percent_values.tolist()
    areas = []

    for year in NLCD_YEARS:
        acres = rasterized_geometry.get_acres_by_bin(files[f"nlcd_impervious_{year}"], bins)

        if year == NLCD_YEARS[0]:
            total_acres = acres.sum()
            outside_nlcd_acres = rasterized_geometry.acres - total_acres
            if outside_nlcd_acres < 1e-6:
                outside_nlcd_acres = 0

        areas.append((percent_values * acres).sum())

    # Transpose
    return np.array(areas).T.tolist() + [outside_nlcd_acres]
