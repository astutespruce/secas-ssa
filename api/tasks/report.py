import logging
import math
from pathlib import Path

import geopandas as gp
from pyogrio import read_info

from analysis.constants import DATA_CRS
from analysis.lib.geometry import dissolve
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from analysis.lib.stats.prescreen import get_available_datasets
from api.errors import DataError
from api.lib.geo import extract_dataset
from api.progress import set_progress
from api.report.xlsx import create_xlsx
from api.settings import TEMP_DIR

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


async def record_progress_callback(ctx, percent, min_progress=0, max_progress=100, message=""):
    progress = math.ceil(min_progress + (max_progress - min_progress) * (percent / 100))
    await set_progress(
        ctx["redis"],
        ctx["job_id"],
        progress,
        message,
    )


async def get_report_inputs(ctx, zip_filename: str, dataset: str, layer: str | None, uuid: str):
    zip_filename = Path(zip_filename)

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Inspecting data files")

    path = f"/vsizip/{zip_filename}/{dataset}"
    info = read_info(path, layer=layer)

    # prescreen columns to read to exclude floating point, dates
    id_fields = [field for field, dtype in zip(info["fields"], info["dtypes"]) if dtype in VALID_DTYPES]

    df = extract_dataset(path, layer=layer, columns=id_fields).to_crs(DATA_CRS)

    # Get attributes that might identify analysis units and drop any fields that are completely null
    fields = {col: len(df[col].unique()) for col in id_fields if not df[col].isnull().all()}

    # Save as feather file for subsequent steps
    df[["geometry"] + list(fields.keys())].to_feather(zip_filename.with_suffix(".feather"))

    # prescreen datasets available
    await set_progress(ctx["redis"], ctx["job_id"], 50, "Checking available datasets")
    datasets = get_available_datasets(df)

    if len(datasets) == 0:
        raise DataError("area of interest does not overlap any of the available datasets")

    await set_progress(ctx["redis"], ctx["job_id"], 100, "Done checking available datasets")

    return {
        "payload": {
            # pass along uuid from task context
            "uuid": uuid,
            "count": info["features"],
            "fields": fields,
            "datasets": list(datasets),
        }
    }, []


async def create_report(ctx, uuid, datasets, field=None, name=None):
    datasets = datasets.split(",") if datasets else []

    await set_progress(ctx["redis"], ctx["job_id"], 0, "Reading dataset")

    filename = (TEMP_DIR / f"{uuid}.feather").resolve()

    # double-check that it exists; this should not occur here
    # because we check for it before submitting job
    if not filename.exists():
        log.error(f"Dataset does not exist for uuid: {uuid}")
        raise ValueError("Dataset does not exist")

    columns = [field] if field else []
    df = gp.read_feather(filename, columns=["geometry"] + columns)

    if not field:
        field = "__analysis_unit"
        df[field] = "all areas"

    if len(df) > 1:
        await set_progress(ctx["redis"], ctx["job_id"], 5, "Merging boundaries")

        try:
            df = dissolve(df, by=field).set_index(field)

        except Exception as ex:
            log.error(f"Failed to dissolve dataframe: {filename} on field: {field}")
            log.error(ex)
            raise DataError("Could not aggregate boundaries for analysis")

    else:
        df = df.set_index(field)

    progress_scale = [10, 75]
    message = "Calculating statistics (may take a while)"

    async def progress_callback(percent):
        await record_progress_callback(
            ctx,
            percent,
            min_progress=progress_scale[0],
            max_progress=progress_scale[1],
            message=message,
        )

    await set_progress(ctx["redis"], ctx["job_id"], progress_scale[0], message)

    results = await get_analysis_unit_results(df, datasets, progress_callback=progress_callback)
    if results is None:
        raise DataError("Dataset does not overlap Southeast states")

    await set_progress(ctx["redis"], ctx["job_id"], progress_scale[1], "Creating XLSX file")
    xlsx = create_xlsx(results, datasets)

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done")

    local_filename = str((TEMP_DIR / f"{uuid}.xlsx"))

    with open(local_filename, "wb") as out:
        out.write(xlsx)

    download_filename = (
        f"Southeast Species Status Landscape Assessment Report - {name}.xlsx"
        if name
        else "Southeast Species Status Landscape Assessment Report.xlsx"
    )

    log.debug(f"Created XLSX at: {local_filename}")
    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    return {
        "local_filename": local_filename,
        "download_filename": download_filename,
        "payload": f"/jobs/{ctx['job_id']}/xlsx",
    }, []
