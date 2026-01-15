from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import StatusUpdate, VideoCreate, VideoResponse
from app.services import VideoService
from core import db_helper, get_logger
from core.models import VideoStatus

logger = get_logger(__name__)
router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", response_model=list[VideoResponse])
async def list_videos(
    status: Annotated[list[VideoStatus] | None, Query()] = None,
    camera_number: Annotated[list[int] | None, Query()] = None,
    location: Annotated[list[str] | None, Query()] = None,
    start_time_from: datetime | None = Query(default=None),
    start_time_to: datetime | None = Query(default=None),
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    logger.info("Getting list of all videos.")
    logger.debug(f"Running VideoService.list_videos method with session = {session}.")

    videos = await VideoService.list_videos(
        session=session,
        statuses=status,
        camera_numbers=camera_number,
        locations=location,
        start_time_from=start_time_from,
        start_time_to=start_time_to,
    )
    return videos


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int, session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    logger.info(f"Getting a video with id: {video_id}.")
    try:
        logger.debug(
            "Running VideoService.get_video with "
            f"video id: {video_id} and session: {session}."
        )
        video = await VideoService.get_video(video_id, session)
    except KeyError as e:
        logger.error(f"VideoService.get_video raised KeyError: {e}.")
        raise HTTPException(status_code=404, detail=str(e))

    return video


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    data: VideoCreate, session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    logger.info("Creating a video with given data.")
    logger.debug(
        f"Running VideoService.create_video with data = {data} and session = {session}."
    )
    try:
        return await VideoService.create_video(data, session)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{video_id}/status", response_model=VideoResponse)
async def update_video_status(
    video_id: int,
    status: StatusUpdate,
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    logger.info(f"Updating a video's status on video with id: {video_id}.")
    logger.debug(
        f"Running VideoService.update_video_status with status = {status} and session = {session}."
    )
    try:
        return await VideoService.update_video_status(video_id, status, session)
    except KeyError as e:
        logger.error(f"VideoService.update_video_status raised KeyError: {e}.")
        raise HTTPException(status_code=404, detail=str(e))
