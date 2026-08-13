import requests
import time
import subprocess

API_BASE = "https://firmware-analysis-workflow-simulator-1.onrender.com/api"

print("Waiting for deployment... Polling /api/health for version 'v3_run_as_root'")
start_time = time.time()
while True:
    try:
        res = requests.get(f"{API_BASE}/health", timeout=10)
        data = res.json()
        if data.get("version") == "v3_run_as_root":
            print(f"Deployment detected! (Took {int(time.time() - start_time)}s)")
            break
        print(f"Still waiting... current version: {data.get('version', 'unknown')}")
    except Exception as e:
        print(f"Error polling health: {e}")
    time.sleep(10)

print("\nStarting test_render.py...")
subprocess.run(["python", "test_render.py"])
