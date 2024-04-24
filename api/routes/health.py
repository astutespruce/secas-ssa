from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get("/api/health", status_code=200)
@router.head("/api/health", status_code=200)
async def health_endpoint():
    return Response()
