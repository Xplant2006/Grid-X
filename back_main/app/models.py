from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

# ==========================================
# 1. USERS TABLE
# ==========================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)  # Storing plain text as requested (no hashing)
    role = Column(String, default="buyer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # RELATIONSHIPS
    jobs = relationship("Job", back_populates="owner")
    agents = relationship("Agent", back_populates="owner") # Renamed from 'devices' to 'agents'


# ==========================================
# 2. AGENTS TABLE (Previously Sellers)
# ==========================================
class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, index=True) # e.g. "agent_xyz"
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String, default="OFFLINE")
    gpu_model = Column(String, nullable=True)
    ram_total = Column(String, nullable=True)
    
    last_heartbeat = Column(DateTime(timezone=True), server_default=func.now())

    # RELATIONSHIPS
    owner = relationship("User", back_populates="agents")
    subtasks = relationship("Subtask", back_populates="assigned_agent")


# ==========================================
# 3. JOBS TABLE
# ==========================================
class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    status = Column(String, default="PROCESSING")

    # FILE URLs
    original_code_url = Column(String)
    original_req_url = Column(String)
    original_data_url = Column(String)

    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # RELATIONSHIPS
    owner = relationship("User", back_populates="jobs")
    subtasks = relationship("Subtask", back_populates="job")


# ==========================================
# 4. SUBTASKS TABLE
# ==========================================
class Subtask(Base):
    __tablename__ = "subtasks"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"))
    assigned_to = Column(String, ForeignKey("agents.id"), nullable=True) # Changed to agents.id
    
    status = Column(String, default="PENDING")
    chunk_file_url = Column(String)
    result_file_url = Column(String, nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # RELATIONSHIPS
    job = relationship("Job", back_populates="subtasks")
    assigned_agent = relationship("Agent", back_populates="subtasks")