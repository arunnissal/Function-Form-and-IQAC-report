import React, { useContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthContext } from '../AuthContext';
import Layout from '../components/Layout';
import api from '../api';

export default function Dashboard() {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();
  const [stats, setStats] = useState({ pending: 0, approved: 0, rejected: 0 });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('requests/');
        const requests = response.data;
        
        let pending = 0;
        let approved = 0;
        let rejected = 0;

        requests.forEach(req => {
          if (req.status === 'APPROVED') {
            approved++;
          } else if (req.status === 'REJECTED') {
            rejected++;
          } else if (req.status !== 'DRAFT') {
            if (user?.role === 'MANAGEMENT' || user?.is_superuser) {
              if (req.status === 'PENDING_MANAGEMENT' || req.status === 'PENDING_FINAL_CONFIRMATION') pending++;
            } else if (user?.role === 'PRINCIPAL') {
              if (req.status === 'PENDING_PRINCIPAL') pending++;
            } else if (user?.role === 'DEAN_COMPUTING') {
              const computingDepts = ['CSE', 'CSE(CS)', 'AIDS', 'IT', 'CSBS'];
              const deptCode = (req.department_code || '').toUpperCase();
              if (req.status === 'PENDING_DEAN' && computingDepts.includes(deptCode)) {
                pending++;
              }
            } else if (user?.role === 'HOD') {
              if (req.status === 'PENDING_HOD') pending++;
            } else {
              // Faculty sees all active workflow requests
              pending++;
            }
          } else if (req.status === 'CANCELLED') {
            rejected++;
          }
        });

        setStats({ pending, approved, rejected });
      } catch (err) {
        console.error('Failed to fetch dashboard stats', err);
      }
    };

    fetchStats();
  }, []);

  const handleCardClick = (filterStatus) => {
    if (['FACULTY', 'HOD'].includes(user?.role)) {
      navigate(`/my-requests?filter=${filterStatus}`);
    } else {
      if (filterStatus === 'PENDING') {
        navigate('/approvals');
      } else {
        navigate(`/my-requests?filter=${filterStatus}`);
      }
    }
  };

  return (
    <Layout title="Dashboard">
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" onClick={() => handleCardClick('PENDING')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} onMouseOver={e => e.currentTarget.style.transform = 'scale(1.02)'} onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'rgba(59, 130, 246, 0.1)', color: 'var(--primary-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '1rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect><line x1="16" y1="2" x2="16" y2="6"></line><line x1="8" y1="2" x2="8" y2="6"></line><line x1="3" y1="10" x2="21" y2="10"></line></svg>
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}>Pending Requests</h3>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: '700', margin: 0, color: 'var(--text-primary)' }}>{stats.pending}</p>
        </div>

        <div className="card" onClick={() => handleCardClick('APPROVED')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} onMouseOver={e => e.currentTarget.style.transform = 'scale(1.02)'} onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'rgba(16, 185, 129, 0.1)', color: '#10b981', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '1rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}>Approved</h3>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: '700', margin: 0, color: 'var(--text-primary)' }}>{stats.approved}</p>
        </div>

        <div className="card" onClick={() => handleCardClick('REJECTED')} style={{ cursor: 'pointer', transition: 'transform 0.2s' }} onMouseOver={e => e.currentTarget.style.transform = 'scale(1.02)'} onMouseOut={e => e.currentTarget.style.transform = 'scale(1)'}>
          <div style={{ display: 'flex', alignItems: 'center', marginBottom: '1rem' }}>
            <div style={{ width: '40px', height: '40px', borderRadius: '8px', background: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', display: 'flex', alignItems: 'center', justifyContent: 'center', marginRight: '1rem' }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
            </div>
            <h3 style={{ margin: 0, fontSize: '1rem', color: 'var(--text-secondary)' }}>Rejected</h3>
          </div>
          <p style={{ fontSize: '2rem', fontWeight: '700', margin: 0, color: 'var(--text-primary)' }}>{stats.rejected}</p>
        </div>
      </div>
      
      <div className="card" style={{ padding: '0', overflow: 'hidden' }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.25rem', margin: 0 }}>Recent Activity</h2>
        </div>
        <div style={{ padding: '1.5rem', textAlign: 'center', color: 'var(--text-secondary)' }}>
          System is running smoothly.
        </div>
      </div>
    </Layout>
  );
}
