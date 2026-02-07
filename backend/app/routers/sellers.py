from fastapi import APIRouter, Depends
from typing import List
from sqlalchemy.orm import Session
from .. import database, models, schemas
from datetime import datetime, timedelta, timezone

router = APIRouter()

@router.get("/agents/online", response_model=List[schemas.AgentList])
def get_online_agents(db: Session = Depends(database.get_db)):
    """
    Returns a list of all agents that have sent a heartbeat recently.
    """
    # 1. Define "Online"
    # If an agent hasn't pinged in 5 minutes, we consider them OFFLINE.
    five_mins_ago = datetime.now(timezone.utc) - timedelta(minutes=5)
    
    # 2. Query the DB
    # We want agents who have updated their 'last_heartbeat' recently
    active_agents = db.query(models.Agent).filter(
        models.Agent.last_heartbeat >= five_mins_ago
    ).all()

    return active_agents