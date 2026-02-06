'use client';

import { useRouter } from 'next/navigation';
import styles from './login.module.css';

export default function LoginPage() {
    const router = useRouter();

    const handleLogin = (role: 'buyer' | 'seller') => {
        // In a real app, we'd do auth here.
        // For MVP, just redirect.
        if (role === 'buyer') {
            router.push('/dashboard/buyer');
        } else {
            router.push('/dashboard/seller');
        }
    };

    return (
        <div className={styles.container}>
            <h1 className={styles.title}>Welcome to Grid-X</h1>
            <p className={styles.subtitle}>The Decentralized Resource Mesh</p>

            <div className={styles.cardContainer}>
                {/* Buyer Card */}
                <div className={styles.card} onClick={() => handleLogin('buyer')}>
                    <h2> I am a Scientist</h2>
                    <p>I need computing power for my simulations.</p>
                    <button>Enter Marketplace</button>
                </div>

                {/* Seller Card */}
                <div className={styles.card} onClick={() => handleLogin('seller')}>
                    <h2> I am a Provider</h2>
                    <p>I want to rent out my idle CPU/GPU.</p>
                    <button>Start Earning</button>
                </div>
            </div>
        </div>
    );
}
