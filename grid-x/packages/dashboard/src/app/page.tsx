import Link from 'next/link';
import styles from './page.module.css';

export default function Home() {
  return (
    <div className={styles.container}>
      <header className={styles.header}>
        <div className={styles.logo}>Grid-X</div>
        <nav>
          <Link href="/login" className={styles.navLink}>Login</Link>
          <Link href="https://github.com/Xplant2006/Grid-X" className={styles.navLink}>GitHub</Link>
        </nav>
      </header>

      <main className={styles.main}>
        <h1 className={styles.title}>
          Turn Idle Silicon into <br />
          <span className={styles.highlight}>Scientific Discovery</span>
        </h1>
        <p className={styles.subtitle}>
          The decentralized resource mesh.
          Rent your CPU/GPU to scientists or access massive compute power instantly.
        </p>

        <div className={styles.ctaGroup}>
          <Link href="/login" className={`${styles.btn} ${styles.primary}`}>
            Get Started
          </Link>
          <Link href="/docs" className={`${styles.btn} ${styles.secondary}`}>
            Documentation
          </Link>
        </div>
      </main>

      <footer className={styles.footer}>
        Demo
      </footer>
    </div>
  );
}
