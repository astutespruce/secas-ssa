from pathlib import Path
import subprocess

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import DATA_CRS, NLCD_INUNDATION_FREQUENCY, MASK_RESOLUTION
from analysis.lib.raster import add_overviews, write_raster, create_lowres_mask

NODATA = 255


# use secas-blueprint boundaries
secas_blueprint_data_dir = Path("../secas-blueprint/data")
nlcd_2019 = secas_blueprint_data_dir / "inputs/nlcd/landcover_2019.tif"

tmp_dir = Path("/tmp")
src_dir = Path("source_data/inundation_frequency")
out_dir = Path("data/inputs/inundation_frequency")
out_dir.mkdir(exist_ok=True)

bnd_raster = rasterio.open(
    secas_blueprint_data_dir / "inputs/boundaries/nonmarine_mask.tif"
)


print("Extracting inundation frequency")

### Build VRT using GDAL CLI
vrt_filename = tmp_dir / "sefi.vrt"
ret = subprocess.run(
    [
        "gdalbuildvrt",
        "-overwrite",
        str(vrt_filename),
    ]
    # there are 2 overlapping files; where they overlap, use OK/TX (put last in vrt)
    + [str(src_dir / "SEIF_v4.tif"), str(src_dir / "SEIF_TX_OK_MERGE.tif")]
)
ret.check_returncode()


### Warp to match the SE Blueprint and mask to inland part of blueprint
outfilename = src_dir / "secas_inundation_frequency.tif"

if not outfilename.exists():
    with rasterio.open(vrt_filename) as src:
        vrt = WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            nodata=NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        )

        data = vrt.read()[0]

        # Set areas outside the SE Blueprint to NODATA
        print("Masking to inland areas in the SE")
        data[(bnd_raster.read(1) == 0)] = NODATA
        # reassign NODATA value that was wrapped from negative to positive
        data[data == 128] = NODATA

        # bin into 0-5, 6-10, 11-50, 51-90, 91-100
        data[(data >= 0) & (data <= 5)] = 0
        data[(data > 5) & (data <= 10)] = 1
        data[(data > 10) & (data <= 50)] = 2
        data[(data > 50) & (data <= 90)] = 3
        data[(data > 90) & (data <= 100)] = 4

        write_raster(outfilename, data, bnd_raster.transform, bnd_raster.crs, NODATA)
        add_overviews(outfilename)


### Combine with NLCD 2019
print("Combining with NLCD 2019")

# NOTE: NLCD values are in contiguous indexes
with rasterio.open(nlcd_2019) as nlcd_src:
    nlcd = nlcd_src.read(1)

out = np.ones_like(data) * NODATA
for code, entry in NLCD_INUNDATION_FREQUENCY.items():
    print(f"Processing {entry}")
    out[(data == entry["inundation_frequency"]) & (nlcd == entry["nlcd"])] = code


outfilename = out_dir / "nlcd_inundation_frequency.tif"
write_raster(outfilename, out, bnd_raster.transform, bnd_raster.crs, NODATA)
add_overviews(outfilename)


bnd_raster.close()


print("Creating mask")
create_lowres_mask(
    out_dir / "nlcd_inundation_frequency.tif",
    out_dir / "nlcd_inundation_frequency_mask.tif",
    resolution=MASK_RESOLUTION,
    ignore_zero=False,
)
