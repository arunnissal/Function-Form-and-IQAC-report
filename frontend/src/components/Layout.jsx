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
        <header style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
          <div style={{display: 'flex', alignItems: 'center'}}>
            <div className="header-mobile-toggle" onClick={() => setSidebarOpen(true)}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            </div>
            <div>
              <h1 style={{fontSize: '1.5rem', marginBottom: '0.25rem'}}>{title || 'Dashboard'}</h1>
              <p style={{color: 'var(--text-secondary)'}} className="desktop-only">Welcome back, {user?.name || user?.email}</p>
            </div>
          </div>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
            <div style={{textAlign: 'right'}} className="header-profile-text">
              <div style={{fontWeight: '600', fontSize: '0.875rem'}}>{user?.name || user?.email}</div>
              <div style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>{user?.role}</div>
            </div>
            <div style={{width: '40px', height: '40px', borderRadius: '50%', background: 'var(--primary-color)', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold'}}>
              {user?.name?.charAt(0) || user?.email?.charAt(0) || 'U'}
            </div>
          </div>
        </header>
        {children}
      </main>
    </div>
  );
}
