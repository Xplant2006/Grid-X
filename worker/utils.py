import requests
import tempfile
import os
import shutil

def create_temp_workspace() -> str:
    """Creates a temporary directory for a specific execution job."""
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    return temp_dir

def clean_workspace(path: str):
    """Removes the temporary directory."""
    if os.path.exists(path):
        shutil.rmtree(path)

import time

def download_file(url: str, save_path: str):
    """Downloads a file from a URL to a local path with RETRY logic."""
    MAX_RETRIES = 3
    for attempt in range(MAX_RETRIES):
        try:
            # Added timeout=30 seconds
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
            
        except Exception as e:
            print(f"⚠️ Download attempt {attempt+1}/{MAX_RETRIES} failed: {e}")
            if attempt == MAX_RETRIES - 1:
                print(f"❌ Final Download Error: {e}")
                return False
            time.sleep(2) # Wait before retry
