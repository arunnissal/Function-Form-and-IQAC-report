import React, { useState, useEffect, useContext } from 'react';
import api from '../api';
import { useNavigate, useParams } from 'react-router-dom';
import Layout from '../components/Layout';
import { AuthContext } from '../AuthContext';
import StatusBadge from '../components/StatusBadge';
import Timeline from '../components/Timeline';
import ApprovalButtons from '../components/ApprovalButtons';

export default function ViewRequest() {
  const navigate = useNavigate();
  const { id } = useParams();
  const { user } = useContext(AuthContext);
  
  const [requestData, setRequestData] = useState(null);
  const [halls, setHalls] = useState([]);
  const [selectedVenue, setSelectedVenue] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [reqRes, hallsRes] = await Promise.all([
          api.get(`requests/${id}/`),
          api.get('halls/')
        ]);
        setRequestData(reqRes.data);
        setHalls(hallsRes.data);
        if (reqRes.data.venue) {
          setSelectedVenue(reqRes.data.venue.toString());
        }
      } catch (err) {
        console.error("Failed to load request data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchInitialData();
  }, [id]);

  const handleApprove = async (remarks) => {
    if (status === 'PENDING_MANAGEMENT' && user?.role === 'MANAGEMENT' && !selectedVenue) {
      alert("Please select a seminar hall to allocate.");
      return;
    }
    setSubmitting(true);
    try {
      if (status === 'PENDING_MANAGEMENT' && user?.role === 'MANAGEMENT') {
        // Provisonally save venue assignment
        await api.patch(`requests/${id}/`, { venue: selectedVenue });
      }
      
      if (status === 'PENDING_FINAL_CONFIRMATION') {
        await api.post(`requests/${id}/confirm_booking/`, { remarks });
      } else {
        await api.post(`requests/${id}/approve/`, { remarks });
      }
      navigate(-1);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to approve request.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReject = async (remarks) => {
    setSubmitting(true);
    try {
      await api.post(`requests/${id}/reject/`, { remarks });
      navigate(-1);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to reject request.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleReturn = async (remarks) => {
    setSubmitting(true);
    try {
      await api.post(`requests/${id}/return_for_correction/`, { remarks });
      navigate(-1);
    } catch (err) {
      alert(err.response?.data?.detail || "Failed to return request.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleForceCancel = async () => {
    if (window.confirm("EMERGENCY: Are you sure you want to forcefully cancel this event? This cannot be undone.")) {
      setSubmitting(true);
      try {
        await api.post(`requests/${id}/cancel_request/`, { remarks: 'Cancelled by higher authority' });
        navigate(-1);
      } catch (err) {
        alert("Failed to cancel event.");
        console.error(err);
      } finally {
        setSubmitting(false);
      }
    }
  };

  const handleDownloadPDF = async () => {
    try {
      const response = await api.get(`requests/${id}/generate_pdf/`, {
        responseType: 'blob'
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `function_request_${id}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error("Failed to download PDF", err);
      alert("Could not generate PDF. Please try again.");
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
    student_transport_required, student_transport_details,
    guest_house, refreshment, power_camera, memento, transport, status, approval_logs
  } = requestData;

  // Determine if the current user can approve/reject this request
  const canApprove = (
    (user?.role === 'HOD' && status === 'PENDING_HOD') ||
    (user?.role === 'DEAN_COMPUTING' && status === 'PENDING_DEAN') ||
    ((user?.role === 'MANAGEMENT' || user?.is_superuser) && status === 'PENDING_MANAGEMENT') ||
    (user?.role === 'PRINCIPAL' && status === 'PENDING_PRINCIPAL') ||
    ((user?.role === 'MANAGEMENT' || user?.is_superuser) && status === 'PENDING_FINAL_CONFIRMATION')
  );

  // Determine if the user can edit this request based on active review stage
  let canEdit = false;
  if (user?.is_superuser) {
    canEdit = true;
  } else if (user?.role === 'FACULTY' && (status === 'DRAFT' || status === 'RETURNED_FOR_CORRECTION')) {
    canEdit = true;
  } else if (user?.role === 'HOD' && status === 'PENDING_HOD') {
    canEdit = true;
  } else if (user?.role === 'DEAN_COMPUTING' && status === 'PENDING_DEAN') {
    canEdit = true;
  } else if (user?.role === 'MANAGEMENT' && status === 'PENDING_MANAGEMENT') {
    canEdit = true;
  }

  return (
    <Layout title={`Request #${id} Details`}>
      <div style={{ maxWidth: '900px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: 'var(--shadow-md)'}}>
        
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem', borderBottom: '2px solid var(--border-color)', paddingBottom: '1rem'}}>
          <h2 style={{margin: 0, color: 'var(--primary-color)'}}>{function_name}</h2>
          <div style={{display: 'flex', alignItems: 'center', gap: '1rem'}}>
            <button 
              onClick={handleDownloadPDF} 
              className="btn btn-outline" 
              style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem', display: 'flex', alignItems: 'center', gap: '0.25rem'}}
            >
              📄 Download PDF
            </button>
            <StatusBadge status={status} />
          </div>
        </div>

        {status === 'RETURNED_FOR_CORRECTION' && (
          <div style={{
            padding: '1.25rem',
            background: '#fffbeb',
            color: '#b45309',
            borderRadius: '6px',
            border: '1px solid #fef3c7',
            marginBottom: '1.5rem',
            fontSize: '0.9rem'
          }}>
            <h4 style={{ margin: '0 0 0.5rem 0', display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#b45309' }}>
              ⚠️ Returned for Correction
            </h4>
            {(() => {
              const returnedLog = approval_logs && [...approval_logs].reverse().find(l => l.status === 'RETURNED_FOR_CORRECTION');
              if (returnedLog) {
                return (
                  <div>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong>Returned By:</strong> {returnedLog.approver_name} ({returnedLog.stage === 'MANAGEMENT' ? 'Management (AO)' : returnedLog.stage})</p>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong>Date & Time:</strong> {new Date(returnedLog.timestamp).toLocaleString()}</p>
                    <p style={{ margin: '0 0 0.25rem 0' }}><strong>Remarks:</strong> &ldquo;{returnedLog.remarks}&rdquo;</p>
                    <p style={{ margin: 0 }}><strong>Current Workflow Stage:</strong> Faculty Action (Revisions Needed)</p>
                  </div>
                );
              }
              return <p style={{ margin: 0 }}>Remarks/Comments: No detailed correction log found.</p>;
            })()}
          </div>
        )}

        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
          {/* Basic Details */}
          <div>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Basic Details</h4>
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.9rem', lineHeight: '1.8' }}>
              <li><strong>Type:</strong> {function_type}</li>
              <li><strong>Dates:</strong> {start_date} to {end_date || start_date} ({number_of_days} days)</li>
              <li><strong>Timing:</strong> {time_from} - {time_to}</li>
              <li><strong>Venue:</strong> {halls.find(h => h.id.toString() === venue?.toString())?.hall_name || 'None Assigned'}</li>
              <li><strong>Target Audience:</strong> {number_of_students} Students ({class_name || 'N/A'})</li>
              {student_transport_required && <li><strong>Student Transport:</strong> Required ({student_transport_details || 'No details provided'})</li>}
              <li><strong>Organizer:</strong> {organizer_name} ({organizer_contact})</li>
              <li><strong>Chief Guest:</strong> {chief_guest_name} - {chief_guest_designation} ({chief_guest_organization || 'N/A'})</li>
            </ul>
          </div>

          {/* Resource Details */}
          <div>
            <h4 style={{ color: 'var(--text-secondary)', marginBottom: '1rem' }}>Resource Requirements</h4>
            <ul style={{ listStyleType: 'none', padding: 0, margin: 0, fontSize: '0.9rem', lineHeight: '1.8' }}>
              {guest_house?.required && <li><strong>Guest House:</strong> {guest_house.number_of_persons} persons ({guest_house.room_type || 'Standard'}) from {guest_house.from_date} to {guest_house.to_date}</li>}
              
              {(refreshment?.tea_required || refreshment?.coffee_required || refreshment?.snacks_required || refreshment?.student_tea_required || refreshment?.student_coffee_required || refreshment?.student_snacks_required) && 
                <li>
                  <strong>Refreshments:</strong>
                  { (refreshment.tea_required || refreshment.coffee_required || refreshment.snacks_required) && ` Guest: ${[refreshment.tea_required && 'Tea', refreshment.coffee_required && 'Coffee', refreshment.snacks_required && 'Snacks'].filter(Boolean).join('/')} @ ${refreshment.required_time || 'N/A'}` }
                  { (refreshment.student_tea_required || refreshment.student_coffee_required || refreshment.student_snacks_required) && ` | Student: ${[refreshment.student_tea_required && 'Tea', refreshment.student_coffee_required && 'Coffee', refreshment.student_snacks_required && 'Snacks'].filter(Boolean).join('/')} @ ${refreshment.student_required_time || 'N/A'}` }
                </li>
              }
              
              {(refreshment?.tiffin_count > 0 || refreshment?.normal_lunch_count > 0 || refreshment?.veg_lunch_count > 0 || refreshment?.non_veg_lunch_count > 0) &&
                <li>
                  <strong>Meals:</strong> Tiffin ({refreshment.tiffin_count}), Normal Lunch ({refreshment.normal_lunch_count}), Veg ({refreshment.veg_lunch_count}), Non-Veg ({refreshment.non_veg_lunch_count}) 
                  {refreshment.lunch_required_time && ` @ ${refreshment.lunch_required_time}`} (Payment: {refreshment.payment_through})
                </li>
              }
              
              {power_camera?.mic_required && 
                <li><strong>Audio/Visual:</strong> Mic: {power_camera.mic_type} (Qty: {power_camera.number_of_mics}), A/C: {power_camera.ac_required ? 'Yes' : 'No'}, Projector: {power_camera.projector_required ? 'Yes' : 'No'}, Laptop: {power_camera.laptop_required ? 'Yes' : 'No'}</li>
              }
              {memento?.required && 
                <li><strong>Memento:</strong> {memento.quantity} items (Rs. {memento.honorarium_worth})</li>
              }
              {transport?.required && 
                <li><strong>Guest Transport:</strong> Pickup: {transport.pickup_location} @ {transport.pickup_time} | Contact: {transport.pickup_person_name} ({transport.pickup_person_contact})</li>
              }
              {!guest_house?.required && !refreshment?.tea_required && !refreshment?.student_tea_required && !power_camera?.mic_required && !memento?.required && !transport?.required && (
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

        {/* Approval Decision Section with Hall Allocation for Management */}
        {canApprove && (
          <div>
            {user?.role === 'MANAGEMENT' && status === 'PENDING_MANAGEMENT' && (
              <div style={{ background: '#f0fdf4', padding: '1.5rem', borderRadius: '8px', border: '1px solid #bbf7d0', marginBottom: '1.5rem' }}>
                <h4 style={{ color: '#166534', margin: '0 0 1rem 0' }}>Assign Seminar Hall (Provisional)</h4>
                <div style={{ marginBottom: '1rem' }}>
                  <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 'bold' }}>Seminar Hall *</label>
                  <select 
                    className="form-input" 
                    value={selectedVenue} 
                    onChange={(e) => setSelectedVenue(e.target.value)}
                    required
                    style={{ background: '#fff' }}
                  >
                    <option value="">-- Select Hall --</option>
                    {halls.map(h => (
                      <option key={h.id} value={h.id}>{h.hall_name} (Cap: {h.capacity})</option>
                    ))}
                  </select>
                </div>
              </div>
            )}

            <ApprovalButtons 
              onApprove={handleApprove} 
              onReject={handleReject} 
              onReturn={handleReturn} 
              isSubmitting={submitting} 
              approveLabel={status === 'PENDING_FINAL_CONFIRMATION' ? '✅ Final Confirm Booking' : '✅ Approve'}
            />
          </div>
        )}

        {/* Vertical Audit Trail Timeline */}
        <div style={{ marginTop: '3rem', borderTop: '2px solid var(--border-color)', paddingTop: '2rem' }}>
          <h3 style={{ color: 'var(--primary-color)', marginBottom: '1.5rem' }}>Approval Workflow Timeline</h3>
          <Timeline logs={approval_logs} />
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '2rem', paddingTop: '1.5rem', borderTop: '1px solid var(--border-color)' }}>
          <button onClick={() => navigate(-1)} className="btn btn-outline">
            &larr; Go Back
          </button>
          
          <div style={{display: 'flex', gap: '1rem'}}>
            {(['MANAGEMENT', 'PRINCIPAL'].includes(user?.role) || user?.is_superuser) && status !== 'REJECTED' && status !== 'CANCELLED' && (
              <button onClick={handleForceCancel} className="btn btn-outline" style={{borderColor: '#ef4444', color: '#ef4444'}} disabled={submitting}>
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
