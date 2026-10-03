import React, { useState, useEffect } from 'react';
import { ErrorBoundary } from './components/ErrorBoundary';
import { Layout } from './components/Layout';
import { DashboardPage } from './pages/DashboardPage';
import { IncidentsPage } from './pages/IncidentsPage';
import { ResourcesPage } from './pages/ResourcesPage';
import { MapPage } from './pages/MapPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { HealthPage } from './pages/HealthPage';
import { NotFoundPage } from './pages/NotFoundPage';

export function App() {
  const [currentPath, setCurrentPath] = useState(window.location.hash || '#/');

  useEffect(() => {
    const handleHashChange = () => {
      setCurrentPath(window.location.hash || '#/');
    };
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleNavigate = (path) => {
    window.location.hash = path;
    setCurrentPath(path);
  };

  const renderActiveRoute = () => {
    switch (currentPath) {
      case '#/':
      case '':
        return <DashboardPage onNavigate={handleNavigate} />;
      case '#/incidents':
        return <IncidentsPage onNavigate={handleNavigate} />;
      case '#/resources':
        return <ResourcesPage onNavigate={handleNavigate} />;
      case '#/map':
        return <MapPage onNavigate={handleNavigate} />;
      case '#/audit':
        return <AuditLogsPage onNavigate={handleNavigate} />;
      case '#/health':
        return <HealthPage onNavigate={handleNavigate} />;
      default:
        return <NotFoundPage onNavigate={handleNavigate} />;
    }
  };

  return (
    <ErrorBoundary>
      <Layout currentPath={currentPath} onNavigate={handleNavigate}>
        {renderActiveRoute()}
      </Layout>
    </ErrorBoundary>
  );
}

export default App;
