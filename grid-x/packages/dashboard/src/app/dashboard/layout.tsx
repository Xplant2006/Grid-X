'use client';

import Sidebar from '@/components/Sidebar';
import styles from './dashboardLayout.module.css';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className={styles.wrapper}>
      <Sidebar />
      <main className={styles.content}>
        {children}
      </main>
    </div>
  );
}
