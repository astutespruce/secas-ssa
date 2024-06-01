import geopandas as gp
import numpy as np
import rasterio
import shapely

from analysis.constants import (
    SLR_DEPTHS,
    SLR_NODATA_VALUES,
    SLR_YEARS,
    SLR_PROJ_COLUMNS,
    SLR_PROJ_SCENARIOS,
)
from api.settings import SHARED_DATA_DIR

SLR_BINS = SLR_DEPTHS + [v["value"] for v in SLR_NODATA_VALUES]


src_dir = SHARED_DATA_DIR / "inputs/threats/slr"
slr_mask_filename = src_dir / "slr_mask.tif"
depth_filename = src_dir / "slr.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"


def summarize_slr_in_aoi(rasterized_geometry):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    Data are at 30 meters, pixel-aligned to extent raster.

    Parameters
    ----------
    rasterized_geometry : RasterizedGeometry

    Returns
    -------
    ndarray
        [area for 0ft inundation, area for 1ft, ..., area for 10f]
    """

    with rasterio.open(depth_filename) as src:
        acres = rasterized_geometry.get_acres_by_bin(src, bins=SLR_BINS)

    nodata_acres = (
        rasterized_geometry.acres - rasterized_geometry.outside_se_acres - acres.sum()
    )

    if nodata_acres < 1e-6:
        nodata_acres = 0

    # set NODATA into value 13
    acres[13] += nodata_acres

    # accumulate values for depths 0-10ft
    acres[:11] = np.cumsum(acres[:11])

    return acres.round(2)


def extract_slr_projections_by_geometry(geometry):
    """Calculate area-weighted average of NOAA 2022 1-degree SLR projections

    Parameters
    ----------
    geometry : shapely geometry
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
    tree = shapely.STRtree(df.geometry.values)
    df = df.iloc[tree.query(geometry, predicate="intersects")].copy()

    if len(df) == 0:
        return None

    # calculate area-weighted means
    intersection_area = shapely.area(shapely.intersection(df.geometry.values, geometry))
    area_factor = intersection_area / intersection_area.sum()

    projections = df[SLR_PROJ_COLUMNS].multiply(area_factor, axis=0).sum().round(2)

    return {
        SLR_PROJ_SCENARIOS[scenario]: [
            projections[f"{year}_{scenario}"] for year in SLR_YEARS
        ]
        for scenario in SLR_PROJ_SCENARIOS
    }
