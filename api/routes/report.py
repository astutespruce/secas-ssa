import logging
import re
import shutil
import tempfile
from pathlib import Path
from typing import Optional
from zipfile import ZipFile

import arq
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.security.api_key import APIKey

from api.errors import DataError
from api.lib.geo import get_dataset
from api.lib.validation import validate_content_type, validate_token
from api.settings import MAX_FILE_SIZE, REDIS, REDIS_QUEUE, TEMP_DIR

log = logging.getLogger("api")

router = APIRouter()


def save_file(file: UploadFile) -> Path:
    """Save file to a temporary directory and return the path.

    The caller is responsible for deleting the file.

    Parameters
    ----------
    file : UploadFile
        file received from API endpoint.

    Returns
    -------
    Path
    """

    try:
        suffix = Path(file.filename).suffix

        fp, outfilename = tempfile.mkstemp(suffix=suffix, dir=TEMP_DIR)
        with open(fp, "wb") as out:
            shutil.copyfileobj(file.file, out)

    finally:
        # always close the file handle from the API handler
        file.file.close()

    outfilename = Path(outfilename)

    # if file is too big, immediately delete and raise exception
    filesize_mb = outfilename.stat().st_size / (1024 * 1024)
    if filesize_mb > MAX_FILE_SIZE:
        outfilename.unlink()
        raise DataError(f"Dataset is too large: {filesize_mb:.2f} MB")

    return outfilename


@router.post("/report")
async def report_upload_endpoint(
    file: UploadFile = File(...),
    token: APIKey = Depends(validate_token),
):
    validate_content_type(file)

    try:
        filename = save_file(file)
        log.debug(f"upload saved to: {filename}")

    except DataError as ex:
        log.error(ex)
        raise HTTPException(status_code=400, detail=str(ex))

    # validate that upload has a shapefile or file geodatabase
    try:
        dataset, layer = get_dataset(ZipFile(filename))

    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    # Create inspect task
    try:
        redis = await arq.create_pool(REDIS)
        job = await redis.enqueue_job(
            "get_report_inputs",
            str(filename),
            dataset,
            layer,
            uuid=filename.stem,
            _queue_name=REDIS_QUEUE,
        )
        return {"job": job.job_id}

    except Exception as ex:
        log.error(f"Error creating background task, is Redis offline?  {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        await redis.aclose()


@router.post("/report/{uuid}/finalize")
async def create_report_endpoint(
    uuid: str,
    datasets: str = Form(),  # comma-delimited list
    field: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    token: APIKey = Depends(validate_token),
):
    if not re.fullmatch(r"[A-Za-z0-9_-]+", uuid):
        raise HTTPException(status_code=400, detail="invalid uuid")

    base_path = TEMP_DIR.resolve()
    filename = (base_path / f"{uuid}.feather").resolve()

    # verify that file exists in temp directory, otherwise return 404;
    # should only happen if there is too much delay between submitting initial
    # task and this task
    if not filename.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    # Create inspect task
    try:
        redis = await arq.create_pool(REDIS)
        job = await redis.enqueue_job(
            "create_report",
            uuid,
            datasets,
            field=field,
            name=name,
            _queue_name=REDIS_QUEUE,
        )
        return {"job": job.job_id}

    except Exception as ex:
        log.error(f"Error creating background task, is Redis offline?  {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        await redis.aclose()
