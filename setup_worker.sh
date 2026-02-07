#!/bin/bash
# Grid-X Worker Setup Script
# This script sets up a worker node to participate in federated learning

set -e  # Exit on error

echo "🚀 Grid-X Worker Setup"
echo "======================"
echo ""

# Check prerequisites
echo "1️⃣ Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi
echo "   ✅ Python 3 found: $(python3 --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi
echo "   ✅ Docker found: $(docker --version)"

# Check Docker permissions
if ! docker ps &>/dev/null; then
    echo "⚠️  Docker permission issue detected"
    echo "   Adding user to docker group..."
    sudo usermod -aG docker $USER
    echo "   ⚠️  You need to log out and back in for this to take effect"
    echo "   Or run: newgrp docker"
    echo ""
    read -p "   Press Enter to continue (you may need sudo for docker commands)..."
fi

# Create virtual environment
echo ""
echo "2️⃣ Creating Python virtual environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "   ✅ Virtual environment created"
else
    echo "   ✅ Virtual environment already exists"
fi

# Activate and install dependencies
echo ""
echo "3️⃣ Installing worker dependencies..."
source .venv/bin/activate
pip install -q --upgrade pip
pip install -q -r worker/requirements.txt
echo "   ✅ Dependencies installed"

# Build Docker image
echo ""
echo "4️⃣ Building Docker sandbox image..."
echo "   This may take 2-3 minutes..."

# Check if image already exists
if docker images | grep -q "secure-executor-base"; then
    echo "   ⚠️  Image already exists. Rebuilding..."
fi

# Try to build
if docker build -f Dockerfile.base -t secure-executor-base:latest . &>/dev/null; then
    echo "   ✅ Docker image built successfully"
else
    echo "   ⚠️  Build failed. Trying with sudo..."
    sudo docker build -f Dockerfile.base -t secure-executor-base:latest .
    echo "   ✅ Docker image built successfully (with sudo)"
fi

# Create worker config
echo ""
echo "5️⃣ Creating worker configuration..."

if [ ! -f "worker_config.env" ]; then
    cat > worker_config.env << EOF
# Grid-X Worker Configuration
# Edit these values before starting the worker

# Backend URL (REQUIRED)
BACKEND_URL=http://localhost:8000

# Unique worker ID (auto-generated, but you can customize)
AGENT_ID=worker_$(hostname)_$(date +%s)

# Worker email (for registration)
WORKER_EMAIL=worker@example.com

# Polling interval in seconds
POLL_INTERVAL=10

# ==========================================
# Resource Limits (per task)
# ==========================================
# Adjust based on your hardware capabilities

# CPU cores per task (e.g., 1.0 = 1 core, 0.5 = half a core, 2.0 = 2 cores)
WORKER_CPU_LIMIT=1.0

# Memory limit in MB (e.g., 2048 = 2GB, 4096 = 4GB)
WORKER_MEMORY_LIMIT=2048

# Disk space limit in MB (e.g., 1024 = 1GB)
WORKER_DISK_LIMIT=1024
EOF
    echo "   ✅ Configuration file created: worker_config.env"
    echo "   ⚠️  IMPORTANT: Edit worker_config.env with your backend URL!"
else
    echo "   ✅ Configuration file already exists"
fi

# Create start script
echo ""
echo "6️⃣ Creating start script..."

cat > start_worker.sh << 'EOF'
#!/bin/bash
# Start Grid-X Worker

# Load configuration
if [ ! -f "worker_config.env" ]; then
    echo "❌ worker_config.env not found!"
    echo "   Run ./setup_worker.sh first"
    exit 1
fi

source worker_config.env

# Validate configuration
if [ -z "$BACKEND_URL" ]; then
    echo "❌ BACKEND_URL not set in worker_config.env"
    exit 1
fi

# Support WORKER_ID as alias for AGENT_ID
if [ -z "$AGENT_ID" ] && [ -n "$WORKER_ID" ]; then
    AGENT_ID="$WORKER_ID"
fi

if [ -z "$AGENT_ID" ]; then
    # Auto-generate if missing
    AGENT_ID="worker_$(hostname)_$(date +%s)"
    echo "⚠️  AGENT_ID/WORKER_ID not set. Using auto-generated: $AGENT_ID"
fi

echo "🚀 Starting Grid-X Worker"
echo "========================"
echo "Backend: $BACKEND_URL"
echo "Agent ID: $AGENT_ID"
echo ""

# Activate virtual environment
source .venv/bin/activate

# Export environment variables
export BACKEND_URL
export AGENT_ID
export WORKER_EMAIL
export WORKER_CPU_LIMIT
export WORKER_MEMORY_LIMIT
export WORKER_DISK_LIMIT

# Display configuration
echo "Resource Limits:"
echo "  CPU: ${WORKER_CPU_LIMIT:-1.0} cores"
echo "  Memory: ${WORKER_MEMORY_LIMIT:-2048}MB"
echo "  Disk: ${WORKER_DISK_LIMIT:-1024}MB"
echo ""

# Start worker
echo "Worker is running. Press Ctrl+C to stop."
echo ""
python worker/main.py 2>&1 | tee worker.log
EOF

chmod +x start_worker.sh
echo "   ✅ Start script created: start_worker.sh"

# Summary
echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "Next steps:"
echo "1. Edit worker_config.env with your backend URL"
echo "2. Run: ./start_worker.sh"
echo ""
echo "Your worker will:"
echo "  • Register with the backend"
echo "  • Poll for tasks every 10 seconds"
echo "  • Execute tasks in isolated Docker containers"
echo "  • Upload results automatically"
echo ""
echo "For more information, see WORKER_SETUP.md"
