import torch
import requests
import io
import time
from sqlalchemy.orm import Session
from . import models
from .routers.front_job import upload_bytes_to_supabase

def aggregate_pytorch_weights(job_id: int, db: Session) -> str:
    """
    Aggregates PyTorch model weights from completed subtasks using Federated Averaging (FedAvg).
    
    Args:
        job_id: The ID of the job whose subtasks to aggregate
        db: Database session
        
    Returns:
        URL of the uploaded aggregated model
    """
    print(f"🔄 Starting aggregation for Job {job_id}...")
    
    # 1. Get all completed subtasks for this job
    subtasks = db.query(models.Subtask).filter(
        models.Subtask.job_id == job_id,
        models.Subtask.status == "COMPLETED"
    ).all()
    
    if not subtasks:
        print(f"❌ No completed subtasks found for aggregation.")
        raise Exception("No completed subtasks to aggregate")
    
    # 2. Download all model weights
    model_weights = []
    
    for subtask in subtasks:
        if not subtask.result_file_url:
            continue
            
        print(f"⬇️ Downloading result from {subtask.result_file_url}...")
        
        # Validating download with retries
        success = False
        for attempt in range(3):
            try:
                resp = requests.get(subtask.result_file_url, timeout=30)
                if resp.status_code == 200:
                    # Load the model weights
                    weights = torch.load(io.BytesIO(resp.content), map_location='cpu')
                    model_weights.append(weights)
                    success = True
                    break
                else:
                    print(f"⚠️  Status {resp.status_code}. Retrying...")
                    time.sleep(1)
            except Exception as e:
                print(f"⚠️  Download error (Attempt {attempt+1}): {e}")
                time.sleep(1)
        
        if not success:
            print(f"❌ Could not download weights for subtask {subtask.id}. Skipping.")
    
    if not model_weights:
        raise Exception("No model weights could be downloaded")
    
    # 3. Perform Federated Averaging
    print(f"➗ Averaging weights from {len(model_weights)} models...")
    averaged_weights = {}
    
    # Get all keys from the first model
    keys = model_weights[0].keys()
    
    for key in keys:
        # Stack all tensors for this key and compute mean
        tensors = [w[key] for w in model_weights]
        stacked = torch.stack(tensors)
        averaged_weights[key] = torch.mean(stacked, dim=0)
    
    # 4. Save aggregated model
    final_bytes = io.BytesIO()
    torch.save(averaged_weights, final_bytes)
    final_bytes.seek(0)
    
    # 5. Upload to Supabase
    file_path = f"jobs/{job_id}/final_model.pth"
    final_url = upload_bytes_to_supabase(final_bytes.getvalue(), file_path, "application/octet-stream")
    
    print(f"✅ Aggregation complete! Final model uploaded to: {final_url}")
    return final_url
