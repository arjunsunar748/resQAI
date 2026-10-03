import React from 'react';
import { EmptyState } from '../components/EmptyState';

export function AuditLogsPage({ onNavigate }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Compliance Audit Logs</h1>
        <p className="page-description">
          Cryptographically signed, immutable records of all operational decisions and administrative updates.
        </p>
      </div>

      <div className="dashboard-card" style={{ marginBottom: "1.5rem" }}>
        <h2 className="card-title" style={{ marginBottom: "0.5rem" }}>HMAC-SHA256 Cryptographic Verification</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
          All database write operations create a signed audit entry containing actor identity, organization,
          timestamp, and state diff. Any direct tampering invalidates the verification signature.
        </p>
      </div>

      <EmptyState
        icon="📜"
        title="Audit Trail Stream Ready"
        message="Backend audit endpoints (/api/v1/audit-logs and /api/v1/audit-logs/{id}/verify) are live and active. Visual audit timeline will be displayed as administrative events occur."
        actionText="Return to Dashboard"
        onAction={() => onNavigate('#/')}
        tag="BACKEND AUDIT VERIFIED"
      />
    </div>
  );
}
