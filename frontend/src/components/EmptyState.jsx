import React from 'react';

/**
 * Standard EmptyState component adhering to Phase 1 guidelines:
 * Explicitly states zero mock statistics, avoiding fake dashboard data.
 */
export function EmptyState({
  title,
  message,
  icon = "📋",
  actionText,
  onAction,
  tag = "PHASE 1 FOUNDATION"
}) {
  return (
    <div className="empty-state" role="region" aria-label={title}>
      <div className="empty-state-icon" aria-hidden="true">{icon}</div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-message">{message}</p>
      {actionText && onAction && (
        <button className="btn-primary" onClick={onAction} style={{ marginBottom: "1rem" }}>
          {actionText}
        </button>
      )}
      <span className="empty-state-tag">[{tag} — NO FAKE DATA]</span>
    </div>
  );
}
