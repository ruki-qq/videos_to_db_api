__all__ = ("router",)

from fastapi import APIRouter

from app.routers.api import video

router = APIRouter()
router.include_router(video.router)
