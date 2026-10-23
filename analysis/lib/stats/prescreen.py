import geopandas as gp
import rasterio

from analysis.constants import ANALYSIS_BOUNDS, DATASETS, MASK_RESOLUTION
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import RasterExtent, WindowGeometryMask
from analysis.lib.stats.inundation_frequency import inundation_frequency_dir
from analysis.lib.stats.landfire import src_dir as landfire_dir
from analysis.lib.stats.nlcd import src_dir as nlcd_dir
from analysis.lib.stats.se_blueprint_indicators import src_dir as indicators_dir
from analysis.lib.stats.slr import src_dir as slr_dir
from analysis.lib.stats.urban import src_dir as urban_dir
from api.settings import SHARED_DATA_DIR

data_dir = SHARED_DATA_DIR / "inputs"

lowres_analysis_extent = RasterExtent(ANALYSIS_BOUNDS, resolution=MASK_RESOLUTION)


indicators = [d for d in DATASETS.values() if d["id"].startswith("se_")]

# all datasets are pixel-aligned 30m, but may have different origin points
raster_datasets = {
    **{d["id"]: indicators_dir / d["filename"].replace(".tif", "_mask.tif") for d in indicators},
    "landfire_evt": landfire_dir / "landfire_evt_mask.tif",
    "nlcd_landcover": nlcd_dir / "landcover_mask.tif",
    "nlcd_impervious": nlcd_dir / "impervious_mask.tif",
    "nlcd_inundation_freq": inundation_frequency_dir / "nlcd_inundation_frequency_mask.tif",
    "slr_depth": slr_dir / "slr_mask.tif",
    "urban": urban_dir / "urban_mask.tif",
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
