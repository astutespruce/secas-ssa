from pathlib import Path
from time import time

import numpy as np
import rasterio
from progress.bar import Bar
from rasterio.windows import Window

from analysis.constants import DATA_CRS, MASK_RESOLUTION, NLCD_CODES, NLCD_INDEXES
from analysis.lib.colors import hex_to_uint8, interpolate_colormap
from analysis.lib.raster import add_overviews, clip_window, create_lowres_mask, remap, write_raster

NODATA = 255
WINDOW_SIZE = 4096

# values are remapped to contiguous integers starting from 0
landcover_colormap = {i: hex_to_uint8(e["color"]) + (255,) for i, e in enumerate(NLCD_INDEXES.values())}
landcover_remap_table = np.array([(k, i) for i, k in enumerate(NLCD_CODES.keys())], dtype="uint8")
impervious_colormap = {
    0: (255, 255, 255, 0),
    **{
        i + 1: hex_to_uint8(color) + (255,)
        for i, color in enumerate(interpolate_colormap({1: "#F3C6A8", 100: "#C40A0A"}))
    },
}


start = time()

# use secas-blueprint boundaries
bnd_dir = Path("../secas-blueprint/data/inputs/boundaries")
src_dir = Path("source_data/nlcd_annual")
out_dir = Path("data/inputs/nlcd_annual")
out_dir.mkdir(parents=True, exist_ok=True)
tmp_dir = Path("/tmp")


landcover_tifs = sorted(src_dir.glob("landcover/*/*.tif"))
impervious_tifs = sorted(src_dir.glob("impervious/*/*.tif"))


with rasterio.open((landcover_tifs + impervious_tifs)[0]) as src:
    windows = []
    for row_off in np.arange(src.height, step=WINDOW_SIZE):
        for col_off in np.arange(src.width, step=WINDOW_SIZE):
            windows.append(Window(row_off=row_off, col_off=col_off, width=WINDOW_SIZE, height=WINDOW_SIZE))

    meta = {
        "driver": "GTiff",
        "dtype": "uint8",
        "nodata": NODATA,
        "width": src.width,
        "height": src.height,
        "count": 1,
        "crs": DATA_CRS,
        "transform": src.transform,
        "compress": "zstd",
        "predictor": 2,
        "tiled": True,
        "blockxsize": 256,
        "blockysize": 256,
    }


################################################################################
### Extract landcover
################################################################################
print("Processing landcover")


for infile in landcover_tifs:
    year_start = time()
    year = int(infile.stem.split("_")[3])

    outfilename = out_dir / f"landcover_{year}.tif"

    if outfilename.exists():
        continue

    with (
        rasterio.Env(GDAL_CACHEMAX=2048, GDAL_NUM_THREADS="ALL_CPUS"),
        rasterio.open(infile) as src,
        rasterio.open(outfilename, "w", **meta) as outfile,
    ):
        outfile.write_colormap(1, landcover_colormap)

        # process data by window to avoid running out of memory
        for window in Bar(message=f"Processing {year}", max=len(windows)).iter(windows):
            # clip window to file
            window = clip_window(window, max_width=src.width, max_height=src.height)
            data = src.read(1, window=window)

            # Remap values to contiguous integers
            # NOTE: NLCD NODATA is 250, but we ignore it here and it gets filled to 255
            data = remap(data, landcover_remap_table, nodata=NODATA, fill=NODATA)
            outfile.write(data, 1, window=window)

    add_overviews(outfilename)

    print(f"Done with {year} in {time() - year_start:.2f}s")


outfilename = out_dir / "landcover_mask.tif"
if not outfilename.exists():
    print("Creating mask")
    create_lowres_mask(
        out_dir / "landcover_2025.tif",
        outfilename,
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )

################################################################################
### Extract percent impervious
################################################################################
print("Processing percent impervious")

for infile in impervious_tifs:
    year_start = time()
    year = int(infile.stem.split("_")[3])

    outfilename = out_dir / f"impervious_{year}.tif"

    if outfilename.exists():
        continue

    with (
        rasterio.Env(GDAL_CACHEMAX=2048, GDAL_NUM_THREADS="ALL_CPUS"),
        rasterio.open(infile) as src,
        rasterio.open(outfilename, "w", **meta) as outfile,
    ):
        outfile.write_colormap(1, impervious_colormap)

        # process data by window to avoid running out of memory
        for window in Bar(message=f"Processing {year}", max=len(windows)).iter(windows):
            # clip window to file
            window = clip_window(window, max_width=src.width, max_height=src.height)
            data = src.read(1, window=window)
            data = np.where(data == int(src.nodata), NODATA, data)
            outfile.write(data, 1, window=window)

    add_overviews(outfilename)

    print(f"Done with {year} in {time() - year_start:.2f}s")


outfilename = out_dir / "impervious_mask.tif"
if not outfilename.exists():
    print("Creating mask")
    create_lowres_mask(
        out_dir / "impervious_2025.tif",
        outfilename,
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )
