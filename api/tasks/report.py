import logging
import math
import tempfile

import geopandas as gp

from analysis.lib.geometry import to_dict_all, dissolve
from analysis.lib.stats.analysis_units import get_analysis_unit_results
from api.errors import DataError
from api.progress import set_progress
from api.report.xlsx import create_xlsx
from api.settings import TEMP_DIR


log = logging.getLogger("api")


async def record_progress_callback(
    ctx, percent, min_progress=0, max_progress=100, message=""
):
    progress = math.ceil(min_progress + (max_progress - min_progress) * (percent / 100))
    await set_progress(
        ctx["redis"],
        ctx["job_id"],
        progress,
        message,
    )


async def create_report(ctx, uuid, datasets, field=None, name=None):
    await set_progress(ctx["redis"], ctx["job_id"], 0, "Reading dataset")

    filename = TEMP_DIR / f"{uuid}.feather"

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

    results = await get_analysis_unit_results(
        df, datasets, progress_callback=progress_callback
    )
    if results is None:
        raise DataError("Dataset does not overlap Southeast states")

    await set_progress(
        ctx["redis"], ctx["job_id"], progress_scale[1], "Creating XLSX file"
    )
    xlsx = create_xlsx(results, datasets)

    await set_progress(ctx["redis"], ctx["job_id"], 95, "Nearly done")

    fp, outfilename = tempfile.mkstemp(suffix=".xlsx", dir=TEMP_DIR)
    with open(fp, "wb") as out:
        out.write(xlsx)

    await set_progress(ctx["redis"], ctx["job_id"], 100, "All done!")

    return {
        "filename": outfilename,
        "payload": f"/api/reports/results/{ctx['job_id']}",
    }, []
