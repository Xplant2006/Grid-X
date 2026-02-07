from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks, Depends
from sqlalchemy.orm import Session
from supabase import create_client
import pandas as pd
import io
import os
from datetime import datetime
from .. import models, database, schemas
import shutil
import time
from typing import List
from datetime import timezone
# ==========================================
# 1. CONFIGURATION
# ==========================================
# Load from environment variables for security
# Create a .env file based on .env.example
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://ryhjmgehgshyuzqhcgwz.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJ5aGptZ2VoZ3NoeXV6cWhjZ3d6Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MDM5MTU5MSwiZXhwIjoyMDg1OTY3NTkxfQ.8q_-WKlxj1_dngzHKE6fUmPUch_QjEIXqFZbnZv5S7w")
BUCKET_NAME = os.getenv("SUPABASE_BUCKET_NAME", "gridx-files")

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
    print(f"   CSV size: {len(csv_content)} bytes")
    
    try:
        # A. Load CSV
        print(f"   Loading CSV into pandas...")
        df = pd.read_csv(io.BytesIO(csv_content))
        total_rows = len(df)
        num_chunks = 5  # Fixed for Hackathon
        chunk_size = total_rows // num_chunks
        print(f"   ✅ Loaded {total_rows} rows, splitting into {num_chunks} chunks")
        
        # B. Loop and Split
        for i in range(num_chunks):
            print(f"   Processing chunk {i+1}/{num_chunks}...")
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
            print(f"      Chunk {i}: {len(subset)} rows, {len(chunk_bytes)} bytes")
            
            # D. Upload Chunk
            chunk_path = f"jobs/{job_id}/chunks/chunk_{i}.csv"
            print(f"      Uploading to: {chunk_path}")
            try:
                chunk_url = upload_bytes_to_supabase(chunk_bytes, chunk_path, "text/csv")
                print(f"      ✅ Uploaded: {chunk_url[:60]}...")
            except Exception as upload_error:
                print(f"      ❌ Upload failed: {upload_error}")
                raise
            
            # E. Create Subtask in DB
            new_subtask = models.Subtask(
                job_id=job_id,
                assigned_to=None, # No agent yet
                status="PENDING",
                chunk_file_url=chunk_url
            )
            db.add(new_subtask)
            print(f"      ✅ Subtask {i+1} created")
        
        # F. Update Job Status
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        job.status = "RUNNING"
        db.commit()
        print(f"✅ [Job {job_id}] Split complete! Created {num_chunks} subtasks. Status: RUNNING.")

    except Exception as e:
        print(f"❌ [Job {job_id}] Splitting Failed: {e}")
        print(f"   Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        # Optional: Set job status to ERROR in DB
        try:
            job = db.query(models.Job).filter(models.Job.id == job_id).first()
            if job:
                job.status = "ERROR"
                db.commit()
        except:
            pass

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

@router.get("/download/{job_id}", response_model=schemas.JobResultResponse)
def get_final_job_result(job_id: int, user_id: int, db: Session = Depends(database.get_db)):
    """
    Called by the Buyer Frontend to get the final download link.
    """
    # 1. Fetch the job
    job = db.query(models.Job).filter(models.Job.id == job_id).first()

    # 2. Safety Check: Does the job exist?
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # 3. Security Check: Does the user_id match the job's owner_id?
    # This prevents User A from guessing User B's job ID and stealing their data.
    if job.owner_id != user_id:
        raise HTTPException(
            status_code=403, 
            detail="Unauthorized: You do not own this job."
        )

    # 4. Return the result
    return {
        "job_id": job.id,
        "title": job.title,
        "status": job.status,
        "final_result_url": job.final_result_url
    }