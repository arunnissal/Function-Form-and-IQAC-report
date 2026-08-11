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
        <h2 className="sidebar-title">Dr. NGPIT</h2>
        <p className="sidebar-subtitle">Function Booking System</p>
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
      <div className="sidebar-footer">
        <div style={{marginBottom: '0.5rem'}}>
          <Link to="/change-password" className="sidebar-footer-link">
            Change Password
          </Link>
        </div>
        <button onClick={logout} className="btn btn-sidebar-logout">
          Log Out
        </button>
      </div>
    </aside>
  );
}
