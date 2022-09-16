from pathlib import Path
import os
import subprocess
import time
from urllib.parse import unquote_plus

import httpx


from api.settings import API_TOKEN

# this assumes API server is running at :5000 and that worker is also running

DELAY = 0.5  # seconds

API_URL = "http://localhost:5000"
# API_URL = "http://localhost:8080"
# API_URL = "http://localhost:8080/southeastssa"

OUT_DIR = Path("/tmp/api")

if not OUT_DIR.exists():
    os.makedirs(OUT_DIR)


def poll_until_done(job_id, current=0, max=100):
    r = httpx.get(f"{API_URL}/api/reports/status/{job_id}?token={API_TOKEN}")

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()
    status = json.get("status")
    progress = json.get("progress")
    message = json.get("message")
    errors = json.get("errors", [])
    task = json.get("task")

    if status == "success":
        return task, json["result"], errors

    if status == "failed":
        print(f"Failed: {json['detail']}")
        return task, None, errors

    print(f"Progress: {progress}, message: {message}, errors: {errors}")

    current += 1
    if current == max:
        print("Max retries hit, stopping...")
        return task, None, None

    time.sleep(DELAY)

    return poll_until_done(job_id, current=current, max=max)


def test_upload_file(filename):
    files = {"file": open(filename, "rb")}
    r = httpx.post(
        f"{API_URL}/api/upload?token={API_TOKEN}",
        files=files,
    )

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()

    job_id = json.get("job")

    if job_id is None:
        raise Exception(json)

    return poll_until_done(job_id)


def test_create_report(uuid, datasets, field, name):
    r = httpx.post(
        f"{API_URL}/api/report?token={API_TOKEN}",
        data={"uuid": uuid, "datasets": datasets, "field": field, "name": name},
    )

    if r.status_code != 200:
        raise Exception(f"Error processing request (HTTP {r.status_code}): {r.text}")

    json = r.json()

    job_id = json.get("job")

    if job_id is None:
        raise Exception(json)

    return poll_until_done(job_id)


def download_file(url):
    r = httpx.get(f"{API_URL}{url}")

    attachment_filename = r.headers["content-disposition"].split("filename*=utf-8''")[1]
    filename = OUT_DIR / unquote_plus(attachment_filename)

    with open(filename, "wb") as out:
        out.write(r.read())

    return filename


if __name__ == "__main__":

    # name, filename = ["Balduina atropurpurea", "examples/Balduina_pop_resiliency_final.zip"]
    # name, filename = ["Rabbitsfoot", "examples/Rabbitsfott_resilience_final_SECAS_only.zip"]
    name, filename = ["Test species", "examples/SingleTest.zip"]

    task, result, errors = test_upload_file(filename)
    print(f"----------------\ntask: {task}\nresult: {result}\nerrors: {errors}\n")

    if result is not None:
        uuid = result["uuid"]

        if result.get("count") == 1:
            field = None
        else:
            # arbitrarily pick first field available
            field = result["fields"].keys()[0]

        # include all present datasets in analysis
        datasets = ",".join(
            dataset
            for dataset, present in result["available_datasets"].items()
            if present
        )

    task, result, errors = test_create_report(uuid, datasets, field, name)
    print(f"----------------\ntask: {task}\nresult: {result}\nerrors: {errors}\n")

    # task, result, errors = test_create_report(
    #     "2xqkIWOUtvA0S77PA_Ff0Q",
    #     datasets="nlcd_landcover",
    #     field=None,
    #     name="test species",
    # )
    # print(f"----------------\ntask: {task}\nresult: {result}\nerrors: {errors}\n")

    outfilename = download_file(result)

    subprocess.run(["open", outfilename])
