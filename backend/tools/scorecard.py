import argparse
import sys
import os
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Add the parent directory to sys.path to import app models
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.models import PipelineSession, ToolRun, LogEntry
from app.config import settings

def calculate_score(project_id):
    findings = []
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        session = db.query(PipelineSession).filter(PipelineSession.project_id == project_id).first()
        if not session:
            print(f"No pipeline session found for project {project_id}")
            return findings
            
        logs = db.query(LogEntry).join(ToolRun).filter(
            ToolRun.session_id == session.id,
            LogEntry.log_type == "STDOUT",
            LogEntry.message.like("%[!]%")
        ).all()
        
        score = 100
        finding_count = 0
        for log in logs:
            for line in log.message.split("\n"):
                if line.startswith("[!]"):
                    finding_count += 1
                    title = line.replace("[!]", "").strip()
                    tool_name = log.tool_run.tool_name if log.tool_run else "System"
                    
                    if tool_name == "trufflehog" or tool_name == "afl++":
                        score -= 15
                    elif tool_name == "entropy" or tool_name == "ghidra":
                        score -= 5
                    else:
                        score -= 2
                        
        score = max(0, score) # minimum score is 0
        
        findings.append({"type": "RiskScore", "match": f"Calculated Aggregate Risk Score: {score}/100 based on {finding_count} findings"})
        
    except Exception as e:
        print(f"Error calculating score: {e}")
    finally:
        db.close()
        
    return findings

def main():
    parser = argparse.ArgumentParser(description="Basic Scorecard Python Fallback")
    parser.add_argument("--target", required=True, help="Path to firmware file")
    parser.add_argument("--project", required=True, help="Project ID")
    parser.add_argument("--run-id", required=True, help="Tool Run ID")
    args = parser.parse_args()

    print(f"Starting Risk Scorecard Generation on project {args.project}...")
    time.sleep(1)
    
    findings = calculate_score(int(args.project))
    
    if findings:
        print(f"Found {len(findings)} finding(s).")
        for f in findings:
            print(f"[!] {f['type']}: {f['match']}")
            time.sleep(0.2)
    else:
         print("[!] RiskScore: Calculated Aggregate Risk Score: 100/100 (No findings)")
        
    print("Scan complete.")
    sys.exit(0)

if __name__ == "__main__":
    main()
