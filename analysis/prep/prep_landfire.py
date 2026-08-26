import math
from pathlib import Path
from time import time

import numpy as np
import pandas as pd
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform_bounds
from rasterio.windows import Window

from analysis.constants import DATA_CRS, MASK_RESOLUTION
from analysis.lib.raster import (
    add_overviews,
    create_lowres_mask,
    remap,
    unique,
    write_raster,
)

LANDFIRE_NODATA = np.int16(-9999)

start = time()

# use secas-blueprint boundaries
bnd_dir = Path("../secas-blueprint/data/inputs/boundaries")
src_dir = Path("source_data/landfire")
out_dir = Path("data/inputs/landfire")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)

bnd_raster = rasterio.open(bnd_dir / "blueprint_extent.tif")

df = pd.read_csv(
    src_dir / "LF2024_EVT_CONUS/CSV_Data/LF2024_EVT.csv", engine="pyarrow"
).rename(columns={"VALUE": "value", "EVT_NAME": "label", "EVT_GP_N": "group"})
df["alpha"] = 255

outfilename = out_dir / "landfire_evt.tif"


if not outfilename.exists():
    start = time()

    for dataset in ["CONUS", "PRVI"]:
        print(f"Extracting LANDFIRE EVT for {dataset}")
        infile = src_dir / f"LF2024_EVT_{dataset}/Tif/LF2024_EVT_{dataset}.tif"
        with rasterio.open(infile) as src:
            target_bounds = transform_bounds(
                bnd_raster.crs, src.crs, *bnd_raster.bounds
            )
            window = src.window(*target_bounds)
            window_floored = window.round_offsets(op="floor", pixel_precision=3)
            w = math.ceil(window.width + window.col_off - window_floored.col_off)
            h = math.ceil(window.height + window.row_off - window_floored.row_off)
            window = Window(window_floored.col_off, window_floored.row_off, w, h)
            # make sure that window is within extent of data
            window = window.intersection(Window(0, 0, src.width, src.height))
            transform = src.window_transform(window)

            data = src.read(1, window=window)

            tmp_filename = tmp_dir / f"landfire_evt_{dataset}.tif"
            write_raster(
                tmp_filename,
                data,
                transform=transform,
                crs=src.crs,
                # PRVI misreports NODATA but all are the same value so set it here
                nodata=LANDFIRE_NODATA,
            )
            del data

    ### Warp to match the Blueprint alignment; they are in the same projection
    with (
        rasterio.open(tmp_dir / "landfire_evt_CONUS.tif") as conus_src,
        rasterio.open(tmp_dir / "landfire_evt_PRVI.tif") as caribbean_src,
    ):
        print("Warping...")
        conus_vrt = WarpedVRT(
            conus_src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            src_nodata=LANDFIRE_NODATA,
            nodata=LANDFIRE_NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )
        conus_data = conus_vrt.read()[0]
        # for whatever reason, this still gets some arbitrary high values set; reset to NODATA
        conus_data = np.where(conus_data == 32767, LANDFIRE_NODATA, conus_data)

        caribbean_vrt = WarpedVRT(
            caribbean_src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            src_nodata=LANDFIRE_NODATA,
            nodata=LANDFIRE_NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )
        caribbean_data = caribbean_vrt.read()[0]

        data = np.where(caribbean_data != LANDFIRE_NODATA, caribbean_data, conus_data)
        del conus_data
        del caribbean_data

        ### Set areas outside the Blueprint to NODATA
        print("Masking to the Blueprint")
        extent_data = bnd_raster.read(1)
        data = np.where((extent_data == 0), LANDFIRE_NODATA, data)
        del extent_data

        values_present = sorted([v for v in unique(data) if v != LANDFIRE_NODATA])
        df = df.loc[df.value.isin(values_present)].reset_index(drop=True)
        # save lookup for later use
        with open("constants/landfire_evt.json", "w") as out:
            df.set_index("value")[["label", "group"]].to_json(out, orient="index")

        # remap to contiguous values
        out_nodata = 32767
        remap_table = df.reset_index()[["value", "index"]].values
        remap_table = np.vstack(
            [remap_table, np.array([[LANDFIRE_NODATA, out_nodata]])]
        ).astype("int16")

        data = remap(
            data, remap_table, nodata=np.int16(out_nodata), fill=np.int16(out_nodata)
        ).astype("uint16")

        write_raster(
            outfilename,
            data,
            transform=bnd_raster.transform,
            crs=bnd_raster.crs,
            nodata=out_nodata,
        )

        del data

        colormap = df[["R", "G", "B", "alpha"]].apply(tuple, axis=1).to_dict()

        with rasterio.open(outfilename, "r+") as src:
            src.write_colormap(1, colormap)

        add_overviews(outfilename)

        tmp_filename.unlink()


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
