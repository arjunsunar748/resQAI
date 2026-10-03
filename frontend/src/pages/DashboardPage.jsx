import React from 'react';
import { EmptyState } from '../components/EmptyState';

export function DashboardPage({ onNavigate }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Operational Command Center</h1>
        <p className="page-description">
          Disaster response coordination platform — Phase 1 Architectural Foundation.
        </p>
      </div>

      <div className="dashboard-grid">
        {/* Core Architecture Status */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Backend Architecture</h2>
            <span className="badge-tag info">Phase 1 Active</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            FastAPI modular service layer connected with PostgreSQL + PostGIS and Redis caching.
          </p>
          <div style={{ marginTop: "auto" }}>
            <button className="btn-primary" onClick={() => onNavigate('#/health')}>
              Inspect Service Diagnostics
            </button>
          </div>
        </div>

        {/* Security & Multi-Org RBAC */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">Security & Governance</h2>
            <span className="badge-tag info">Configured</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Fine-grained RBAC with 9 roles, 31 permissions, rotating JWT tokens, and tamper-evident HMAC audit trail.
          </p>
          <div style={{ marginTop: "auto" }}>
            <button className="btn-primary" onClick={() => onNavigate('#/audit')}>
              View Audit Specifications
            </button>
          </div>
        </div>

        {/* Human-in-the-Loop AI Boundary */}
        <div className="dashboard-card">
          <div className="card-header">
            <h2 className="card-title">AI Decision Policy</h2>
            <span className="badge-tag emergency">Governance Rule</span>
          </div>
          <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem", marginBottom: "1rem" }}>
            Strict Principle 1 & 3: AI never autonomously dispatches emergency teams. Consequential actions require human approval.
          </p>
        </div>
      </div>

      {/* Clearly Marked Empty States — No Fake Statistics */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.5rem" }}>
        <EmptyState
          icon="🚨"
          title="No Active Disaster Incidents"
          message="Live incident intake, citizen reporting, and spatial triage workflows will be activated in Phase 2. Zero mock data is generated."
          actionText="View Incident Specs"
          onAction={() => onNavigate('#/incidents')}
          tag="PHASE 1 EMPTY STATE"
        />

        <EmptyState
          icon="🚑"
          title="No Dispatched Emergency Units"
          message="Ambulance fleets, rescue teams, and emergency shelters will be coordinated under Phase 3 resource mobilization."
          actionText="View Resource Specs"
          onAction={() => onNavigate('#/resources')}
          tag="PHASE 1 EMPTY STATE"
        />
      </div>
    </div>
  );
}
