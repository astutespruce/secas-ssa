import logging
from secrets import compare_digest

import arq

from arq.jobs import Job, JobStatus
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
)
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from api.errors import DataError
from api.settings import (
    REDIS,
    REDIS_QUEUE,
    API_SECRET,
)
from api.progress import get_progress


log = logging.getLogger("api")

router = APIRouter()
security = HTTPBasic()


@router.get("/api/reports/status/{job_id}")
async def job_status_endpoint(job_id: str):
    """Return the status of a job.

    Job status values derived from JobStatus enum at:
    https://github.com/samuelcolvin/arq/blob/master/arq/jobs.py
    ['deferred', 'queued', 'in_progress', 'complete', 'not_found']

    We add ['success', 'failed'] status values here.

    Parameters
    ----------
    job_id : str

    Returns
    -------
    JSON
        {"status": "...", "progress": 0-100, "result": "...only if complete...", "detail": "...only if failed..."}
    """

    redis = await arq.create_pool(REDIS)

    try:
        job = Job(job_id, redis=redis, _queue_name=REDIS_QUEUE)
        status = await job.status()
        info = await job.info()

        if status == JobStatus.not_found:
            raise HTTPException(status_code=404, detail="Job not found")

        if status != JobStatus.complete:
            progress, message, errors = await get_progress(redis, job_id)

            return {
                "task": info.function,
                "status": status,
                "progress": progress,
                "message": message,
                "errors": errors,
            }

        try:
            # this re-raises the underlying exception raised in the worker
            result, errors = await job.result()

            if info.success:
                return {
                    "task": info.function,
                    "status": "success",
                    "result": result.get("payload", None),
                    "errors": errors,
                }

        except DataError as ex:
            message = str(ex)

        except Exception as ex:
            log.error(ex)
            message = "Internal server error"
            raise HTTPException(status_code=500, detail="Internal server error")

        return {"task": info.function, "status": "failed", "detail": message}

    finally:
        await redis.close()


@router.get("/admin/jobs/status")
async def get_jobs(credentials: HTTPBasicCredentials = Depends(security)):
    """Return summary information about queued and completed jobs"""

    correct_username = compare_digest(credentials.username, "admin")
    correct_password = compare_digest(credentials.password, API_SECRET)
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    redis = await arq.create_pool(REDIS)

    try:
        queued = [
            {"job": job.function, "args": job.args, "start": job.enqueue_time}
            for job in await redis.queued_jobs(queue_name=REDIS_QUEUE)
        ]

        results = [
            {
                "job": job.function,
                "args": job.args,
                "start": job.enqueue_time,
                "success": job.success,
                "elapsed": job.finish_time - job.enqueue_time,
            }
            for job in await redis.all_job_results()
        ]

        return {"queued": queued, "completed": results}

    finally:
        await redis.close()
