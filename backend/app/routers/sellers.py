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


@router.get("/seller-tasks/{user_id}", response_model=schemas.SellerTaskResponse)
def get_seller_tasks(user_id: int, db: Session = Depends(database.get_db)):
    # 1. Find all agents owned by this seller
    agent_ids = db.query(models.Agent.id).filter(models.Agent.owner_id == user_id).all()
    
    # Convert list of tuples to list of strings: [('agent1',), ('agent2',)] -> ['agent1', 'agent2']
    flat_agent_ids = [a[0] for a in agent_ids]

    # 2. Fetch all subtasks assigned to any of those agents
    tasks = db.query(models.Subtask).filter(
        models.Subtask.assigned_to.in_(flat_agent_ids)
    ).order_by(models.Subtask.completed_at.desc()).all()

    return {
        "user_id": user_id,
        "total_completed": len([t for t in tasks if t.status == "COMPLETED"]),
        "tasks": tasks
    }

@router.get("/my-agents/{user_id}", response_model=schemas.AgentListResponse)
def get_user_agents(user_id: int, db: Session = Depends(database.get_db)):
    # 1. Query all agents belonging to this user
    agents = db.query(models.Agent).filter(models.Agent.owner_id == user_id).all()
    
    # 2. Return the list formatted by our schema
    return {
        "user_id": user_id,
        "agents": agents
    }