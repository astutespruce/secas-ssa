# Southeast Species Status Landscape Assessment Tool - API

## Overview

Use case: user uploads shapefile containing one or more population units, indicated
by values in a field. User identifies the population unit ID field and chooses
datasets to analyze from datasets that overlap with the population units.

## Starting background jobs and API server

### Development environment

Background jobs use `arq` which relies on `redis` installed on the host.

On MacOS 10.15, start `redis`:

```bash
redis-server /usr/local/etc/redis.conf
```

On MacOS 12.4 (M1 / Arm64), start `redis`:

```bash
redis-server /opt/homebrew/etc/redis.conf
```

To start `arq` with reload capability:

```
arq api.worker.WorkerSettings --watch ./api
```

To start the API in development mode:

```
uvicorn api.api:app --reload --port 5000
```

### Staging / production environment or Docker setup

See `deploy/staging/README.md`.

## API requests

To make custom report requests using HTTPie:

```bash
http -f POST :5000/api/upload token=="<token from .env>" file@<filename>.zip
```

This creates a background job and returns:

```
{
    "job": "<job_id>"
}
```

To query job status:

```
http :5000/api/reports/status/<job_id>
```

On success of a job, it will return

```json
{
    "task": <task ID>,
    "result": <varies by task>,
    "errors": [<list of non-breaking errors, if any>]
}
```

On failure of a job, it will an HTTP 500 error

To download XLSX from a successful job:

```
http :5000/api/reports/results/<job_id>
```

This sets the `Content-Type` header to attachment and uses the passed-in name
for the filename.

To list queued and completed jobs:

```
http :5000/admin/jobs/status -a admin
```

Username is admin, password is `API_SECRET` in `.env`
