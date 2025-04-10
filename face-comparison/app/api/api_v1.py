from fastapi import APIRouter
from app.api.endpoints.face_comparison import router as compare_router

router = APIRouter()

router.include_router(compare_router, tags=["face_comparison"])
