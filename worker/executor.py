import docker
import os
import tarfile
import threading
from typing import Optional, Tuple

client = docker.from_env()

def build_base_image(tag="secure-executor-base:latest"):
    """Builds the base image if it doesn't exist."""
    print(f"Building base image {tag}...")
    # Assumes Dockerfile.base is in the parent directory of this file's execution context
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        client.images.build(
            path=base_dir,
            dockerfile="Dockerfile.base",
            tag=tag,
            rm=True
        )
        print("Base image build complete.")
    except Exception as e:
        print(f"Error building base image: {e}")

def run_in_sandbox(
    source_dir: str,
    cpu_limit: float = 1.0,
    mem_limit: str = "512m",
    entry_point: str = "main.py"
) -> dict:
    """
    Runs the code in source_dir inside a secure container.
    """
    
    # Ensure absolute path
    source_dir = os.path.abspath(source_dir)
    
    try:
        print(f"running {entry_point} inside {source_dir}...")
        
        # Command: Install dependencies if file exists, then run script
        # We enabled network so pip install works
        command = f"/bin/bash -c 'if [ -f requirements.txt ]; then pip install -r requirements.txt; fi && python {entry_point}'"
        
        container = client.containers.run(
            image="secure-executor-base:latest",
            command=command,
            volumes={source_dir: {'bind': '/app', 'mode': 'rw'}},
            working_dir="/app",
            detach=True,
            # Hackathon Mode: Enable network so users can pip install anything
            # Production: Disable network ("none") and pre-install packages
            network_mode="bridge", 
            mem_limit=mem_limit,
            nano_cpus=int(cpu_limit * 1e9)
        )
        
        # Wait for completion
        container.wait()
        
        # Get logs and status
        # Since wait() returns dict on newer docker-py versions, we reload container object to get attrs
        container.reload()
        exit_code = container.attrs['State']['ExitCode']
        logs = container.logs()
        
        container.remove()
        
        status = "success" if exit_code == 0 else "error"
        decoded_logs = logs.decode('utf-8', errors='replace')
        
        return {
            "status": status,
            "exit_code": exit_code,
            "logs": decoded_logs
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e), "logs": ""}
