from pathlib import Path

import numpy as np
import pygeos as pg
import geopandas as gp

from analysis.constants import (
    SLR_DEPTHS,
    SLR_NODATA_VALUES,
    SLR_YEARS,
    SLR_PROJ_COLUMNS,
    SLR_PROJ_SCENARIOS,
)
from analysis.lib.raster import (
    extract_count_in_geometry,
)

SLR_BINS = SLR_DEPTHS + [v["value"] for v in SLR_NODATA_VALUES]


src_dir = Path("../secas-blueprint/data/inputs/threats/slr")
slr_mask_filename = src_dir / "slr_mask.tif"
depth_filename = src_dir / "slr.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"


def extract_slr_depth_by_mask(
    shape_mask, window, cellsize, rasterized_acres, outside_se_acres
):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    shape_mask : ndarray, True outside shapes
    window : rasterio.windows.Window
        for extracting area of shape_mask from raster
    cellsize : float
        area of each pixel
    rasterized_acres : float
        area of shape_mask in acres
    outside_se_acres : float
        area outside of Southeast Blueprint within shape_mask

    Returns
    -------
    ndarray
        [area for 0ft inundation, area for 1ft, ..., area for 10f]
    """

    acres = (
        extract_count_in_geometry(
            depth_filename, shape_mask, window, bins=SLR_BINS, boundless=True
        )
        * cellsize
    )

    nodata_acres = rasterized_acres - outside_se_acres - acres.sum()
    # combine areas not modeled with SLR nodata areas
    acres[12] += nodata_acres

    # if all areas in the polygon have no inundation but have data, return
    # not inundated
    if np.allclose(acres[11], rasterized_acres):
        return "not_inundated"

    # if all areas in the polygon have no SLR data, return None
    if np.allclose(acres[12], rasterized_acres):
        return "not_available"

    # if all areas are in inland counties, return not applicable
    if np.allclose(acres[13], rasterized_acres):
        return "not_applicable"

    # accumulate values for depths 0-10ft
    acres[:11] = np.cumsum(acres[:11])

    return acres.round(2)


def extract_slr_projections_by_geometry(geometry):
    """Calculate area-weighted average of NOAA 2022 1-degree SLR projections

    Parameters
    ----------
    geometry : pygeos geometry
        Geometry (unioned) that defines the boundary for analysis

    Returns
    -------
    dict
        {
            "low": [2020 ft, ..., 2100 ft],
            ...,
            "high": [2020 ft, ..., 2100 ft],
        }
    """
    # intersect with 1-degree pixels; there should always be data available if
    # there are SLR depth data
    df = gp.read_feather(proj_filename)
    tree = pg.STRtree(df.geometry.values.data)
    df = df.iloc[tree.query(geometry, predicate="intersects")].copy()

    if len(df) == 0:
        return None

    # calculate area-weighted means
    intersection_area = pg.area(pg.intersection(df.geometry.values.data, geometry))
    area_factor = intersection_area / intersection_area.sum()

    projections = df[SLR_PROJ_COLUMNS].multiply(area_factor, axis=0).sum().round(2)

    return {
        SLR_PROJ_SCENARIOS[scenario]: [
            projections[f"{year}_{scenario}"] for year in SLR_YEARS
        ]
        for scenario in SLR_PROJ_SCENARIOS
    }
