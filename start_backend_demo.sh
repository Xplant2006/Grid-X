#!/bin/bash
# Quick Demo Setup Script for Backend Server

echo "🚀 Grid-X Backend Demo Setup"
echo "============================"
echo ""

# Get IP address
IP=$(hostname -I | awk '{print $1}')
echo "📍 Your IP address: $IP"
echo ""

# Check if backend is ready
if [ ! -d "backend" ]; then
    echo "❌ Error: Run this from Grid-X project root"
    exit 1
fi

# Start backend
echo "🔧 Starting backend server..."
echo "   Backend will be accessible at: http://$IP:8000"
echo "   Workers should use this URL"
echo ""

cd backend
../.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

