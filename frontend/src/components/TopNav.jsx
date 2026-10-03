import React from 'react';

export function TopNav({ onToggleSidebar, activePath }) {
  const getPageTitle = (path) => {
    switch (path) {
      case '#/incidents': return 'Disaster Incidents Management';
      case '#/resources': return 'Emergency Fleet & Resource Mobilization';
      case '#/map': return 'Spatial GIS Command Map';
      case '#/audit': return 'Tamper-Evident Audit Compliance Trail';
      case '#/health': return 'System Health & Readiness Diagnostics';
      default: return 'Command Center Overview';
    }
  };

  return (
    <header className="topbar" role="banner">
      <div className="topbar-left">
        <button
          className="mobile-toggle-btn"
          onClick={onToggleSidebar}
          aria-label="Toggle navigation menu"
        >
          ☰
        </button>
        <div className="breadcrumb-trail">
          <span>Operations</span>
          <span>/</span>
          <span className="breadcrumb-active">{getPageTitle(activePath)}</span>
        </div>
      </div>

      <div className="topbar-right">
        <div className="system-status-indicator" role="status" aria-label="System operational status">
          <span className="pulse-dot" />
          <span>BACKEND ONLINE</span>
        </div>

        <div className="user-profile-badge">
          <div className="avatar-circle" aria-hidden="true">EC</div>
          <div className="user-info">
            <span className="user-name">Emergency Coordinator</span>
            <span className="user-role">Kathmandu DEOC (Level 3)</span>
          </div>
        </div>
      </div>
    </header>
  );
}
