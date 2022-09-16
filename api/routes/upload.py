import logging
from pathlib import Path
import secrets
import shutil

import arq
from fastapi import (
    APIRouter,
    File,
    UploadFile,
    HTTPException,
    Depends,
)
from fastapi.security.api_key import APIKey

from api.errors import DataError
from api.settings import REDIS, REDIS_QUEUE, TEMP_DIR, MAX_FILE_SIZE
from api.validation import validate_token, validate_content_type


log = logging.getLogger("api")

router = APIRouter()


def save_file(file: UploadFile, uuid: str) -> Path:
    """Save file to a temporary directory and return the path.

    The caller is responsible for deleting the file.

    Parameters
    ----------
    file : UploadFile
        file received from API endpoint.
    uuid : str
        UUID of uploaded file, for tracking between jobs

    Returns
    -------
    Path
    """

    try:
        suffix = Path(file.filename).suffix
        outfilename = Path(TEMP_DIR) / f"{uuid}{suffix}"

        with open(outfilename, "wb") as out:
            shutil.copyfileobj(file.file, out)

    finally:
        # always close the file handle from the API handler
        file.file.close()

    # if file is too big, immediately delete and raise exception
    filesize_mb = outfilename.stat().st_size / (1024 * 1024)
    if filesize_mb > MAX_FILE_SIZE:
        outfilename.unlink()
        raise DataError(f"Dataset is too large: {filesize_mb:.2f} MB")

    return outfilename


@router.post("/api/upload")
async def report_upload_endpoint(
    file: UploadFile = File(...),
    token: APIKey = Depends(validate_token),
):
    validate_content_type(file)

    uuid = secrets.token_urlsafe(16)

    try:
        filename = save_file(file, uuid)
        log.debug(f"upload saved to: {filename}")

    except DataError as ex:
        log.error(ex)
        raise HTTPException(status_code=400, detail=str(ex))

    # Create inspect task
    try:
        redis = await arq.create_pool(REDIS)
        job = await redis.enqueue_job(
            "inspect",
            filename,
            uuid=uuid,
            _queue_name=REDIS_QUEUE,
        )
        return {"job": job.job_id}

    except Exception as ex:
        log.error(f"Error creating background task, is Redis offline?  {ex}")
        raise HTTPException(status_code=500, detail="Internal server error")

    finally:
        await redis.close()
