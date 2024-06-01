import geopandas as gp
import numpy as np
import pandas as pd
import shapely
import rasterio

from analysis.constants import M2_ACRES, SECAS_STATES
from analysis.lib.geometry import to_dict
from analysis.lib.raster import WindowGeometryMask, get_window, get_overlapping_windows
from analysis.lib.stats.inundation_frequency import (
    summarize_nlcd_inundation_frequency_in_aoi,
)
from analysis.lib.stats.sarp import extract_sarp_huc12_stats
from analysis.lib.stats.slr import (
    summarize_slr_in_aoi,
    extract_slr_projections_by_geometry,
)
from analysis.lib.stats.urban import summarize_urban_in_aoi
from analysis.lib.stats.nlcd import (
    summarize_nlcd_landcover_in_aoi,
    summarize_nlcd_impervious_in_aoi,
)
from analysis.lib.stats.se_blueprint_indicators import summarize_indicator_in_aoi
from api.settings import SHARED_DATA_DIR


data_dir = SHARED_DATA_DIR / "inputs"
bnd_dir = data_dir / "boundaries"
boundary_filename = bnd_dir / "se_boundary.feather"
extent_filename = bnd_dir / "blueprint_extent.tif"
extent_mask_filename = bnd_dir / "blueprint_extent_mask.tif"
states_filename = bnd_dir / "states.feather"


WINDOW_SIZE = 2048  # approx 16 MB for 8 bit data


class RasterizedGeometry(object):
    """Helper class to detect and extract data for a rasterized geometry
    Similar to RasterizedGeometry in secas-blueprint respository but without a
    low resolution mask for detecting datasets (handled prior to calling here)
    """

    def __init__(self, geometry):
        """_summary_

        Parameters
        ----------
        geometry : shapely geometry
        """
        self.bounds = shapely.bounds(geometry)

        all_shapes = [to_dict(geometry)]

        # create masks and windows
        with rasterio.open(extent_filename) as src:
            windows, ratio = get_overlapping_windows(
                src, geometry, bounds=self.bounds, window_size=WINDOW_SIZE
            )

            num_windows = len(windows)
            self.masks = []

            # threshold for using windows determined by testing performance
            if num_windows >= 50 or (num_windows > 1 and ratio <= 0.25):
                print(f"Using {len(windows)} windows for reading (ratio: {ratio:.3f})")
                for window in windows:
                    # clip geometry to window then rasterize
                    clipped = shapely.clip_by_rect(geometry, *src.window_bounds(window))
                    mask = WindowGeometryMask(src, window, shapes=[to_dict(clipped)])
                    self.masks.append(mask)

            else:
                print(
                    f"Using 1 window for reading (overlapping windows: {num_windows}, ratio: {ratio:.3f})"
                )
                window = get_window(src, self.bounds)
                mask = WindowGeometryMask(src, window, all_shapes)
                self.masks.append(mask)

            # cell size in acres
            self.cellsize = src.res[0] * src.res[1] * M2_ACRES

            self.pixels = sum(mask.shape_mask.sum() for mask in self.masks)
            self.acres = self.pixels * self.cellsize

            self.within_se_pixels = sum(
                mask.get_pixel_count_by_bin(src, bins=[0, 1])[1] for mask in self.masks
            )
            self.within_se_acres = self.within_se_pixels * self.cellsize

            self.outside_se_acres = (
                self.pixels - self.within_se_pixels
            ) * self.cellsize

    def get_pixel_count_by_bin(self, dataset, bins):
        """Get count of pixels in each bin

        Parameters
        ----------
        dataset : open rasterio dataset
        bins : list-like
            List-like of values ranging from 0 to max value (not sparse!).
            Counts will be generated that correspond to this list of bins.

        Returns
        -------
        ndarray
            Total number of pixels for each bin
        """
        return np.sum(
            [mask.get_pixel_count_by_bin(dataset, bins) for mask in self.masks], axis=0
        )

    def get_acres_by_bin(self, dataset, bins):
        """Get acres in each bin

        Parameters
        ----------
        dataset : open rasterio dataset
        bins : list-like
            List-like of values ranging from 0 to max value (not sparse!).
            Counts will be generated that correspond to this list of bins.

        Returns
        -------
        ndarray
            Total number of acres for each bin
        """
        return self.get_pixel_count_by_bin(dataset, bins) * self.cellsize


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
    left, right = shapely.STRtree(states.geometry.values).query(
        df.geometry.values, predicate="intersects"
    )
    state_join = (
        pd.DataFrame(
            {"state": states.state.values.take(right)}, index=df.index.values.take(left)
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
    df["bounds"] = shapely.bounds(df.geometry.values).tolist()

    results = []

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
        rasterized_geometry = RasterizedGeometry(row.geometry)

        result = {
            "pixels": rasterized_geometry.pixels,
            "rasterized_acres": rasterized_geometry.acres,
            "overlap": rasterized_geometry.within_se_acres,
            "outside_se": rasterized_geometry.outside_se_acres,
        }

        # short-circuit if there are no overlapping pixels
        if rasterized_geometry.within_se_acres == 0:
            results.append(result)

            if progress_callback is not None:
                await progress_callback(100 * count / len(df))

            count += 1
            continue

        # Extract SLR
        if "slr_depth" in datasets or "slr_proj" in datasets:
            result["slr_depth"] = summarize_slr_in_aoi(rasterized_geometry)
            # extract_slr_depth_by_mask(mask_config)

        if "slr_proj" in datasets:
            result["slr_proj"] = extract_slr_projections_by_geometry(row.geometry)

        # Extract urban
        if "urban" in datasets:
            result["urban"] = summarize_urban_in_aoi(rasterized_geometry)

        # Extract NLCD
        if "nlcd_landcover" in datasets:
            result["nlcd_landcover"] = summarize_nlcd_landcover_in_aoi(
                rasterized_geometry
            )

        if "nlcd_impervious" in datasets:
            result["nlcd_impervious"] = summarize_nlcd_impervious_in_aoi(
                rasterized_geometry
            )

        # Extract SE Blueprint indicators
        se_blueprint_indicators = [
            dataset for dataset in datasets if dataset.startswith("se_blueprint")
        ]
        for dataset in se_blueprint_indicators:
            result[dataset] = summarize_indicator_in_aoi(dataset, rasterized_geometry)

        # Extract inundation frequency
        if "nlcd_inundation_freq" in datasets:
            result["nlcd_inundation_freq"] = summarize_nlcd_inundation_frequency_in_aoi(
                rasterized_geometry
            )

        results.append(result)

        if progress_callback is not None:
            await progress_callback(100 * count / len(df))

        count += 1

    df = df[["states", "count", "acres"]].join(pd.DataFrame(results, index=df.index))

    if sarp_huc12_stats is not None:
        df = df.join(sarp_huc12_stats)

    return df
