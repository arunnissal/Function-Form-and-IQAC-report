import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import Layout from '../components/Layout';

export default function ApprovalQueue() {
  const navigate = useNavigate();
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRequests();
  }, []);

  const fetchRequests = async () => {
    try {
      const response = await api.get('requests/queue/');
      setRequests(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Approval Queue">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>
          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading queue...</div>
          ) : requests.length === 0 ? (
            <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
              <div style={{fontSize: '3rem', marginBottom: '1rem'}}>✅</div>
              <h3 style={{color: 'var(--text-primary)'}}>All Caught Up!</h3>
              <p style={{color: 'var(--text-secondary)'}}>There are no requests waiting for your approval.</p>
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>ID</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Function Name</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Department</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Date</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {requests.map(req => (
                  <tr key={req.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '1rem', color: 'var(--text-secondary)'}}>#{req.id}</td>
                    <td style={{padding: '1rem', fontWeight: '500'}}>{req.function_name}</td>
                    <td style={{padding: '1rem'}}>{req.department_code || 'N/A'}</td>
                    <td style={{padding: '1rem'}}>{req.start_date || 'N/A'}</td>
                    <td style={{padding: '1rem', textAlign: 'center'}}>
                      <button onClick={() => navigate(`/request/${req.id}`)} className="btn btn-primary" style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem'}}>
                        Review Request
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
