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
    # Usually executed from project root
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    dockerfile_path = os.path.join(base_dir, "Dockerfile.base")
    
    # We need to pass the directory containing the Dockerfile
    client.images.build(
        path=base_dir,
        dockerfile="Dockerfile.base",
        tag=tag,
        rm=True
    )
    print("Base image build complete.")

def run_in_sandbox(
    source_dir: str,
    cpu_limit: float = 0.5,
    mem_limit: str = "128m",
    entry_point: str = "main.py"
) -> dict:
    """
    Runs the code in source_dir inside a secure container.
    
    Args:
        source_dir: host path to the directory containing user code.
        cpu_limit: CPU count limit (e.g. 0.5).
        mem_limit: Memory limit (e.g. "128m").
        entry_point: Python file to run.
        
    Returns:
        Dict containing exit_code, stdout, stderr, and execution_time (approx).
    """
    
    # Ensure absolute path
    source_dir = os.path.abspath(source_dir)
    
def run_in_sandbox(code: str, requirements: str, data_url: str) -> str:
    """
    Runs user code in a sandboxed Docker container with configurable resource limits.
    
    Resource limits can be configured via environment variables:
    - WORKER_CPU_LIMIT: CPU cores (default: 1.0)
    - WORKER_MEMORY_LIMIT: Memory in MB (default: 2048)
    - WORKER_DISK_LIMIT: Disk space in MB (default: 1024)
    """
    # Get configurable resource limits from environment
    cpu_limit = float(os.getenv("WORKER_CPU_LIMIT", "1.0"))
    memory_limit = int(os.getenv("WORKER_MEMORY_LIMIT", "2048"))  # MB
    disk_limit = int(os.getenv("WORKER_DISK_LIMIT", "1024"))  # MB
    
    print(f"🔒 Running in sandbox with limits:")
    print(f"   CPU: {cpu_limit} cores")
    print(f"   Memory: {memory_limit}MB")
    print(f"   Disk: {disk_limit}MB")
    
    # Create a temporary directory for this run
    temp_dir = tempfile.mkdtemp()
    try:
        # Write code and requirements
        code_path = os.path.join(temp_dir, "train.py")
        req_path = os.path.join(temp_dir, "requirements.txt")
        with open(code_path, "w") as f:
            f.write(code)
        with open(req_path, "w") as f:
            f.write(requirements)

        # Download data
        data_path = os.path.join(temp_dir, "data.csv")
        resp = requests.get(data_url)
        with open(data_path, "wb") as f:
            f.write(resp.content)

        # Run container with configurable limits
        container = client.containers.run(
            image="secure-executor-base:latest",
            command=["bash", "-c", "pip install -q -r requirements.txt && python train.py"],
            volumes={temp_dir: {"bind": "/app", "mode": "rw"}},
            working_dir="/app",
            detach=True,
            network_mode="none",  # No internet
            mem_limit=f"{memory_limit}m",  # Configurable memory limit
            nano_cpus=int(cpu_limit * 1e9),  # Configurable CPU limit (convert to nanocpus)
            storage_opt={"size": f"{disk_limit}m"}  # Configurable disk limit
        )
        # Separate stdout/stderr if possible, but docker api returns bytes.
        # We can also inspect the container for exit code
        container.reload()
        exit_code = container.attrs['State']['ExitCode']
        
        container.remove()
        
        return {
            "status": "success",
            "exit_code": exit_code,
            "logs": logs.decode('utf-8', errors='replace')
        }
        
    except docker.errors.ContainerError as e:
        return {"status": "error", "message": str(e)}
    except docker.errors.ImageNotFound:
        return {"status": "error", "message": "Base image not found. Please build it first."} 
    except Exception as e:
        # Try to cleanup
        try:
             # Logic to find and kill if variable 'container' exists
             pass 
        except:
            pass
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    # Test build
    build_base_image()
