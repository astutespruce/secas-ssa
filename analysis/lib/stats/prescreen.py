import geopandas as gp
import rasterio

from analysis.constants import DATASETS
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import WindowGeometryMask, get_window, window_overlaps
from analysis.lib.stats.inundation_frequency import inundation_frequency_dir
from analysis.lib.stats.landfire import src_dir as landfire_dir
from analysis.lib.stats.nlcd import src_dir as nlcd_dir
from analysis.lib.stats.se_blueprint_indicators import src_dir as indicators_dir
from analysis.lib.stats.slr import src_dir as slr_dir
from analysis.lib.stats.urban import src_dir as urban_dir
from api.settings import SHARED_DATA_DIR

data_dir = SHARED_DATA_DIR / "inputs"
boundary_filename = data_dir / "boundaries/se_boundary.feather"
extent_filename = data_dir / "boundaries/blueprint_extent.tif"
extent_mask_filename = data_dir / "boundaries/blueprint_extent_mask.tif"


indicators = [d for d in DATASETS.values() if d["id"].startswith("se_")]

# all datasets are pixel-aligned 30m, but may have different origin points
raster_datasets = {
    **{
        d["id"]: indicators_dir / d["filename"].replace(".tif", "_mask.tif")
        for d in indicators
    },
    "landfire_evt": landfire_dir / "landfire_evt_mask.tif",
    "nlcd_landcover": nlcd_dir / "landcover_mask.tif",
    "nlcd_impervious": nlcd_dir / "impervious_mask.tif",
    "nlcd_inundation_freq": inundation_frequency_dir
    / "nlcd_inundation_frequency_mask.tif",
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

    datasets = set()

    with rasterio.open(extent_mask_filename) as src:
        window = get_window(src, df.total_bounds)

        if not window_overlaps(window, src):
            return datasets

        shapes = to_dict_all(df.geometry.values)
        lowres_mask = WindowGeometryMask(src, window, shapes, all_touched=True)

        if lowres_mask.detect_data(src):
            # HUC12 data are always available within Southeast boundary
            datasets.add("sarp_aquatic_barriers")
            datasets.add("sarp_aquatic_network_alteration")

            # protected areas are generally available; there is no optimal way to check
            # this without running the full intersection
            datasets.add("protected_areas")

        else:
            return datasets

    for dataset_id, filename in raster_datasets.items():
        with rasterio.open(filename) as src:
            if lowres_mask.detect_data(src):
                datasets.add(dataset_id)

    if "slr_depth" in datasets:
        # SLR projections available where SLR depth is available
        datasets.add("slr_proj")

    return datasets
