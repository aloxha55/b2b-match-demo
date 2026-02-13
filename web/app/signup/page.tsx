'use client';

import { FormEvent, useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch, setToken } from '@/lib/api';

export default function SignupPage() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const data = await apiFetch('/auth/signup', {
        method: 'POST',
        body: JSON.stringify({ email, password })
      }, false);
      setToken(data.access_token);
      router.push('/profile');
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="card">
      <h2>Create account</h2>
      <form onSubmit={onSubmit}>
        <label>Email</label>
        <input value={email} onChange={(e) => setEmail(e.target.value)} type="email" required />
        <label>Password</label>
        <input value={password} onChange={(e) => setPassword(e.target.value)} type="password" minLength={8} required />
        {error && <p className="error">{error}</p>}
        <button type="submit">Sign up</button>
      </form>
    </div>
  );
}
