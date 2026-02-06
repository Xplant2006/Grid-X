const os = require('os');

// Configuration
const HUB_URL = 'http://localhost:3000/api';
// Generate a persistent ID for this machine
const NODE_ID = 'node_' + os.hostname().replace(/[^a-z0-9]/gi, '_') + '_' + Math.floor(Math.random() * 1000);

async function register() {
    const specs = {
        cpu: `${os.cpus().length} vCPUs (${os.cpus()[0].model})`,
        ram: `${Math.round(os.totalmem() / 1024 / 1024 / 1024)} GB`
    };

    console.log(`[Grid-X] Registering Node: ${NODE_ID}`);
    console.log(`[Grid-X] Specs:`, specs);

    try {
        const res = await fetch(`${HUB_URL}/nodes/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: NODE_ID,
                name: os.hostname(),
                specs
            })
        });
        const data = await res.json();
        console.log(`[Grid-X] Server replied:`, data);
        poll();
    } catch (err) {
        console.error('[Error] Could not connect to Hub. Is localhost:3000 running?');
    }
}

async function poll() {
    console.log('[Grid-X] Listening for jobs...');
    // Real polling implementation would go here (GET /api/tasks?nodeId=...)
    // For now, we mainly want to keep the "Active Node" status alive.
    setInterval(async () => {
        try {
            await fetch(`${HUB_URL}/nodes/register`, { // Re-register acts as heartbeat
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ id: NODE_ID, status: 'idle', specs: { cpu: 'heartbeat', ram: 'heartbeat' } }) // Simplified heartbeat
            });
        } catch (e) { }
    }, 5000);
}

// Check for dependencies, otherwise just run raw node
if (typeof fetch === 'undefined') {
    console.error('This agent requires Node.js v18+ (verified native fetch support).');
    process.exit(1);
}

register();
