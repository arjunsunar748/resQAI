import React from 'react';
import { EmptyState } from '../components/EmptyState';

export function IncidentsPage({ onNavigate }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Disaster Incidents Management</h1>
        <p className="page-description">
          Multi-level incident triage, ground verification, and severity assessment.
        </p>
      </div>

      <EmptyState
        icon="🚨"
        title="Incident Management System Initialized"
        message="Incident models, verification workflows, and GIS coordinate mapping will be deployed in Phase 2. To comply with Principle 8 & 9, no mock government incidents or fake casualties are displayed."
        actionText="Return to Dashboard"
        onAction={() => onNavigate('#/')}
        tag="PHASE 2 WORKFLOW PENDING"
      />
    </div>
  );
}
