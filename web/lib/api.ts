const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export function getToken() {
  if (typeof window === 'undefined') return '';
  return localStorage.getItem('token') || '';
}

export function setToken(token: string) {
  localStorage.setItem('token', token);
}

export function clearToken() {
  localStorage.removeItem('token');
}

export async function apiFetch(path: string, options: RequestInit = {}, auth = true) {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(options.headers || {})
  };

  if (auth) {
    const token = getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, { ...options, headers });
  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.detail || 'Request failed');
  }

  return data;
}
