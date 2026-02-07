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
    
    # Resource constraints
    # nano_cpus = int(cpu_limit * 1e9)
    
    # Security:
    # 1. Network disabled (network_mode="none")
    # 2. Read-only root (read_only=True) - BUT we need to write pyc or pip install? 
    #    Better: Mount /tmp as tmpfs. 
    #    For requirements, if we want to support them, we need a pre-step.
    #    For this MVP, we assume dependencies are either standard or user bundles them (or we skip pip install for pure isolation).
    #    Let's try to support pip install by doing it with network enabled first? 
    #    Actually, keeping it simple and SECURE as requested: NO NETWORK. 
    #    If they need libs, they should bundle 'em or we rely on pre-installed in base image.
    
    try:
        container = client.containers.run(
            image="secure-executor-base:latest",
            command=f"python3 {entry_point}",
            volumes={
                source_dir: {'bind': '/app', 'mode': 'rw'} # rw needed if they write output? Let's say rw for /app, but risky implementation. 
            },
            working_dir="/app",
            mem_limit=mem_limit,
            nano_cpus=int(cpu_limit * 1_000_000_000),
            network_mode="none", # Strict isolation
            detach=True,
            user="sandbox", # Run as non-root
            read_only=False, # Set to true for harder hardening, but might break some python caching
            # cap_drop=["ALL"], # Drop all capabilities
            security_opt=["no-new-privileges"]
        )
        
        container.wait(timeout=30) # 30s timeout execution
        
        logs = container.logs(stdout=True, stderr=True)
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
