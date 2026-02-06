'use client';

import styles from './seller.module.css';

export default function SellerDashboard() {
    const command = 'npx grid-x-agent --connect https://grid.demo --token 12345';

    return (
        <div className={styles.dashboard}>
            <header className={styles.header}>
                <h1>Provider Dashboard</h1>
                <div className={styles.user}>
                    User: @CryptoMiner99
                </div>
            </header>

            <main className={styles.main}>
                {/* Connection Instructions */}
                <section className={styles.connectSection}>
                    <h2>Connect your Device</h2>
                    <p>This browser cannot run Docker directly. Run this command in your terminal to join the mesh:</p>
                    <div className={styles.codeBlock}>
                        <code>{command}</code>
                        <button onClick={() => navigator.clipboard.writeText(command)}>Copy</button>
                    </div>
                </section>

                {/* Live Stats */}
                <section className={styles.statsGrid}>
                    <div className={styles.statCard}>
                        <h3>Status</h3>
                        <span className={styles.active}>Listening</span>
                    </div>
                    <div className={styles.statCard}>
                        <h3>Jobs Completed</h3>
                        <span>142</span>
                    </div>
                    <div className={styles.statCard}>
                        <h3>Credits Earned</h3>
                        <span>$42.50</span>
                    </div>
                </section>

                {/* Recent Activity */}
                <section className={styles.activity}>
                    <h2>Recent Activity</h2>
                    <div className={styles.list}>
                        <div className={styles.item}>
                            <span>Job #1293</span>
                            <span>Computed SHA-256</span>
                            <span className={styles.earn}>+$0.10</span>
                        </div>
                        <div className={styles.item}>
                            <span>Job #1292</span>
                            <span>Rendered Frame</span>
                            <span className={styles.earn}>+$0.50</span>
                        </div>
                    </div>
                </section>
            </main>
        </div>
    );
}
