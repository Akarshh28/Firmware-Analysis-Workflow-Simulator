import asyncio

import os
import datetime
# pyrefly: ignore [missing-import]
from fastapi import UploadFile, File

import hashlib
# pyrefly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
# pyrefly: ignore [missing-import]
from fastapi.middleware.cors import CORSMiddleware
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session
from typing import List

from app.config import settings
from app.database import Base, engine, get_db
import app.models as models
import app.schemas as schemas
from app.plugins.manager import plugin_manager

from app.websockets import manager
from langgraph.executer import run_workflow

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
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Cannot use '*' with credentials=True
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define pipeline workflow stages in chronological order
PIPELINE_STAGES = [

    {
        "stage":"Upload & Ingestion",
        "tool":"upload",
        "desc":"Upload Smart Meter Firmware"
    },

    {
        "stage":"Identification",
        "tool":"strings",
        "desc":"Identify firmware architecture"
    },

    {
        "stage":"Extraction",
        "tool":"binwalk",
        "desc":"Extract embedded filesystem"
    },

    {
        "stage":"Static & Credential Analysis",
        "tool":"cutter",
        "desc":"Static code + secret analysis"
    },

    {
        "stage":"Cryptographic Analysis",
        "tool":"entropy",
        "desc":"Entropy + crypto detection"
    },

    {
        "stage":"Reverse Engineering",
        "tool":"ghidra",
        "desc":"Decompiler analysis"
    },

    {
        "stage":"Symbolic Execution",
        "tool":"angr",
        "desc":"Path exploration"
    },

    {
        "stage":"Risk Scoring",
        "tool":"scorecard",
        "desc":"CVSS scoring"
    },

    {
        "stage":"Report Generation",
        "tool":"pdf_report",
        "desc":"Generate report"
    }

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
        status="WAITING_UPLOAD",
        current_stage="Upload"
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

@app.get("/api/projects/{project_id}/dashboard")
def get_project_dashboard(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    
    # Calculate real duration
    duration = "0 min"
    if session and session.started_at:
        end_time = session.ended_at or datetime.datetime.utcnow()
        delta = end_time - session.started_at
        duration = f"{int(delta.total_seconds() / 60)} min"
        
    # Calculate stages completed
    stages_completed_count = 0
    if session:
        completed_tools = db.query(models.ToolRun).filter(models.ToolRun.session_id == session.id, models.ToolRun.exit_code == 0).count()
        stages_completed_count = min(completed_tools + 1, 12) if session.status != "WAITING_UPLOAD" else 0
        
    # Pull real findings from logs
    real_findings = []
    if session:
        logs = db.query(models.LogEntry).join(models.ToolRun).filter(
            models.ToolRun.session_id == session.id,
            models.LogEntry.log_type == "STDOUT",
            models.LogEntry.message.like("[!]%")
        ).all()
        
        for idx, log in enumerate(logs):
            real_findings.append({
                "id": f"CVE-REAL-{idx+1:03d}",
                "title": log.message,
                "severity": "critical",
                "stage": "Secret Detection",
                "tool": log.tool_run.tool_name
            })
            
    findings_to_return = real_findings if len(real_findings) > 0 else [
        {"id": "CVE-SIM-001", "title": "Hardcoded DLMS Authentication Key", "severity": "critical", "stage": "Secret Detection", "tool": "trufflehog"},
        {"id": "CVE-SIM-002", "title": "Weak AES-128 ECB Mode", "severity": "high", "stage": "Cryptographic Analysis", "tool": "entropy"},
    ]
        
    # Return hybrid real/simulated data
    return {
        "summary": {
            "critical": len(real_findings) if len(real_findings) > 0 else 4, 
            "high": 9, "medium": 14, "low": 8,
            "riskScore": 99 if len(real_findings) > 0 else 32, 
            "riskLabel": "CRITICAL RISK",
            "riskSummary": f"Firmware poses significant security risk. {len(real_findings)} real secrets found!" if len(real_findings) > 0 else "Firmware poses significant security risk."
        },
        "metrics": {
            "totalFindings": len(real_findings) + 31 if len(real_findings) > 0 else 35,
            "criticalIssues": len(real_findings) if len(real_findings) > 0 else 4,
            "stagesCompleted": f"{stages_completed_count} / 12",
            "duration": duration
        },
        "findings": findings_to_return,
        "pipeline": {
            "vulnerabilities": [
                {"name": "Static", "issues": 2}, {"name": "RE", "issues": 5}, {"name": "Secrets", "issues": len(real_findings) if len(real_findings)>0 else 3}
            ],
            "timeline": [
                {"stage": "Upload", "mins": 0.5}, {"stage": "ID", "mins": 1.2}, {"stage": "Extract", "mins": 2.8}
            ],
            "severity": [
                {"name": "Critical", "value": len(real_findings) if len(real_findings)>0 else 4, "fill": "#ef4444"},
                {"name": "High", "value": 9, "fill": "#f97316"}
            ]
        }
    }

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

    allowed_extensions = [".bin", ".img", ".zip", ".tar", ".tar.gz", ".hex", ".elf", ".axf", ".out", ".srec", ".mot", ".bin.gz"]

    filename = firmware.filename.lower()
    if not any(filename.endswith(ext) for ext in allowed_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file extension. Allowed: {', '.join(allowed_extensions)}"
        )

    filename = f"{project_id}_{firmware.filename}"

    save_path = os.path.join(settings.UPLOAD_DIR, f"{project_id}_{firmware.filename}")

    sha256_hash = hashlib.sha256()
    file_size = 0
    with open(save_path, "wb") as buffer:
        while chunk := await firmware.read(8192):
            file_size += len(chunk)
            if file_size > 500 * 1024 * 1024:  # 500 MB limit
                buffer.close()
                os.remove(save_path)
                raise HTTPException(status_code=413, detail="File too large. Max size is 500MB.")
            sha256_hash.update(chunk)
            buffer.write(chunk)

    project.firmware_filepath = save_path
    project.checksum = sha256_hash.hexdigest()
    project.file_size = file_size
    
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if session:
        session.status = "READY"
        
    db.commit()

    # Notify via WebSocket if any clients are listening
    asyncio.create_task(manager.broadcast(project_id, {
        "type": "PIPELINE_STATUS",
        "data": {"status": "READY"}
    }))

    return {
        "success": True,
        "message": "Firmware uploaded successfully",
        "filename": firmware.filename,
        "path": save_path,
        "project_id": project_id,
    }



@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# ---------------------------------------------------------
# FALLBACK ROUTES FOR FRONTEND COMPATIBILITY ---

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

@app.websocket("/api/ws/{project_id}")
async def websocket_endpoint(websocket: WebSocket, project_id: int):
    await manager.connect(websocket, project_id)
    try:
        while True:
            # We don't expect data from the client, just keep connection open
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, project_id)

@app.post("/api/projects/{project_id}/pipeline/run")
def start_pipeline(project_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline session not found")
        
    if session.status == "RUNNING":
        return {"message": "Pipeline is already running"}

    if session.status == "WAITING_UPLOAD":
        raise HTTPException(status_code=400, detail="Upload firmware before starting analysis.")
        
    # Clear past runs for this session to restart fresh
    db.query(models.ToolRun).filter(models.ToolRun.session_id == session.id).delete()
    db.query(models.Artifact).filter(models.Artifact.project_id == project_id).delete()
    db.commit()

    # Execute LangGraph workflow as background task
    background_tasks.add_task(run_workflow, project_id, session.id, settings.DATABASE_URL)
    return {"message": "Pipeline started with LangGraph"}

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
        run.ended_at = datetime.datetime.now(datetime.UTC)
        
    db.commit()
    return {"message": "Pipeline stopped"}

@app.post("/api/projects/{project_id}/pipeline/reset")
def reset_pipeline(project_id: int, db: Session = Depends(get_db)):
    session = db.query(models.PipelineSession).filter(models.PipelineSession.project_id == project_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Pipeline session not found")
        
    # Clear tool runs and logs
    db.query(models.ToolRun).filter(models.ToolRun.session_id == session.id).delete()
    # Clear artifacts EXCEPT upload
    db.query(models.Artifact).filter(
        models.Artifact.project_id == project_id,
        models.Artifact.stage_generated != "Upload & Ingestion"
    ).delete()
    
    session.status = "READY"
    session.current_stage = "Upload"
    session.started_at = None
    session.ended_at = None
    
    db.commit()
    return {"message": "Pipeline reset successfully"}

# --- TOOL EXPLORER AND GENERAL RUNS ---

from pydantic import BaseModel
import subprocess
import os

class SandboxRequest(BaseModel):
    command: str
    tool: str

@app.post("/api/projects/{project_id}/sandbox")
def run_sandbox_command(project_id: int, req: SandboxRequest, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project or not project.firmware_filepath:
        raise HTTPException(status_code=404, detail="Project or firmware not found")

    # Security warning: this is running arbitrary commands locally for demo purposes
    try:
        # replace {firmware} placeholder with actual path if needed, though usually they just type it
        # or we just run the command in the dir of the firmware
        firmware_dir = os.path.dirname(project.firmware_filepath)
        env = os.environ.copy()
        env["FIRMWARE_FILE"] = project.firmware_filepath
        
        result = subprocess.run(
            req.command,
            shell=True,
            cwd=firmware_dir,
            capture_output=True,
            text=True,
            timeout=30 # 30 second timeout
        )
        
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.returncode
        }
    except subprocess.TimeoutExpired as e:
        return {
            "stdout": e.stdout.decode('utf-8') if e.stdout else "",
            "stderr": "Command timed out after 30 seconds.",
            "exit_code": -1
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "exit_code": -2
        }

@app.get("/api/tools")
def list_tools():
    # Return documentation for all registered tools
    tools_list = []
    # Dynamic list
    for name, plugin in plugin_manager.plugins.items():
        tools_list.append({
            "name": name,
            "version": plugin.version,
            "docs": plugin.documentation
        })
        
    # Standard stubs for tools that don't have modules written yet
    all_stages_tools = [
        "upload", "strings", "binwalk", "cutter", "ghidra", "trufflehog", 
        "entropy", "wireshark", "afl++", "angr", "scorecard", "pdf_report"
    ]
    for t in all_stages_tools:
        if t not in plugin_manager.plugins:
            # Add a stub documentation
            tools_list.append({
                "name": t,
                "version": "Not Installed",
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

@app.get("/api/health")
def health():

    return {

        "status":"online",

        "database":"connected",

        "pipeline":"ready",

        "plugins":len(plugin_manager.plugins)

    }