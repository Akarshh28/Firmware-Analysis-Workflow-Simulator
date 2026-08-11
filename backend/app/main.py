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
    allow_origins=["*"],  # Cannot use '*' with credentials=True
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define pipeline workflow stages in chronological order
if settings.MODE == "real":
    PIPELINE_STAGES = [
        {"stage": "Upload & Ingestion", "tool": "upload", "desc": "Upload Smart Meter Firmware"},
        {"stage": "Extraction", "tool": "binwalk", "desc": "Extract embedded filesystem"},
        {"stage": "Identification", "tool": "strings", "desc": "Identify firmware architecture"},
        {"stage": "Cryptographic Analysis", "tool": "entropy", "desc": "Entropy + crypto detection"},
        {"stage": "YARA Analysis", "tool": "yara", "desc": "YARA signature scanning"},
        {"stage": "Symbol Analysis", "tool": "symbol_analysis", "desc": "Symbol table analysis"},
        {"stage": "Risk Scoring", "tool": "scorecard", "desc": "CVSS scoring"},
        {"stage": "Report Generation", "tool": "pdf_report", "desc": "Generate report"}
    ]
else:
    PIPELINE_STAGES = [
        {"stage": "Upload & Ingestion", "tool": "upload", "desc": "Upload Smart Meter Firmware"},
        {"stage": "Identification", "tool": "strings", "desc": "Identify firmware architecture"},
        {"stage": "Extraction", "tool": "binwalk", "desc": "Extract embedded filesystem"},
        {"stage": "Static & Credential Analysis", "tool": "cutter", "desc": "Static code + secret analysis"},
        {"stage": "Reverse Engineering", "tool": "ghidra", "desc": "Decompiler analysis"},
        {"stage": "Static & Credential Analysis", "tool": "trufflehog", "desc": "Secret detection"},
        {"stage": "Cryptographic Analysis", "tool": "entropy", "desc": "Entropy + crypto detection"},
        {"stage": "Network Analysis", "tool": "wireshark", "desc": "Network protocol analysis"},
        {"stage": "Dynamic Analysis", "tool": "afl++", "desc": "Fuzzing"},
        {"stage": "Symbolic Execution", "tool": "angr", "desc": "Path exploration"},
        {"stage": "Risk Scoring", "tool": "scorecard", "desc": "CVSS scoring"},
        {"stage": "Report Generation", "tool": "pdf_report", "desc": "Generate report"}
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
        total_secs = int(delta.total_seconds())
        if total_secs < 60:
            duration = f"{total_secs} sec"
        else:
            mins = total_secs // 60
            secs = total_secs % 60
            duration = f"{mins}m {secs}s"
        
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
            models.LogEntry.log_type.in_(["STDOUT", "JSON_FINDINGS"])
        ).all()
        
        finding_idx = 1
        import json
        for log in logs:
            tool_name = log.tool_run.tool_name if log.tool_run else "System"
            if log.log_type == "JSON_FINDINGS":
                try:
                    findings_data = json.loads(log.message)
                    for f in findings_data:
                        real_findings.append({
                            "id": f"CVE-REAL-{finding_idx:03d}",
                            "title": f.get("description", f.get("value", "Unknown Finding")),
                            "severity": f.get("severity", "info").lower(),
                            "stage": "Security Analysis",
                            "tool": tool_name,
                            "cvss": 9.0 if f.get("severity") == "critical" else (7.0 if f.get("severity") == "high" else (5.0 if f.get("severity") == "medium" else 2.0)),
                            "cwe": f.get("cwe", "CWE-000"),
                            "description": f.get("description", "A finding was detected by real analysis."),
                            "poc": f"JSON Data: {json.dumps(f)}",
                            "remediation": "Investigate this specific finding."
                        })
                        finding_idx += 1
                except Exception:
                    pass
            elif log.log_type == "STDOUT" and "[!]" in log.message:
                for line in log.message.split("\n"):
                    line = line.strip()
                    if line.startswith("[!]"):
                        title = line.replace("[!]", "").strip()
                        tool_name = log.tool_run.tool_name if log.tool_run else "System"
                        
                        # Generate production-level details based on tool
                        cvss = 5.0
                        severity = "medium"
                        cwe = "CWE-000"
                        desc = f"An anomaly or potential finding was detected by {tool_name} during analysis. The raw output is: {title}."
                        poc = f"[{tool_name}] output:\n{title}"
                        remediation = "Investigate the extracted artifact or pattern to determine its security impact."
                        
                        if tool_name == "strings":
                            cvss = 4.3
                            severity = "low"
                            cwe = "CWE-200"
                            desc = f"The strings extraction analysis identified potentially sensitive information embedded within the binary. Specifically, it matched the pattern for: {title}. Hardcoded strings can expose internal network layouts, diagnostic URLs, or debugging paths to attackers."
                            poc = f"$ strings firmware.bin | grep -i '{title.split(':', 1)[0] if ':' in title else title}'\n{title}"
                            remediation = "1. Avoid hardcoding sensitive paths or URLs in the firmware.\n2. Consider encrypting or obfuscating critical strings at compile time."
                        elif tool_name == "trufflehog":
                            cvss = 9.8
                            severity = "critical"
                            cwe = "CWE-798"
                            desc = f"A hardcoded cryptographic secret or credential was detected in the firmware image. The scanner reported: {title}. Hardcoded credentials allow unauthorized access, privilege escalation, or decryption of secure communications."
                            poc = f"$ trufflehog filesystem ./extracted_firmware/\n[+] Secret Found: {title}"
                            remediation = "1. Immediately rotate any compromised credentials.\n2. Store secrets securely using a hardware secure element or trusted execution environment (TEE).\n3. Avoid placing API keys or passwords in the compiled firmware."
                        elif tool_name == "entropy":
                            cvss = 6.5
                            severity = "medium"
                            cwe = "CWE-326"
                            desc = f"High entropy regions were detected, suggesting encrypted or compressed data. {title}. If custom encryption is used, it may be vulnerable to cryptanalysis."
                            poc = f"$ binwalk -E firmware.bin\nHigh entropy section found: {title}"
                            remediation = "1. Ensure standard, well-vetted cryptographic libraries are used.\n2. Verify that entropy is not a result of obfuscation intended to hide malicious payloads."
                        elif tool_name == "afl++":
                            cvss = 8.8
                            severity = "high"
                            cwe = "CWE-119"
                            desc = f"The dynamic fuzzer caused a crash or anomalous behavior during execution. {title}. This indicates a potential memory corruption vulnerability such as a buffer overflow."
                            poc = f"$ afl-fuzz -i seeds/ -o findings/ -- ./binary @@\nCrash detected: {title}"
                            remediation = "1. Analyze the crashing input and fix the memory corruption bug.\n2. Compile with stack canaries and ASLR.\n3. Validate all inputs before processing."
                        
                        real_findings.append({
                            "id": f"CVE-REAL-{finding_idx:03d}",
                            "title": title,
                            "severity": severity,
                            "stage": "Security Analysis",
                            "tool": tool_name,
                            "cvss": cvss,
                            "cwe": cwe,
                            "description": desc,
                            "poc": poc,
                            "remediation": remediation
                        })
                        finding_idx += 1
            
    findings_to_return = real_findings
    
    # Calculate severities
    crit_count = sum(1 for f in real_findings if f["severity"] == "critical")
    high_count = sum(1 for f in real_findings if f["severity"] == "high")
    med_count = sum(1 for f in real_findings if f["severity"] == "medium")
    low_count = sum(1 for f in real_findings if f["severity"] == "low")
    
    # Calculate risk score
    risk_score = min(100, (crit_count * 25) + (high_count * 15) + (med_count * 5) + (low_count * 1))
    risk_label = "CRITICAL RISK" if risk_score > 75 else "HIGH RISK" if risk_score > 50 else "MEDIUM RISK" if risk_score > 25 else "LOW RISK"
    
    total_findings = crit_count + high_count + med_count + low_count
    
    # Calculate timeline and vulnerabilities per stage
    pipeline_vulnerabilities = []
    pipeline_timeline = []
    
    for stage_def in PIPELINE_STAGES:
        stage_name = stage_def["stage"]
        # UI expects short names for charts
        short_names = {
            "Upload & Ingestion": "Upload", "Identification": "ID", "Extraction": "Extract",
            "Static & Credential Analysis": "Static", "Reverse Engineering": "RE",
            "Cryptographic Analysis": "Crypto", "Network Analysis": "Network",
            "Dynamic Analysis": "Fuzzing", "Symbolic Execution": "Symbolic",
            "Risk Scoring": "Risk", "Report Generation": "Report"
        }
        short_name = short_names.get(stage_name, stage_name.split()[0])
        
        # We need to map tool_name to vulnerabilities since stage names might overlap (e.g. Cutter and Trufflehog both are Static & Credential Analysis)
        tool_name = stage_def["tool"]
        issues = sum(1 for f in real_findings if f.get("tool") == tool_name and f.get("severity") in ["critical", "high", "medium", "low"])
        
        # To avoid duplicates in vulnerabilities array if multiple tools use the same stage name
        existing_vuln = next((v for v in pipeline_vulnerabilities if v["name"] == short_name), None)
        if existing_vuln:
            existing_vuln["issues"] += issues
        else:
            pipeline_vulnerabilities.append({"name": short_name, "issues": issues})
        
        # timeline
        mins = 0.0
        if session:
            run = db.query(models.ToolRun).filter(
                models.ToolRun.session_id == session.id,
                models.ToolRun.tool_name == tool_name
            ).first()
            if run and run.started_at and run.ended_at:
                mins = round((run.ended_at - run.started_at).total_seconds() / 60.0, 2)
        pipeline_timeline.append({"stage": short_name, "mins": mins or 0.1})
        
    from .obis_parser import OBISParser
    obis_mappings = []
    if session:
        all_logs = db.query(models.LogEntry).join(models.ToolRun).filter(
            models.ToolRun.session_id == session.id
        ).all()
        
        extracted_codes = {}
        for log in all_logs:
            if log.message:
                parsed_list = OBISParser.extract_from_text(log.message)
                for parsed in parsed_list:
                    code = parsed["code"]
                    if code not in extracted_codes:
                        tool_name = log.tool_run.tool_name if log.tool_run else "Unknown"
                        source_str = "Network (Wireshark)" if tool_name == "wireshark" else "Config (Strings)" if tool_name == "strings" else f"Binary ({tool_name})"
                        
                        status = "Extracted"
                        if parsed["access"] == "Read/Write" or (tool_name == "wireshark" and "Serial" not in parsed["name"]):
                            status = "Vulnerable"
                            
                        extracted_codes[code] = {
                            "code": code,
                            "name": parsed["name"],
                            "access": parsed["access"],
                            "source": source_str,
                            "status": status
                        }
        
        obis_mappings = list(extracted_codes.values())

    # Determine Protocol Verdict and DLMS Suite
    dlms_suite = "Unknown"
    protocol_verdict = "No DLMS/COSEM or IEC 61850 evidence found"
    
    try:
        state_path = os.path.join(settings.ARTIFACTS_DIR, f"{project_id}_real_state.json")
        if os.path.exists(state_path):
            import json
            with open(state_path, "r") as f:
                state_data = json.load(f)
            
            # Use report generator to compute verdict if possible, but for simplicity here we compute based on hits
            strings_results = state_data.get("strings_results", {})
            yara_results = state_data.get("yara_results", {})
            
            has_dlms = False
            has_iec = False
            has_acse = False
            
            for leaf, res in strings_results.items():
                if res.get("success"):
                    matches = res.get("matches", {})
                    if "dlms_cosem" in matches: has_dlms = True
                    if "iec61850" in matches: has_iec = True
                    if "acse_association" in matches: has_acse = True
                    
            if has_dlms:
                protocol_verdict = "DLMS/COSEM likely"
            elif has_iec:
                protocol_verdict = "IEC 61850 (DLMS/COSEM not present)"
            elif has_acse:
                protocol_verdict = "ACSE present but unconfirmed"
                
            for leaf, res in yara_results.items():
                if res.get("success"):
                    for match in res.get("matches", []):
                        if "dlms" in match.get("rule", "").lower():
                            protocol_verdict = "DLMS/COSEM confirmed"
                            break

            # Suite determination based on findings
            dlms_suite = "Suite 1 (AES-GCM-128)"
            for f in real_findings:
                if f.get("cwe") in ["CWE-798", "CWE-327", "CWE-319"]:
                    dlms_suite = "Suite 0 (Vulnerable / Plaintext)"
                    break
    except Exception as e:
        print(f"Error determining verdict: {e}")
    return {
        "summary": {
            "critical": crit_count, 
            "high": high_count, "medium": med_count, "low": low_count,
            "riskScore": risk_score, 
            "riskLabel": risk_label,
            "riskSummary": f"Firmware analysis complete. {crit_count} critical vulnerabilities and {total_findings} total findings detected.",
            "dlmsSuite": dlms_suite,
            "protocolVerdict": protocol_verdict
        },
        "metrics": {
            "totalFindings": total_findings,
            "criticalIssues": crit_count,
            "stagesCompleted": f"{stages_completed_count} / {len(PIPELINE_STAGES)}" if session else f"0 / {len(PIPELINE_STAGES)}",
            "duration": duration
        },
        "findings": findings_to_return,
        "obis_mappings": obis_mappings,
        "pipeline": {
            "vulnerabilities": pipeline_vulnerabilities,
            "timeline": pipeline_timeline,
            "severity": [
                {"name": "Critical", "value": crit_count, "fill": "#ef4444"},
                {"name": "High", "value": high_count, "fill": "#f97316"},
                {"name": "Medium", "value": med_count, "fill": "#f59e0b"},
                {"name": "Low", "value": low_count, "fill": "#22c55e"}
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
    return {"status": "ok", "version": "v3_run_as_root"}

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
        elif tool_name == "upload" and session.status != "WAITING_UPLOAD":
            status = "success"
            exit_code = 0
            
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
        
        import shlex
        result = subprocess.run(
            shlex.split(req.command),
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
    tools_list = []
    all_stages_tools = [
        "upload", "strings", "binwalk", "cutter", "ghidra", "trufflehog", 
        "entropy", "wireshark", "afl++", "angr", "yara", "scorecard", "pdf_report"
    ]
    for t in all_stages_tools:
        if t == "yara":
            tools_list.append({
                "name": t,
                "version": "4.3.2",
                "docs": {
                    "purpose": "YARA Rule Set Editor/Viewer: Scans the extracted firmware for known threat signatures, crypto materials, and bad coding patterns using explicit rule sets.",
                    "input": "Extracted firmware files or memory dumps.",
                    "output": "Matching YARA rules and offsets.",
                    "workflow": "Runs concurrently with Static Analysis to flag known bad patterns.",
                    "commands": [
                        {"command": "yara -r rules/dlms_crypto.yar _flash.bin.extracted/", "explanation": "Scan extracted filesystem for DLMS crypto keys"},
                        {"command": "yara -r rules/hardcoded_passwords.yar _flash.bin.extracted/", "explanation": "Scan for default admin credentials"}
                    ],
                    "common_errors": ["Syntax error in rule file"],
                    "troubleshooting": "Validate YARA rules with 'yara -c'. Ensure the rules directory is accessible.",
                    "best_practices": "Keep rule sets updated with latest threat intel. Group rules by CVE or component.",
                    "references": ["YARA Documentation", "DLMS Security Suite Signatures"]
                }
            })
        else:
            tools_list.append({
                "name": t,
                "version": "1.0",
                "docs": {
                    "purpose": f"Documentation for tool: {t}",
                    "input": "Target firmware binary",
                    "output": "Analysis log and generated artifacts",
                    "workflow": "Standard stage of cybersecurity pipeline",
                    "commands": [{"command": f"{t} --help", "explanation": "Help command"}],
                    "common_errors": ["Binary not found in PATH"],
                    "troubleshooting": "Ensure binary is installed and executable.",
                    "best_practices": "Check configurations.",
                    "references": ["FAWS Wiki"]
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

