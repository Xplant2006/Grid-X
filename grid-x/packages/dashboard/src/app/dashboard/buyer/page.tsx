'use client';

import { useEffect, useState } from 'react';
import styles from './buyer.module.css';
import { API_BASE } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface Job {
  id: number;
  title: string;
  status: string;
  created_at: string;
  original_code_url?: string;
  original_data_url?: string;
}

interface Agent {
  id: string;
  status: string;
  gpu_model: string;
  ram_total: string;
  last_heartbeat: string;
}

export default function BuyerDashboard() {
  const { user } = useAuth();

  // ─── Upload State ──────────────────────────────────────────────
  const [title, setTitle] = useState('');
  const [codeFile, setCodeFile] = useState<File | null>(null);
  const [reqFile, setReqFile] = useState<File | null>(null);
  const [dataFile, setDataFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState('');

  // ─── Jobs & Agents ─────────────────────────────────────────────
  const [jobs, setJobs] = useState<Job[]>([]);
  const [agents, setAgents] = useState<Agent[]>([]);

  /* ===================== Upload Job ===================== */
  const handleUpload = async () => {
    if (!user || !codeFile || !reqFile || !dataFile || !title) {
      alert('All fields are required');
      return;
    }

    const formData = new FormData();
    formData.append('title', title);
    formData.append('user_id', String(user.id));
    formData.append('file_code', codeFile);
    formData.append('file_req', reqFile);
    formData.append('file_data', dataFile);

    try {
      setUploadStatus('Uploading...');
      const res = await fetch(`${API_BASE}/jobs/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await res.json();
      setUploadStatus(data.message || 'Submitted');
      fetchJobs(); // refresh job list
    } catch {
      setUploadStatus('Upload failed');
    }
  };

  /* ===================== Fetch Jobs ===================== */
const fetchJobs = async () => {
  if (!user) return;

  const res = await fetch(`${API_BASE}/jobs/list/${user.id}`, {
    headers: {
      "ngrok-skip-browser-warning": "69420", // The value can be anything
    },
  });

  if (!res.ok) return;
  const data = await res.json();
  setJobs(data);
};

  /* ===================== Fetch Agents ===================== */
const fetchAgents = async () => {
  const res = await fetch(`${API_BASE}/stats/agents/online`, {
    headers: {
      "ngrok-skip-browser-warning": "69420", // The value can be anything
    },
  });
  if (!res.ok) {
    console.error(await res.text());
    return;
  }

  const data = await res.json();
  setAgents(data);
};

  /* ===================== Polling ===================== */
 useEffect(() => {
  if (!user) return;

  fetchJobs();
  fetchAgents();

  const interval = setInterval(() => {
    fetchJobs();
    fetchAgents();
  }, 5000);

  return () => clearInterval(interval);
}, [user]);


  /* ===================== Download Result ===================== */
  const downloadResult = async (jobId: number) => {
    try {
      const res = await fetch(
        `${API_BASE}/jobs/download?user_id=${user?.id}&job_id=${jobId}`
      );

      if (!res.ok) {
        alert('Result not available yet');
        return;
      }

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);

      const a = document.createElement('a');
      a.href = url;
      a.download = `job_${jobId}_result.zip`;
      a.click();
    } catch {
      alert('Download failed');
    }
  };

  /* ===================== UI ===================== */
  return (
    <div className={styles.dashboard}>
  <header className={styles.header}>
    <h1>Scientist Workstation</h1>
    <p>Submit jobs, monitor progress, and explore available compute.</p>
  </header>

  <div className={styles.grid}>
    {/* Upload */}
    <section className={styles.card}>
      <h2>Upload New Job</h2>

      <input
        className={styles.input}
        placeholder="Job Title"
        value={title}
        onChange={(e) => setTitle(e.target.value)}
      />

      <label className={styles.file}>
        Code file (.py/.ipynb)        <input type="file" onChange={(e) => setCodeFile(e.target.files?.[0] || null)} />
      </label>

      <label className={styles.file}>
        Requirements        <input type="file" onChange={(e) => setReqFile(e.target.files?.[0] || null)} />
      </label>

      <label className={styles.file}>
        Dataset (.csv)
        <input type="file" onChange={(e) => setDataFile(e.target.files?.[0] || null)} />
      </label>

      <button className={styles.primaryBtn} onClick={handleUpload}>
        Submit Job
      </button>

      <span className={styles.status}>{uploadStatus}</span>
    </section>

    {/* Jobs */}
    <section className={styles.card}>
      <h2>My Jobs</h2>

      {jobs.length === 0 && <p className={styles.muted}>No jobs submitted yet.</p>}

      <ul className={styles.list}>
        {jobs.map(job => (
          <li key={job.id} className={styles.jobItem}>
            <div>
              <strong>{job.title}</strong>
              <span className={styles.badge}>{job.status}</span>
            </div>

            {job.status.toUpperCase() === 'COMPLETED' && (
              <button onClick={() => downloadResult(job.id)}>⬇ Download</button>
            )}
          </li>
        ))}
      </ul>
    </section>

    {/* Agents */}
    <section className={styles.card}>
      <h2>Available Sellers</h2>

      {agents.length === 0 && <p className={styles.muted}>No agents online.</p>}

      <ul className={styles.list}>
        {agents.map(agent => (
          <li key={agent.id} className={styles.agentItem}>
            <strong>{agent.gpu_model}</strong>
            <span>{agent.ram_total}</span>
            <span className={styles.badge}>{agent.status}</span>
          </li>
        ))}
      </ul>
    </section>
  </div>
</div>

  );
}
