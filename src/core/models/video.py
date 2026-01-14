from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import INTERVAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VideoStatus(Enum):
    NEW = "new"
    TRANSCODED = "transcoded"
    RECOGNIZED = "recognized"


class Video(Base):
    video_path: Mapped[str] = mapped_column(
        Text,
        CheckConstraint("char_length(video_path) > 0", name="video_path_not_empty"),
        nullable=False,
        info={"description": "Path to the video file"},
    )
    start_time: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
    )
    duration: Mapped[timedelta] = mapped_column(
        INTERVAL,
        nullable=False,
    )
    camera_number: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("camera_number > 0", name="camera_number_positive"),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(
        String(511),
        CheckConstraint("char_length(location) > 0", name="location_not_empty"),
        nullable=False,
    )
    status: Mapped[VideoStatus] = mapped_column(
        SAEnum(VideoStatus),
        default=VideoStatus.NEW,
        server_default=VideoStatus.NEW.value,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
