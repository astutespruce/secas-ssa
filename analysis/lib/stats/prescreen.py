import geopandas as gp
import rasterio

from analysis.constants import ANALYSIS_BOUNDS, DATASETS, MASK_RESOLUTION
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import RasterExtent, WindowGeometryMask
from analysis.lib.stats.inundation_frequency import mask_filename as inundation_frequency_mask_filename
from analysis.lib.stats.landfire import mask_filename as landfire_mask_filename
from analysis.lib.stats.nlcd import impervious_mask_filename, landcover_mask_filename
from analysis.lib.stats.se_blueprint_indicators import src_dir as indicators_dir
from analysis.lib.stats.slr import mask_filename as slr_mask_filename
from analysis.lib.stats.urban import mask_filename as urban_mask_filename

lowres_analysis_extent = RasterExtent(ANALYSIS_BOUNDS, resolution=MASK_RESOLUTION)


raster_datasets = {
    **{
        d["id"]: indicators_dir / d["filename"].replace(".tif", "_mask.tif")
        for d in DATASETS.values()
        if d["id"].startswith("se_blueprint")
    },
    "landfire_evt": landfire_mask_filename,
    "nlcd_landcover": landcover_mask_filename,
    "nlcd_impervious": impervious_mask_filename,
    "nlcd_inundation_freq": inundation_frequency_mask_filename,
    "slr_depth": slr_mask_filename,
    "urban": urban_mask_filename,
}


def get_available_datasets(df: gp.GeoDataFrame) -> set[str]:
    """Find all datasets that overlap features in df

    Parameters
    ----------
    df : gp.GeoDataFrame

    Returns
    -------
    set[str]
    """

    window = lowres_analysis_extent.get_window(df.total_bounds, boundless=False)

    if window.width == 0 or window.height == 0:
        return set()

    shapes = to_dict_all(df.geometry.values)
    lowres_mask = WindowGeometryMask(lowres_analysis_extent.transform, window, shapes, all_touched=True)

    # these datasets are generally available; there is no optimal way to check
    # this without running the full intersection
    datasets = {"sarp_aquatic_barriers", "sarp_aquatic_network_alteration", "protected_areas"}

    for dataset_id, filename in raster_datasets.items():
        with rasterio.open(filename) as src:
            if lowres_mask.detect_data(src):
                datasets.add(dataset_id)

    if "slr_depth" in datasets:
        # SLR projections available where SLR depth is available
        datasets.add("slr_proj")

    return datasets
