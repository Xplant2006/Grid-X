#!/bin/bash
# Grid-X Worker Packaging Script
# Creates a standalone package for worker distribution

echo "📦 Packaging Grid-X Worker..."
echo "============================="

OUTPUT_FILE="gridx-worker.tar.gz"

# Check if we are in the right directory
if [ ! -d "worker" ] || [ ! -f "Dockerfile.base" ]; then
    echo "❌ Error: Please run this script from the project root"
    exit 1
fi

# Create temporary directory
TEMP_DIR="gridx-worker-dist"
rm -rf $TEMP_DIR
mkdir -p $TEMP_DIR

# Copy files
echo "📄 Copying files..."
cp -r worker $TEMP_DIR/
cp Dockerfile.base $TEMP_DIR/
cp setup_worker.sh $TEMP_DIR/
if [ -f "WORKER_SETUP.md" ]; then
    cp WORKER_SETUP.md $TEMP_DIR/README.md
else
    echo "⚠️ WORKER_SETUP.md not found, creating dummy README"
    echo "# Grid-X Worker" > $TEMP_DIR/README.md
fi
cp -n worker_config.env $TEMP_DIR/worker_config.env.default 2>/dev/null || true # Optional default config

# Build archive
echo "🗜️ Creating archive..."
tar -czf $OUTPUT_FILE -C $TEMP_DIR .

# Cleanup
rm -rf $TEMP_DIR

echo ""
echo "✅ Package created: $OUTPUT_FILE"
echo ""
echo "To setup a new worker:"
echo "1. Copy $OUTPUT_FILE to the new machine"
echo "2. Run: mkdir gridx-worker && tar -xzf $OUTPUT_FILE -C gridx-worker"
echo "3. Run: cd gridx-worker && ./setup_worker.sh"
