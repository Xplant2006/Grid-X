import requests

def create_temp_workspace() -> str:
    """Creates a temporary directory for a specific execution job."""
    temp_dir = tempfile.mkdtemp(prefix="sandbox_")
    return temp_dir

def clean_workspace(path: str):
    """Removes the temporary directory."""
    if os.path.exists(path):
        shutil.rmtree(path)

def download_file(url: str, save_path: str):
    """Downloads a file from a URL to a local path."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        print(f"❌ Download failed for {url}: {e}")
        return False
