import { NextResponse } from 'next/server';
import { store } from '@/lib/store';

// POST /api/jobs (Submit a job)
export async function POST(request: Request) {
    const data = await request.json();

    const jobId = Math.random().toString(36).substring(7);

    store.addJob({
        id: jobId,
        buyerId: 'demo-buyer',
        script: data.script,
        status: 'pending',
        logs: ['> Job received by Hub', '> Waiting for assignment...'],
        createdAt: Date.now()
    });

    return NextResponse.json({ success: true, jobId });
}

// GET /api/jobs?id=123 (Poll for status/logs)
export async function GET(request: Request) {
    const { searchParams } = new URL(request.url);
    const id = searchParams.get('id');

    if (!id) return NextResponse.json({ error: 'Missing id' }, { status: 400 });

    const job = store.getJob(id);
    if (!job) return NextResponse.json({ error: 'Job not found' }, { status: 404 });

    return NextResponse.json({ job });
}
