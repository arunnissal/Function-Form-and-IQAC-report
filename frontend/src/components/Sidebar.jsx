import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../AuthContext';

export default function Sidebar({ isOpen }) {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  const isActive = (path) => location.pathname === path ? 'active' : '';

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2 style={{fontSize: '1.25rem', color: 'var(--primary-color)'}}>Dr.NGPIT ERP</h2>
        <p style={{fontSize: '0.75rem', color: 'var(--text-secondary)'}}>Function Requirement</p>
      </div>
      <nav className="sidebar-nav">
        <Link to="/dashboard" className={`sidebar-link ${isActive('/dashboard')}`}>Dashboard</Link>
        
        {user?.role === 'FACULTY' && (
          <Link to="/new-request" className={`sidebar-link ${isActive('/new-request')}`}>New Request</Link>
        )}
        
        {['FACULTY', 'HOD'].includes(user?.role) && (
          <Link to="/my-requests" className={`sidebar-link ${isActive('/my-requests')}`}>
            {user?.role === 'HOD' ? 'Dept Requests' : 'My Requests'}
          </Link>
        )}
        
        <Link to="/calendar" className={`sidebar-link ${isActive('/calendar')}`}>Event Calendar</Link>

        {['HOD', 'DEAN_COMPUTING', 'MANAGEMENT', 'PRINCIPAL'].includes(user?.role) && (
          <Link to="/approvals" className={`sidebar-link ${isActive('/approvals')}`}>Approvals</Link>
        )}



        
        {(user?.is_superuser || user?.role === 'MANAGEMENT') && (
          <>
            <Link to="/manage-halls" className={`sidebar-link ${isActive('/manage-halls')}`}>Seminar Halls</Link>
            <Link to="/manage-departments" className={`sidebar-link ${isActive('/manage-departments')}`}>Departments</Link>
            <Link to="/manage-staff" className={`sidebar-link ${isActive('/manage-staff')}`}>Manage Staff</Link>
          </>
        )}
      </nav>
      <div style={{padding: '1.5rem', borderTop: '1px solid var(--border-color)', marginTop: 'auto'}}>
        <div style={{marginBottom: '0.5rem'}}>
          <Link to="/change-password" style={{display: 'block', textAlign: 'center', fontSize: '0.875rem', color: 'var(--primary-color)', textDecoration: 'none', padding: '0.5rem'}}>
            Change Password
          </Link>
        </div>
        <button onClick={logout} className="btn btn-outline" style={{padding: '0.5rem 1rem', width: '100%'}}>
          Log Out
        </button>
      </div>
    </aside>
  );
}
