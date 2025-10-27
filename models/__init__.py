"""Models package (v2.0)"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, DateTime, Enum as SAEnum, ForeignKey, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class JobStatus:
    DISCOVERED = "discovered"
    ENQUEUED = "enqueued"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    RETRIED = "retried"


class TranscriptionJob(Base):
    __tablename__ = "transcription_jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_uri: Mapped[str] = mapped_column(String(1024), nullable=False, index=True)
    collaborator_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    source_hash: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True, default=JobStatus.DISCOVERED)
    attempts: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    artifacts: Mapped[list["ProcessingArtifact"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )
    logs: Mapped[list["ProcessingLog"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )


class ProcessingArtifact(Base):
    __tablename__ = "processing_artifacts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("transcription_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(16), nullable=False)  # pdf, docx, json
    path: Mapped[str] = mapped_column(String(2048), nullable=False)
    gdrive_path: Mapped[Optional[str]] = mapped_column(String(1024), nullable=True)
    size: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)

    job: Mapped["TranscriptionJob"] = relationship(back_populates="artifacts")


class ProcessingLog(Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    job_id: Mapped[int] = mapped_column(ForeignKey("transcription_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(16), nullable=False)  # info, warning, error
    message: Mapped[str] = mapped_column(String(4000), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, index=True)

    job: Mapped["TranscriptionJob"] = relationship(back_populates="logs")


__all__ = [
    "JobStatus",
    "TranscriptionJob",
    "ProcessingArtifact",
    "ProcessingLog",
]


