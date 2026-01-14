from datetime import datetime, timedelta

from pydantic import BaseModel, Field, ConfigDict

from core.models import VideoStatus


class VideoBase(BaseModel):
    video_path: str = Field(..., min_length=1, description="Путь до видеофайла")
    start_time: datetime = Field(..., description="Время начала записи")
    duration: timedelta = Field(..., gt=timedelta(0), description="Длительность видео")
    camera_number: int = Field(..., gt=0, description="Номер камеры")
    location: str = Field(..., min_length=1, description="Локация")


class VideoCreate(VideoBase):
    pass


class VideoResponse(VideoBase):
    id: int
    status: VideoStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StatusUpdate(BaseModel):
    status: VideoStatus
