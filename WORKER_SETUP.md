# Grid-X Worker Setup Guide

Welcome to the Grid-X Compute Network!
This package contains everything you need to run a Grid-X worker node on Linux/macOS.

## Prerequisites
1. **Python 3.10+** (Check with `python3 --version`)
2. **Docker** (Check with `docker --version`)
   - Ensure Docker is running! (`docker info`)

## Quick Start
1. **Run the Setup Script**:
   This prepares the environment, builds the Docker image, and configures your worker.
   ```bash
   chmod +x setup_worker.sh
   ./setup_worker.sh
   ```

2. **Configuration Prompts**:
   - **Backend URL**: Enter existing backend URL (e.g., `http://YOUR_SERVER_IP:8000`) or default `http://localhost:8000`.
   - **Worker Email**: CRITICAL! Enter the email address you used to register on the Grid-X platform (e.g., `hadhi@ek.com`). If not registered, register first!

3. **Start the Worker**:
   ```bash
   ./start_worker.sh
   ```
   You should see: "🚀 Grid-X Worker Starting..." and successful registration logs.

## Troubleshooting
- **Permission Denied**: Run `chmod +x *.sh`.
- **Docker Permission Denied**: Run `sudo usermod -aG docker $USER` and log out/in.
- **Worker Registration Failed (404)**: Ensure your `WORKER_EMAIL` in `worker_config.env` matches a registered user on the backend.

## Checking Logs
Logs are saved to `worker.log`. View them live:
```bash
tail -f worker.log
```
