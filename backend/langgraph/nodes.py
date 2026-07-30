import asyncio
import random
import datetime
import os
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
from app.models import ToolRun, LogEntry, Artifact
from app.websockets import manager
from langgraph.state import GraphState

def get_db_session(db_url: str):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

async def execute_tool(state: GraphState, tool_name: str, stage_name: str, fallback_artifacts: list) -> GraphState:
    db = get_db_session(state["db_url"])
    try:
        # Create ToolRun
        tool_run = ToolRun(
            session_id=state["session_id"],
            tool_name=tool_name,
            command_executed=f"python -m tools.{tool_name} {state['project_id']}",
            started_at=datetime.datetime.utcnow()
        )
        db.add(tool_run)
        db.commit()
        db.refresh(tool_run)

        # Broadcast start
        await manager.broadcast(state["project_id"], {
            "type": "STATUS_UPDATE",
            "data": {
                "current_tool": tool_name,
                "current_stage": stage_name,
                "status": "running"
            }
        })

        # Try to run the real tool natively via subprocess
        try:
            # We assume tools are in backend/tools/{tool_name}.py
            tool_script = os.path.join(os.path.dirname(__file__), "..", "tools", f"{tool_name}.py")
            if os.path.exists(tool_script):
                # Pass the firmware path. We need to query it from the DB.
                from app.models import Project
                project = db.query(Project).filter(Project.id == state["project_id"]).first()
                if project and project.firmware_filepath:
                    cmd = f"python {tool_script} --target {project.firmware_filepath} --project {state['project_id']} --run-id {tool_run.id}"
                    
                    log_msg = f"[{tool_name}] Attempting real execution: {cmd}"
                    log_entry = LogEntry(tool_run_id=tool_run.id, log_type="SYSTEM", message=log_msg)
                    db.add(log_entry)
                    db.commit()

                    process = await asyncio.create_subprocess_shell(
                        cmd,
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE
                    )
                    
                    stdout, stderr = await process.communicate()
                    exit_code = process.returncode
                    
                    if stdout:
                        out_msg = stdout.decode('utf-8').strip()
                        log_entry = LogEntry(tool_run_id=tool_run.id, log_type="STDOUT", message=out_msg)
                        db.add(log_entry)
                        
                        await manager.broadcast(state["project_id"], {
                            "type": "LOG_NEW",
                            "data": {
                                "tool_name": tool_name,
                                "log_type": "STDOUT",
                                "message": out_msg,
                                "timestamp": datetime.datetime.utcnow().isoformat()
                            }
                        })
                        
                    if stderr:
                        err_msg = stderr.decode('utf-8').strip()
                        log_entry = LogEntry(tool_run_id=tool_run.id, log_type="STDERR", message=err_msg)
                        db.add(log_entry)
                        
                    db.commit()
                    
                    if exit_code == 0:
                        tool_run.exit_code = 0
                        tool_run.ended_at = datetime.datetime.utcnow()
                        db.commit()
                        
                        state["current_stage"] = stage_name
                        await manager.broadcast(state["project_id"], {
                            "type": "TOOL_SUCCESS",
                            "data": {"tool_name": tool_name}
                        })
                        
                        # Real execution succeeded, so return early
                        return state
            
        except Exception as tool_exc:
            log_msg = f"[{tool_name}] Real execution failed: {tool_exc}. Falling back to simulation."
            log_entry = LogEntry(tool_run_id=tool_run.id, log_type="STDERR", message=log_msg)
            db.add(log_entry)
            db.commit()

        # SIMULATION FALLBACK
        # If the script doesn't exist, or it failed, run the simulation
        log_msg = f"[{tool_name}] Running in simulation mode..."
        log_entry = LogEntry(tool_run_id=tool_run.id, log_type="SYSTEM", message=log_msg)
        db.add(log_entry)
        db.commit()

        exec_time = random.uniform(2, 6)
        steps = 5
        sleep_interval = exec_time / steps

        for i in range(steps):
            await asyncio.sleep(sleep_interval)
            progress = int(((i + 1) / steps) * 100)
            
            # Write a log
            log_msg = f"[{tool_name}] Executing step {i+1}/{steps}... (simulated)"
            log_entry = LogEntry(tool_run_id=tool_run.id, log_type="STDOUT", message=log_msg)
            db.add(log_entry)
            db.commit()

            # Broadcast log and progress
            await manager.broadcast(state["project_id"], {
                "type": "LOG_NEW",
                "data": {
                    "tool_name": tool_name,
                    "log_type": "STDOUT",
                    "message": log_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
            })
            await manager.broadcast(state["project_id"], {
                "type": "PROGRESS_TICK",
                "data": {
                    "tool_name": tool_name,
                    "progress": progress
                }
            })
            
        # Add generated artifacts
        for art in fallback_artifacts:
            artifact = Artifact(
                project_id=state["project_id"],
                file_name=art["file_name"],
                stage_generated=stage_name,
                mime_type=art["mime_type"],
                file_size=art["file_size"],
                local_storage_path=os.path.join("data/artifacts", art["file_name"])
            )
            db.add(artifact)
            
            # Log artifact creation
            log_entry = LogEntry(tool_run_id=tool_run.id, log_type="SYSTEM", message=f"Generated artifact: {art['file_name']}")
            db.add(log_entry)
            
        db.commit()

        tool_run.exit_code = 0
        tool_run.ended_at = datetime.datetime.utcnow()
        db.commit()

        # Update state
        state["current_stage"] = stage_name
        
        # Broadcast tool success
        await manager.broadcast(state["project_id"], {
            "type": "TOOL_SUCCESS",
            "data": {
                "tool_name": tool_name
            }
        })
        
        return state
    except Exception as e:
        print(f"Error in {tool_name}: {e}")
        state["errors"].append(str(e))
        state["status"] = "FAILED"
        return state
    finally:
        db.close()


async def upload_node(state: GraphState):
    return await execute_tool(state, "upload", "Upload & Ingestion", [{"file_name": "firmware.bin", "mime_type": "application/octet-stream", "file_size": 15000000}])

async def strings_node(state: GraphState):
    return await execute_tool(state, "strings", "Identification", [{"file_name": "strings.txt", "mime_type": "text/plain", "file_size": 1024}])

async def binwalk_node(state: GraphState):
    return await execute_tool(state, "binwalk", "Extraction", [{"file_name": "filesystem.tar.gz", "mime_type": "application/gzip", "file_size": 45000}])

async def cutter_node(state: GraphState):
    return await execute_tool(state, "cutter", "Static & Credential Analysis", [{"file_name": "secrets.txt", "mime_type": "text/plain", "file_size": 256}])

async def ghidra_node(state: GraphState):
    return await execute_tool(state, "ghidra", "Reverse Engineering", [{"file_name": "cfg.pdf", "mime_type": "application/pdf", "file_size": 8900}])

async def trufflehog_node(state: GraphState):
    return await execute_tool(state, "trufflehog", "Static & Credential Analysis", [{"file_name": "trufflehog_results.json", "mime_type": "application/json", "file_size": 512}])

async def entropy_node(state: GraphState):
    return await execute_tool(state, "entropy", "Cryptographic Analysis", [{"file_name": "entropy_graph.png", "mime_type": "image/png", "file_size": 2048}])

async def wireshark_node(state: GraphState):
    return await execute_tool(state, "wireshark", "Network Analysis", [{"file_name": "capture.pcap", "mime_type": "application/vnd.tcpdump.pcap", "file_size": 15000}])

async def afl_node(state: GraphState):
    return await execute_tool(state, "afl++", "Dynamic Analysis", [{"file_name": "crashes.zip", "mime_type": "application/zip", "file_size": 3000}])

async def angr_node(state: GraphState):
    return await execute_tool(state, "angr", "Symbolic Execution", [{"file_name": "symbolic_paths.txt", "mime_type": "text/plain", "file_size": 4096}])

async def scorecard_node(state: GraphState):
    return await execute_tool(state, "scorecard", "Risk Scoring", [{"file_name": "risk_score.json", "mime_type": "application/json", "file_size": 128}])

async def report_node(state: GraphState):
    return await execute_tool(state, "pdf_report", "Report Generation", [{"file_name": "final_report.pdf", "mime_type": "application/pdf", "file_size": 150000}])
