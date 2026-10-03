import React, { useEffect, useState } from 'react';
import { LoadingState } from '../components/LoadingState';

export function HealthPage() {
  const [healthData, setHealthData] = useState(null);
  const [readinessData, setReadinessData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true);
        const [hRes, rRes] = await Promise.all([
          fetch('http://localhost:8000/health').then(r => r.json()).catch(() => ({ status: 'OFFLINE' })),
          fetch('http://localhost:8000/health/ready').then(r => r.json()).catch(() => ({ status: 'NOT READY' })),
        ]);
        setHealthData(hRes);
        setReadinessData(rRes);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchHealth();
  }, []);

  if (loading) return <LoadingState message="Probing backend health and readiness probes..." />;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">System Diagnostics & Health Probes</h1>
        <p className="page-description">
          Real-time container health, dependency readiness, and API latency checks.
        </p>
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Backend API Liveness</h2>
            <span className="badge-tag info">{healthData?.status || "CHECKING"}</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
            Endpoint: <code style={{ color: "var(--color-accent)" }}>GET /health</code>
          </p>
          <pre style={{ backgroundColor: "var(--bg-primary)", padding: "0.75rem", borderRadius: "var(--radius-sm)", fontSize: "0.75rem", color: "var(--text-secondary)", overflowX: "auto" }}>
            {JSON.stringify(healthData, null, 2)}
          </pre>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Dependency Readiness</h2>
            <span className="badge-tag info">{readinessData?.status || "CHECKING"}</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>
            Endpoint: <code style={{ color: "var(--color-accent)" }}>GET /health/ready</code>
          </p>
          <pre style={{ backgroundColor: "var(--bg-primary)", padding: "0.75rem", borderRadius: "var(--radius-sm)", fontSize: "0.75rem", color: "var(--text-secondary)", overflowX: "auto" }}>
            {JSON.stringify(readinessData, null, 2)}
          </pre>
        </div>
      </div>
    </div>
  );
}
