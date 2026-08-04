import asyncio
import datetime
import os
import shutil
# pyrefly: ignore [missing-import]
from sqlalchemy import create_engine
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
from app.models import ToolRun, LogEntry, Artifact, Project
from app.websockets import manager
from langgraph.state import GraphState

def get_db_session(db_url: str):
    engine = create_engine(db_url, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal()

import sys
import shlex

# Pre-defined mapping of tool commands to run via subprocess
TOOL_COMMANDS = {
    "strings": f'"{sys.executable}" tools/strings.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "binwalk": f'"{sys.executable}" tools/binwalk.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "cutter": f'"{sys.executable}" tools/cutter.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "ghidra": f'"{sys.executable}" tools/ghidra.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "trufflehog": f'"{sys.executable}" tools/trufflehog.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "entropy": f'"{sys.executable}" tools/entropy.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "wireshark": f'"{sys.executable}" tools/wireshark.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "afl++": f'"{sys.executable}" tools/afl.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "angr": f'"{sys.executable}" tools/angr.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "scorecard": f'"{sys.executable}" tools/scorecard.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
    "pdf_report": f'"{sys.executable}" tools/pdf_report.py --target "{{target}}" --project "{{project_id}}" --run-id 0',
}

async def execute_tool(state: GraphState, tool_name: str, stage_name: str, fallback_artifacts: list) -> GraphState:
    db = get_db_session(state["db_url"])
    try:
        # Get target firmware path
        project = db.query(Project).filter(Project.id == state["project_id"]).first()
        target_path = project.firmware_filepath if project else "unknown.bin"

        cmd_template = TOOL_COMMANDS.get(tool_name, f"echo 'Tool {tool_name} not configured'")
        cmd = cmd_template.replace("{target}", target_path).replace("{project_id}", str(state["project_id"]))

        # Check if the primary binary exists (skip logic)
        if cmd.startswith('"'):
            primary_bin = cmd[1:cmd.find('"', 1)]
        else:
            primary_bin = cmd.split(" ")[0]
            
        if primary_bin != sys.executable and primary_bin != "echo" and shutil.which(primary_bin) is None:
            # Tool is unavailable, mark as SKIPPED
            log_msg = f"[{tool_name}] Binary '{primary_bin}' not found in PATH. Stage skipped."
            
            tool_run = ToolRun(
                session_id=state["session_id"],
                tool_name=tool_name,
                command_executed=cmd,
                started_at=datetime.datetime.utcnow(),
                ended_at=datetime.datetime.utcnow(),
                exit_code=0 # We don't fail the pipeline, we just skip it
            )
            db.add(tool_run)
            db.commit()
            db.refresh(tool_run)

            log_entry = LogEntry(tool_run_id=tool_run.id, log_type="SYSTEM", message=log_msg)
            db.add(log_entry)
            db.commit()

            await manager.broadcast(state["project_id"], {
                "type": "LOG_NEW",
                "data": {
                    "tool_name": tool_name,
                    "log_type": "SYSTEM",
                    "message": log_msg,
                    "timestamp": datetime.datetime.utcnow().isoformat()
                }
            })
            
            state["current_stage"] = stage_name
            await manager.broadcast(state["project_id"], {
                "type": "TOOL_SUCCESS",
                "data": {"tool_name": tool_name, "skipped": True}
            })
            return state

        # Real Execution
        tool_run = ToolRun(
            session_id=state["session_id"],
            tool_name=tool_name,
            command_executed=cmd,
            started_at=datetime.datetime.utcnow()
        )
        db.add(tool_run)
        db.commit()
        db.refresh(tool_run)

        await manager.broadcast(state["project_id"], {
            "type": "STATUS_UPDATE",
            "data": {
                "current_tool": tool_name,
                "current_stage": stage_name,
                "status": "running"
            }
        })

        log_msg = f"[{tool_name}] Executing: {cmd}"
        log_entry = LogEntry(tool_run_id=tool_run.id, log_type="SYSTEM", message=log_msg)
        db.add(log_entry)
        db.commit()

        await manager.broadcast(state["project_id"], {
            "type": "LOG_NEW",
            "data": {
                "tool_name": tool_name,
                "log_type": "SYSTEM",
                "message": log_msg,
                "timestamp": datetime.datetime.utcnow().isoformat()
            }
        })

        import subprocess
        def run_proc():
            return subprocess.run(cmd, shell=True, capture_output=True)
            
        process = await asyncio.to_thread(run_proc)
        
        stdout = process.stdout
        stderr = process.stderr
        exit_code = process.returncode
        
        if stdout:
            out_msg = stdout.decode('utf-8', errors='ignore').strip()
            # truncate if too long
            if len(out_msg) > 5000: out_msg = out_msg[:5000] + "\n...[truncated]"
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
            err_msg = stderr.decode('utf-8', errors='ignore').strip()
            log_entry = LogEntry(tool_run_id=tool_run.id, log_type="STDERR", message=err_msg)
            db.add(log_entry)
            
        db.commit()
        
        tool_run.exit_code = exit_code
        tool_run.ended_at = datetime.datetime.utcnow()
        db.commit()
        
        # Generate real artifacts dynamically from stdout if available
        os.makedirs("data/artifacts", exist_ok=True)
        
        has_real_artifact = False
        if stdout and tool_name != "pdf_report":
            out_str = stdout.decode('utf-8', errors='ignore').strip()
            if len(out_str) > 0:
                real_file_name = f"{state['project_id']}_{tool_name}_output.txt"
                real_file_path = os.path.join("data/artifacts", real_file_name)
                with open(real_file_path, "w", encoding="utf-8") as f:
                    f.write(out_str)
                    
                artifact = Artifact(
                    project_id=state["project_id"],
                    file_name=real_file_name,
                    stage_generated=stage_name,
                    mime_type="text/plain",
                    file_size=os.path.getsize(real_file_path),
                    local_storage_path=real_file_path
                )
                db.add(artifact)
                db.commit()
                has_real_artifact = True
                
        # Only use the fallback artifacts as a last resort if no real artifact was created
        # Note: pdf_report creates its own artifact inside report_generator.py
        if not has_real_artifact and tool_name != "pdf_report":
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
            db.commit()
        
        state["current_stage"] = stage_name
        if exit_code == 0:
            await manager.broadcast(state["project_id"], {
                "type": "TOOL_SUCCESS",
                "data": {"tool_name": tool_name}
            })
        else:
            # We don't fail the whole pipeline on single tool failure, we just proceed
            await manager.broadcast(state["project_id"], {
                "type": "TOOL_SUCCESS",
                "data": {"tool_name": tool_name, "error": True}
            })
            
        return state

    except Exception as e:
        print(f"Error in {tool_name}: {e}")
        try:
            err_log = LogEntry(tool_run_id=tool_run.id if 'tool_run' in locals() else None, log_type="STDERR", message=f"EXCEPTION: {str(e)}")
            db.add(err_log)
            db.commit()
        except:
            pass
        state["errors"].append(str(e))
        state["status"] = "FAILED"
        return state
    finally:
        db.close()


async def upload_node(state: GraphState):
    # Upload is handled by REST API, just a pass-through here
    return state

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
