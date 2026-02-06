import { NextResponse } from 'next/server';
import { store } from '@/lib/store';

// POST /api/nodes/register 
// Used by the Agent to say "I'm here!"
export async function POST(request: Request) {
    const data = await request.json();

    if (!data.id || !data.specs) {
        return NextResponse.json({ error: 'Missing id or specs' }, { status: 400 });
    }

    store.addNode({
        id: data.id,
        name: data.name || 'Unknown Node',
        specs: data.specs,
        status: 'idle',
        lastHeartbeat: Date.now()
    });

    return NextResponse.json({ success: true, message: 'Registered' });
}
