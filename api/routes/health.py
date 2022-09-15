from fastapi import APIRouter
from fastapi.responses import Response

router = APIRouter()


@router.get("/api/health")
async def health_endpoint():
    return Response(status_code=200)
