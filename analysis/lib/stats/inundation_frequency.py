from collections import defaultdict

import rasterio

from analysis.constants import DATASETS, NLCD_INDEXES, NLCD_INUNDATION_FREQUENCY
from api.settings import DATA_DIR

BINS = list(NLCD_INUNDATION_FREQUENCY.keys())

src_dir = DATA_DIR / "inputs"

mask_filename = src_dir / DATASETS["nlcd_inundation_freq"]["filename"].replace(".tif", "_mask.tif")


def open_rasters(datasets):
    """Open raster file for each dataset included in dataset_ids

    Parameters
    ----------
    dataset_ids : list of str
        list of dataset IDs

    Returns
    -------
    dict
        {<dataset_id>: <rasterio file handle>, ...}
    """
    if "nlcd_inundation_freq" in datasets:
        return {"nlcd_inundation_freq": rasterio.open(src_dir / DATASETS["nlcd_inundation_freq"]["filename"])}

    return {}


def summarize_nlcd_inundation_frequency_in_aoi(src, rasterized_geometry):
    """Calculate the area of overlap between shapes and inundation frequency
    by NLCD 2021 land cover class.

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    src : rasterio reader
    rasterized_geometry : RasterizedGeometry

    Returns
    -------

    dict

        {<NLCD index>: [<inundation freq bin 0 acres>,...], ...}
    """

    acres = rasterized_geometry.get_acres_by_bin(src, BINS)

    results = defaultdict(list)
    for key, entry in NLCD_INUNDATION_FREQUENCY.items():
        results[NLCD_INDEXES[entry["nlcd"]]["label"]].append(acres[key])

    # drop any that are not present
    results = {k: v for k, v in results.items() if sum(v) > 0}

    return results
