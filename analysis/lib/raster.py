import math
from itertools import product

import numba as nb
import numpy as np
import rasterio
import shapely
from affine import Affine
from rasterio.enums import Resampling
from rasterio.mask import geometry_mask
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window
from rasterio.windows import bounds as window_bounds
from rasterio.windows import transform as transform_for_window

from analysis.constants import DATA_CRS, OVERVIEW_FACTORS


@nb.njit(
    [
        "(int8[:, :],bool_[:, :],uint64[:],int8)",
        "(uint8[:, :],bool_[:, :],uint64[:],uint8)",
        "(int16[:, :],bool_[:, :],uint64[:],int16)",
        "(uint16[:, :],bool_[:, :],uint64[:],uint16)",
    ],
    fastmath=True,
    nogil=True,
    cache=True,
)
def count_values_inplace(arr, mask, out, nodata):
    """Calculate count of each value in arr.

    About 2x as fast as np.bincount

    Parameters
    ----------
    arr : ndarray of shape (rows, cols)
        contains input values to be summarized
    mask : bool ndarray of shape (rows, cols)
        mask values are True for the areas to be counted
    out : ndarray of shape (num_values, )
        output array updated in place
    nodata : value in dtype that matches arr
        NODATA value in arr
    """
    c = nb.uint64(1)
    for row in nb.prange(arr.shape[0]):
        for col in nb.prange(arr.shape[1]):
            if mask[row, col]:
                value = arr[row, col]
                if value != nodata:
                    out[value] += c


@nb.njit(
    [
        "(int8[:,:],)",
        "(uint8[:,:],)",
        "(int16[:,:],)",
        "(uint16[:,:],)",
    ],
    fastmath=True,
    nogil=True,
    cache=True,
)
def unique(arr):
    """Extract unique values in arr.

    About 2x as fast as np.unique.

    Parameters
    ----------
    arr : ndarray of shape (rows, cols)

    Returns
    -------
    set
    """
    out = set()
    for row in nb.prange(arr.shape[0]):
        for col in nb.prange(arr.shape[1]):
            out.add(arr[row, col])

    return out


@nb.njit(
    [
        "uint8[:,:](uint8[:,:],uint8[:,:],uint8,uint8)",
        "int16[:,:](int16[:,:],int16[:,:],int16,int16)",
        "uint16[:,:](uint16[:,:],uint16[:,:],uint16,uint16)",
    ],
    cache=True,
)
def remap(arr, remap_table, nodata, fill):
    """Remap a 2D array of values

    Parameters
    ----------
    arr : array of shape [:,:]
        array of values to remap
    remap_table : array of shape [n,2], same dtype as arr
        array of pairs of source value, target value
    nodata : same dtype as arr
        value to use for mapping nodata
    fill : same dtype as arr
        value to use for filling output array

    Returns
    -------
    array of shape [:,:]
        array is same shape as arr
    """

    i = 0
    j = 0
    rows = arr.shape[0]
    cols = arr.shape[1]

    # process potentially sparse remap table into indexed array
    max_value = np.max(remap_table[:, 0])
    table = np.ones(shape=(max_value + 1,), dtype=remap_table.dtype) * fill
    for i in range(len(remap_table)):
        table[remap_table[i][0]] = remap_table[i][1]

    out = np.full(shape=arr.shape, fill_value=fill)

    for i in range(rows):
        for j in range(cols):
            value = arr[i, j]
            if value == nodata:
                out[i, j] = nodata
            elif value <= max_value:
                out[i, j] = table[value]

    return out


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
    return Window(col_off=col_off, row_off=row_off, width=window.width, height=window.height)


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
        dst_transform = Affine(resolution, 0, src.transform.c, 0, -resolution, src.transform.f)
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
    window : reasterio.windows.Window
    dataset : open rasterio dataset

    Returns
    -------
    bool
    """
    clipped_window = clip_window(window, dataset.width, dataset.height)
    if clipped_window.width > 0 and clipped_window.height > 0:
        return True

    return False


class WindowGeometryMask(object):
    """Geometry mask with an associated read window for optimized
    reading from the dataset

    NOTE: all pixels within geometry mask are True
    """

    def __init__(self, transform, window, shapes, all_touched=False):
        """Create full resolution geometry mask and associated read window

        Parameters
        ----------
        transform : Affine
            transform for the full extent that is the basis for window
        window : rasterio.windows.Window
        shapes : list-like of GeoJSON geometry objects
        """
        self.transform = transform
        self.window = window
        self.window_transform = transform_for_window(window, transform)
        self.shape_mask = geometry_mask(
            shapes,
            transform=self.window_transform,
            out_shape=(int(window.height), int(window.width)),
            all_touched=all_touched,
            invert=True,
        )

        # DEBUG:
        # write_raster(
        #     "/tmp/shape_mask.tif",
        #     self.shape_mask.astype("uint8"),
        #     transform=self.window_transform,
        #     crs=DATA_CRS,
        #     nodata=0,
        # )

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

        if dataset.transform.a != self.transform.a or dataset.transform.e != self.transform.e:
            raise ValueError(f"{dataset.name} resolution does not match that used for mask windows")

        if dataset.transform == self.transform:
            read_window = self.window

        else:
            read_window = shift_window(self.window, self.window_transform, dataset.transform)
            if not window_overlaps(read_window, dataset):
                return False

        nodata = getattr(np, dataset.dtypes[0])(dataset.nodata)
        data = dataset.read(1, window=read_window, boundless=True)

        # if there are non-nodata values within geometry mask, then there are data
        if (data[self.shape_mask] != nodata).any():
            return True

        return False

    def get_pixel_count_by_bin(self, dataset, num_values=None, out=None):
        """Get count of pixels in each bin

        Parameters
        ----------
        dataset : open rasterio dataset
        num_values : int, optional (default: None)
        out : ndarray of shape (num_values, ), optional (default: None)
            output array, updated in place if provided

        Returns
        -------
        ndarray
            Total number of pixels for each bin
        """
        # DEBUG: check for implementation errors
        if dataset.transform.a != self.transform.a or dataset.transform.e != self.transform.e:
            raise ValueError(f"{dataset.name} resolution does not match that used for mask windows")

        read_window = (
            self.window
            if dataset.transform == self.transform
            else shift_window(self.window, self.window_transform, dataset.transform)
        )
        nodata = getattr(np, dataset.dtypes[0])(dataset.nodata)
        data = dataset.read(1, window=read_window, boundless=True)

        if out is None:
            if num_values is None:
                raise ValueError("Either num_values or out must be provided")

            out = np.zeros((num_values,), dtype="uint64")

        # extract values inside geometry except where they are NODATA
        count_values_inplace(data, self.shape_mask, out, nodata)
        return out


class RasterExtent:
    """Helper class to calculate windows instead of having an extent raster"""

    def __init__(self, bounds: list[float], resolution: float):
        self.bounds = bounds
        self.resolution = resolution
        self.transform = Affine(resolution, 0, bounds[0], 0, -resolution, bounds[3])
        self.width = math.ceil((bounds[2] - bounds[0]) / resolution)
        self.height = math.ceil((bounds[3] - bounds[1]) / resolution)

    def window_bounds(self, window: Window):
        return window_bounds(window, self.transform)

    def window_transform(self, window: Window):
        return transform_for_window(window, self.transform)

    def get_overlapping_windows(self, geometry, bounds, window_size):
        """Extract windows of window_size for reading within extent that overlap with
        geometry.

        Parameters
        ----------
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
        start_row = math.floor(math.floor((self.bounds[3] - bounds[3]) / self.resolution) / window_size) * window_size
        end_row = math.ceil(math.ceil((self.bounds[3] - bounds[1]) / self.resolution) / window_size) * window_size + 1
        start_col = math.floor(math.floor((bounds[0] - self.bounds[0]) / self.resolution) / window_size) * window_size
        end_col = math.ceil(math.ceil((bounds[2] - self.bounds[0]) / self.resolution) / window_size) * window_size + 1

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

        window_boxes = shapely.box(*np.array([self.window_bounds(w) for w in windows]).T)
        shapely.prepare(geometry)
        ix = shapely.intersects(geometry, window_boxes)
        windows = np.array(windows)[ix]

        return windows, len(windows) / total_windows

    def get_window(self, bounds, boundless=True):
        """Calculate the window into extent that contains bounds, for boundless reading.

        If boundless is False and the window falls outside the bounds of the extent,
        one or both of the dimensions may be 0.

        Parameters
        ----------
        bounds : list-like of [xmin, ymin, xmax, ymax]
        boundless : bool, optional (default: True)
            if True, returned window may extend beyond the dataset

        Returns
        -------
        rasterio.windows.Window instance
        """

        start_row = math.floor((self.bounds[3] - bounds[3]) / self.resolution)
        end_row = math.ceil((self.bounds[3] - bounds[1]) / self.resolution)
        start_col = math.floor((bounds[0] - self.bounds[0]) / self.resolution)
        end_col = math.ceil((bounds[2] - self.bounds[0]) / self.resolution)
        height = end_row - start_row
        width = end_col - start_col

        window = Window(col_off=start_col, row_off=start_row, width=width, height=height)
        if boundless:
            return window

        return clip_window(window, self.width, self.height)
