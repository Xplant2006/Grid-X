# Grid-X GitHub Commit Guide

## Pre-Commit Checklist

### ✅ Secrets and Credentials
- [ ] `.env` file is gitignored (contains actual credentials)
- [ ] `.env.example` exists (template without secrets)
- [ ] No hardcoded API keys in code
- [ ] `worker_config.env.example` exists (template)

### ✅ Database Files
- [ ] `*.db` files are gitignored
- [ ] No SQLite databases in commit

### ✅ Logs and Outputs
- [ ] `*.log` files are gitignored
- [ ] Test output files excluded

### ✅ Documentation
- [ ] README.md is up to date
- [ ] WORKER_SETUP.md exists
- [ ] Setup scripts are executable

---

## Files to Commit

### Core Backend
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py (✅ updated with .env loading)
│   ├── database.py (✅ updated with absolute path)
│   ├── models.py
│   ├── schemas.py
│   ├── aggregation.py (✅ updated)
│   └── routers/
│       ├── __init__.py
│       ├── front_auth.py
│       ├── front_job.py (✅ updated with env vars)
│       ├── agent.py (✅ updated with aggregation fix)
│       └── sellers.py
└── requirements.txt
```

### Worker Files
```
worker/
├── main.py
├── executor.py
├── utils.py
└── requirements.txt
```

### Docker
```
Dockerfile.base
.dockerignore
build_docker.sh
```

### Scripts
```
setup_worker.sh
start_worker.sh
start_backend_demo.sh
test_auto_aggregation.sh
```

### Testing
```
tests/
└── test_full_workflow.py
```

### Utilities (Optional)
```
trigger_aggregation.py
force_complete_job.py
test_supabase.py
```

### Configuration
```
.env.example
worker_config.env.example
.gitignore
```

### Documentation
```
README.md
WORKER_SETUP.md
```

---

## Files to EXCLUDE (Already in .gitignore)

### Secrets
- `.env` (actual credentials)
- `worker_config.env` (actual config)

### Databases
- `backend/sql_app.db`
- `backend/app/sql_app.db`
- `*.db`

### Logs
- `backend.log`
- `test_output.log`
- `*.log`

### Virtual Environment
- `.venv/`
- `venv/`

### Python Cache
- `__pycache__/`
- `*.pyc`

---

## Commit Commands

### 1. Check Status
```bash
git status
```

### 2. Add Files
```bash
# Add all tracked and new files (respects .gitignore)
git add .

# Or add specific files
git add backend/app/
git add worker/
git add tests/
git add *.sh
git add README.md
git add .env.example
git add worker_config.env.example
```

### 3. Verify What Will Be Committed
```bash
# Check what's staged
git status

# Make sure .env is NOT in the list!
# Make sure *.db files are NOT in the list!
```

### 4. Commit
```bash
git commit -m "feat: Complete federated learning system with automatic aggregation

- Fixed environment variable loading in main.py
- Fixed database path consistency
- Fixed automatic aggregation trigger in agent.py
- Added comprehensive test suite
- Added worker setup scripts
- Added demo setup guide
- Updated documentation"
```

### 5. Push to GitHub
```bash
# First time
git remote add origin https://github.com/YOUR_USERNAME/Grid-X.git
git branch -M main
git push -u origin main

# Subsequent pushes
git push
```

---

## Verify Before Push

### Critical Checks

1. **No Secrets in Commit**
```bash
# Search for potential secrets
git diff --cached | grep -i "supabase_key\|service_role\|password"
# Should return nothing!
```

2. **No Database Files**
```bash
git status | grep "\.db"
# Should return nothing!
```

3. **No .env File**
```bash
git status | grep "\.env$"
# Should return nothing! (.env.example is OK)
```

---

## After First Push

### Create GitHub Repository

1. Go to https://github.com/new
2. Name: `Grid-X`
3. Description: "Federated Learning Platform with PyTorch"
4. Public or Private (your choice)
5. Don't initialize with README (you already have one)
6. Create repository

### Add Remote and Push
```bash
git remote add origin https://github.com/YOUR_USERNAME/Grid-X.git
git branch -M main
git push -u origin main
```

### Add Topics (Optional)
- federated-learning
- pytorch
- machine-learning
- distributed-computing
- docker
- fastapi

---

## README Badges (Optional)

Add to top of README.md:

```markdown
![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)
![Docker](https://img.shields.io/badge/Docker-required-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
```

---

## Post-Commit Setup for Others

When someone clones your repo, they need to:

1. **Copy environment template**
```bash
cp .env.example .env
# Edit .env with their Supabase credentials
```

2. **Setup Python environment**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

3. **Build Docker image**
```bash
./build_docker.sh
```

4. **Start backend**
```bash
./start_backend_demo.sh
```

---

## Quick Commit Script

Create `commit_to_github.sh`:

```bash
#!/bin/bash

echo "🔍 Pre-commit checks..."

# Check for secrets
if git diff --cached | grep -qi "supabase.*key.*eyJ"; then
    echo "❌ ERROR: Supabase key found in commit!"
    exit 1
fi

# Check for .env
if git status --short | grep "^A.*\.env$"; then
    echo "❌ ERROR: .env file in commit!"
    exit 1
fi

# Check for .db files
if git status --short | grep "\.db$"; then
    echo "❌ ERROR: Database files in commit!"
    exit 1
fi

echo "✅ All checks passed!"
echo ""
echo "Files to be committed:"
git status --short

echo ""
read -p "Proceed with commit? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git add .
    git commit -m "$1"
    echo "✅ Committed! Ready to push."
else
    echo "❌ Commit cancelled"
fi
```

Usage:
```bash
chmod +x commit_to_github.sh
./commit_to_github.sh "Your commit message here"
```

---

## Summary

**Safe to commit:**
- ✅ All source code
- ✅ Test scripts
- ✅ Setup scripts
- ✅ Documentation
- ✅ `.env.example` (template)
- ✅ `.gitignore`

**DO NOT commit:**
- ❌ `.env` (actual credentials)
- ❌ `*.db` (databases)
- ❌ `*.log` (logs)
- ❌ `.venv/` (virtual environment)

**Your repository is ready for GitHub!** 🚀
