# Changelog

## [1.0.0-production] - 2026-07-30

### Architectural Overhaul
- **Deployment Ready**: Segmented the app for dual-deployment architecture (Vercel for Frontend, Render for Backend).
- **Docker Support**: Created monolithic `Dockerfile`, `docker-compose.yml`, and `entrypoint.sh` for easy deployment of the entire backend with all 12 heavy cybersecurity tools pre-installed (Binwalk, Ghidra, AFL++, etc.).
- **Devcontainer**: Configured `.devcontainer` for seamless VS Code integration.
- **Environment Variables**: Replaced hardcoded localhost strings across the frontend with `process.env.NEXT_PUBLIC_API_URL` for production readiness.

### Pipeline & Execution Engine
- **Strict 12-Stage Pipeline**: Hardcoded the pipeline to execute exactly 12 tools in strict sequential order:
  1. Upload
  2. Strings
  3. Binwalk
  4. Cutter
  5. Entropy
  6. Ghidra
  7. Trufflehog
  8. AFL++
  9. angr
  10. Wireshark
  11. Risk Scorecard
  12. PDF Report Generation
- **Real Subprocess Execution**: Replaced all fake `time.sleep()` simulations with actual `subprocess.Popen` wrappers that execute system binaries.
- **Smart Fallback**: The pipeline intelligently detects missing tools in the `$PATH` and gracefully marks the stage as "Skipped" rather than halting the entire pipeline or faking success.

### WebSockets & Live Streaming
- **Live Execution Streaming**: Developed a FastAPI `WebSocket` manager that streams stdout/stderr and progress ticks in real time.
- **Frontend Integration**: Updated `PipelineSimulator` and `pipelineStore` to consume live WebSockets, updating terminal UI instantly as tools execute on the backend.

### Upload System
- **Drag & Drop**: Completely rewrote `Upload.tsx` to support drag & drop functionality with intuitive UI.
- **Strict Validation**: Enforces a 500MB size limit and validates file extensions (.bin, .hex, .img, .zip, .tar, .tar.gz, .7z, .elf, .axf, .out).
- **Progress Tracking**: Hooked into Axios `onUploadProgress` to show a real-time upload progress bar.
- **SHA256 Hashing**: Backend calculates SHA256 in chunks during upload and displays it in the UI.
- **Pipeline Locking**: The "Run Pipeline" button remains disabled until a successful upload and validation completes.

### Backend APIs & Database
- **Hardened APIs**: Fixed routing for all critical endpoints to prevent 404/500 errors (`/api/run`, `/api/upload`, `/api/reset`, `/api/dashboard`, etc.).
- **Data Models**: Enhanced `ToolRun`, `PipelineSession`, and `Artifact` tables to support strict tracking of exit codes, execution times, and SHA256 hashes.

### PDF Reporting
- **Report Generation**: Built a professional PDF generator (`report_generator.py`) using `reportlab`. It aggregates logs, findings, and hashes, generating a downloadable artifact at Stage 12.

### UI & Dashboard
- **Backend-Driven Data**: Stripped out all dummy data and hardcoded fallback charts from the Dashboard. It now parses actual `[!]` stdout flags to populate the CVSS scorecard and risk metrics.
- **Action Buttons**: Hooked up the `Run Pipeline` and `Reset` buttons properly to their backend counterparts. Added spinning loading states to prevent double clicks.
