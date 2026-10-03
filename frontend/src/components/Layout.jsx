import React, { useState } from 'react';
import { Sidebar } from './Sidebar';
import { TopNav } from './TopNav';

export function Layout({ children, currentPath, onNavigate }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="app-container">
      <Sidebar
        currentPath={currentPath}
        onNavigate={onNavigate}
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
      />
      
      <div className="main-wrapper">
        <TopNav
          activePath={currentPath}
          onToggleSidebar={() => setSidebarOpen(!sidebarOpen)}
        />
        
        <main className="content-area" id="main-content">
          {children}
        </main>
      </div>
    </div>
  );
}
