#!/bin/bash
# Start backend and run test to verify automatic aggregation

echo "🚀 Starting backend server..."
cd backend
../.venv/bin/uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

echo "⏳ Waiting for backend to start..."
sleep 5

echo "🧪 Running end-to-end test..."
.venv/bin/python tests/test_full_workflow.py

echo ""
echo "📋 Checking backend logs for aggregation messages..."
echo "=================================================="
grep -E "🔍|🎉|🔄|Aggregation" backend.log || echo "No aggregation messages found in logs"

echo ""
echo "📊 Checking latest job status..."
.venv/bin/python -c "
import sqlite3
conn = sqlite3.connect('backend/app/sql_app.db')
c = conn.cursor()
c.execute('SELECT id, status, final_result_url FROM jobs ORDER BY id DESC LIMIT 1')
job = c.fetchone()
print(f'Latest Job: ID={job[0]}, Status={job[1]}')
if job[2]:
    print(f'Final Model: {job[2]}')
else:
    print('Final Model: NOT SET (aggregation did not complete)')
"

echo ""
echo "To see full backend logs: cat backend.log"
