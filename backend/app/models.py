# pyrefly: ignore [missing-import]
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import relationship
import datetime
from app.database import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    target_architecture = Column(String, default="ARM Cortex-M4")
    firmware_filepath = Column(String, nullable=True)
    status = Column(String, default="ACTIVE")  # ACTIVE, COMPLETED, ARCHIVED
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    sessions = relationship("PipelineSession", back_populates="project", cascade="all, delete-orphan")
    artifacts = relationship("Artifact", back_populates="project", cascade="all, delete-orphan")

class PipelineSession(Base):
    __tablename__ = "pipeline_sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, default="IDLE")  # IDLE, RUNNING, FAILED, SUCCESS
    current_stage = Column(String, default="Firmware Upload")
    started_at = Column(DateTime, nullable=True)
    ended_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="sessions")
    tool_runs = relationship("ToolRun", back_populates="session", cascade="all, delete-orphan")

class ToolRun(Base):
    __tablename__ = "tool_runs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("pipeline_sessions.id", ondelete="CASCADE"), nullable=False)
    tool_name = Column(String, nullable=False)  # binwalk, angr, ghidra, etc.
    command_executed = Column(Text, nullable=True)
    exit_code = Column(Integer, nullable=True)
    started_at = Column(DateTime, default=datetime.datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)

    session = relationship("PipelineSession", back_populates="tool_runs")
    logs = relationship("LogEntry", back_populates="tool_run", cascade="all, delete-orphan")

class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(Integer, primary_key=True, index=True)
    tool_run_id = Column(Integer, ForeignKey("tool_runs.id", ondelete="CASCADE"), nullable=False)
    log_type = Column(String, default="STDOUT")  # STDOUT, STDERR, SYSTEM
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    tool_run = relationship("ToolRun", back_populates="logs")

class Artifact(Base):
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    file_name = Column(String, nullable=False)
    stage_generated = Column(String, nullable=False)  # Identification, Extraction, etc.
    mime_type = Column(String, default="application/octet-stream")
    file_size = Column(Integer, default=0)
    local_storage_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    project = relationship("Project", back_populates="artifacts")
