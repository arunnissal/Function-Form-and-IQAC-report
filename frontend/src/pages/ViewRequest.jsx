import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { AuthContext } from '../AuthContext';

export default function ViewRequest() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  
  const [requestData, setRequestData] = useState(null);
  const [halls, setHalls] = useState([]);
  const [remarks, setRemarks] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [reqRes, hallsRes] = await Promise.all([
          api.get(`requests/${id}/`),
          api.get('halls/')
        ]);
        setRequestData(reqRes.data);
        setHalls(hallsRes.data);
      } catch (err) {
        console.error("Failed to load request data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, [id]);

  const handleAction = async (action) => {
    try {
      await api.post(`requests/${id}/${action}/`, { remarks });
      navigate(-1); // Go back to where they came from
    } catch (err) {
      alert(`Failed to ${action} request.`);
      console.error(err);
    }
  };

  const handleForceCancel = async () => {
    if (window.confirm("EMERGENCY: Are you sure you want to forcefully cancel this event? This cannot be undone.")) {
      try {
        await api.post(`requests/${id}/cancel_request/`, { remarks: 'Cancelled by higher authority' });
        navigate(-1);
      } catch (err) {
        alert("Failed to cancel event.");
        console.error(err);
      }
    }
  };

  if (loading) {
    return (
      <Layout title={`View Request #${id}`}>
        <div style={{padding: '4rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading request details...</div>
      </Layout>
    );
  }

  if (!requestData) {
    return (
      <Layout title="Request Not Found">
        <div style={{padding: '4rem', textAlign: 'center', color: '#ef4444'}}>Failed to load request.</div>
      </Layout>
    );
  }

  const {
    function_name, function_type, start_date, end_date, number_of_days, time_from, time_to, venue,
    number_of_students, class_name, organizer_name, organizer_contact, chief_guest_name, chief_guest_designation,
    guest_house, refreshment, power_camera, memento, transport, status
  } = requestData;

  const getStatusBadge = (s) => {
    const badges = {
      'DRAFT': { color: '#64748b', bg: '#f1f5f9', label: 'Draft' },
      'PENDING_HOD': { color: '#d97706', bg: '#fef3c7', label: 'Pending HOD' },
      'PENDING_DEAN': { color: '#0891b2', bg: '#cffafe', label: 'Pending Dean' },
      'PENDING_MANAGEMENT': { color: '#2563eb', bg: '#dbeafe', label: 'Pending Management' },
      'PENDING_PRINCIPAL': { color: '#7c3aed', bg: '#f3e8ff', label: 'Pending Principal' },
      'APPROVED': { color: '#15803d', bg: '#dcfce3', label: 'Approved' },
      'REJECTED': { color: '#b91c1c', bg: '#fee2e2', label: 'Rejected' }
    };
    const b = badges[s] || badges['DRAFT'];
    return <span style={{ padding: '0.3rem 0.8rem', borderRadius: '9999px', fontSize: '0.75rem', fontWeight: 'bold', color: b.color, backgroundColor: b.bg }}>{b.label}</span>;
  };

  // Determine if the current user can approve/reject this request
  const canApprove = (
    (user?.role === 'HOD' && status === 'PENDING_HOD') ||
    (user?.role === 'DEAN_COMPUTING' && status === 'PENDING_DEAN') ||
    ((user?.role === 'MANAGEMENT' || user?.is_superuser) && status === 'PENDING_MANAGEMENT') ||
    (user?.role === 'PRINCIPAL' && status === 'PENDING_PRINCIPAL')
  );

  // Determine if the user can edit this request
  let canEdit = false;
  if (user?.is_superuser) {
    canEdit = true;
  } else if (status === 'DRAFT' || status === 'REJECTED') {
    if (['FACULTY', 'HOD'].includes(user?.role)) canEdit = true;
  } else if (user?.role === 'HOD' && status === 'PENDING_HOD') {
    canEdit = true;
  } else if (['MANAGEMENT', 'PRINCIPAL'].includes(user?.role)) {
    if (['PENDING_MANAGEMENT', 'PENDING_PRINCIPAL', 'APPROVED'].includes(status)) canEdit = true;
  }

  return (
    <Layout title={`Request #${id} Details`}>
      <div style={{ maxWidth: '900px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: 'var(--shadow-md)'}}>
        
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '2px solid var(--border-color)', paddingBottom: '1rem'}}>
          <h2 style={{margin: 0, color: 'var(--primary-color)'}}>{function_name}</h2>
          <div>{getStatusBadge(status)}</div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
          {/* Basic Details */}
          <div>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Basic Details</h4>
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.9rem', lineHeight: '1.8' }}>
              <li><strong>Type:</strong> {function_type}</li>
              <li><strong>Dates:</strong> {start_date} to {end_date || start_date} ({number_of_days} days)</li>
              <li><strong>Timing:</strong> {time_from} - {time_to}</li>
              <li><strong>Venue:</strong> {halls.find(h => h.id.toString() === venue?.toString())?.hall_name || 'None'}</li>
              <li><strong>Target Audience:</strong> {number_of_students} Students ({class_name || 'N/A'})</li>
              <li><strong>Organizer:</strong> {organizer_name} ({organizer_contact})</li>
              <li><strong>Chief Guest:</strong> {chief_guest_name} - {chief_guest_designation}</li>
            </ul>
          </div>

          {/* Resource Details */}
          <div>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Resource Requirements</h4>
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.9rem', lineHeight: '1.8' }}>
              {guest_house?.required && <li><strong>Guest House:</strong> {guest_house.room_type} Room</li>}
              {(refreshment?.tea_required || refreshment?.coffee_required) && 
                <li><strong>Refreshments:</strong> VIP: {refreshment.vip_count}, Staff: {refreshment.staff_count}, Students: {refreshment.student_count}</li>
              }
              {power_camera?.mic_required && 
                <li><strong>Audio/Visual:</strong> Mics (Cord: {power_camera.cordless_mics}, Collar: {power_camera.collar_mics}), A/C: {power_camera.ac_required ? 'Yes' : 'No'}</li>
              }
              {memento?.required && 
                <li><strong>Memento:</strong> {memento.quantity} items (Rs. {memento.honorarium_worth})</li>
              }
              {transport?.required && 
                <li><strong>Transport:</strong> Pickup: {transport.pickup_location} @ {transport.pickup_time}</li>
              }
              {!guest_house?.required && !refreshment?.tea_required && !power_camera?.mic_required && !memento?.required && !transport?.required && (
                <li style={{color: 'var(--text-secondary)'}}>No additional resources required.</li>
              )}
            </ul>
          </div>
        </div>

        {/* Extended Details */}
        {memento?.reception_items && (
          <div style={{marginBottom: '2rem', background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border-color)'}}>
            <h4 style={{ color: 'var(--text-secondary)', margin: '0 0 1rem 0' }}>Reception & Event Setup</h4>
            <div style={{fontSize: '0.9rem', lineHeight: '1.8'}}>
              <p style={{margin: '0 0 0.5rem 0'}}><strong>Reception Items:</strong> {memento.reception_items}</p>
              <p style={{margin: 0}}><strong>Seating:</strong> Dias ({memento.dias_seats}), Audience ({memento.audience_seats}), Table Cloths ({memento.table_cloths})</p>
            </div>
          </div>
        )}

        {/* Approval / Rejection Action Area */}
        {canApprove && (
          <div style={{marginTop: '2rem', background: '#f0fdf4', padding: '1.5rem', borderRadius: '8px', border: '1px solid #bbf7d0'}}>
            <h4 style={{ color: '#166534', margin: '0 0 1rem 0' }}>Approval Action Required</h4>
            <div style={{marginBottom: '1rem'}}>
              <label style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 'bold', color: '#166534'}}>Remarks (Optional)</label>
              <textarea 
                className="form-input" 
                rows="3" 
                value={remarks} 
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Leave a comment or reason for rejection..."
                style={{borderColor: '#bbf7d0'}}
              />
            </div>
            <div style={{display: 'flex', gap: '1rem', flexWrap: 'wrap'}}>
              <button onClick={() => handleAction('approve')} className="btn" style={{background: '#10b981', color: 'white', flex: 1}}>✅ Approve Request</button>
              <button onClick={() => handleAction('reject')} className="btn btn-outline" style={{borderColor: '#ef4444', color: '#ef4444', flex: 1}}>❌ Reject Request</button>
            </div>
          </div>
        )}

        {/* Management direct rejection capability at any stage */}
        {!canApprove && user?.role === 'MANAGEMENT' && ['PENDING_HOD', 'PENDING_DEAN', 'PENDING_PRINCIPAL'].includes(status) && (
          <div style={{marginTop: '2rem', background: '#fff1f2', padding: '1.5rem', borderRadius: '8px', border: '1px solid #fecdd3'}}>
            <h4 style={{ color: '#9f1239', margin: '0 0 1rem 0' }}>Administrative Reject Option</h4>
            <div style={{marginBottom: '1rem'}}>
              <label style={{display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 'bold', color: '#9f1239'}}>Rejection Remarks (Required)</label>
              <textarea 
                className="form-input" 
                rows="3" 
                value={remarks} 
                onChange={(e) => setRemarks(e.target.value)}
                placeholder="Please enter the reason for rejection..."
                style={{borderColor: '#fecdd3'}}
              />
            </div>
            <button onClick={() => {
              if(!remarks.trim()){
                alert("Please provide rejection remarks.");
                return;
              }
              handleAction('reject');
            }} className="btn" style={{background: '#e11d48', color: 'white', width: '100%'}}>
              ❌ Reject Request
            </button>
          </div>
        )}

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <button onClick={() => navigate(-1)} className="btn btn-outline">
            &larr; Go Back
          </button>
          
          <div style={{display: 'flex', gap: '1rem'}}>
            {(['MANAGEMENT', 'PRINCIPAL'].includes(user?.role) || user?.is_superuser) && status !== 'REJECTED' && (
              <button onClick={handleForceCancel} className="btn btn-outline" style={{borderColor: '#ef4444', color: '#ef4444'}}>
                ⚠️ Force Cancel Event
              </button>
            )}

            {canEdit && (
              <button onClick={() => navigate(`/edit-request/${id}`)} className="btn btn-outline" style={{borderColor: 'var(--primary-color)', color: 'var(--primary-color)'}}>
                ✏️ Edit Requirements
              </button>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}
