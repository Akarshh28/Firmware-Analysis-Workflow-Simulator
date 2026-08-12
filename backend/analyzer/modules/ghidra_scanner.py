import os
import subprocess
import json
import uuid
import sys
from app.config import settings

def scan_with_ghidra(target_bin: str) -> dict:
    """
    Spawns Ghidra Headless Analyzer to run the FAWS Jython script.
    """
    # Use environment variable or fallback to a common default path on Windows
    ghidra_path = os.getenv("GHIDRA_PATH", "C:\\ghidra\\support\\analyzeHeadless.bat")
    
    if not os.path.exists(ghidra_path):
        return {
            "success": False,
            "error": f"Ghidra analyzeHeadless.bat not found at {ghidra_path}. Please set GHIDRA_PATH.",
            "findings": []
        }

    # Setup directories
    project_dir = os.path.join(settings.ARTIFACTS_DIR, "ghidra_temp")
    os.makedirs(project_dir, exist_ok=True)
    
    project_name = f"faws_{uuid.uuid4().hex[:8]}"
    
    scripts_dir = os.path.join(settings.BASE_DIR, "analyzer", "ghidra_scripts")
    output_json = os.path.join(project_dir, f"{project_name}_findings.json")
    
    # Build Ghidra headless command
    # analyzeHeadless <project_location> <project_name> -import <target_file> -postScript <script_name> [args...]
    cmd = [
        ghidra_path,
        project_dir,
        project_name,
        "-import", target_bin,
        "-scriptPath", scripts_dir,
        "-postScript", "dlms_analyzer.py", output_json,
        "-deleteProject" # Clean up after analysis
    ]
    
    try:
        # Run Ghidra
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait for completion (Ghidra analysis can take several minutes)
        stdout, stderr = process.communicate(timeout=600) # 10 min timeout
        
        if process.returncode != 0 and not os.path.exists(output_json):
            return {
                "success": False,
                "error": f"Ghidra execution failed: {stderr[-500:] if stderr else 'Unknown error'}",
                "findings": []
            }
            
        # Parse JSON output
        if os.path.exists(output_json):
            with open(output_json, "r") as f:
                findings = json.load(f)
                
            return {
                "success": True,
                "findings": findings
            }
        else:
            return {
                "success": True,
                "findings": []
            }
            
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "Ghidra analysis timed out after 10 minutes.",
            "findings": []
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "findings": []
        }
