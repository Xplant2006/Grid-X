'use client';

import { useAuth } from '@/context/AuthContext';
import styles from './sidebar.module.css';

export default function Sidebar() {
  const { user } = useAuth();

  if (!user) return null;

  return (
    <aside className={styles.sidebar}>
      <div className={styles.userBlock}>
        <div className={styles.email}>{user.email}</div>
        <div className={styles.userId}>User ID: {user.id}</div>
        <div className={styles.role}>Role: {user.role}</div>
      </div>
    </aside>
  );
}
