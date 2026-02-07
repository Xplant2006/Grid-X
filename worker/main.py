import time
import requests
import os
import logging
import uuid
import sys

# Add the parent directory to sys.path so we can import from app
# This assumes the worker is run from the project root (e.g. python worker/main.py)
sys.path.append(os.getcwd())

from worker.utils import create_temp_workspace, clean_workspace, download_file
from worker.executor import run_in_sandbox, build_base_image

# CONFIGURATION
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
AGENT_ID = os.getenv("AGENT_ID", str(uuid.uuid4()))
GPU_MODEL = "NVIDIA GeForce RTX 3090" # Mock
RAM_TOTAL = "24GB"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def register_agent():
    """Rgister this worker with the backend."""
    try:
        # For Hackathon, we hardcode an email that exists in the DB.
        # In production, this would be a config.
        payload = {
            "id": AGENT_ID,
            "email": "agent@gridx.com", # Needs to match a user in DB
            "gpu_model": GPU_MODEL,
            "ram_total": RAM_TOTAL
        }
        resp = requests.post(f"{BACKEND_URL}/agent/register", json=payload)
        resp.raise_for_status()
        logging.info(f"✅ Registered as {AGENT_ID}")
    except Exception as e:
        logging.warning(f"Registration warning (might already exist or user missing): {e}")

def send_heartbeat(status="IDLE"):
    """Tell backend we are alive."""
    try:
        payload = {"id": AGENT_ID, "status": status}
        requests.post(f"{BACKEND_URL}/agent/heartbeat", json=payload, timeout=2)
    except Exception:
        pass # Ignore network blips

def poll_for_task():
    """Ask backend for work."""
    try:
        payload = {"agent_id": AGENT_ID}
        resp = requests.post(f"{BACKEND_URL}/agent/request_task", json=payload)
        resp.raise_for_status()
        data = resp.json()
        
        task_id = data.get("task_id")
        if task_id:
            return data
    except Exception as e:
        logging.error(f"Polling error: {e}")
    return None

def execute_task(task_data):
    """Run the assigned task."""
    workspace = create_temp_workspace()
    logging.info(f"🔨 Processing Task {task_data['task_id']} in {workspace}")
    
    try:
        # 1. Download Files
        logging.info("⬇️ Downloading files...")
        download_file(task_data['code_url'], os.path.join(workspace, "train.py"))
        download_file(task_data['requirements_url'], os.path.join(workspace, "requirements.txt"))
        download_file(task_data['chunk_data_url'], os.path.join(workspace, "data.csv"))
        
        # 2. Execute
        logging.info("⚙️ Running code...")
        # We assume entry point is train.py
        result = run_in_sandbox(workspace, entry_point="train.py")
        
        logging.info(f"Execution Result: {result['status']}")
        logging.info(f"Logs: {result['logs'][:200]}...") # Show first 200 chars

        # 3. Check for Output Model
        model_path = os.path.join(workspace, "model.pth")
        result_url = None
        
        if os.path.exists(model_path):
            logging.info("📤 Uploading model.pth...")
            # Upload to Supabase via Backend (or direct if we had keys here)
            # For this MVP, we will upload to a backend helper endpoint OR 
            # (Best Practice) The backend should give us a Presigned URL.
            # 
            # Constraint: The current backend design relies on 'upload_bytes_to_supabase' on server side.
            # To fix this without major refactor, we can POST the file to a new endpoint on backend 
            # or usage the existing /front_job.ts logic but that's for jobs.
            #
            # QUICK FIX: We will just mock the "upload" by sending it to a generic file receiver
            # or we create a specific endpoint in agent.py for uploading results.
            # 
            # Let's assume we implement a simple /agent/upload_result endpoint in the backend next.
            # For now, I will add a placeholder call.
            with open(model_path, "rb") as f:
                 files = {'file': ('model.pth', f, 'application/octet-stream')}
                 upload_resp = requests.post(
                     f"{BACKEND_URL}/agent/upload_result", 
                     files=files,
                     data={"agent_id": AGENT_ID, "task_id": task_data['task_id']}
                 )
                 result_url = upload_resp.json().get("url")
        
        else:
            logging.warning("⚠️ No model.pth found. Task might have failed or not saved output.")

        # 4. Complete
        complete_payload = {
            "task_id": task_data['task_id'],
            "agent_id": AGENT_ID,
            "result_url": result_url
        }
        requests.post(f"{BACKEND_URL}/agent/complete_task", json=complete_payload)
        logging.info("✅ Task Completed!")
        
    except Exception as e:
        logging.error(f"Task Execution Failed: {e}")
    finally:
        clean_workspace(workspace)

def main():
    logging.info("🚀 Grid-X Worker Starting...")
    build_base_image() # Ensure docker image exists
    register_agent()
    
    while True:
        send_heartbeat("IDLE")
        
        task = poll_for_task()
        if task:
            send_heartbeat("BUSY")
            execute_task(task)
        
        time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Shutting down worker...")
