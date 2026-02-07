from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .database import engine, Base
# Import the routers we created
from .routers import front_auth, front_job, sellers, agent

# Load environment variables from .env file
load_dotenv()

# ==========================================
# 1. INITIALIZE DATABASE
# ==========================================
# This automatically creates the tables (Users, Agents, Jobs, Subtasks)
# inside sql_app.db if they don't exist yet.
Base.metadata.create_all(bind=engine)

# ==========================================
# 2. SETUP APP & SECURITY
# ==========================================
app = FastAPI(title="GridX Backend", description="Distributed Compute Network API")

# CORS Middleware
# This is CRITICAL. It allows your React/HTML frontend to talk to this backend.
# allow_origins=["*"] means "Allow anyone" (Perfect for Hackathons)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 3. PLUG IN THE ROUTERS
# ==========================================
# This keeps your code clean. We import logic from other files and "mount" them here.

# Frontend Routes (For the Website)
app.include_router(front_auth.router, prefix="/auth", tags=["Frontend: Auth"])
app.include_router(front_job.router, prefix="/jobs", tags=["Frontend: Jobs"])
app.include_router(sellers.router, prefix="/stats", tags=["Frontend: Dashboard"])

# Agent Routes (For the Python Scripts on Laptops)
app.include_router(agent.router, prefix="/agent", tags=["Agent: Operations"])

# ==========================================
# 4. ROOT ENDPOINT (Health Check)
# ==========================================
@app.get("/")
def read_root():
    return {
        "status": "online", 
        "message": "GridX Server is Running! 🚀",
        "docs_url": "http://localhost:8000/docs"
    }