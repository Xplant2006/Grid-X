# Worker Setup Guide

This guide explains how to set up a worker node to rent out your CPU for Grid-X federated learning tasks.

## Prerequisites

- **Docker**: Required for sandboxed code execution
- **Python 3.11+**: For running the worker script
- **Linux/macOS**: Recommended (Windows with WSL2 also works)
- **Stable internet**: For communicating with the backend

## Quick Setup (5 minutes)

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Grid-X.git
cd Grid-X
```

### 2. Run the Setup Script

```bash
chmod +x setup_worker.sh
./setup_worker.sh
```

This will:
- Create a Python virtual environment
- Install worker dependencies
- Build the Docker sandbox image
- Configure Docker permissions

### 3. Configure Worker

Edit the worker configuration:

```bash
nano worker_config.env
```

Set these variables:
```bash
BACKEND_URL=https://your-backend-url.com  # The Grid-X backend URL
AGENT_ID=worker_$(hostname)_$(date +%s)   # Unique worker ID
```

### 4. Start the Worker

```bash
./start_worker.sh
```

Your worker is now running and will:
- Register with the backend
- Poll for available tasks every 10 seconds
- Execute tasks in isolated Docker containers
- Upload results automatically
- Earn credits for completed tasks

## Manual Setup

If you prefer manual setup:

### 1. Install Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r worker/requirements.txt
```

### 2. Build Docker Image

```bash
docker build -f Dockerfile.base -t secure-executor-base:latest .
```

### 3. Configure Docker Permissions

```bash
sudo usermod -aG docker $USER
# Log out and back in for this to take effect
```

### 4. Start Worker

```bash
export BACKEND_URL="https://your-backend-url.com"
export AGENT_ID="worker_$(hostname)_$(date +%s)"
python worker/main.py
```

## Worker Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `BACKEND_URL` | Grid-X backend API URL | Yes | - |
| `AGENT_ID` | Unique identifier for this worker | Yes | - |
| `POLL_INTERVAL` | Seconds between task polls | No | 10 |
| `MAX_CONCURRENT_TASKS` | Max parallel tasks | No | 1 |
| `WORKER_CPU_LIMIT` | CPU cores per task | No | 1.0 |
| `WORKER_MEMORY_LIMIT` | Memory in MB per task | No | 2048 |
| `WORKER_DISK_LIMIT` | Disk space in MB per task | No | 1024 |

### Configuring Resource Limits

Edit `worker_config.env` to set your hardware limits:

```bash
# Example: High-performance worker with 4 cores and 8GB RAM
WORKER_CPU_LIMIT=2.0          # Use 2 CPU cores per task
WORKER_MEMORY_LIMIT=4096      # Allow 4GB RAM per task
WORKER_DISK_LIMIT=2048        # Allow 2GB disk per task

# Example: Low-resource worker
WORKER_CPU_LIMIT=0.5          # Use half a CPU core
WORKER_MEMORY_LIMIT=1024      # Allow 1GB RAM
WORKER_DISK_LIMIT=512         # Allow 512MB disk
```

**Recommendations:**
- Leave some resources for your system (don't allocate 100%)
- Start conservative and increase if stable
- Monitor with `docker stats` while running

### Resource Limits

You can configure limits per task in `worker_config.env`:

**Default limits:**
- **CPU**: 1 core (configurable: `WORKER_CPU_LIMIT`)
- **Memory**: 2GB RAM (configurable: `WORKER_MEMORY_LIMIT`)
- **Disk**: 1GB temporary (configurable: `WORKER_DISK_LIMIT`)
- **Network**: Isolated (no internet access during execution)

**Example configurations:**
```bash
# Powerful machine: 4 cores, 16GB RAM
WORKER_CPU_LIMIT=2.0
WORKER_MEMORY_LIMIT=8192
WORKER_DISK_LIMIT=4096

# Modest machine: 2 cores, 4GB RAM
WORKER_CPU_LIMIT=0.5
WORKER_MEMORY_LIMIT=1024
WORKER_DISK_LIMIT=512
```

## Monitoring Your Worker

### Check Worker Status

```bash
# View worker logs
tail -f worker.log

# Check if worker is registered
curl http://your-backend-url.com/agent/status/$AGENT_ID
```

### View Completed Tasks

```bash
# Check how many tasks completed
grep "Task completed" worker.log | wc -l
```

## Troubleshooting

### Docker Permission Denied

```bash
sudo usermod -aG docker $USER
newgrp docker  # Or log out and back in
```

### Worker Can't Connect to Backend

- Check `BACKEND_URL` is correct
- Verify backend is running: `curl $BACKEND_URL`
- Check firewall settings

### Docker Image Build Fails

- Ensure you have at least 5GB free disk space
- Run: `docker system prune -af` to clean up
- Try building again

### No Tasks Available

This is normal! It means:
- No jobs are currently submitted
- Other workers claimed the tasks first
- Your worker will keep polling automatically

## Security & Privacy

### What Workers Execute

- Workers run **user-submitted Python code** in isolated Docker containers
- Code has **no internet access** during execution
- Code has **no access to your host system**
- Each task runs as a **non-root user** inside the container

### What Data Workers See

- Workers download **chunks of CSV data** (not the full dataset)
- Workers **never see other workers' data**
- Workers only upload **model weights** (not raw data)

### Stopping the Worker

```bash
# Graceful shutdown
pkill -f "python worker/main.py"

# Or press Ctrl+C if running in foreground
```

## Earnings & Payments

[Add your payment/credit system details here]

## Support

- **Issues**: https://github.com/YOUR_USERNAME/Grid-X/issues
- **Docs**: https://github.com/YOUR_USERNAME/Grid-X/wiki
- **Discord**: [Your Discord link]
