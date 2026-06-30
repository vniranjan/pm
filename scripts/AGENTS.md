# Scripts Agent Notes

This folder contains local helper scripts for running and validating the Dockerized app.

Current scripts:
- `start-mac.sh`, `stop-mac.sh`
- `start-linux.sh`, `stop-linux.sh`
- `start-windows.ps1`, `stop-windows.ps1`
- `smoke-test.sh` (checks `GET /` and `GET /api/health` on localhost:8000)

All start/stop scripts run Docker Compose from the repository root.
