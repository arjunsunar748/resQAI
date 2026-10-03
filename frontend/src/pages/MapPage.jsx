import React from 'react';
import { EmptyState } from '../components/EmptyState';

export function MapPage({ onNavigate }) {
  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Spatial GIS Command Map</h1>
        <p className="page-description">
          Geographic situational awareness, administrative boundaries, and incident clusters.
        </p>
      </div>

      <div style={{ height: "420px", display: "flex", alignItems: "center", justifyContent: "center", backgroundColor: "var(--bg-card)", border: "1px solid var(--border-color)", borderRadius: "var(--radius-md)" }}>
        <EmptyState
          icon="🗺️"
          title="Leaflet & PostGIS Map Layer Container"
          message="Provider-agnostic map integration (defaulting to OpenStreetMap / PostGIS) will be mounted in Phase 2 with Nepal provincial and district boundary overlays."
          actionText="Return to Dashboard"
          onAction={() => onNavigate('#/')}
          tag="GIS INTEGRATION READY"
        />
      </div>
    </div>
  );
}
