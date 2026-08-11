import React, { useContext, useState, useEffect } from 'react';
import { AuthContext } from '../AuthContext';
import { useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';

export default function Layout({ children, title }) {
  const { user } = useContext(AuthContext);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  useEffect(() => {
    setSidebarOpen(false);
  }, [location]);

  return (
    <div className="app-container">
      {sidebarOpen && <div className="sidebar-overlay" onClick={() => setSidebarOpen(false)}></div>}
      <Sidebar isOpen={sidebarOpen} />
      <main className="main-content">
        <header className="layout-header">
          <div className="layout-header-left">
            <div className="header-mobile-toggle" onClick={() => setSidebarOpen(true)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            </div>
            <div>
              <h1 className="layout-title">{title || 'Dashboard'}</h1>
              <p className="layout-subtitle desktop-only">Welcome back, {user?.name || user?.email}</p>
            </div>
          </div>
          <div className="layout-header-right">
            <div className="profile-info header-profile-text">
              <div className="profile-name">{user?.name || user?.email}</div>
              <div className="profile-role">{user?.role}</div>
            </div>
            <div className="profile-avatar">
              {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
