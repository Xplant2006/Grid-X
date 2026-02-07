import torch
import os
import requests
import io
from . import models, database
from sqlalchemy.orm import Session
from .routers.front_job import upload_bytes_to_supabase

def aggregate_pytorch_weights(job_id: int, db: Session):
    """
    Downloads all completed subtask results (state_dicts),
    averages them (FedAvg), and uploads the final model.
    """
    print(f"🔄 Starting aggregation for Job {job_id}...")
    
    # 1. Get all subtasks
    subtasks = db.query(models.Subtask).filter(
        models.Subtask.job_id == job_id,
        models.Subtask.status == "COMPLETED"
    ).all()
    
    if not subtasks:
        print("❌ No completed subtasks found for aggregation.")
        return

    state_dicts = []
    
    # 2. Download and Load each model
    for task in subtasks:
        if not task.result_file_url:
            continue
            
        try:
            print(f"⬇️ Downloading result from {task.result_file_url}...")
            response = requests.get(task.result_file_url)
            response.raise_for_status()
            
            # Load into memory
            buffer = io.BytesIO(response.content)
            state_dict = torch.load(buffer, map_location=torch.device('cpu'))
            state_dicts.append(state_dict)
            
        except Exception as e:
            print(f"❌ Failed to load result for task {task.id}: {e}")

    if not state_dicts:
        print("❌ No valid state dicts to aggregate.")
        return

    # 3. Federated Averaging (FedAvg)
    # W_avg = sum(W_i) / N
    print(f"➗ Averaging weights from {len(state_dicts)} models...")
    
    avg_state_dict = {}
    base_model = state_dicts[0]
    
    for key in base_model.keys():
        # Stack all weights for this key
        # shape: (num_models, *weight_shape)
        try:
            # Check if it's a float tensor (skip LongTensor/int buffers if any, or handle them)
            # usually weights are float.
            if base_model[key].is_floating_point():
                stacked = torch.stack([d[key] for d in state_dicts])
                avg_state_dict[key] = torch.mean(stacked, dim=0)
            else:
                # For non-floating point (like batchnorm num_batches_tracked), 
                # we usually just take one of them or sum them. 
                # For simplicity in FedAvg, taking the first one (or max) 
                # is a common simplification if they should be identical.
                # Let's take the first one for metadata tracking.
                avg_state_dict[key] = base_model[key]
        except Exception as e:
            print(f"⚠️ Error averaging key {key}: {e}")
            avg_state_dict[key] = base_model[key]

    # 4. Save Final Model
    buffer = io.BytesIO()
    torch.save(avg_state_dict, buffer)
    final_bytes = buffer.getvalue()
    
    # 5. Upload to Supabase
    file_path = f"jobs/{job_id}/final_model.pth"
    final_url = upload_bytes_to_supabase(final_bytes, file_path, "application/octet-stream")
    print(f"✅ Aggregation Complete! URL: {final_url}")
    
    return final_url
