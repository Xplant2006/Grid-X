'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import styles from '../login/login.module.css'; // reuse login styles
import { API_BASE } from '@/lib/api';
import { useAuth } from '@/context/AuthContext';

export default function RegistrationPage() {
  const router = useRouter();
  const { setUser } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'buyer' | 'seller'>('buyer');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, role }),
      });

      if (!res.ok) {
        const msg = await res.text();
        setError(msg || 'Registration failed');
        return;
      }

      const user = await res.json();

      // Persist user
      localStorage.setItem('user', JSON.stringify(user));
      setUser(user);

      // Redirect based on role
      if (user.role === 'buyer') {
        router.push('/dashboard/buyer');
      } else {
        router.push('/dashboard/seller');
      }
    } catch (err) {
      console.error(err);
      setError('Cannot reach backend');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Create your Grid-X Account</h1>
      <p className={styles.subtitle}>Join the decentralized compute mesh</p>

      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.fields}>
          <div className={styles.field}>
            <label>Email</label>
            <input
              type="email"
              placeholder="user@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className={styles.field}>
            <label>Password</label>
            <input
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <div className={styles.field}>
            <label>Role</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value as 'buyer' | 'seller')}
            >
              <option value="buyer">Scientist (Buyer)</option>
              <option value="seller">Provider (Seller)</option>
            </select>
          </div>
        </div>

        {error && <p className={styles.error}>{error}</p>}

        <button type="submit" className={styles.primaryBtn} disabled={loading}>
          {loading ? 'Creating account…' : 'Register'}
        </button>
      </form>
    </div>
  );
}
