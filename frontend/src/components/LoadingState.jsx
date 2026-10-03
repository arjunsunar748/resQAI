import React from 'react';

/**
 * Accessible loading indicator for asynchronous data transitions.
 */
export function LoadingState({ message = "Synchronizing operational feed..." }) {
  return (
    <div className="loading-container" role="status" aria-live="polite">
      <div className="spinner" aria-hidden="true" />
      <p style={{ color: "var(--text-secondary)", fontSize: "0.9rem" }}>{message}</p>
      <span className="sr-only" style={{ display: "none" }}>Loading content</span>
    </div>
  );
}
