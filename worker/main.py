from fastapi import FastAPI, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import logging
import shutil
import os

from app.utils import create_temp_workspace, save_and_extract_zip, clean_workspace
from app.executor import run_in_sandbox, build_base_image

app = FastAPI(title="Secure Code Executor")

# Ensure base image exists on startup
@app.on_event("startup")
def startup_event():
    try:
        build_base_image()
    except Exception as e:
        logging.error(f"Failed to build base image: {e}")

@app.post("/run")
async def run_code(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    cpu_limit: float = Form(0.5),
    mem_limit: str = Form("128m")
):
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only zip files are allowed.")

    # Create workspace
    workspace = create_temp_workspace()
    
    try:
        # Save and extract
        await save_and_extract_zip(file, workspace)
        
        # Check for main.py
        if not os.path.exists(os.path.join(workspace, "main.py")):
             # Clean up immediately if invalid
             clean_workspace(workspace)
             raise HTTPException(status_code=400, detail="Zip must contain main.py at the root.")
             
        # Run execution
        # Note regarding background tasks: If we want to return the result, we must await here.
        # If we want async processing, we'd return a job ID.
        # For simplicity in this script, we wait and return the result.
        
        result = run_in_sandbox(workspace, cpu_limit=cpu_limit, mem_limit=mem_limit)
        
        return JSONResponse(content=result)
        
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
    finally:
        # Schedule cleanup
        background_tasks.add_task(clean_workspace, workspace)

@app.get("/health")
def health():
    return {"status": "ok"}
