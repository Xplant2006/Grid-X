# Grid-X Frontend API Guide

This document details the API endpoints available for the frontend application. The base URL (e.g., `http://localhost:8000`) should be prepended to all paths.

## 1. Authentication & User Profile

### Register User
Creates a new user account.

- **Endpoint**: `POST /register`
- **Description**: Registers a new user with email and password.
- **Request Body** (JSON):
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword",
    "role": "buyer" // Optional, default is "buyer"
  }
  ```
- **Response** (JSON):
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Errors**:
  - `400 Bad Request`: "Email already registered"

### Login User
Authenticates a user.

- **Endpoint**: `POST /login`
- **Description**: Verifies email and password.
- **Request Body** (JSON):
  ```json
  {
    "email": "user@example.com",
    "password": "securepassword"
  }
  ```
- **Response** (JSON):
  Returns the user object on success.
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Errors**:
  - `401 Unauthorized`: "Invalid email or password"

### Get Wallet Balance
Retrieves the credit balance and role for a user.

- **Endpoint**: `GET /wallet/{user_id}`
- **Description**: Fetches current credits.
- **Path Parameters**:
  - `user_id`: Integer ID of the user.
- **Response** (JSON):
  ```json
  {
    "user_id": 1,
    "credits": 100.0,
    "role": "buyer"
  }
  ```
- **Errors**:
  - `404 Not Found`: "User not found"

---

## 2. Jobs (Buyer Operations)

### Upload Job
Submits a new job with code, requirements, and data files.

- **Endpoint**: `POST /upload`
- **Description**: Uploads a job. Splits the data file in the background.
- **Request Body** (multipart/form-data):
  - `title`: (text) Title of the job.
  - `user_id`: (text/int) ID of the user submitting the job.
  - `file_code`: (file) Python script (e.g., `train.py`).
  - `file_req`: (file) Requirements file (e.g., `requirements.txt`).
  - `file_data`: (file) Data CSV file (e.g., `data.csv`).
- **Response** (JSON):
  ```json
  {
    "job_id": 123,
    "message": "Upload successful! Splitting data in background.",
    "status": "PROCESSING"
  }
  ```

### List My Jobs
Retrieves all jobs created by a specific user.

- **Endpoint**: `GET /list/{user_id}`
- **Description**: returns a list of jobs.
- **Path Parameters**:
  - `user_id`: Integer ID of the user.
- **Response** (JSON Array):
  ```json
  [
    {
      "id": 1,
      "title": "My Training Job",
      "status": "COMPLETED", // PROCESSING, RUNNING, COMPLETED, ERROR
      "created_at": "2023-10-27T10:00:00Z",
      "original_code_url": "https://...",
      "original_data_url": "https://...",
      "final_result_url": "https://..." // Null if not complete
    },
    ...
  ]
  ```

### Download Job Result
Gets the direct download link for a completed job result.

- **Endpoint**: `GET /download/{job_id}`
- **Description**: returns the final result URL if the job is complete and belongs to the user.
- **Query Parameters**:
  - `user_id`: (integer) ID of the user requesting the download (for verification).
- **Response** (JSON):
  ```json
  {
    "job_id": 1,
    "title": "My Training Job",
    "status": "COMPLETED",
    "final_result_url": "https://supabase..."
  }
  ```
- **Errors**:
  - `404 Not Found`: "Job not found"
  - `403 Forbidden`: "Unauthorized: You do not own this job."

---

## 3. Marketplace & Agents (Seller Operations)

### Get Online Agents
Lists legitimate active agents on the network.

- **Endpoint**: `GET /agents/online`
- **Description**: Returns agents that have sent a heartbeat in the last 5 minutes.
- **Response** (JSON Array):
  ```json
  [
    {
      "id": "agent_uuid_...",
      "status": "IDLE", // IDLE, BUSY, OFFLINE
      "gpu_model": "NVIDIA RTX 3090",
      "ram_total": "32GB",
      "last_heartbeat": "2023-10-27T10:05:00Z"
    },
    ...
  ]
  ```

### Get My Agents
Lists all agents owned by a specific user (Seller).

- **Endpoint**: `GET /my-agents/{user_id}`
- **Description**: Shows all agents registered to this user account.
- **Path Parameters**:
  - `user_id`: Integer ID of the user.
- **Response** (JSON):
  ```json
  {
    "user_id": 1,
    "agents": [
      {
        "id": "agent_uuid_...",
        "status": "IDLE",
        "gpu_model": "NVIDIA RTX 3090",
        "ram_total": "32GB",
        "last_heartbeat": "2023-10-27T10:05:00Z"
      }
    ]
  }
  ```

### Get Seller Tasks
Lists tasks assigned to a seller's agents.

- **Endpoint**: `GET /seller-tasks/{user_id}`
- **Description**: Returns all subtasks worked on by any agent owned by this user.
- **Path Parameters**:
  - `user_id`: Integer ID of the user.
- **Response** (JSON):
  ```json
  {
    "user_id": 1,
    "total_completed": 5,
    "tasks": [
      {
        "id": 101,
        "job_id": 1,
        "assigned_to": "agent_uuid_...",
        "status": "COMPLETED",
        "result_file_url": "https://...",
        "completed_at": "2023-10-27T10:30:00Z"
      },
      ...
    ]
  }
  ```
