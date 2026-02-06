// This is a simple in-memory database for the MVP.
// In a real app, this would be SQLite or Postgres.

export interface Node {
    id: string;
    name: string;
    specs: {
        cpu: string;
        ram: string;
    };
    status: 'idle' | 'working' | 'offline';
    lastHeartbeat: number;
}

export interface Job {
    id: string;
    buyerId: string;
    script: string;
    status: 'pending' | 'running' | 'completed' | 'failed';
    assignedNodeId?: string;
    logs: string[];
    result?: string;
    createdAt: number;
}

class GridStore {
    nodes: Node[] = [];
    jobs: Job[] = [];

    constructor() {
        // Seed with one "Demo Node" so the grid isn't empty initially, 
        // but the user can register more dynamically.
        this.nodes.push({
            id: 'demo-node-1',
            name: 'Demo Cloud Provider',
            specs: { cpu: '4 vCPU', ram: '8GB' },
            status: 'idle',
            lastHeartbeat: Date.now()
        });
    }

    addNode(node: Node) {
        this.nodes = this.nodes.filter(n => n.id !== node.id); // Update if exists
        this.nodes.push(node);
    }

    getNodes() {
        // Filter out nodes that haven't heartbeated in 30 seconds
        const now = Date.now();
        return this.nodes.map(n => ({
            ...n,
            status: (now - n.lastHeartbeat > 30000) ? 'offline' : n.status
        }));
    }

    addJob(job: Job) {
        this.jobs.push(job);
    }

    getJob(id: string) {
        return this.jobs.find(j => j.id === id);
    }

    updateJobLog(id: string, log: string) {
        const job = this.jobs.find(j => j.id === id);
        if (job) {
            job.logs.push(log);
        }
    }
}

// Global singleton to persist across hot-reloads in dev (mostly)
// eslint-disable-next-line @typescript-eslint/no-explicit-any
const globalForStore = global as unknown as { gridStore: GridStore };

export const store = globalForStore.gridStore || new GridStore();

if (process.env.NODE_ENV !== 'production') globalForStore.gridStore = store;
