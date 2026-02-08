# 🚀 Grid-X Worker Setup Guide

> **Monetize your idle compute power with Grid-X.**  
> This package contains everything you need to run a Grid-X worker node on Linux or macOS.

---

## � How This Package Was Created

This package (`gridx-worker.tar.gz`) was generated using the **Grid-X Package Manager**.

### If you are on the Source Machine (Developer):
To create a new distribution package for fresh devices:

1.  Navigate to the project root.
2.  Run the packager script:
    ```bash
    ./package_worker.sh
    ```
3.  This creates `gridx-worker.tar.gz` containing:
    - Worker code (`worker/`)
    - Setup Wizard (`setup_worker.sh`)
    - Docker config (`Dockerfile.base`)
    - This Guide (`WORKER_SETUP.md` -> `README.md`)

---

## �📋 Prerequisites (Target Machine)

Before you start on the fresh device, ensure you have:
- **Python 3.10+** (verify with `python3 --version`)
- **Docker** running (verify with `docker info`)
- **Stable Internet Connection**

---

## ⚡ Quick Start (Target Machine)

### 1. Extract the Package
Copy `gridx-worker.tar.gz` to your fresh machine and run:

```bash
# Create directory and extract
mkdir gridx-worker
tar -xzf gridx-worker.tar.gz -C gridx-worker
cd gridx-worker
```

### 2. Run the Setup Wizard
This script will prepare your environment, install dependencies, and build the secure sandbox.

```bash
chmod +x setup_worker.sh
./setup_worker.sh
```

### 3. Configure Your Worker
The wizard will prompt you for two things:

*   **Backend URL**:
    *   If testing locally: Press `Enter` to use default (`http://localhost:8000`)
    *   If connecting to a server: Enter the IP (e.g., `http://192.168.1.50:8000`)

*   **Worker Email** (CRITICAL):
    *   Enter the email you used to register on the Grid-X platform (e.g., `hadhi@ek.com`).
    *   *Note: If you haven't registered, please restart this step after registering.*

### 4. Start Earning!
Once setup is complete, launch the worker:

```bash
./start_worker.sh
```

You should see:
> `🚀 Grid-X Worker Starting...`  
> `✅ Registered as worker_...`

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| **Permission Denied** | Run `chmod +x *.sh` to make scripts executable. |
| **Docker Permission Denied** | Run `sudo usermod -aG docker $USER`, then log out and back in. |
| **Registration Failed (404)** | Your email is not found in the database. Check `worker_config.env` or register on the website. |
| **Connection Refused** | Check if the Backend is running and if the URL in `worker_config.env` is correct. |

---

## 📊 Monitoring

Logs are automatically saved to `worker.log`.  
To view them in real-time:

```bash
tail -f worker.log
```
