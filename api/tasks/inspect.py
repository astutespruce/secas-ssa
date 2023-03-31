import logging
from zipfile import ZipFile

from pyogrio import list_layers, read_dataframe, read_info
import shapely

from analysis.constants import DATA_CRS
from analysis.lib.geometry import make_valid, to_dict_all
from analysis.lib.stats.prescreen import get_available_datasets
from api.errors import DataError
from api.progress import set_progress


log = logging.getLogger("api")

# valid data types for fields that can be used to identify groups of data within a dataset
VALID_DTYPES = {
    "object",
    "int8",
    "uint8",
    "int16",
    "uint16",
    "int32",
    "uint32",
    "int64",
    "uint64",
}


def get_dataset(zip_filename):
    """Gets singular geospatial dataset and layer for analysis.

    Validates rules:
    - There must be only one data source (.shp or .gdb) in the zip file.
    - There must be only one data layer in that data source.
    - The data source must contain the required files (.prj for shapefile; .
      dbf is not used so not required)

    Parameters
    ----------
    zip : str
        full path to zip file

    Returns
    -------
    (str, str)
        tuple of geospatial file within zip file, name of layer
    """

    with ZipFile(zip_filename) as zipfile:
        # exclude OS-specific hidden files and directories
        files = set(
            f for f in zipfile.namelist() if "__MACOSX" not in f or ".DS_Store" in f
        )

        geo_files = [f for f in files if f.endswith(".shp") or f.endswith(".gdb")]
        num_files = len(geo_files)

        if num_files == 0:
            log.error("Upload zip file does not contain shp or FGDB files")

            raise DataError("zip file must include a shapefile or FGDB")

        if num_files > 1:
            log.error(
                f"Upload zip file contains {num_files} shp or FGDB files:\n{geo_files}"
            )

            raise DataError("zip file must include only one shapefile or FGDB")

    filename = geo_files[0]

    if filename.endswith(".shp"):
        missing = []
        for ext in (".prj", ".shx"):
            if filename.replace(".shp", ext) not in files:
                missing.append(ext)

        if missing:
            log.error(f"Upload zip file contains .shp but not {','.join(missing)}")
            raise DataError("zip file must include .shp, .prj, and .shx files")

    # Validate that dataset is a polygon and has only a single layer
    layers = list_layers(f"zip://{zip_filename}/{filename}")

    if layers.shape[0] > 1:
        log.error(f"Upload data source contains multiple data layers\n{layers}")
        raise DataError("data source must contain only one data layer")

    if "Polygon" not in layers[0, 1]:
        log.error(f"Upload data source is not a polygon: {layers[0,1]}")
        raise DataError("data source must be a Polygon type")

    return filename, layers[0, 0]


async def inspect(ctx, zip_filename, uuid):
    await set_progress(ctx["redis"], ctx["job_id"], 0, "Inspecting data files")

    ### get dataset and layer, and validate that only one polygon layer is present
    dataset, layer = get_dataset(zip_filename)
    path = f"zip://{zip_filename}/{dataset}"

    log.info(f"detected dataset: {path}, layer={layer}")

    info = read_info(path, layer=layer)

    # pass along uuid from task context
    results = {
        "uuid": uuid,
        "count": info["features"],
        "fields": dict(),
        "available_datasets": {},
    }

    # prescreen columns to read to exclude floating point, dates
    columns = [
        field
        for field, dtype in zip(info["fields"], info["dtypes"])
        if dtype in VALID_DTYPES
    ]

    try:
        df = read_dataframe(path, layer=layer, columns=columns)
    except Exception as ex:
        log.error(f"Failed to read dataframe: {path}, layer={layer}")
        log.error(ex)
        raise DataError("Could not read dataset")

    ### Get attributes that might identify analysis units
    # not needed if there is only 1 feature
    # calculate the number of unique values per field
    if info["features"] > 1:
        # exclude any fields that are entirely null
        results["fields"] = {
            col: len(df[col].unique()) for col in columns if not df[col].isnull().all()
        }

    keep_cols = ["geometry"] + list(results["fields"].keys())

    ### Reproject dataset to standard projection
    await set_progress(
        ctx["redis"], ctx["job_id"], 5, "Reprojecting to standard projection"
    )
    try:
        df = df.to_crs(DATA_CRS)
    except Exception:
        log.error(f"Failed to reproject dataframe: {path}, layer={layer}")
        raise DataError("Could not reproject dataset to standard projection")

    ### Make geometry valid
    await set_progress(ctx["redis"], ctx["job_id"], 10, "Making valid")
    # make valid and only keep polygon parts
    try:
        df["geometry"] = make_valid(df.geometry.values)
        df = df.explode(index_parts=False)
        df = df.loc[
            shapely.get_type_id(df.geometry.values) == 3, keep_cols
        ].reset_index(drop=True)
    except Exception as ex:
        log.error(f"Failed to clean dataframe: {path}, layer={layer}")
        log.error(ex)
        raise DataError("Could not extract valid polgon boundaries from dataset")

    if len(df) == 0:
        raise DataError("No valid polygon boundaries available in dataset")

    # Save as feather file for subsequent steps
    outfilename = str(zip_filename).replace(".zip", ".feather")
    df.to_feather(outfilename)

    ### prescreen datasets available
    await set_progress(ctx["redis"], ctx["job_id"], 50, "Checking available datasets")
    results["available_datasets"] = get_available_datasets(
        to_dict_all(df.geometry.values), df.total_bounds
    )

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    return {"payload": results}, []
