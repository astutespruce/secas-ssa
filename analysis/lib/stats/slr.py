from pathlib import Path

from progress.bar import Bar
import numpy as np
import pandas as pd
import pygeos as pg
import geopandas as gp
import rasterio

from analysis.constants import (
    AREA_PRECISION,
    M2_ACRES,
    SLR_PROJ_COLUMNS,
    SLR_YEARS,
    SLR_PROJ_SCENARIOS,
)
from analysis.lib.raster import (
    detect_data,
    boundless_raster_geometry_mask,
    extract_count_in_geometry,
)


src_dir = Path("data/inputs/threats/slr")
slr_mask_filename = src_dir / "slr_mask.tif"
depth_filename = src_dir / "slr.tif"
proj_filename = src_dir / "noaa_1deg_cells.feather"


def extract_slr_by_geometry(geometry, shapes, bounds):
    """Calculate the area of overlap between geometries and each level of SLR
    between 0 (currently inundated) and 6 meters.

    Values are cumulative; the total area inundated is added to each higher
    level of SLR

    This is only applicable to inland (non-marine) areas that are near the coast.

    Parameters
    ----------
    geometry : pygeos geometry
        Geometry (unioned) that defines the boundary for analysis; same as shapes
    shapes : list-like of geometry objects that provide __geo_interface__
        Should be limited to features that intersect with bounds of SLR datasets
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        {
            "shape_mask": <area>,
            "depth": [area for 0ft inundation, area for 1ft, ..., area for 10f],
            "projections": {
                "low": [2020 ft, ..., 2100 ft],
                ...,
                "high": [2020 ft, ..., 2100 ft],
            }
        }
    """

    # prescreen to make sure data are present
    with rasterio.open(slr_mask_filename) as src:
        if not detect_data(src, shapes, bounds):
            return None

    results = {}

    # create mask and window
    with rasterio.open(depth_filename) as src:
        try:
            shape_mask, transform, window = boundless_raster_geometry_mask(
                src, shapes, bounds, all_touched=False
            )

        except ValueError:
            return None

        # square meters to acres
        cellsize = src.res[0] * src.res[1] * M2_ACRES

        data = src.read(1, window=window, boundless=True)
        nodata = src.nodatavals[0]
        mask = (data == nodata) | shape_mask
        data = np.where(mask, nodata, data)

    results["shape_mask"] = (
        ((~shape_mask).sum() * cellsize).round(AREA_PRECISION).astype("float32")
    )

    if results["shape_mask"] == 0:
        return None

    bins = np.arange(11)
    counts = extract_count_in_geometry(
        depth_filename, shape_mask, window, bins=bins, boundless=True
    )

    # accumulate values
    for bin in bins[1:]:
        counts[bin] = counts[bin] + counts[bin - 1]

    results["depth"] = (counts * cellsize).round(AREA_PRECISION).tolist()

    # intersect with 1-degree pixels; there should always be data available if
    # there are SLR depth data
    df = gp.read_feather(proj_filename)
    tree = pg.STRtree(df.geometry.values.data)
    df = df.iloc[tree.query(geometry, predicate="intersects")].copy()

    # calculate area-weighted means
    intersection_area = pg.area(pg.intersection(df.geometry.values.data, geometry))
    area_factor = intersection_area / intersection_area.sum()

    projections = df[SLR_PROJ_COLUMNS].multiply(area_factor, axis=0).sum().round(2)

    results["projections"] = {
        SLR_PROJ_SCENARIOS[scenario]: [
            projections[f"{year}_{scenario}"] for year in SLR_YEARS
        ]
        for scenario in SLR_PROJ_SCENARIOS
    }

    return results
