from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import VideoCreate, VideoResponse, StatusUpdate
from core.models import Video


class VideoService:
    @staticmethod
    async def list_videos(session: AsyncSession) -> Sequence[Video]:
        """List all videos."""

        videos = await session.execute(select(Video))
        return videos.scalars.all()

    @staticmethod
    async def get_video(video_id: int, session: AsyncSession):
        """Get a video by id."""

        video = await session.get(Video, video_id)

        if not video:
            raise KeyError(f"Video with id: {video_id} not found.")

        return video

    @staticmethod
    async def create_video(data: VideoCreate, session: AsyncSession):
        """Create a new video."""

        video = Video(**data.model_dump())
        session.add(video)
        await session.commit()
        await session.refresh(video)
        return VideoResponse.model_validate(video)

    @staticmethod
    async def update_video_status(
        video_id: int, update: StatusUpdate, session: AsyncSession
    ):
        """Update a video status."""

        video = await session.get(Video, video_id)
        if not video:
            raise KeyError(f"Video with id: {video_id} not found.")

        video.status = update.status
        await session.commit()
        await session.refresh(video)
        return VideoResponse.model_validate(video)
