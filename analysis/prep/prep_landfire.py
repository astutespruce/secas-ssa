import math
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import rasterio
from progress.bar import Bar
from pyogrio import read_dataframe
from rasterio.windows import Window
from rasterio.windows import transform as transform_for_window

from analysis.constants import DATA_CRS, MASK_RESOLUTION, STANDARD_RESOLUTION
from analysis.lib.raster import add_overviews, clip_window, create_lowres_mask, remap, shift_window

LANDFIRE_NODATA = np.int16(-9999)
NODATA = np.int16(32767)
WINDOW_SIZE = 4096


# use secas-blueprint boundaries
src_dir = Path("source_data/landfire")
out_dir = Path("data/inputs/landfire")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)


conus_filename, carib_filename = [
    src_dir / f"LF2024_EVT_{dataset}/Tif/LF2024_EVT_{dataset}.tif" for dataset in ["CONUS", "PRVI"]
]

df = (
    pd.concat(
        [
            read_dataframe(src_dir / f"LF2024_EVT_{dataset}/Tif/LF2024_EVT_{dataset}.tif.vat.dbf")
            for dataset in ["CONUS", "PRVI"]
        ],
        ignore_index=True,
    )
    .rename(columns={"Value": "src_value", "EVT_NAME": "label", "EVT_GP_N": "group"})[
        ["src_value", "label", "group", "R", "G", "B"]
    ]
    .drop_duplicates()
)

df["alpha"] = 255

df = df.loc[df.src_value != LANDFIRE_NODATA].sort_values(by="label").reset_index(drop=True)
df["value"] = df.index.astype("int16")
df[["value", "label", "group"]].to_feather(out_dir / "landfire_evt.feather")

# Remap values to contiguous integers
remap_table = df[["src_value", "value"]].values
remap_table = np.ascontiguousarray(np.vstack([remap_table, np.array([[LANDFIRE_NODATA, NODATA]])])).astype("int16")
colormap = df[["R", "G", "B", "alpha"]].apply(tuple, axis=1).to_dict()


outfilename = out_dir / "landfire_evt.tif"
if not outfilename.exists():
    start = time()

    # NOTE: CONUS is same projecion and alignment as NLCD, PRVI is nearly so
    with rasterio.open(conus_filename) as conus, rasterio.open(carib_filename) as carib:
        xmin = conus.bounds[0]
        ymin = carib.bounds[1]
        xmax = carib.bounds[2]
        ymax = conus.bounds[3]
        xmax = math.ceil((xmax - xmin) / STANDARD_RESOLUTION) * STANDARD_RESOLUTION + xmin
        ymin = ymax - math.ceil((ymax - ymin) / STANDARD_RESOLUTION) * STANDARD_RESOLUTION
        height = int((ymax - ymin) / STANDARD_RESOLUTION)
        width = int((xmax - xmin) / STANDARD_RESOLUTION)

        # align based on CONUS
        transform = conus.transform

        windows = []
        for row_off in np.arange(height, step=WINDOW_SIZE):
            for col_off in np.arange(width, step=WINDOW_SIZE):
                windows.append(Window(row_off=row_off, col_off=col_off, width=WINDOW_SIZE, height=WINDOW_SIZE))

        meta = {
            "driver": "GTiff",
            "dtype": "int16",
            "nodata": NODATA,
            "width": width,
            "height": height,
            "count": 1,
            "crs": DATA_CRS,
            "transform": transform,
            "compress": "zstd",
            "tiled": True,
            "blockxsize": 256,
            "blockysize": 256,
        }

        with (
            rasterio.Env(GDAL_CACHEMAX=2048, GDAL_NUM_THREADS="ALL_CPUS"),
            rasterio.open(outfilename, "w", BIGTIFF="YES", **meta) as outfile,
        ):
            for src in [conus, carib]:
                # process data by window to avoid running out of memory
                for window in Bar(message=f"Processing {src.name}", max=len(windows)).iter(windows):
                    # clip output window to output extent
                    out_window = clip_window(window, max_width=width, max_height=height)

                    read_window = clip_window(
                        shift_window(out_window, transform_for_window(out_window, transform), src.transform),
                        max_width=src.width,
                        max_height=src.height,
                    )

                    if read_window.width == 0 or read_window.height == 0:
                        continue

                    data = src.read(1, window=read_window)
                    data = remap(data, remap_table, nodata=np.int16(NODATA), fill=np.int16(NODATA)).astype("int16")

                    out_window = shift_window(read_window, transform_for_window(read_window, src.transform), transform)
                    outfile.write(data, 1, window=out_window)

            # add_overviews(outfilename)

    # with rasterio.open(outfilename, "r+") as outfile:
    #     outfile.write_colormap(1, colormap)


outfilename = out_dir / "landfire_evt_mask.tif"
if not outfilename.exists():
    print("Creating mask")
    create_lowres_mask(
        out_dir / "landfire_evt.tif",
        outfilename,
        resolution=MASK_RESOLUTION,
        ignore_zero=False,
    )

print(f"Done with LANDFIRE EVT in {time() - start:.2f}s")
