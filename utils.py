import os
import shutil
import zipfile
import tempfile
import uuid
from pathlib import Path
from fastapi import UploadFile

def create_temp_workspace() -> str:
    """Creates a temporary directory for a specific execution job."""
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    return temp_dir

def clean_workspace(path: str):
    """Removes the temporary directory."""
    if os.path.exists(path):
        shutil.rmtree(path)

async def save_and_extract_zip(file: UploadFile, extract_to: str):
    """Saves uploaded zip and extracts it to the target directory."""
    zip_path = os.path.join(extract_to, f"{uuid.uuid4()}.zip")
    
    with open(zip_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Security check: Prevent Zip Slip
            for member in zip_ref.namelist():
                if member.startswith("/") or ".." in member:
                    raise ValueError(f"Malicious zip file path detected: {member}")
                
            zip_ref.extractall(extract_to)
    finally:
        # Cleanup the zip file itself, we only need extracted content
        if os.path.exists(zip_path):
            os.remove(zip_path)
