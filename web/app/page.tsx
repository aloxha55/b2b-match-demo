import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="card">
      <h2>Welcome</h2>
      <p>Get started by creating an account or logging in.</p>
      <Link href="/signup">Sign up</Link> / <Link href="/login">Log in</Link>
    </div>
  );
}
