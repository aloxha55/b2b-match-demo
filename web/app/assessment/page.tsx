'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { apiFetch } from '@/lib/api';

const steps = [
  {
    title: 'Governance',
    fields: [
      { id: 'q1', text: 'Leadership roles are clearly defined' },
      { id: 'q2', text: 'Board/advisor support is active' },
      { id: 'q3', text: 'Policies and controls are documented' }
    ]
  },
  {
    title: 'Financials',
    fields: [
      { id: 'q4', text: 'Financial statements are up to date' },
      { id: 'q5', text: 'Cash flow is forecasted regularly' },
      { id: 'q6', text: 'Unit economics are tracked' }
    ]
  },
  {
    title: 'Market & Operations',
    fields: [
      { id: 'q7', text: 'Target market is clearly segmented' },
      { id: 'q8', text: 'Customer acquisition process is repeatable' },
      { id: 'q9', text: 'Operational KPIs are monitored' },
      { id: 'q10', text: 'Core processes are documented' },
      { id: 'q11', text: 'Team capabilities match growth goals' },
      { id: 'q12', text: 'Risk mitigation plans are in place' }
    ]
  }
];

export default function AssessmentPage() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [error, setError] = useState('');

  const current = steps[step];
  const setAnswer = (id: string, value: number) => setAnswers((prev) => ({ ...prev, [id]: value }));

  const onSubmit = async () => {
    setError('');
    try {
      await apiFetch('/assessments', {
        method: 'POST',
        body: JSON.stringify({ answers })
      });
      router.push('/results');
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="card">
      <h2>Investment Readiness Assessment</h2>
      <p className="small">Step {step + 1} of {steps.length}: {current.title}</p>
      {current.fields.map((field) => (
        <div key={field.id}>
          <label>{field.text} (1=low, 5=high)</label>
          <select value={answers[field.id] || 3} onChange={(e) => setAnswer(field.id, Number(e.target.value))}>
            {[1, 2, 3, 4, 5].map((n) => (<option key={n} value={n}>{n}</option>))}
          </select>
        </div>
      ))}
      {error && <p className="error">{error}</p>}
      {step > 0 && <button className="secondary" onClick={() => setStep(step - 1)}>Back</button>}
      {step < steps.length - 1 ? (
        <button onClick={() => setStep(step + 1)}>Next</button>
      ) : (
        <button onClick={onSubmit}>Submit assessment</button>
      )}
    </div>
  );
}
