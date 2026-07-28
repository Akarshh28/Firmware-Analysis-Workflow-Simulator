import asyncio
import os
import datetime
from fastapi import UploadFile, File
import shutil
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.config import settings
from app.database import Base, engine, get_db
import app.models as models
import app.schemas as schemas
from app.plugins.manager import plugin_manager
from app.plugins.base import ToolInput

# Initialize DB tables automatically
Base.metadata.create_all(bind=engine)
os.makedirs(settings.ARTIFACTS_DIR, exist_ok=True)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend service for FAWS - Firmware Analysis Workflow Simulator",
    version="1.0.0"
)

# Set up CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify front-end client URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define pipeline workflow stages in chronological order
PIPELINE_STAGES = [
    {"stage": "Firmware", "tool": "upload", "desc": "Upload smart meter binary"},
    {"stage": "Identification", "tool": "strings", "desc": "Identify compiler and CPU architecture details"},
    {"stage": "Extraction", "tool": "binwalk", "desc": "Scan and extract compressed file structures"},
    {"stage": "Static Analysis", "tool": "cutter", "desc": "Locate DLMS parser entry points"},
    {"stage": "Reverse Engineering", "tool": "ghidra", "desc": "Decompile target DLMS/COSEM parser flow"},
    {"stage": "Secret Detection", "tool": "trufflehog", "desc": "Scan for hardcoded security keys/credentials"},
    {"stage": "Cryptographic Analysis", "tool": "entropy", "desc": "Examine entropy maps for hidden encryption"},
    {"stage": "Protocol Analysis", "tool": "wireshark", "desc": "Scan simulated packets and handshake cycles"},
    {"stage": "Symbolic Execution", "tool": "angr", "desc": "Solve branch assertions using symbolic analysis"},
    {"stage": "Fuzzing", "tool": "afl", "desc": "Fuzz smart meter message structures"},
    {"stage": "Risk Assessment", "tool": "scorecard", "desc": "Produce CVSS vulnerability mappings"},
    {"stage": "Report Generation", "tool": "pdf_report", "desc": "Render final security audit summary"}
]

@app.get("/")
def read_root():
    return {
        "status": "online",
        "app_name": settings.PROJECT_NAME,
        "mode": settings.MODE
    }

# --- PROJECTS ROUTES ---

@app.get("/api/projects", response_model=List[schemas.ProjectResponse])
def list_projects(db: Session = Depends(get_db)):
    return db.query(models.Project).all()

@app.post("/api/projects", response_model=schemas.ProjectResponse)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    db_project = models.Project(
        name=project.name,
        description=project.description,
        target_architecture=project.target_architecture
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Initialize an idle pipeline session for the project
    db_session = models.PipelineSession(
        project_id=db_project.id,
        status="IDLE",
        current_stage="Firmware"
    )
    db.add(db_session)
    db.commit()
    
    return db_project

@app.get("/api/projects/{project_id}", response_model=schemas.ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    return db_project

@app.delete("/api/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

@app.post("/api/projects/{project_id}/upload")
async def upload_firmware(
    project_id: int,
    firmware: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    project = (
        db.query(models.Project)
        .filter(models.Project.id == project_id)
        .first()
    )

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    allowed_extensions = [".bin", ".hex", ".elf", ".img"]

    ext = os.path.splitext(firmware.filename)[1].lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only .bin, .hex, .elf and .img firmware files are allowed."
        )

    save_path = os.path.join(
        settings.ARTIFACTS_DIR,
        firmware.filename
    )

    with open(save_path, "wb") as buffer:
        shutil.copyfileobj(firmware.file, buffer)

    project.firmware_filepath = save_path
    db.commit()

    return {
        "message": "Firmware uploaded successfully",
        "filename": firmware.filename,
        "path": save_path,
    }

# --- PIPELINE ROUTING AND CONTROL ---

@app.get("/api/projects/{project_id}/pipeline")
def get_pipeline(project_id: int, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline session not found")
    
    # Return stages with status mapping from db runs
    stages_with_status = []
    for stage_def in PIPELINE_STAGES:
        tool_name = stage_def["tool"]
        # Find if a run exists for this tool under the session
        run = db.query(models.ToolRun).filter(
            models.ToolRun.session_id == session.id,
            models.ToolRun.tool_name == tool_name
        ).order_by(models.ToolRun.id.desc()).first()
        
        status = "idle"
        exit_code = None
        if run:
            if run.exit_code is None:
                status = "running"
            elif run.exit_code == 0:
                status = "success"
            else:
                status = "failed"
            exit_code = run.exit_code
            
        stages_with_status.append({
            "stage": stage_def["stage"],
            "tool": tool_name,
            "description": stage_def["desc"],
            "status": status,
            "exit_code": exit_code
        })
        
    return {
        "session_id": session.id,
        "status": session.status,
        "current_stage": session.current_stage,
        "stages": stages_with_status
    }

async def run_pipeline_task(session_id: int, db_url: str):
    # Run in background to process each stage
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    bg_engine = create_engine(db_url)
    BgSession = sessionmaker(bind=bg_engine)
    session = BgSession()
    
    try:
        db_session = session.query(models.PipelineSession).filter(models.PipelineSession.id == session_id).first()
        if not db_session:
            return
            
        db_session.status = "RUNNING"
        db_session.started_at = datetime.datetime.utcnow()
        session.commit()
        
        # Simulated run sequence for FAWS
        for stage_def in PIPELINE_STAGES:
            tool_name = stage_def["tool"]
            if tool_name == "upload":
                continue  # Skip raw upload state
                
            db_session.current_stage = stage_def["stage"]
            session.commit()
            
            # Start tool run
            tool_run = models.ToolRun(
                session_id=session_id,
                tool_name=tool_name,
                command_executed=f"{tool_name} --run",
                started_at=datetime.datetime.utcnow()
            )
            session.add(tool_run)
            session.commit()
            
            # Retrieve plugin execution (always simulated initially)
            plugin = plugin_manager.get_plugin(tool_name)
            
            # Add status system logs
            sys_log_start = models.LogEntry(
                tool_run_id=tool_run.id,
                log_type="SYSTEM",
                message=f"Starting simulated execution for {tool_name}..."
            )
            session.add(sys_log_start)
            session.commit()
            
            if plugin:
                # We simulate execution
                tool_input = ToolInput(target_filepath="flash.bin", extra_args={})
                output = await plugin.execute_simulated(tool_input)
                
                # Write logs
                for log_line in output.logs:
                    le = models.LogEntry(
                        tool_run_id=tool_run.id,
                        log_type=log_line.get("log_type", "STDOUT"),
                        message=log_line.get("message", "")
                    )
                    session.add(le)
                
                # Write artifacts if generated
                for art_def in output.generated_files:
                    art = models.Artifact(
                        project_id=db_session.project_id,
                        file_name=art_def["file_name"],
                        stage_generated=stage_def["stage"],
                        mime_type=art_def["mime_type"],
                        file_size=art_def["file_size"],
                        local_storage_path=os.path.join(settings.ARTIFACTS_DIR, art_def["file_name"])
                    )
                    session.add(art)
                    
                tool_run.exit_code = output.exit_code
                tool_run.ended_at = datetime.datetime.utcnow()
                
                if not output.success:
                    db_session.status = "FAILED"
                    session.commit()
                    break
            else:
                # Mock fallback if plugin file isn't created yet
                await asyncio.sleep(1.5)
                le_info = models.LogEntry(
                    tool_run_id=tool_run.id,
                    log_type="STDOUT",
                    message=f"Executing {tool_name} mock run..."
                )
                le_success = models.LogEntry(
                    tool_run_id=tool_run.id,
                    log_type="STDOUT",
                    message="Process finished successfully."
                )
                session.add(le_info)
                session.add(le_success)
                
                tool_run.exit_code = 0
                tool_run.ended_at = datetime.datetime.utcnow()
                
            session.commit()
            
        else:
            db_session.status = "SUCCESS"
            db_session.current_stage = "Report Generation"
            
        db_session.ended_at = datetime.datetime.utcnow()
        session.commit()
        
    except Exception as e:
        print(f"Error in pipeline background thread: {e}")
        if db_session:
            db_session.status = "FAILED"
            session.commit()
    finally:
        session.close()

@app.post("/api/projects/{project_id}/pipeline/run")
def start_pipeline(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline session not found")
        
    if session.status == "RUNNING":
        return {"message": "Pipeline is already running"}
        
    # Clear past runs for this session to restart fresh
    db.query(models.ToolRun).filter(models.ToolRun.session_id == session.id).delete()
    db.commit()
    
    background_tasks.add_task(run_pipeline_task, session.id, settings.DATABASE_URL)
    return {"message": "Pipeline started in background"}

@app.post("/api/projects/{project_id}/pipeline/stop")
def stop_pipeline(project_id: int, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline session not found")
        
    if session.status != "RUNNING":
        return {"message": "Pipeline is not running"}
        
    session.status = "FAILED"
    session.ended_at = datetime.datetime.utcnow()
    
    # Mark any running tool as failed
    running_runs = db.query(models.ToolRun).filter(
        models.ToolRun.session_id == session.id,
        models.ToolRun.exit_code == None
    ).all()
    for run in running_runs:
        run.exit_code = -999
        run.ended_at = datetime.datetime.utcnow()
        
    db.commit()
    return {"message": "Pipeline stopped"}

# --- TOOL EXPLORER AND GENERAL RUNS ---

@app.get("/api/tools")
def list_tools():
    # Return documentation for all registered tools
    tools_list = []
    # Dynamic list
    for name, plugin in plugin_manager.plugins.items():
        tools_list.append({
            "name": name,
            "docs": plugin.documentation
        })
        
    # Standard stubs for tools that don't have modules written yet
    all_stages_tools = ["strings", "cutter", "ghidra", "trufflehog", "entropy", "wireshark", "afl", "scorecard", "pdf_report"]
    for t in all_stages_tools:
        if t not in plugin_manager.plugins:
            # Add a stub documentation
            tools_list.append({
                "name": t,
                "docs": {
                    "purpose": f"Placeholder for tool: {t}",
                    "input": "Generic analysis node input",
                    "output": "Generic analysis node output",
                    "workflow": "Standard stage of cybersecurity pipeline",
                    "commands": [{"command": f"{t} --help", "explanation": "Help command"}],
                    "common_errors": ["Connection timed out"],
                    "troubleshooting": "Restart execution container.",
                    "best_practices": "Check configurations.",
                    "references": ["C3iHub Smart Meter Analysis wiki"]
                }
            })
            
    return tools_list

@app.get("/api/projects/{project_id}/logs")
def get_project_logs(project_id: int, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    logs = db.query(models.LogEntry).join(models.ToolRun).filter(
        models.ToolRun.session_id == session.id
    ).order_by(models.LogEntry.timestamp.asc()).all()
    
    return [
        {
            "id": log.id,
            "tool_name": log.tool_run.tool_name,
            "log_type": log.log_type,
            "message": log.message,
            "timestamp": log.timestamp
        } for log in logs
    ]
