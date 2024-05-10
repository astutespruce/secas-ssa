import geopandas as gp
import pandas as pd
import shapely
import rasterio

from analysis.constants import M2_ACRES, SECAS_STATES
from analysis.lib.geometry import to_dict_all
from analysis.lib.raster import boundless_raster_geometry_mask, shift_window
from analysis.lib.stats.inundation_frequency import (
    extract_nlcd_inundation_frequency_by_mask,
)
from analysis.lib.stats.sarp import extract_sarp_huc12_stats
from analysis.lib.stats.slr import (
    extract_slr_depth_by_mask,
    extract_slr_projections_by_geometry,
)
from analysis.lib.stats.urban import extract_urban_by_mask
from analysis.lib.stats.nlcd import (
    extract_nlcd_landcover_by_mask,
    extract_nlcd_impervious_by_mask,
)
from analysis.lib.stats.se_blueprint_indicators import extract_indicator_by_mask
from api.settings import SHARED_DATA_DIR


data_dir = SHARED_DATA_DIR / "inputs"
bnd_dir = data_dir / "boundaries"
boundary_filename = bnd_dir / "se_boundary.feather"
extent_filename = bnd_dir / "blueprint_extent.tif"
extent_mask_filename = bnd_dir / "blueprint_extent_mask.tif"
states_filename = bnd_dir / "states.feather"


class AOIMaskConfig(object):
    """Class to store prescreen and rasterized mask information for masking
    other raster datasets"""

    def __init__(self, shapes, bounds):
        """_summary_

        Parameters
        ----------
        shapes : list-like of geometry objects that provide __geo_interface__
        bounds : list-like of [xmin, ymin, xmax, ymax]
        """
        # create mask and window
        with rasterio.open(extent_filename) as src:
            (
                self.shape_mask,
                self._mask_transform,
                self._mask_window,
            ) = boundless_raster_geometry_mask(src, shapes, bounds, all_touched=False)

            self.cellsize = src.res[0] * src.res[1] * M2_ACRES
            self.mask_pixels = (~self.shape_mask).sum()
            self.mask_acres = self.mask_pixels * self.cellsize

            data = src.read(1, window=self._mask_window, boundless=True)
            # count pixels within extent that are within the shape_mask
            self.overlap_acres = (data[~self.shape_mask]).sum() * self.cellsize
            if self.overlap_acres < 1e-6:
                self.overlap_acres = 0

            self.outside_se_acres = self.mask_acres - self.overlap_acres
            if self.outside_se_acres < 1e-6:
                self.outside_se_acres = 0

    def get_mask_window(self, target_transform):
        return shift_window(self._mask_window, self._mask_transform, target_transform)


async def get_analysis_unit_results(df, datasets, progress_callback=None):
    """Calculate statistics for each analysis unit

    Parameters
    ----------
    df : GeoDataFrame
        each row is a separate analysis unit
    datasets : list-like
        list of dataset IDs to query
    progress_callback : function, optional (default: None)
        function to call each after each analysis unit is processed

    Returns
    -------
    DataFrame
    """

    states = gp.read_feather(states_filename, columns=["state", "id", "geometry"])
    states = states.loc[states.id.isin(SECAS_STATES)]
    tree = shapely.STRtree(df.geometry.values)
    left, right = tree.query(states.geometry.values, predicate="intersects")
    state_join = (
        pd.DataFrame(
            {"state": states.state.values.take(left)}, index=df.index.values.take(right)
        )
        .groupby(level=0)
        .state.unique()
        .apply(sorted)
        .apply(lambda x: ", ".join(x))
        .rename("states")
    )

    df = df.join(state_join)
    df["count"] = shapely.get_num_geometries(df.geometry.values)
    df["acres"] = shapely.area(df.geometry.values) * M2_ACRES
    df["__geo__"] = to_dict_all(df.geometry.values)
    df["bounds"] = shapely.bounds(df.geometry.values).tolist()

    results = []

    # TODO: prefilter polygons to those that overlap boundary

    sarp_huc12_stats = None
    if (
        len(
            set(
                ["sarp_aquatic_barriers", "sarp_aquatic_network_alteration"]
            ).intersection(datasets)
        )
        > 0
    ):
        sarp_huc12_stats = extract_sarp_huc12_stats(df)

    count = 0

    for index, row in df.iterrows():
        print(f"Processing {index}")
        mask_config = AOIMaskConfig(shapes=[row.__geo__], bounds=row.bounds)

        result = {
            "pixels": mask_config.mask_pixels,
            "rasterized_acres": mask_config.mask_acres,
            "overlap": mask_config.overlap_acres,
            "outside_se": mask_config.outside_se_acres,
        }

        if mask_config.overlap_acres == 0:
            results.append(result)

            if progress_callback is not None:
                await progress_callback(100 * count / len(df))

            count += 1
            continue

        # Extract SLR
        if "slr_depth" in datasets or "slr_proj" in datasets:
            result["slr_depth"] = extract_slr_depth_by_mask(mask_config)

        if "slr_proj" in datasets:
            result["slr_proj"] = extract_slr_projections_by_geometry(row.geometry)

        # Extract urban
        if "urban" in datasets:
            result["urban"] = extract_urban_by_mask(mask_config)

        # Extract NLCD
        if "nlcd_landcover" in datasets:
            result["nlcd_landcover"] = extract_nlcd_landcover_by_mask(mask_config)

        if "nlcd_impervious" in datasets:
            result["nlcd_impervious"] = extract_nlcd_impervious_by_mask(mask_config)

        # Extract SE Blueprint indicators
        se_blueprint_indicators = [
            dataset for dataset in datasets if dataset.startswith("se_blueprint")
        ]
        for dataset in se_blueprint_indicators:
            result[dataset] = extract_indicator_by_mask(dataset, mask_config)

        # Extract inundation frequency
        if "nlcd_inundation_freq" in datasets:
            result["nlcd_inundation_freq"] = extract_nlcd_inundation_frequency_by_mask(
                mask_config
            )

        results.append(result)

        if progress_callback is not None:
            await progress_callback(100 * count / len(df))

        count += 1

    df = df[["states", "count", "acres"]].join(pd.DataFrame(results, index=df.index))

    if sarp_huc12_stats is not None:
        df = df.join(sarp_huc12_stats)

    return df
