import asyncio
import datetime
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import sessionmaker
from app.database import SessionLocal
from app.models import PipelineSession
from langgraph.builder import graph
from app.websockets import manager

async def run_workflow(project_id: int, session_id: int, db_url: str):
    db = SessionLocal()
    try:
        session = db.query(PipelineSession).filter(PipelineSession.id == session_id).first()
        if not session:
            return
            
        session.status = "RUNNING"
        session.started_at = datetime.datetime.utcnow()
        db.commit()

        await manager.broadcast(project_id, {
            "type": "PIPELINE_STATUS",
            "data": {"status": "RUNNING"}
        })

        initial_state = {
            "project_id": project_id,
            "session_id": session_id,
            "db_url": db_url,
            "current_stage": "Upload",
            "logs": [],
            "artifacts": [],
            "errors": [],
            "status": "RUNNING"
        }

        # Execute graph
        final_state = await graph.ainvoke(initial_state)

        # Update final state
        session = db.query(PipelineSession).filter(PipelineSession.id == session_id).first()
        if final_state.get("status") == "FAILED":
            session.status = "FAILED"
        else:
            session.status = "COMPLETED"
        
        session.ended_at = datetime.datetime.utcnow()
        db.commit()

        await manager.broadcast(project_id, {
            "type": "PIPELINE_STATUS",
            "data": {"status": session.status}
        })
        
    except Exception as e:
        print(f"Workflow execution error: {e}")
        session = db.query(PipelineSession).filter(PipelineSession.id == session_id).first()
        if session:
            session.status = "FAILED"
            session.ended_at = datetime.datetime.utcnow()
            db.commit()
            
        await manager.broadcast(project_id, {
            "type": "PIPELINE_STATUS",
            "data": {"status": "FAILED", "error": str(e)}
        })
    finally:
        db.close()
