# pyrefly: ignore [missing-import]
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# --- LOG SCHEMAS ---
class LogEntryBase(BaseModel):
    log_type: str
    message: str
    timestamp: datetime

class LogEntryResponse(LogEntryBase):
    id: int
    tool_run_id: int

    class Config:
        from_attributes = True

# --- TOOL RUN SCHEMAS ---
class ToolRunBase(BaseModel):
    tool_name: str
    command_executed: Optional[str] = None
    exit_code: Optional[int] = None
    started_at: datetime
    ended_at: Optional[datetime] = None

class ToolRunResponse(ToolRunBase):
    id: int
    session_id: int
    logs: List[LogEntryResponse] = []

    class Config:
        from_attributes = True

# --- PIPELINE SESSION SCHEMAS ---
class PipelineSessionBase(BaseModel):
    status: str
    current_stage: str
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class PipelineSessionResponse(PipelineSessionBase):
    id: int
    project_id: int
    tool_runs: List[ToolRunResponse] = []

    class Config:
        from_attributes = True

# --- ARTIFACT SCHEMAS ---
class ArtifactBase(BaseModel):
    file_name: str
    stage_generated: str
    mime_type: str
    file_size: int
    local_storage_path: str
    created_at: datetime

class ArtifactResponse(ArtifactBase):
    id: int
    project_id: int

    class Config:
        from_attributes = True

# --- PROJECT SCHEMAS ---
class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_architecture: str = "ARM Cortex-M4"
    status: str = "ACTIVE"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    target_architecture: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    firmware_filepath: Optional[str] = None
    created_at: datetime
    sessions: List[PipelineSessionResponse] = []
    artifacts: List[ArtifactResponse] = []

    class Config:
        from_attributes = True
# --- FIRMWARE UPLOAD SCHEMAS ---

class FirmwareUploadResponse(BaseModel):
    filename: str
    filesize: int
    filepath: str
    message: str