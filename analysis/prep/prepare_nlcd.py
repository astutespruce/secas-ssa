from pathlib import Path
import math
from time import time

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
from rasterio.windows import Window

from analysis.constants import DATA_CRS, NLCD_CODES, NLCD_INDEXES
from analysis.lib.raster import add_overviews, write_raster
from analysis.lib.speedups import remap

NODATA = 255

start = time()

# use secas-blueprint boundaries
bnd_dir = Path("../secas-blueprint/data/boundaries")
src_dir = Path("source_data/nlcd/landcover")
out_dir = Path("data/inputs/nlcd")
tmp_dir = Path("/tmp")

out_dir.mkdir(parents=True, exist_ok=True)

# values are remapped to contiguous integers starting from 0
colormap = {i: e["color"] + (255,) for i, e in enumerate(NLCD_INDEXES.values())}
remap_table = np.array([(k, i) for i, k in enumerate(NLCD_CODES.keys())], dtype="uint8")

bnd_raster = rasterio.open(bnd_dir / "nonmarine_mask.tif")

for infile in src_dir.glob("*/*.img"):
    year = int(infile.stem.split("_")[1])
    outfilename = out_dir / f"landcover_{year}.tif"

    if outfilename.exists():
        continue

    year_start = time()
    print(f"Extracting {infile}")

    ### Extract within extent of SE Base Blueprint
    with rasterio.open(infile) as src:
        window = src.window(*bnd_raster.bounds)
        window_floored = window.round_offsets(op="floor", pixel_precision=3)
        w = math.ceil(window.width + window.col_off - window_floored.col_off)
        h = math.ceil(window.height + window.row_off - window_floored.row_off)
        window = Window(window_floored.col_off, window_floored.row_off, w, h)
        # make sure that window is within extent of data
        window = window.intersection(Window(0, 0, src.width, src.height))
        transform = src.window_transform(window)

        data = src.read(1, window=window)
        tmp_filename = tmp_dir / f"nlcd_landcover_{year}.tif"
        write_raster(tmp_filename, data, transform=transform, crs=src.crs, nodata=0)

    ### Warp to match the SE Blueprint
    # This is a very minor shift because projections are very similar (WGS84 => NAD83)
    with rasterio.open(tmp_filename) as src:
        vrt = WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            nodata=0,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

        ### Set areas outside the SE Blueprint to NODATA
        print("Masking to inland areas in the SE")
        data[(data == 0) | (bnd_raster.read(1) == 0)] = NODATA

        ### Remap values to contiguous integers
        print("Remapping to contiguous integers")
        data = remap(data, remap_table, nodata=NODATA)

        write_raster(
            outfilename,
            data,
            transform=bnd_raster.transform,
            crs=bnd_raster.crs,
            nodata=NODATA,
        )

        with rasterio.open(outfilename, "r+") as src:
            src.write_colormap(1, colormap)

        add_overviews(outfilename)

        tmp_filename.unlink()

        print(f"Done with {year} in {time()-year_start:.2f}s")
