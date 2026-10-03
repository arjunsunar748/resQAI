import React from 'react';

export function NotFoundPage({ onNavigate }) {
  return (
    <div style={{ textAlign: "center", padding: "4rem 1.5rem" }} role="region" aria-label="Page not found">
      <h1 style={{ fontSize: "3rem", fontWeight: "800", color: "var(--color-emergency)", marginBottom: "0.5rem" }}>
        404
      </h1>
      <h2 style={{ fontSize: "1.4rem", fontWeight: "600", color: "var(--text-primary)", marginBottom: "0.75rem" }}>
        Operational Route Not Found
      </h2>
      <p style={{ color: "var(--text-secondary)", fontSize: "0.95rem", maxWidth: "480px", margin: "0 auto 1.75rem auto" }}>
        The requested tactical dashboard view or disaster resource link does not exist or has been relocated.
      </p>
      <button className="btn-primary" onClick={() => onNavigate('#/')}>
        Return to Command Center
      </button>
    </div>
  );
}
