from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page
from fastapi_pagination.async_paginator import apaginate
from sqlalchemy.ext.asyncio import AsyncSession

from app.services import VideoService
from app.schemas import VideoCreate, VideoResponse, StatusUpdate
from core import db_helper, get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/videos", tags=["videos"])


@router.get("", response_model=Page[VideoResponse])
async def list_videos(
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    logger.info("Getting list of all videos.")
    logger.debug(f"Running VideoService.list_videos method with session = {session}.")

    return await apaginate(await VideoService.list_videos(session))


@router.get("/{video_id}", response_model=VideoResponse)
async def get_video(
    video_id: int, session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    logger.info(f"Getting a video with id: {video_id}.")
    try:
        logger.debug(
            f"Running VideoService.get_video method with video id: {video_id} and session: {session}."
        )
        video = await VideoService.get_video(video_id, session)
    except KeyError as e:
        logger.error(f"VideoService.get_video method returned a KeyError: {e}.")
        raise HTTPException(status_code=404, detail=str(e))

    return VideoResponse.model_validate(video)


@router.post("", response_model=VideoResponse, status_code=status.HTTP_201_CREATED)
async def create_video(
    data: VideoCreate, session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    logger.info("Creating a video with given data.")
    logger.debug(
        f"Running VideoService.create_video method with data = {data} and session = {session}."
    )
    return await VideoService.create_video(data, session)


@router.patch("/{video_id}/status", response_model=VideoResponse)
async def update_video_status(
    video_id: int,
    status: StatusUpdate,
    session: AsyncSession = Depends(db_helper.get_scoped_session),
):
    logger.info(f"Updating a video's status on video with id: {video_id}.")
    logger.debug(
        f"Running VideoService.update_video_status method with status = {status} and session = {session}."
    )
    return await VideoService.update_video_status(video_id, status, session)
