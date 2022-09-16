import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.responses import Response
import sentry_sdk
from sentry_sdk.integrations.asgi import SentryAsgiMiddleware

from api.settings import (
    LOGGING_LEVEL,
    ALLOWED_ORIGINS,
    SENTRY_DSN,
)
from api.routes.health import router as health_router

from api.routes.report import router as report_router
from api.routes.status import router as status_router
from api.routes.upload import router as upload_router


### Setup logging
logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": "%(levelprefix)s %(asctime)s %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        },
        "loggers": {
            "api": {"handlers": ["default"], "level": LOGGING_LEVEL},
        },
    }
)
log = logging.getLogger("api")


### Create the main API app and routes
app = FastAPI()
app.include_router(health_router)
app.include_router(report_router)
app.include_router(status_router)
app.include_router(upload_router)

### Setup middleware
if SENTRY_DSN:
    log.info("setting up sentry")
    sentry_sdk.init(dsn=SENTRY_DSN)
    app.add_middleware(SentryAsgiMiddleware)


@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    """Middleware that wraps HTTP requests and catches exceptions.

    These need to be caught here in order to ensure that the
    CORS middleware is used for the response, otherwise the client
    gets CORS related errors instead of the actual error.

    Parameters
    ----------
    request : Request
    call_next : func
        next func in the chain to call
    """
    try:
        return await call_next(request)

    except Exception as ex:
        log.error(f"Error processing request: {ex}")
        return Response("Internal server error", status_code=500)


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)
