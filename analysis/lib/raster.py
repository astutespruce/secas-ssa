from itertools import product
import math

from affine import Affine
import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.mask import geometry_mask
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window
import shapely

from analysis.constants import OVERVIEW_FACTORS, DATA_CRS
from api.settings import SHARED_DATA_DIR

data_dir = SHARED_DATA_DIR / "inputs"
extent_filename = data_dir / "boundaries/blueprint_extent.tif"
extent_mask_filename = data_dir / "boundaries/blueprint_extent_mask.tif"


def get_window(dataset, bounds, boundless=True):
    """Calculate the window into dataset that contains bounds, for boundless reading.

    If boundless is False and the window falls outside the bounds of the dataset,
    one or both of the dimensions may be 0.

    Parameters
    ----------
    dataset : open rasterio dataset
    bounds : list-like of [xmin, ymin, xmax, ymax]
    boundless : bool, optional (default: True)
        if True, returned window may extend beyond the dataset

    Returns
    -------
    rasterio.windows.Window instance
    """
    window = dataset.window(*bounds)
    window_floored = window.round_offsets(op="floor", pixel_precision=3)
    col_off = window_floored.col_off
    row_off = window_floored.row_off
    width = math.ceil(window.width + window.col_off - window_floored.col_off)
    height = math.ceil(window.height + window.row_off - window_floored.row_off)

    window = Window(col_off, row_off, width, height)
    if boundless:
        return window

    return clip_window(window, dataset.width, dataset.height)


def clip_window(window, max_width, max_height):
    """
    Convert a boundless window to a bounded window where the col_off and
    row_off are >= 0 and height and width fit within max_width and height.

    Parameters
    ----------
    window : rasterio.windows.Window
    max_width : int
    max_height : int

    Returns
    -------
    rasterio.windows.Window
    """
    col_off = window.col_off
    row_off = window.row_off
    width = window.width
    height = window.height
    if col_off < 0:
        width = max(width + col_off, 0)
        col_off = 0
    if row_off < 0:
        height = max(height + row_off, 0)
        row_off = 0
    if col_off + width > max_width:
        width = max(max_width - col_off, 0)
    if row_off + height > max_height:
        height = max(max_height - row_off, 0)

    return Window(col_off, row_off, width, height)


def shift_window(window, window_transform, transform):
    """Shift window based on one transform to a window appropriate for a different
    transform.

    Parameters
    ----------
    window : rasterio.windows.Window
    window_transform : affine.Affine
        transform upon which window is based
    transform : affine.Affine
        the transform to which to shift the window

    Returns
    -------
    rasterio.windows.Window
    """
    col_off = int(round((window_transform.c - transform.c) / transform.a))
    row_off = int(round((window_transform.f - transform.f) / transform.e))
    return Window(
        col_off=col_off, row_off=row_off, width=window.width, height=window.height
    )


def boundless_raster_geometry_mask(dataset, shapes, bounds, all_touched=False):
    """Alternative to rasterio.mask::raster_geometry_mask that allows boundless
    reads from raster data sources.

    Parameters
    ----------
    dataset : open rasterio dataset
    shapes : list-like of geometry objects that provide __geo_interface__
    bounds : list-like of [xmin, ymin, xmax, ymax]
    all_touched : bool, optional (default: False)
    """

    window = get_window(dataset, bounds)

    transform = dataset.window_transform(window)
    out_shape = (int(window.height), int(window.width))
    mask = geometry_mask(
        shapes, transform=transform, out_shape=out_shape, all_touched=all_touched
    )

    return mask, transform, window


def detect_data(datasets, shapes, bounds):
    """Detect if any data pixels are found in shapes.

    Typically this is performed against a reduced resolution version of a data
    file as a pre-screening step.

    Parameters
    ----------
    datasets : dict
        {<id>: <filename>, ...}
    shapes : list-like of GeoJSON features
    bounds : list-like of [xmin, ymin, xmax, ymax]

    Returns
    -------
    dict
        {<id>: True if there are data pixels present in shapes, otherwise False}
    """

    with rasterio.open(extent_mask_filename) as src:
        window = get_window(src, bounds)

        # fail fast if no overlap with data extent
        clipped_window = clip_window(window, max_width=src.width, max_height=src.height)
        if clipped_window.width == 0 or clipped_window.height == 0:
            return {}

        transform = src.window_transform(window)

        # create mask
        # note: this intentionally uses all_touched=True
        mask = geometry_mask(
            shapes,
            transform=transform,
            out_shape=(window.height, window.width),
            all_touched=True,
        )

    available_datasets = {}
    for id, filename in datasets.items():
        with rasterio.open(filename) as src:
            read_window = shift_window(window, transform, src.transform)
            clipped_window = clip_window(
                read_window, max_width=src.width, max_height=src.height
            )
            if clipped_window.width == 0 or clipped_window.height == 0:
                available_datasets[id] = False
                continue

            data = src.read(1, window=read_window, boundless=True)
            available_datasets[id] = np.any(
                data[~(mask | (data == np.uint8(src.nodata)))]
            ).item()

    return available_datasets


def create_lowres_mask(filename, outfilename, resolution, ignore_zero=False):
    """Create a resampled lower resolution mask.

    This is used to pre-screen areas where data are present for higher-resolution
    analysis.

    Any non-nodata pixels are converted to 1 based on the max pixel value per
    resampled pixel.

    Parameters
    ----------
    filename : str
    outfilename : str
    resolution : int
        target resolution
    ignore_zero : bool, optional (default: False)
        if True, 0 values are treated as nodata
    """
    with rasterio.open(filename) as src:
        nodata = src.nodatavals[0]
        # output is still precisely aligned to same upper left coordinate
        dst_transform = Affine(
            resolution, 0, src.transform.c, 0, -resolution, src.transform.f
        )
        width = math.ceil((src.width * src.transform.a) / resolution)
        height = math.ceil((src.height * (-src.transform.e)) / resolution)

        with WarpedVRT(
            src,
            width=width,
            height=height,
            nodata=nodata,
            transform=dst_transform,
            resampling=Resampling.max,
        ) as vrt:
            data = vrt.read()

            if ignore_zero:
                data[data == 0] = nodata

            data[data != nodata] = 1

            meta = src.profile.copy()
            meta.update({"width": width, "height": height, "transform": dst_transform})

            # add compression
            meta["compress"] = "lzw"

            with rasterio.open(outfilename, "w", **meta) as out:
                out.write(data)


def add_overviews(filename):
    """Add overviews to file for faster rendering.

    Parameters
    ----------
    filename : str
    """
    with rasterio.open(filename, "r+") as src:
        src.build_overviews(OVERVIEW_FACTORS, Resampling.nearest)


def extract_window(src, window, transform, nodata):
    """Extract raster data from src within window, and warp to DATA_CRS

    Parameters
    ----------
    src : open rasterio Dataset
    window : rasterio Window boject
    transform : rasterio Transform object
    nodata : int or float

    Returns
    -------
    2d array
    """
    vrt = WarpedVRT(
        src,
        width=window.width,
        height=window.height,
        nodata=nodata,
        transform=transform,
        crs=DATA_CRS,
        resampling=Resampling.nearest,
    )

    return vrt.read()[0]


def write_raster(filename, data, transform, crs, nodata):
    """Write data to a GeoTIFF.

    Parameters
    ----------
    filename : str
    data : 2d ndarray
    transform : rasterio transform object
    crs : rasterio.crs object
    nodata : int
    """

    meta = {
        "driver": "GTiff",
        "dtype": data.dtype,
        "nodata": nodata,
        "width": data.shape[1],
        "height": data.shape[0],
        "count": 1,
        "crs": crs,
        "transform": transform,
        "compress": "lzw",
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }
    with rasterio.open(filename, "w", **meta) as out:
        out.write(data, 1)


def window_overlaps(window, dataset):
    """Verify that window overlaps with extent of dataset

    Parameters
    ----------
    window : reasterio.wndows.Window
    dataset : open rasterio dataset

    Returns
    -------
    bool
    """
    clipped_window = clip_window(window, dataset.width, dataset.height)
    if clipped_window.width > 0 and clipped_window.height > 0:
        return True

    return False


def get_overlapping_windows(src, geometry, bounds, window_size):
    """Extract windows of window_size for reading from src that overlap with
    geometry.

    Parameters
    ----------
    src : open rasterio Dataset
    geometry : shapely geometry
    bounds : [xmin, ymin, xmax, ymax]
        Bounds of geometry
    window_size : int

    Returns
    -------

    tuple of:
        (
            ndarray of rasterio.windows.Window,
            ratio of number of overlapping windows to total number of windows in extent
        )
    """

    # Select all windows that intersect geometry
    res = src.res[0]
    src_bounds = src.bounds
    start_row = max(
        math.floor(math.floor((src_bounds[3] - bounds[3]) / res) / window_size)
        * window_size,
        0,
    )
    end_row = min(
        math.ceil(math.ceil((src_bounds[3] - bounds[1]) / res) / window_size)
        * window_size
        + 1,
        src.height,
    )

    start_col = max(
        math.floor(math.floor((bounds[0] - src_bounds[0]) / res) / window_size)
        * window_size,
        0,
    )
    end_col = min(
        math.ceil(math.ceil((bounds[2] - src_bounds[0]) / res) / window_size)
        * window_size
        + 1,
        src.width,
    )

    windows = [
        Window(row_off=row_off, col_off=col_off, width=window_size, height=window_size)
        for row_off, col_off in product(
            range(start_row, end_row, window_size),
            range(start_col, end_col, window_size),
        )
    ]

    total_windows = len(windows)

    if total_windows == 0:
        return [], 0

    window_boxes = shapely.box(*np.array([src.window_bounds(w) for w in windows]).T)
    shapely.prepare(geometry)
    ix = shapely.intersects(geometry, window_boxes)
    windows = np.array(windows)[ix]

    return windows, len(windows) / total_windows


class WindowGeometryMask(object):
    """Geometry mask with an associated read window for optimized
    reading from the dataset

    NOTE: all pixels within geometry mask are True
    """

    def __init__(self, dataset, window, shapes, all_touched=False):
        """Create full resolution geometry mask and associated read window

        Parameters
        ----------
        dataset : open rasterio dataset
        window : rasterio.windows.Window
        shapes : list-like of GeoJSON geometry objects
        """
        self.dataset_transform = dataset.transform
        self.window = window
        self.window_transform = dataset.window_transform(window)
        self.shape_mask = geometry_mask(
            shapes,
            transform=self.window_transform,
            out_shape=(int(window.height), int(window.width)),
            all_touched=all_touched,
            invert=True,
        )

    def detect_data(self, dataset):
        """Detect if there are any non-NODATA pixel values in the dataset within
        the geometry mask.

        Intended to be used for a low-resolution version of the geometry mask
        and dataset.

        Parameters
        ----------
        dataset : open rasterio dataset

        Returns
        -------
        bool
            returns True if there are non-NODATA pixel values present
        """
        # DEBUG: check for implementation errors
        # FIXME: comment out
        if (
            dataset.transform.a != self.dataset_transform.a
            or dataset.transform.e != self.dataset_transform.e
        ):
            raise ValueError(
                f"{dataset.name} resolution does not match that used for mask windows"
            )

        if dataset.transform == self.dataset_transform:
            read_window = self.window

        else:
            read_window = shift_window(
                self.window, self.window_transform, dataset.transform
            )
            if not window_overlaps(read_window, dataset):
                return False

        nodata = getattr(np, dataset.dtypes[0])(dataset.nodata)
        data = dataset.read(1, window=read_window, boundless=True)

        # if there are non-nodata values within geometry mask, then there are data
        if (data[self.shape_mask] != nodata).any():
            return True

        return False

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
        # DEBUG: check for implementation errors
        # FIXME: comment out
        if (
            dataset.transform.a != self.dataset_transform.a
            or dataset.transform.e != self.dataset_transform.e
        ):
            raise ValueError(
                f"{dataset.name} resolution does not match that used for mask windows"
            )

        read_window = (
            self.window
            if dataset.transform == self.dataset_transform
            else shift_window(self.window, self.window_transform, dataset.transform)
        )
        nodata = getattr(np, dataset.dtypes[0])(dataset.nodata)
        data = dataset.read(1, window=read_window, boundless=True)

        # extract values inside geometry except where they are NODATA
        values = data[self.shape_mask & (data != nodata)]
        return np.bincount(values, minlength=len(bins))
