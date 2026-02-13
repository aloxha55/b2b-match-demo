import './globals.css';
import Link from 'next/link';
import type { ReactNode } from 'react';

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="container">
          <div className="card">
            <h1>Investment Readiness Platform</h1>
            <p className="small">Assess your business and prepare for investor conversations.</p>
            <nav className="small">
              <Link href="/">Home</Link> | <Link href="/profile">Company Profile</Link> | <Link href="/assessment">Assessment</Link> | <Link href="/results">Results</Link> | <Link href="/admin">Admin</Link>
            </nav>
          </div>
          {children}
        </div>
      </body>
    </html>
  );
}
