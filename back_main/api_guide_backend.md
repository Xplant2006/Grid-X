# Backend API Guide for Agents (Python Client)

This guide details the API endpoints used by the compute agents (Python scripts) to communicate with the backend.

**Base URL**: `http://localhost:8000` (or your deployed URL)
**Router Prefix**: `/agent`

All agent-related endpoints are prefixed with `/agent`.

---

## 1. Registration & Heartbeat

### Register Agent
Registers a new machine/agent and links it to a human user's account via email.
**Use Case**: Called once when the agent script starts for the first time or re-registers.

- **Endpoint**: `POST /agent/register`
- **Content-Type**: `application/json`
- **Request Body** (`AgentRegister`):
  ```json
  {
    "id": "uuid-gen-by-client-1234",
    "email": "user@example.com",
    "gpu_model": "NVIDIA RTX 4090",
    "ram_total": "64GB"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "New Agent uuid-gen-by-client-1234 registered!",
    "status": "created"
  }
  ```
- **Errors**:
  - `404 Not Found`: "Owner email not found. Please register on the website first."

### Report Heartbeat
Tells the server "I am alive" and updates current status.
**Use Case**: Called every few seconds (e.g., 10s) by the agent loop.

- **Endpoint**: `POST /agent/heartbeat`
- **Content-Type**: `application/json`
- **Request Body** (`AgentHeartbeat`):
  ```json
  {
    "id": "uuid-gen-by-client-1234",
    "status": "IDLE" 
  }
  ```
  *Status options*: `"IDLE"`, `"BUSY"`, `"WORKING"`, `"OFFLINE"` (implicitly set by server if timeout).

- **Response**: `200 OK`
  ```json
  {
    "message": "Heartbeat received",
    "server_time": "2023-10-27T10:00:05Z"
  }
  ```
- **Errors**:
  - `404 Not Found`: "Agent not registered" (If database was wiped or ID is wrong).

---

## 2. Task Management

### Request Task
Agent asks the server if there is any pending work to do.
**Use Case**: Called by the agent when its status is `IDLE`.

- **Endpoint**: `POST /agent/request_task`
- **Content-Type**: `application/json`
- **Request Body** (`TaskRequest`):
  ```json
  {
    "agent_id": "uuid-gen-by-client-1234"
  }
  ```
- **Response** (`TaskResponse`):
  **Case A: No Work Available**
  ```json
  {
    "task_id": null,
    "job_id": null,
    "code_url": null,
    "requirements_url": null,
    "chunk_data_url": null
  }
  ```
  **Case B: Work Assigned**
  ```json
  {
    "task_id": 55,
    "job_id": 12,
    "code_url": "https://supabase.../train.py",
    "requirements_url": "https://supabase.../requirements.txt",
    "chunk_data_url": "https://supabase.../chunk_0.csv"
  }
  ```

### Complete Task
Agent reports that it has finished processing a subtask and uploads the result URL.
**Use Case**: Called after the agent successfully runs the Python script and uploads the result.

- **Endpoint**: `POST /agent/complete_task`
- **Content-Type**: `application/json`
- **Request Body** (`TaskComplete`):
  ```json
  {
    "agent_id": "uuid-gen-by-client-1234",
    "task_id": 55,
    "result_url": "https://supabase.../results_chunk_0.csv"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "message": "Task marked as completed. Good job!"
  }
  ```
- **Errors**:
  - `404 Not Found`: "Subtask not found".
  - `400 Bad Request`: "This task was not assigned to you".

---

## 3. Recommended Agent Workflow (Pseudo-Code)

```python
# 1. Start Up
my_id = generate_uuid()
user_email = input("Enter owner email: ")
api.post("/agent/register", json={
    "id": my_id, 
    "email": user_email, 
    "gpu_model": get_gpu(),
    "ram_total": get_ram()
})

# 2. Main Loop
while True:
    # A. Send Heartbeat
    api.post("/agent/heartbeat", json={"id": my_id, "status": current_status})

    # B. If IDLE, ask for work
    if current_status == "IDLE":
        task = api.post("/agent/request_task", json={"agent_id": my_id}).json()
        
        if task["task_id"] is not None:
             current_status = "BUSY"
             # ... Download files (code, reqs, data) ...
             # ... Run the code ...
             # ... Upload results ...
             
             api.post("/agent/complete_task", json={
                 "agent_id": my_id,
                 "task_id": task["task_id"],
                 "result_url": uploaded_result_url
             })
             
             current_status = "IDLE"

    sleep(10)
```
