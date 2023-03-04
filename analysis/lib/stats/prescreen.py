from analysis.constants import DATASETS
from analysis.lib.raster import detect_data

from analysis.lib.stats.slr import src_dir as slr_dir
from analysis.lib.stats.nlcd import src_dir as nlcd_dir
from analysis.lib.stats.urban import src_dir as urban_dir
from analysis.lib.stats.se_blueprint_indicators import src_dir as indicators_dir
from analysis.lib.stats.inundation_frequency import inundation_frequency_dir


indicators = [d for d in DATASETS.values() if d["id"].startswith("se_")]

# all datasets are pixel-aligned 30m
raster_datasets = {
    **{
        d["id"]: indicators_dir / d["filename"].replace(".tif", "_mask.tif")
        for d in indicators
    },
    "slr_depth": slr_dir / "slr_mask.tif",
    "urban": urban_dir / "urban_mask.tif",
    "nlcd_landcover": nlcd_dir / "landcover_mask.tif",
    "nlcd_impervious": nlcd_dir / "impervious_mask.tif",
    "nlcd_inundation_freq": inundation_frequency_dir
    / "nlcd_inundation_frequency_mask.tif",
}


def get_available_datasets(shapes, bounds):
    available_datasets = detect_data(raster_datasets, shapes, bounds)
    available_datasets["slr_proj"] = available_datasets["slr_depth"]

    # HUC12 data are always available
    available_datasets["sarp_aquatic_barriers"] = True
    available_datasets["sarp_aquatic_network_alteration"] = True

    return available_datasets
