import uuid

from sqlalchemy import BigInteger, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "videos"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    creator_id: Mapped[str] = mapped_column(String(36), nullable=False)
    video_created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), index=True
    )
    views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    likes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class VideoSnapshot(Base):
    __tablename__ = "video_snapshots"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    video_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("videos.id"), index=True
    )
    views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    likes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    reports_count: Mapped[int] = mapped_column(BigInteger, default=0)
    delta_views_count: Mapped[int] = mapped_column(BigInteger, default=0)
    delta_likes_count: Mapped[int] = mapped_column(BigInteger, default=0)
    delta_comments_count: Mapped[int] = mapped_column(BigInteger, default=0)
    delta_reports_count: Mapped[int] = mapped_column(BigInteger, default=0)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), index=True)
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
