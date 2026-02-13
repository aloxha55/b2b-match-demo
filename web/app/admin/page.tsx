'use client';

import { useEffect, useState } from 'react';
import { apiFetch } from '@/lib/api';

type Company = { id: number; name: string; sector: string; country: string; size: string; owner_email: string };
type Assessment = { company_id: number; company_name: string; owner_email: string; total_score: number; created_at: string };

export default function AdminPage() {
  const [companies, setCompanies] = useState<Company[]>([]);
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [error, setError] = useState('');

  useEffect(() => {
    Promise.all([apiFetch('/admin/companies'), apiFetch('/admin/assessments')])
      .then(([companiesRes, assessmentsRes]) => {
        setCompanies(companiesRes);
        setAssessments(assessmentsRes);
      })
      .catch((err) => setError((err as Error).message));
  }, []);

  return (
    <div className="card">
      <h2>Admin Dashboard</h2>
      {error && <p className="error">{error}</p>}
      <h3>Companies</h3>
      <div className="small">
        {companies.map((company) => (
          <p key={company.id}>{company.name} ({company.country}, {company.sector}) - {company.owner_email}</p>
        ))}
      </div>
      <h3>Assessments</h3>
      <div className="small">
        {assessments.map((assessment) => (
          <p key={`${assessment.company_id}-${assessment.created_at}`}>
            {assessment.company_name} - {assessment.total_score}/100 ({new Date(assessment.created_at).toLocaleString()})
          </p>
        ))}
      </div>
    </div>
  );
}
