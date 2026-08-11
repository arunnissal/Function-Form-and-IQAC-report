import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import api from '../api';
import Layout from '../components/Layout';

export default function MyRequests() {
  const [searchParams] = useSearchParams();
  const filterParam = searchParams.get('filter');
  const navigate = useNavigate();
  
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentFilter, setCurrentFilter] = useState(filterParam || 'ALL');

  useEffect(() => {
    const fetchRequests = async () => {
      try {
        const response = await api.get('requests/');
        setRequests(response.data);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchRequests();
  }, []);

  const getStatusBadge = (status) => {
    const badges = {
      'DRAFT': { color: '#64748b', bg: '#f1f5f9', label: 'Draft' },
      'PENDING_HOD': { color: '#ca8a04', bg: '#fef08a', label: 'Pending HOD' },
      'PENDING_DEAN': { color: '#0891b2', bg: '#cffafe', label: 'Pending Dean' },
      'PENDING_MANAGEMENT': { color: '#ca8a04', bg: '#fef08a', label: 'Pending Management' },
      'PENDING_PRINCIPAL': { color: '#ca8a04', bg: '#fef08a', label: 'Pending Principal' },
      'PENDING_FINAL_CONFIRMATION': { color: '#e11d48', bg: '#ffe4e6', label: 'Pending Final Confirmation' },
      'APPROVED': { color: '#15803d', bg: '#dcfce3', label: 'Approved' },
      'REJECTED': { color: '#b91c1c', bg: '#fee2e2', label: 'Rejected' }
    };
    const b = badges[status] || badges['DRAFT'];
    return (
      <span style={{
        padding: '0.25rem 0.75rem',
        borderRadius: '9999px',
        fontSize: '0.75rem',
        fontWeight: '600',
        color: b.color,
        backgroundColor: b.bg
      }}>
        {b.label}
      </span>
    );
  };

  const filteredRequests = requests.filter(req => {
    if (currentFilter === 'ALL') return true;
    if (currentFilter === 'APPROVED') return req.status === 'APPROVED';
    if (currentFilter === 'REJECTED') return req.status === 'REJECTED';
    if (currentFilter === 'PENDING') return !['APPROVED', 'REJECTED', 'DRAFT'].includes(req.status);
    return true;
  });

  const handleDownloadPDF = async (reqId) => {
    try {
      const response = await api.get(`requests/${reqId}/generate_pdf/`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `function_request_${reqId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Failed to download PDF", err);
      alert("Could not generate PDF. Please try again.");
    }
  };

  return (
    <Layout title="My Requests">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
          <h2>Track Requests</h2>
          <select 
            value={currentFilter} 
            onChange={(e) => setCurrentFilter(e.target.value)}
            className="form-input"
            style={{width: '200px'}}
          >
            <option value="ALL">All Requests</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>

          <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>
            {loading ? (
              <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading requests...</div>
            ) : filteredRequests.length === 0 ? (
              <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
                <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📄</div>
                <h3 style={{color: 'var(--text-primary)'}}>No requests found</h3>
                <p style={{color: 'var(--text-secondary)'}}>You haven't submitted any function requests yet.</p>
              </div>
            ) : (
              <table style={{width: '100%', borderCollapse: 'collapse'}}>
                <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                  <tr>
                    <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>ID</th>
                    <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Function Name</th>
                    <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Venue</th>
                    <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Start Date</th>
                    <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Status</th>
                    <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRequests.map(req => (
                    <tr key={req.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                      <td style={{padding: '1rem', color: 'var(--text-secondary)'}}>#{req.id}</td>
                      <td style={{padding: '1rem', fontWeight: '500'}}>{req.function_name}</td>
                      <td style={{padding: '1rem'}}>{req.venue_name || 'N/A'}</td>
                      <td style={{padding: '1rem'}}>{req.start_date || 'N/A'}</td>
                      <td style={{padding: '1rem'}}>{getStatusBadge(req.status)}</td>
                      <td style={{padding: '1rem', display: 'flex', gap: '0.5rem', justifyContent: 'center', alignItems: 'center'}}>
                        <button onClick={() => navigate(`/request/${req.id}`)} className="btn btn-outline" style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem', borderColor: '#3b82f6', color: '#3b82f6'}}>
                          View
                        </button>
                        <button onClick={() => handleDownloadPDF(req.id)} className="btn btn-outline" style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem', borderColor: '#64748b', color: '#64748b'}}>
                          📄 PDF
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>
    </Layout>
  );
}
