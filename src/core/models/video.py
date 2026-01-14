from datetime import datetime, timedelta
from enum import Enum

from sqlalchemy import CheckConstraint, DateTime, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import INTERVAL, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class VideoStatus(Enum):
    NEW = "new"
    TRANSCODED = "transcoded"
    RECOGNIZED = "recognized"


class Video(Base):
    video_path: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(TIMESTAMP(timezone=True))
    duration: Mapped[timedelta] = mapped_column(INTERVAL, nullable=False)
    camera_number: Mapped[int] = mapped_column(
        Integer,
        CheckConstraint("camera_number > 0"),
        nullable=False,
    )
    location: Mapped[str] = mapped_column(String(511), nullable=False)
    status: Mapped[VideoStatus] = mapped_column(
        Enum(VideoStatus),
        default=VideoStatus.NEW,
        server_default=VideoStatus.NEW.value,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
