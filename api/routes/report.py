import logging
from typing import Optional

import arq
from arq.jobs import Job, JobStatus
from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Depends,
)
from fastapi.responses import FileResponse
from fastapi.security.api_key import APIKey

from api.settings import REDIS, REDIS_QUEUE, TEMP_DIR
from api.validation import validate_token


log = logging.getLogger("api")

router = APIRouter()


@router.post("/api/report")
async def create_report_endpoint(
    uuid: str = Form(),
    datasets: str = Form(),  # comma-delimited list
    field: Optional[str] = Form(None),
    name: Optional[str] = Form(None),
    token: APIKey = Depends(validate_token),
):
    filename = TEMP_DIR / f"{uuid}.feather"

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
        await redis.close()


@router.get("/api/reports/results/{job_id}")
async def download_report_endpoint(job_id: str):
    redis = await arq.create_pool(REDIS)

    try:
        job = Job(job_id, redis=redis, _queue_name=REDIS_QUEUE)
        status = await job.status()

        if status == JobStatus.not_found:
            raise HTTPException(status_code=404, detail="Job not found")

        if status != JobStatus.complete:
            raise HTTPException(status_code=400, detail="Job not complete")

        info = await job.result_info()
        if not info.success:
            raise HTTPException(
                status_code=400, detail="Job failed, cannot return results"
            )

        results, _ = info.result

        path = results["filename"]

        name = info.kwargs.get("name", None)
        suffix = f" - {name}" if name else ""

        return FileResponse(
            path,
            filename=f"Southeast Species Status Landscape Assessment Report{suffix}.xlsx",
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    finally:
        await redis.close()
