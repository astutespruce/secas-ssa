from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT

from analysis.constants import DATA_CRS, NLCD_INUNDATION_FREQUENCY, MASK_RESOLUTION
from analysis.lib.raster import add_overviews, write_raster, create_lowres_mask

NODATA = 255


# use secas-blueprint boundaries
secas_blueprint_data_dir = Path("../secas-blueprint/data")
nlcd_2021 = secas_blueprint_data_dir / "inputs/nlcd/landcover_2021.tif"

tmp_dir = Path("/tmp")
src_dir = Path("source_data/inundation_frequency")
out_dir = Path("data/inputs/inundation_frequency")
out_dir.mkdir(exist_ok=True)

bnd_raster = rasterio.open(
    secas_blueprint_data_dir / "inputs/boundaries/contiguous_southeast_inland_mask.tif"
)


print("Extracting inundation frequency")

# Warp to match the SE Blueprint and mask to inland part of blueprint
outfilename = src_dir / "secas_inundation_frequency.tif"

if not outfilename.exists():
    with rasterio.open(src_dir / "SEIF_v4.tif") as src:
        with WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            src_nodata=128,
            nodata=127,  # data is int8, have to use safe upper value when reading
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
            dtype=("int8"),
        ) as vrt:
            data = vrt.read()[0].astype("uint8")
            data[data == 127] = NODATA

    with rasterio.open(src_dir / "SEIF_TX_OK_MERGE.tif") as src:
        with WarpedVRT(
            src,
            width=bnd_raster.width,
            height=bnd_raster.height,
            nodata=NODATA,
            transform=bnd_raster.transform,
            crs=DATA_CRS,
            resampling=Resampling.nearest,
        ) as vrt:
            ok_tx_data = vrt.read()[0]

    # where they overlap, use OK/TX
    ix = ok_tx_data != NODATA
    data[ix] = ok_tx_data[ix]

    # Set areas outside the SE Blueprint to NODATA
    print("Masking to inland areas in the SE")
    data[(bnd_raster.read(1) == 0)] = NODATA

    # bin into 0-5, 6-10, 11-50, 51-90, 91-100
    data[(data >= 0) & (data <= 5)] = 0
    data[(data > 5) & (data <= 10)] = 1
    data[(data > 10) & (data <= 50)] = 2
    data[(data > 50) & (data <= 90)] = 3
    data[(data > 90) & (data <= 100)] = 4

    write_raster(outfilename, data, bnd_raster.transform, bnd_raster.crs, NODATA)
    add_overviews(outfilename)


### Combine with NLCD 2021
print("Combining with NLCD 2021")

# NOTE: NLCD values are in contiguous indexes
with rasterio.open(nlcd_2021) as nlcd_src:
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
