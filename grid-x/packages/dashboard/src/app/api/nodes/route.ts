import { NextResponse } from 'next/server';
import { store } from '@/lib/store';

// GET /api/nodes
// Used by the Buyer Dashboard to list available nodes
export async function GET() {
    const nodes = store.getNodes(); // Filters out offline nodes
    return NextResponse.json({ nodes });
}
