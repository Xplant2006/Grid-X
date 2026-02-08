Worker Quick Start Guide
For Workers: How to Rent Out Your CPU
TL;DR - 3 Simple Steps
bash
# 1. Clone and setup
git clone https://github.com/YOUR_USERNAME/Grid-X.git
cd Grid-X
# 2. Start setup (Follow interactive prompts!)
./setup_worker.sh
# 3. Start earning!
./start_worker.sh
What the Setup Does
setup_worker.sh
 automatically:
✅ Checks Python & Docker are installed
✅ Creates Python virtual environment
✅ Installs worker dependencies
✅ Builds Docker sandbox image (~2GB, takes 2-3 min)
✅ Prompts you for Backend URL & Email (NEW!)
✅ Creates configuration file
✅ Creates start script
What You Need:
Docker (for running tasks securely)
Python 3.11+
5GB free disk space (for Docker image)
Stable internet
Configuration
The setup script now asks for this automatically!

If you need to change it later, edit worker_config.env:

bash
# Change this to the actual Grid-X backend URL
BACKEND_URL=https://gridx-backend.example.com
# Your unique worker ID (auto-generated, can customize)
AGENT_ID=worker_mycomputer_12345
# Your email for registration
WORKER_EMAIL=myemail@example.com
Running the Worker
bash
./start_worker.sh
What happens:

Worker registers with backend
Polls for tasks every 10 seconds
Downloads task code & data chunk
Runs training in isolated Docker container
Uploads trained model weights
Repeats!
Logs saved to: worker.log

Resource Usage
Each task uses:

CPU: 1 core
RAM: 2GB max
Disk: 1GB temporary
Network: Only for downloading/uploading (no internet during execution)
Security
What Workers Run:
User-submitted Python training code
Runs in isolated Docker container
No internet access during execution
No access to your files
Runs as non-root user
What Workers See:
Small chunk of CSV data (not full dataset)
Training code
Never see other workers' data
What Workers Upload:
Model weights only (not raw data)
Stopping the Worker
bash
# Press Ctrl+C in the terminal
# Or:
pkill -f "python worker/main.py"
Troubleshooting
"Docker permission denied"
bash
sudo usermod -aG docker $USER
newgrp docker
"No tasks available"
This is normal! Means:

No jobs currently submitted
Other workers claimed tasks first
Worker keeps polling automatically
"Can't connect to backend"
Check BACKEND_URL in worker_config.env
Verify: curl $BACKEND_URL
Monitoring
bash
# View live logs
tail -f worker.log
# Count completed tasks
grep "Task completed" worker.log | wc -l
Full Documentation
See 
WORKER_SETUP.md
 for detailed setup instructions and troubleshooting.


Comment
Ctrl+Alt+M
