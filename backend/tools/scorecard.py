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

import json

def calculate_score(project_id):
    engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    findings = []
    try:
        session = db.query(PipelineSession).filter(PipelineSession.project_id == project_id).first()
        if not session:
            return findings

        json_logs = db.query(LogEntry).join(ToolRun).filter(
            ToolRun.session_id == session.id,
            LogEntry.log_type == "JSON_FINDINGS",
        ).all()

        severity_weight = {"critical": 4, "high": 3, "medium": 2, "low": 1, "info": 0}
        seen = set()          # dedupe identical (category, value) repeats
        weighted_sum = 0
        finding_count = 0

        for log in json_logs:
            try:
                items = json.loads(log.message)
            except (json.JSONDecodeError, TypeError):
                continue
            for item in items:
                key = (item.get("category"), item.get("value"))
                if key in seen:
                    continue
                seen.add(key)
                finding_count += 1
                sev = str(item.get("severity", "info")).lower()
                weighted_sum += severity_weight.get(sev, 0)

        if finding_count == 0:
            score = 100
        else:
            avg_severity = weighted_sum / finding_count      # 0 (all info) to 4 (all critical)
            score = round(100 * (1 - avg_severity / 4))
        score = max(0, min(100, score))

        findings.append({
            "type": "RiskScore",
            "match": f"Calculated Aggregate Risk Score: {score}/100 based on {finding_count} unique findings",
        })
    except Exception as e:
        print(f"Error calculating score: {e}")
    finally:
        db.close()
    return findings
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
