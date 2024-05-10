import geopandas as gp
import shapely

from analysis.constants import DATASETS
from analysis.lib.raster import detect_data
from analysis.lib.geometry import to_dict_all
from analysis.lib.stats.slr import src_dir as slr_dir
from analysis.lib.stats.nlcd import src_dir as nlcd_dir
from analysis.lib.stats.urban import src_dir as urban_dir
from analysis.lib.stats.se_blueprint_indicators import src_dir as indicators_dir
from analysis.lib.stats.inundation_frequency import inundation_frequency_dir
from api.settings import SHARED_DATA_DIR


data_dir = SHARED_DATA_DIR / "inputs"
boundary_filename = data_dir / "boundaries/se_boundary.feather"


indicators = [d for d in DATASETS.values() if d["id"].startswith("se_")]

# all datasets are pixel-aligned 30m, but may have different origin points
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


def verify_overlap(df):
    bnd = gp.read_feather(boundary_filename).geometry.values[0]
    return (
        len(shapely.STRtree(df.geometry.values).query(bnd, predicate="intersects")) > 0
    )


def get_available_datasets(df):
    shapes = to_dict_all(df.geometry.values)

    available_datasets = detect_data(
        raster_datasets,
        shapes,
        df.total_bounds,
    )

    # SLR projections available where SLR depth is available
    available_datasets["slr_proj"] = available_datasets.get("slr_depth", False)

    # HUC12 data are always available within Southeast boundary
    available_datasets["sarp_aquatic_barriers"] = True
    available_datasets["sarp_aquatic_network_alteration"] = True

    return available_datasets
