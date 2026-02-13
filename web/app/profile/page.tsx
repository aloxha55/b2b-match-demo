'use client';

import { FormEvent, useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';

export default function ProfilePage() {
  const [form, setForm] = useState({ name: '', sector: '', country: '', size: '' });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    apiFetch('/company/profile')
      .then((data) => setForm({ name: data.name, sector: data.sector, country: data.country, size: data.size }))
      .catch(() => null);
  }, []);

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setMessage('');
    try {
      await apiFetch('/company/profile', {
        method: 'PUT',
        body: JSON.stringify(form)
      });
      setMessage('Company profile saved.');
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="card">
      <h2>Company Profile</h2>
      <form onSubmit={onSubmit}>
        <label>Company name</label>
        <input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} required />
        <label>Sector</label>
        <input value={form.sector} onChange={(e) => setForm({ ...form, sector: e.target.value })} required />
        <label>Country</label>
        <input value={form.country} onChange={(e) => setForm({ ...form, country: e.target.value })} required />
        <label>Company size</label>
        <select value={form.size} onChange={(e) => setForm({ ...form, size: e.target.value })} required>
          <option value="">Select size</option>
          <option value="1-10">1-10</option>
          <option value="11-50">11-50</option>
          <option value="51-200">51-200</option>
          <option value="200+">200+</option>
        </select>
        {error && <p className="error">{error}</p>}
        {message && <p className="success">{message}</p>}
        <button type="submit">Save Profile</button>
      </form>
    </div>
  );
}
