import numpy as np
import shapely

from analysis.constants import ANALYSIS_BOUNDS, M2_ACRES, STANDARD_RESOLUTION
from analysis.lib.geometry import to_dict
from analysis.lib.raster import RasterExtent, WindowGeometryMask
from api.settings import SHARED_DATA_DIR

data_dir = SHARED_DATA_DIR / "inputs"
bnd_dir = data_dir / "boundaries"
states_filename = bnd_dir / "states.feather"

WINDOW_SIZE = 2048  # approx 16 MB for 8 bit data

# analysis extent defines the transform and other properties of the full analysis extent
# instead of needing an extent raster
analysis_extent = RasterExtent(ANALYSIS_BOUNDS, resolution=STANDARD_RESOLUTION)


class RasterizedGeometry(object):
    """Helper class to detect and extract data for a rasterized geometry."""

    def __init__(self, geometry):
        """_summary_

        Parameters
        ----------
        geometry : shapely geometry
        """
        self.bounds = shapely.bounds(geometry)

        all_shapes = [to_dict(geometry)]

        # create masks and windows
        windows, ratio = analysis_extent.get_overlapping_windows(geometry, bounds=self.bounds, window_size=WINDOW_SIZE)

        num_windows = len(windows)
        self.masks = []

        # threshold for using windows determined by testing performance
        if num_windows >= 50 or (num_windows > 1 and ratio <= 0.25):
            for window in windows:
                # clip geometry to window then rasterize
                clipped = shapely.clip_by_rect(geometry, *analysis_extent.window_bounds(window))
                mask = WindowGeometryMask(analysis_extent.transform, window, shapes=[to_dict(clipped)])
                self.masks.append(mask)

        else:
            window = analysis_extent.get_window(self.bounds)
            mask = WindowGeometryMask(analysis_extent.transform, window, all_shapes)
            self.masks.append(mask)

        # cell size in acres
        self.cellsize = STANDARD_RESOLUTION * STANDARD_RESOLUTION * M2_ACRES

        self.pixels = sum(mask.shape_mask.sum() for mask in self.masks)
        self.acres = self.pixels * self.cellsize

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
        count = np.zeros((len(bins),), dtype="uint64")
        for mask in self.masks:
            mask.get_pixel_count_by_bin(dataset, out=count)

        return count

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
