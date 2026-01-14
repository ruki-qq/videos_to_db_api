from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import StatusUpdate, VideoCreate
from core.models import Video, VideoStatus


class VideoService:
    @staticmethod
    async def list_videos(
        session: AsyncSession,
        statuses: Sequence[VideoStatus] | None = None,
        camera_numbers: Sequence[int] | None = None,
        locations: Sequence[str] | None = None,
        start_time_from: datetime | None = None,
        start_time_to: datetime | None = None,
    ) -> Sequence[Video]:
        """List videos with optional filters."""

        query: Select[tuple[Video]] = select(Video)

        if statuses:
            query = query.where(Video.status.in_(statuses))
        if camera_numbers:
            query = query.where(Video.camera_number.in_(camera_numbers))
        if locations:
            query = query.where(Video.location.in_(locations))
        if start_time_from:
            query = query.where(Video.start_time >= start_time_from)
        if start_time_to:
            query = query.where(Video.start_time <= start_time_to)

        query = query.order_by(Video.start_time.desc())

        result = await session.execute(query)
        return result.scalars().all()

    @staticmethod
    async def get_video(video_id: int, session: AsyncSession) -> Video:
        """Get a video by id."""

        video = await session.get(Video, video_id)

        if not video:
            raise KeyError(f"Video with id: {video_id} not found.")

        return video

    @staticmethod
    async def create_video(data: VideoCreate, session: AsyncSession) -> Video:
        """Create a new video."""

        video = Video(**data.model_dump())
        session.add(video)
        await session.commit()
        await session.refresh(video)
        return video

    @staticmethod
    async def update_video_status(
        video_id: int, update: StatusUpdate, session: AsyncSession
    ) -> Video:
        """Update a video status."""

        video = await session.get(Video, video_id)
        if not video:
            raise KeyError(f"Video with id: {video_id} not found.")

        video.status = update.status
        await session.commit()
        await session.refresh(video)
        return video
