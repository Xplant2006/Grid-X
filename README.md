# Grid-X: Federated Learning Platform

A distributed federated learning system that enables collaborative machine learning across multiple agents without sharing raw data.

## 🚀 Features

- **Federated Learning**: Train models across distributed workers using FedAvg
- **Secure Execution**: Docker-based sandboxed code execution
- **REST API**: FastAPI backend for job management
- **Worker Agents**: Autonomous workers that poll for tasks and execute training
- **Cloud Storage**: Supabase integration for file storage
- **CSV Data Splitting**: Automatic data partitioning across workers

## 📋 Prerequisites

- Python 3.11+
- Docker (for worker sandboxing)
- Supabase account (for file storage)

## 🛠️ Setup

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Grid-X.git
cd Grid-X
```

### 2. Create Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Backend dependencies
pip install -r backend/requirements.txt

# Worker dependencies
pip install -r worker/requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env and add your Supabase credentials
```

Required environment variables:
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key (NOT the anon key)
- `SUPABASE_BUCKET_NAME`: Storage bucket name (default: `gridx-files`)

### 5. Build Docker Image

```bash
chmod +x build_docker.sh
./build_docker.sh
```

## 🏃 Running the System

### Start the Backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
- API docs: `http://localhost:8000/docs`

### Start a Worker

```bash
export BACKEND_URL="http://localhost:8000"
export AGENT_ID="worker_1"
python worker/main.py
```

## 🧪 Testing

### Run Integration Tests

```bash
python tests/test_integration_simple.py
```

### Test Supabase Connection

```bash
python test_supabase.py
```

## 📁 Project Structure

```
Grid-X/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Database models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── database.py          # Database configuration
│   │   ├── aggregation.py       # FedAvg implementation
│   │   └── routers/
│   │       ├── front_auth.py    # Authentication endpoints
│   │       ├── front_job.py     # Job management endpoints
│   │       └── agent.py         # Worker agent endpoints
│   └── requirements.txt
├── worker/
│   ├── main.py                  # Worker polling loop
│   ├── executor.py              # Docker sandbox execution
│   └── requirements.txt
├── tests/
│   └── test_integration_simple.py
├── Dockerfile.base              # Base image for worker sandbox
├── .dockerignore
├── .gitignore
├── .env.example                 # Environment variable template
└── README.md
```

## 🔐 Security Notes

- **Never commit `.env`** - It contains sensitive credentials
- Use **service_role key** for backend operations (bypasses RLS)
- Use **anon key** for frontend/client operations
- Docker containers run as non-root user for security

## 📊 How It Works

1. **User submits job**: Upload training code, requirements, and CSV data
2. **Backend splits data**: CSV is split into 5 chunks, uploaded to Supabase
3. **Workers poll for tasks**: Idle workers request tasks from backend
4. **Sandboxed execution**: Code runs in isolated Docker containers
5. **Result upload**: Workers upload trained model weights
6. **Aggregation**: Backend performs FedAvg when all subtasks complete
7. **Final model**: Aggregated model is available for download

## 🐛 Troubleshooting

### Docker Permission Errors
```bash
sudo usermod -aG docker $USER
# Then log out and back in
```

### Supabase Upload Fails
- Check you're using the **service_role key**, not anon key
- Verify bucket exists and is public
- Check RLS policies allow uploads

### No Tasks Available
- Check backend logs for CSV splitting errors
- Verify Supabase credentials are correct
- Ensure database tables were created

## 📝 License

MIT License
