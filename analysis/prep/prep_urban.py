from pathlib import Path
from time import time

import numpy as np
import rasterio
from progress.bar import Bar
from rasterio.windows import Window

from analysis.constants import DATA_CRS, MASK_RESOLUTION, URBAN_YEARS
from analysis.lib.raster import add_overviews, clip_window, create_lowres_mask, remap

NODATA = np.uint8(255)
WINDOW_SIZE = 4096
CHUNK_SIZE = 256  # number of rows to read at a time from urban, its internal chunks are full width but 1 row in height

src_dir = Path("../secas-blueprint/source_data")
out_dir = Path("data/inputs/urban")
out_dir.mkdir(parents=True, exist_ok=True)
tmp_dir = Path("/tmp")

# NOTE: NLCD 2021 (legacy) and urban are exactly aligned
with rasterio.open(src_dir / "urban/urban_probabilities/fv2_probability_newDevelopment_2030.tif") as src:
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
### Read NLCD 2021; this is used to assign the already urban class in SE Blueprint
################################################################################
already_urban_filename = tmp_dir / "nlcd_2021_urban.tif"
if not already_urban_filename.exists():
    with (
        rasterio.Env(GDAL_CACHEMAX=2048, GDAL_NUM_THREADS="ALL_CPUS"),
        rasterio.open(src_dir / "nlcd/nlcd_2021_land_cover_l48_20230630/nlcd_2021_land_cover_l48_20230630.img") as src,
        rasterio.open(already_urban_filename, "w", **meta) as outfile,
    ):
        remap_table = np.array([(21, 1), (22, 1), (23, 1), (24, 1)], dtype="uint8")

        for window in Bar(message=f"Extracting already urban from NLCD 2021", max=len(windows)).iter(windows):
            window = clip_window(window, max_width=src.width, max_height=src.height)
            data = src.read(1, window=window)

            # classify urban as 1 everything else as 0
            # 0 is NLCD NODATA
            data = np.where(data == 0, NODATA, remap(data, remap_table, nodata=NODATA, fill=np.uint8(0)))
            outfile.write(data, 1, window=window)


with (
    rasterio.Env(GDAL_CACHEMAX=2048, GDAL_NUM_THREADS="ALL_CPUS"),
    rasterio.open(already_urban_filename) as already_urban,
):
    # urban data are chunked in full width x 1 row, so we read multiple rows at a time but
    # full width
    windows = []
    for row_off in np.arange(already_urban.height, step=CHUNK_SIZE):
        windows.append(Window(row_off=row_off, col_off=0, width=already_urban.width, height=CHUNK_SIZE))

    for year in URBAN_YEARS:
        year_start = time()

        outfilename = out_dir / f"urban_{year}.tif"
        with (
            rasterio.open(src_dir / f"urban/urban_probabilities/fv2_probability_newDevelopment_{year}.tif") as src,
            rasterio.open(outfilename, "w", **meta) as outfile,
        ):
            for window in Bar(message=f"Extracting {year} urban data", max=len(windows)).iter(windows):
                window = clip_window(window, max_width=src.width, max_height=src.height)
                data = src.read(1, window=window)

                # nan is areas not projected to urbanize and actual NODATA
                data[np.isnan(data)] = np.float32(0.0)

                # probability values are number of runs out of 50 that predicted
                # urbanization; convert back to the number of runs
                data = (data * np.float32(50.0)).astype("uint8")

                # set a value of 51 where already urban and mask to NODATA of NLCD
                already_urban_data = already_urban.read(1, window=window)
                data = np.where(already_urban_data == 1, np.uint8(51), data)
                data = np.where(already_urban_data == NODATA, NODATA, data)

                del already_urban_data

                outfile.write(data, 1, window=window)

                del data

        add_overviews(outfilename)

        print(f"Done with {year} in {time() - year_start:.2f}s")


print("Creating urban mask")
outfilename = out_dir / "urban_mask.tif"
if not outfilename.exists():
    create_lowres_mask(
        out_dir / "urban_2100.tif",
        outfilename,
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )


already_urban_filename.unlink()
