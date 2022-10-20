from pathlib import Path
import os

from arq.connections import RedisSettings
from dotenv import load_dotenv


load_dotenv()
TEMP_DIR = Path(os.getenv("TEMP_DIR", "/tmp/ssa-reports"))
TEMP_DIR.mkdir(exist_ok=True, parents=True)

SHARED_DATA_DIR = Path(os.getenv("SHARED_DATA_DIR", "data"))

# CORS is only set by API server when running in local development
ENABLE_CORS = bool(os.getenv("ENABLE_CORS", False))
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

API_TOKEN = os.getenv("API_TOKEN")
API_SECRET = os.getenv("API_SECRET")
MAX_JOBS = int(os.getenv("MAX_JOBS", 2))
MAX_FILE_SIZE = float(os.getenv("MAX_FILE_SIZE", 100))  # MB
LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "DEBUG")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = os.getenv("REDIS_PORT", 6379)
SENTRY_DSN = os.getenv("SENTRY_DSN")
SENTRY_ENV = os.getenv("SENTRY_ENV")

REDIS = RedisSettings(host=REDIS_HOST, port=REDIS_PORT)

REDIS_QUEUE = "southeast-ssa"

# retain files for 24 hours to aid troubleshooting
FILE_RETENTION = 86400

# time jobs out after 10 minutes
JOB_TIMEOUT = 600
