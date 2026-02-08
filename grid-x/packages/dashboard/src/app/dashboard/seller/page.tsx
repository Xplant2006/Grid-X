'use client';

import { useEffect, useState } from 'react';
import styles from './seller.module.css';
import { API_BASE } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

interface Agent {
  id: string;
  status: 'IDLE' | 'BUSY' | 'OFFLINE';
  gpu_model: string;
  ram_total: string;
  last_heartbeat: string;
}

interface SellerTask {
  id: number;
  job_id: number;
  assigned_to: string;
  status: 'COMPLETED';
  completed_at: string;
}

export default function SellerDashboard() {
  const { user } = useAuth();

  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<SellerTask[]>([]);
  const [jobsCompleted, setJobsCompleted] = useState(0);
  const [credits, setCredits] = useState<number | null>(null);

  /* ================= Wallet ================= */
  const fetchWallet = async () => {
    if (!user) return;

    const res = await fetch(`${API_BASE}/wallet/${user.id}`);
    if (!res.ok) {
      console.error(await res.text());
      return;
    }

    const data = await res.json();
    setCredits(data.credits);
  };

  /* ================= My Agents ================= */
  const fetchMyAgents = async () => {
    if (!user) return;

    const res = await fetch(`${API_BASE}/stats/my-agents/${user.id}`, {
    headers: {
      "ngrok-skip-browser-warning": "69420", // The value can be anything
    },
  });
    if (!res.ok) return;

    const data = await res.json();
    setAgents(data.agents || []);
  };

  /* ================= Seller Tasks ================= */
  const fetchSellerTasks = async () => {
    if (!user) return;

    const res = await fetch(`${API_BASE}/stats/seller-tasks/${user.id}`, {
    headers: {
      "ngrok-skip-browser-warning": "69420", // The value can be anything
    },
  });
    if (!res.ok) return;

    const data = await res.json();
    setTasks(data.tasks || []);
    setJobsCompleted(data.total_completed || 0);
  };

  /* ================= Polling ================= */
  useEffect(() => {
    if (!user) return;

    fetchWallet();
    fetchMyAgents();
    fetchSellerTasks();

    const interval = setInterval(() => {
      fetchMyAgents();
      fetchSellerTasks();
    }, 5000);

    return () => clearInterval(interval);
  }, [user]);

  /* ================= Status Mapping ================= */
  const getStatusLabel = (status: Agent['status']) => {
    if (status === 'BUSY') return 'Running';
    if (status === 'IDLE') return 'Inactive';
    return 'Offline';
  };

  /* ================= UI ================= */
  return (
    <div className={styles.dashboard}>
      <h1>Provider Dashboard</h1>

      {/* ─── Stats ─── */}
      <div className={styles.statsGrid}>
        <div className={styles.statCard}>
          <span>Wallet Balance</span>
          <strong>
            {credits !== null ? `${credits} credits` : '0'}
          </strong>
        </div>

        <div className={styles.statCard}>
          <span>Jobs Completed</span>
          <strong>{jobsCompleted}</strong>
        </div>
      </div>

      {/* ─── My Agents ─── */}
      <section className={styles.card}>
       <h2>My Agents</h2>
<p className={styles.muted}>Devices registered to your account</p>


        {agents.length === 0 && (
          <p className={styles.muted}>[___No agents registered__]</p>
        )}

        <ul className={styles.list}>
          {agents.map(agent => (
            <li key={agent.id} className={styles.agentRow}>
              <div>
                <strong>{agent.gpu_model}</strong>
                <span className={styles.sub}>{agent.ram_total}</span>
              </div>
              <span className={styles.status}>
                {getStatusLabel(agent.status)}
              </span>
            </li>
          ))}
        </ul>
      </section>

      {/* ─── Task History ─── */}
      <section className={styles.card}>
       <h2>Task History</h2>
<p className={styles.muted}>Completed tasks executed by your agents</p>

        {tasks.length === 0 && (
          <p className={styles.muted}>[__No completed tasks yet__]</p>
        )}

        <ul className={styles.list}>
          {tasks.map(task => (
            <li key={task.id} className={styles.taskRow}>
              <span>Job #{task.id}</span>
              <span className={styles.done}>COMPLETED</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
