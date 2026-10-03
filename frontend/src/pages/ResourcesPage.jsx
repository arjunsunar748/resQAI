import React from 'react';
import { EmptyState } from '../components/EmptyState';

export function ResourcesPage({ onNavigate }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Emergency Resources & Fleet</h1>
        <p className="page-description">
          Tracking ambulances, rescue boats, fire engines, emergency hospitals, and relief shelters.
        </p>
      </div>

      <EmptyState
        icon="🚑"
        title="Resource Registry Initialized"
        message="Resource tracking and proximity dispatch logic are scheduled for Phase 3. Real equipment and facility inventories will be managed per organization."
        actionText="Return to Dashboard"
        onAction={() => onNavigate('#/')}
        tag="PHASE 3 WORKFLOW PENDING"
      />
    </div>
  );
}
