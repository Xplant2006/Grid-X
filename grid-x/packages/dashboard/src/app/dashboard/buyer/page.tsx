'use client';

import { useState, useEffect } from 'react';
import styles from './buyer.module.css';

interface Node {
    id: string;
    name: string;
    specs: { cpu: string; ram: string };
    status: string;
}

export default function BuyerDashboard() {
    const [code, setCode] = useState('import time\nprint("Hello Grid-X")\ntime.sleep(2)\nprint("Done")');
    const [logs, setLogs] = useState<string[]>([]);
    const [status, setStatus] = useState('Ready to Deploy');
    const [nodes, setNodes] = useState<Node[]>([]);
    const [activeJobId, setActiveJobId] = useState<string | null>(null);

    // Poll for Active Nodes
    useEffect(() => {
        const fetchNodes = async () => {
            try {
                const res = await fetch('/api/nodes');
                const data = await res.json();
                setNodes(data.nodes || []);
            } catch (err) { console.error('Failed to fetch nodes', err); }
        };
        fetchNodes();
        const interval = setInterval(fetchNodes, 5000);
        return () => clearInterval(interval);
    }, []);

    // Poll for Job Logs if a job is running
    useEffect(() => {
        if (!activeJobId) return;

        const pollJob = async () => {
            try {
                const res = await fetch(`/api/jobs?id=${activeJobId}`);
                const data = await res.json();
                if (data.job) {
                    setLogs(data.job.logs || []);
                    if (data.job.status === 'completed' || data.job.status === 'failed') {
                        setStatus('Job ' + data.job.status);
                        setActiveJobId(null); // Stop polling
                    }
                }
            } catch (err) { console.error(err); }
        };

        const interval = setInterval(pollJob, 1000);
        return () => clearInterval(interval);
    }, [activeJobId]);

    const handleDeploy = async () => {
        setStatus('Deploying...');
        setLogs(['> Submitting to Hub...']);

        try {
            const res = await fetch('/api/jobs', {
                method: 'POST',
                body: JSON.stringify({ script: code })
            });
            const data = await res.json();
            if (data.success) {
                setActiveJobId(data.jobId);
                setLogs(prev => [...prev, `> Job ID: ${data.jobId}`, '> Waiting for Node assignment...']);
            }
        } catch (err) {
            setStatus('Error');
            setLogs(prev => [...prev, '> Failed to submit job.']);
        }
    };

    const activeNodeCount = nodes.filter(n => n.status !== 'offline').length;

    return (
        <div className={styles.dashboard}>
            <header className={styles.header}>
                <h1>Scientist Workstation</h1>
                <div className={styles.stats}>
                    <span>Active Nodes: {activeNodeCount}</span>
                    <span>Targeting: Standard Grid</span>
                </div>
            </header>

            <main className={styles.main}>
                {/* Left: Code Editor */}
                <section className={styles.panel}>
                    <h2>Script.py</h2>
                    <textarea
                        className={styles.editor}
                        value={code}
                        onChange={(e) => setCode(e.target.value)}
                    />
                </section>

                {/* Center: Configuration & Uploads */}
                <section className={styles.panel}>
                    <h2>Configuration</h2>
                    <div className={styles.uploadBox}>
                        <label>requirements.txt</label>
                        <input type="file" />
                    </div>
                    <div className={styles.uploadBox}>
                        <label>dataset.csv</label>
                        <input type="file" />
                    </div>

                    <div className={styles.activeNodesList}>
                        <h3>Available Resources</h3>
                        <ul>
                            {nodes.map(n => (
                                <li key={n.id} style={{ color: n.status === 'offline' ? '#555' : '#888' }}>
                                    {n.name} ({n.specs.cpu}) - {n.status}
                                </li>
                            ))}
                        </ul>
                    </div>

                    <div className={styles.actions}>
                        <button
                            className={styles.deployBtn}
                            onClick={handleDeploy}
                            disabled={status === 'Deploying...'}
                        >
                            {status === 'Deploying...' ? 'Running...' : 'Deploy to Grid'}
                        </button>
                    </div>
                </section>

                {/* Right: Live Terminal */}
                <section className={`${styles.panel} ${styles.terminalPanel}`}>
                    <div className={styles.terminalHeader}>
                        <span className={styles.statusDot} data-status={activeJobId ? 'active' : 'idle'}></span>
                        Live Terminal
                    </div>
                    <div className={styles.terminal}>
                        {logs.map((log, i) => (
                            <div key={i} className={styles.logLine}>{log}</div>
                        ))}
                        <div className={styles.cursor}>_</div>
                    </div>
                </section>
            </main>
        </div>
    );
}
