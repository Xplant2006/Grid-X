from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from .. import database, models, schemas
import shutil
import os
import io
import time
import pandas as pd
from supabase import create_client
from typing import List
# ==========================================
# 1. CONFIGURATION
# ==========================================
# REPLACE WITH YOUR ACTUAL KEYS!
SUPABASE_URL = "https://ryhjmgehgshyuzqhcgwz.supabase.co"
SUPABASE_KEY = "sb_publishable_O1gBSZCqAYSosVSclzYEQg_NdzMeMiw"
BUCKET_NAME = "gridx-files"

# Initialize Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

router = APIRouter()

# ==========================================
# 2. HELPER: UPLOAD TO SUPABASE
# ==========================================
def upload_bytes_to_supabase(file_bytes: bytes, destination_path: str, content_type: str):
    """Uploads raw bytes to Supabase Storage and returns the public URL."""
    try:
        supabase.storage.from_(BUCKET_NAME).upload(
            path=destination_path,
            file=file_bytes,
            file_options={"content-type": content_type, "x-upsert": "true"}
        )
        return supabase.storage.from_(BUCKET_NAME).get_public_url(destination_path)
    except Exception as e:
        print(f"❌ Upload Error: {e}")
        raise HTTPException(status_code=500, detail="File upload failed")

# ==========================================
# 3. BACKGROUND TASK: SPLITTER
# ==========================================
def split_csv_and_create_subtasks(job_id: int, csv_content: bytes, db: Session):
    """
    Takes the uploaded CSV, splits it into 5 chunks, uploads chunks, 
    and creates Subtask rows in the database.
    """
    print(f"🔪 [Job {job_id}] Starting background split...")
    
    try:
        # A. Load CSV
        df = pd.read_csv(io.BytesIO(csv_content))
        total_rows = len(df)
        num_chunks = 5  # Fixed for Hackathon
        chunk_size = total_rows // num_chunks
        
        # B. Loop and Split
        for i in range(num_chunks):
            start = i * chunk_size
            # If last chunk, take everything till the end
            if i == num_chunks - 1:
                subset = df.iloc[start:]
            else:
                subset = df.iloc[start : start + chunk_size]
            
            # C. Convert Chunk to CSV bytes
            buffer = io.BytesIO()
            subset.to_csv(buffer, index=False)
            chunk_bytes = buffer.getvalue()
            
            # D. Upload Chunk
            chunk_path = f"jobs/{job_id}/chunks/chunk_{i}.csv"
            chunk_url = upload_bytes_to_supabase(chunk_bytes, chunk_path, "text/csv")
            
            # E. Create Subtask in DB
            new_subtask = models.Subtask(
                job_id=job_id,
                assigned_to=None, # No agent yet
                status="PENDING",
                chunk_file_url=chunk_url
            )
            db.add(new_subtask)
        
        # F. Update Job Status
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        job.status = "RUNNING"
        db.commit()
        print(f"✅ [Job {job_id}] Split complete! Status: RUNNING.")

    except Exception as e:
        print(f"❌ [Job {job_id}] Splitting Failed: {e}")
        # Optional: Set job status to ERROR in DB

# ==========================================
# 4. THE ENDPOINT
# ==========================================
@router.post("/upload")
async def upload_job(
    title: str = Form(...),
    user_id: int = Form(...), # Retrieve from localStorage in frontend
    file_code: UploadFile = File(...), # train.py
    file_req: UploadFile = File(...),  # requirements.txt
    file_data: UploadFile = File(...), # data.csv
    background_tasks: BackgroundTasks = BackgroundTasks(),
    db: Session = Depends(database.get_db)
):
    # 1. Read Files
    code_bytes = await file_code.read()
    req_bytes = await file_req.read()
    data_bytes = await file_data.read() # Needed for splitting later

    # 2. Create Unique Folder Paths
    # Format: jobs/{user_id}_{timestamp}/filename
    timestamp = int(time.time())
    base_path = f"jobs/{user_id}_{timestamp}"
    
    # 3. Upload Original Files
    code_url = upload_bytes_to_supabase(code_bytes, f"{base_path}/train.py", "text/x-python")
    req_url = upload_bytes_to_supabase(req_bytes, f"{base_path}/requirements.txt", "text/plain")
    data_url = upload_bytes_to_supabase(data_bytes, f"{base_path}/data.csv", "text/csv")

    # 4. Create Job Entry in DB
    new_job = models.Job(
        title=title,
        status="PROCESSING", # Start here, background task will update to RUNNING
        owner_id=user_id,
        original_code_url=code_url,
        original_req_url=req_url,
        original_data_url=data_url
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    # 5. Trigger Background Splitting
    # We pass the 'data_bytes' we already read so we don't need to download it again
    background_tasks.add_task(split_csv_and_create_subtasks, new_job.id, data_bytes, db)

    return {
        "job_id": new_job.id,
        "message": "Upload successful! Splitting data in background.",
        "status": "PROCESSING"
    }

@router.get("/list/{user_id}", response_model=List[schemas.JobResponse])
def get_my_jobs(user_id: int, db: Session = Depends(database.get_db)):
    """
    Fetch all jobs belonging to a specific user.
    """
    # 1. Query the database
    # filter(models.Job.owner_id == user_id) ensures you only see YOUR jobs
    jobs = db.query(models.Job).filter(models.Job.owner_id == user_id).all()
    
    # 2. Return them (FastAPI converts them to JSON automatically)
    return jobs