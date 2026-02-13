'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';

type Assessment = {
  total_score: number;
  section_scores: Record<string, number>;
  recommendations: string[];
  created_at: string;
};

export default function ResultsPage() {
  const [data, setData] = useState<Assessment | null>(null);
  const [error, setError] = useState('');

  useEffect(() => {
    apiFetch('/assessments/latest')
      .then(setData)
      .catch((err) => setError((err as Error).message));
  }, []);

  if (error) {
    return <div className="card"><p className="error">{error}</p></div>;
  }

  if (!data) {
    return <div className="card"><p>Loading results...</p></div>;
  }

  return (
    <div className="card">
      <h2>Assessment Results</h2>
      <h3>Total score: {data.total_score}/100</h3>
      <div className="grid two">
        {Object.entries(data.section_scores).map(([section, score]) => (
          <div key={section} className="card">
            <strong>{section}</strong>
            <p>{score}/100</p>
          </div>
        ))}
      </div>
      <h3>Recommendations</h3>
      <ul>
        {data.recommendations.map((recommendation) => <li key={recommendation}>{recommendation}</li>)}
      </ul>
    </div>
  );
}
