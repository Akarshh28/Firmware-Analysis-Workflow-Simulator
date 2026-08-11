import requests
import time
import sys

API_BASE = "http://127.0.0.1:8000/api"
ZIP_PATH = r"C:\Users\akars\OneDrive\Desktop\Firmware Analysis workflow simulator\backend\data\uploads\30_Relion670_Firmware update 1p1r01 to 27.zip"

print(f"Checking {API_BASE}/health")
try:
    res = requests.get(f"{API_BASE}/health", timeout=10)
    print("Health:", res.status_code, res.text)
except Exception as e:
    print("Health check failed:", e)
    sys.exit(1)

print("Creating project...")
res = requests.post(f"{API_BASE}/projects", json={"name": "Relion670 Render Test", "mode": "real"})
if res.status_code != 200:
    print("Failed to create project:", res.text)
    sys.exit(1)
project_id = res.json()["id"]
print(f"Project ID: {project_id}")

print("Uploading zip...")
with open(ZIP_PATH, "rb") as f:
    res = requests.post(f"{API_BASE}/projects/{project_id}/upload", files={"firmware": f})
if res.status_code != 200:
    print("Upload failed:", res.text)
    sys.exit(1)

print("Running pipeline...")
res = requests.post(f"{API_BASE}/projects/{project_id}/pipeline/run")
if res.status_code != 200:
    print("Pipeline run failed:", res.text)
    sys.exit(1)

print("Polling pipeline status...")
while True:
    time.sleep(5)
    res = requests.get(f"{API_BASE}/projects/{project_id}/pipeline")
    data = res.json()
    status = data.get("status")
    print("Status:", status)
    if status in ["COMPLETED", "FAILED"]:
        print("Final Status:", status)
        break

print("Fetching dashboard...")
res = requests.get(f"{API_BASE}/projects/{project_id}/dashboard")
dash = res.json()

print("\n--- RESULTS ---")
print("Total Findings:", dash.get("metrics", {}).get("totalFindings"))
print("Risk Score:", dash.get("metrics", {}).get("riskScore", "Not in metrics"))
print("Protocol Verdict:", dash.get("protocolVerdict"))

print("\n--- ALL FINDINGS ---")
for idx, f in enumerate(dash.get("findings", [])):
    title = f.get("title", f.get("description", "Unknown Title"))
    print(f"[{idx+1}] {title}")
    if "Risk Score" in title:
        print(" -> SCORECARD FOUND!")

print("\nFetching logs for errors...")
res = requests.get(f"{API_BASE}/projects/{project_id}/logs")
logs = res.json()
for log in logs:
    if "error" in log.get("message", "").lower() or "failed" in log.get("message", "").lower():
        print("LOG:", log.get("message"))
