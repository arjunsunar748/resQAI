import React from 'react';

export function Sidebar({ currentPath, onNavigate, isOpen, onClose }) {
  const navItems = [
    { path: '#/', label: 'Operational Dashboard', icon: '📊' },
    { path: '#/incidents', label: 'Disaster Incidents', icon: '🚨' },
    { path: '#/resources', label: 'Emergency Resources', icon: '🚑' },
    { path: '#/map', label: 'GIS Live Map', icon: '🗺️' },
    { path: '#/audit', label: 'Compliance Audit Logs', icon: '📜' },
    { path: '#/health', label: 'System Diagnostics', icon: '⚡' },
  ];

  const handleLinkClick = (path) => {
    onNavigate(path);
    if (onClose) onClose();
  };

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`} aria-label="Main Navigation">
      <div className="sidebar-header">
        <span className="logo-badge" aria-label="ResQ Agent Emergency Badge">RESQ</span>
        <div>
          <div className="brand-title">RESQ AGENT</div>
          <div className="brand-subtitle">Emergency Operations</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const isActive = currentPath === item.path || (item.path === '#/' && currentPath === '');
          return (
            <button
              key={item.path}
              className={`nav-link ${isActive ? 'active' : ''}`}
              onClick={() => handleLinkClick(item.path)}
              aria-current={isActive ? 'page' : undefined}
            >
              <span aria-hidden="true">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div>Platform: RESQ AGENT v1.0.0</div>
        <div>Jurisdiction: Nepal (Federal)</div>
      </div>
    </aside>
  );
}
