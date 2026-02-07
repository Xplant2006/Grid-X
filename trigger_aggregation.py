#!/usr/bin/env python3
"""
Manual Aggregation Trigger
Manually triggers aggregation for a completed job to test the aggregation logic
"""

# Load .env FIRST before importing backend modules
from dotenv import load_dotenv
from pathlib import Path

env_file = Path(__file__).parent / '.env'
load_dotenv(env_file)

# Now import backend modules
import sys
sys.path.insert(0, 'backend')

from app.database import SessionLocal
from app.aggregation import aggregate_pytorch_weights

def main():
    if len(sys.argv) < 2:
        print("Usage: python trigger_aggregation.py <job_id>")
        print("\nExample: python trigger_aggregation.py 9")
        sys.exit(1)
    
    job_id = int(sys.argv[1])
    
    print(f"🔄 Manually triggering aggregation for job {job_id}...")
    
    db = SessionLocal()
    try:
        final_url = aggregate_pytorch_weights(job_id, db)
        
        # Update job status
        from app import models
        job = db.query(models.Job).filter(models.Job.id == job_id).first()
        if job:
            job.status = "COMPLETED"
            job.final_result_url = final_url
            db.commit()
            
            print(f"✅ Aggregation successful!")
            print(f"   Final model URL: {final_url}")
        else:
            print(f"❌ Job {job_id} not found")
            
    except Exception as e:
        print(f"❌ Aggregation failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    main()
