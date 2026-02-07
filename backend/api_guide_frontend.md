# Backend API Guide for Frontend Developers

This guide details the API endpoints available for the frontend application. The backend is built with FastAPI.

**Base URL**: `http://localhost:8000` (or your deployed URL)

## 1. Authentication (`/auth`)
Defined in `app/routers/front_auth.py`.

### Register User
Create a new user account.

- **Endpoint**: `POST /auth/register`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secretpassword"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Errors**:
  - `400 Bad Request`: Email already registered.

### Login User
Authenticate a user.

- **Endpoint**: `POST /auth/login`
- **Content-Type**: `application/json`
- **Request Body**:
  ```json
  {
    "email": "user@example.com",
    "password": "secretpassword"
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "id": 1,
    "email": "user@example.com",
    "role": "buyer",
    "created_at": "2023-10-27T10:00:00Z"
  }
  ```
- **Errors**:
  - `401 Unauthorized`: Invalid email or password.

---

## 2. Jobs (`/jobs`)
Defined in `app/routers/front_job.py`.

### Upload New Job
Upload code, requirements, and data to start a new processing job.

- **Endpoint**: `POST /jobs/upload`
- **Content-Type**: `multipart/form-data`
- **Form Data**:
  - `title` (text): Title of the job.
  - `user_id` (text/int): ID of the user submitting the job.
  - `file_code` (file): Python script (e.g., `train.py`).
  - `file_req` (file): Requirements file (e.g., `requirements.txt`).
  - `file_data` (file): CSV data file (e.g., `data.csv`).
- **Response**: `200 OK`
  ```json
  {
    "job_id": 12,
    "message": "Upload successful! Splitting data in background.",
    "status": "PROCESSING"
  }
  ```

### List My Jobs
Get a list of all jobs submitted by a specific user.

- **Endpoint**: `GET /jobs/list/{user_id}`
- **Path Parameters**:
  - `user_id`: Integer ID of the user.
- **Response**: `200 OK`
  ```json
  [
    {
      "id": 12,
      "title": "My Training Job",
      "status": "PROCESSING",
      "created_at": "2023-10-27T10:05:00Z",
      "original_code_url": "https://...",
      "original_data_url": "https://..."
    }
  ]
  ```

---

## 3. Sellers / Agents (`/sellers`)
Defined in `app/routers/sellers.py`.

### List Online Agents
Get a list of currently active agents (sellers) available for work.

- **Endpoint**: `GET /sellers/agents/online`
- **Response**: `200 OK`
  ```json
  [
    {
      "id": "agent_uuid_123",
      "status": "IDLE",
      "gpu_model": "RTX 3090",
      "ram_total": "32GB",
      "last_heartbeat": "2023-10-27T10:10:00Z"
    }
  ]
  ```

## Notes
- **TimESTAMPS**: All timestamps are returned in ISO 8601 format (UTC).
- **Status Codes**: 
    - `200`: Success
    - `400`: Client Error (Bad Input)
    - `401`: Unauthorized
    - `404`: Not Found
    - `500`: Server Error

---

## 4. Common Workflows

### A. User Signup & Login
1. **Sign Up**: Frontend collects email/password -> `POST /auth/register`.
2. **Login**: Frontend collects email/password -> `POST /auth/login`. 
   - **Store the `id`** (User ID) from the response in `localStorage` or Context. You will need this for uploading jobs.

### B. Submitting a Job
1. User selects files (Python script, Requirements, Data CSV).
2. User enters a Title.
3. Frontend retrieves `user_id` from storage.
4. **Upload**: Construct `FormData` -> `POST /jobs/upload`.
5. Display the returned `job_id` and status ("PROCESSING") to the user.

### C. Monitoring Jobs
1. **Poll for Updates**: Use `GET /jobs/list/{user_id}` to show the user's dashboard.
2. The `status` field will change from `PROCESSING` -> `RUNNING` -> `COMPLETED`.
3. When `COMPLETED`, you (the frontend) might want to show a download button (logic for results download depends on the `Subtask` flow, usually you'd query specific subtask results, but for now `jobs/list` gives the high-level status).

### D. Finding Sellers
1. **Show Network Status**: `GET /sellers/agents/online`.
2. Display a grid/list of available GPUs to show the user the network is alive.
