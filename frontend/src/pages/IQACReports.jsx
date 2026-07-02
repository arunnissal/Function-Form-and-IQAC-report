import React, { useState, useEffect, useContext } from 'react';
import { useSearchParams } from 'react-router-dom';
import api, { baseURL } from '../api';
import Layout from '../components/Layout';
import { AuthContext } from '../AuthContext';

export default function IQACReports() {
  const { user } = useContext(AuthContext);
  const [searchParams] = useSearchParams();
  const filterParam = searchParams.get('filter');
  
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedReq, setSelectedReq] = useState(null);
  const [formData, setFormData] = useState({});
  const [guests, setGuests] = useState([]);
  const [files, setFiles] = useState({});
  const [currentFilter, setCurrentFilter] = useState(filterParam || 'APPROVED');
  const [reportLoading, setReportLoading] = useState(false);

  useEffect(() => {
    fetchRequests();
  }, []);

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

  const filteredRequests = requests.filter(req => {
    if (currentFilter === 'ALL') return true;
    if (currentFilter === 'PENDING') return !['APPROVED', 'REJECTED', 'DRAFT'].includes(req.status);
    return req.status === currentFilter;
  });

  const openReportForm = async (req) => {
    setSelectedReq(req);
    setReportLoading(true);
    setFiles({});
    
    // Auto-fill defaults
    const defaultData = {
      dept_ref_no: '',
      funding_agency: 'NA',
      objective: req.function_name + ' - ' + (req.type_of_training || 'Event'),
      alumni_contribution: 'NA',
      budget_proposed: '-',
      budget_actual: '-',
      participants_internal: req.number_of_students || 0,
      participants_external: 0,
      outcome: ''
    };
    
    const defaultGuests = [{
      name: req.chief_guest_name || '',
      designation: req.chief_guest_designation || '',
      organization_address: req.chief_guest_organization || '',
      mobile: '', email: '', topic: ''
    }];

    try {
      const res = await api.get(`iqac/${req.id}/`);
      setFormData({
        dept_ref_no: res.data.dept_ref_no || defaultData.dept_ref_no,
        funding_agency: res.data.funding_agency || defaultData.funding_agency,
        objective: res.data.objective || defaultData.objective,
        alumni_contribution: res.data.alumni_contribution || defaultData.alumni_contribution,
        budget_proposed: res.data.budget_proposed || defaultData.budget_proposed,
        budget_actual: res.data.budget_actual || defaultData.budget_actual,
        participants_internal: res.data.participants_internal || defaultData.participants_internal,
        participants_external: res.data.participants_external || defaultData.participants_external,
        outcome: res.data.outcome || defaultData.outcome,
      });
      if (res.data.guests && res.data.guests.length > 0) {
        setGuests(res.data.guests);
      } else {
        setGuests(defaultGuests);
      }
    } catch (e) {
      // If 404, just use defaults
      setFormData(defaultData);
      setGuests(defaultGuests);
    } finally {
      setReportLoading(false);
    }
  };

  const handleFileChange = (e, field) => {
    setFiles(prev => ({ ...prev, [field]: e.target.files[0] }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const data = new FormData();
    Object.keys(formData).forEach(key => {
      data.append(key, formData[key]);
    });
    data.append('guests', JSON.stringify(guests));
    
    Object.keys(files).forEach(key => {
      if (files[key]) {
        data.append(key, files[key]);
      }
    });

    try {
      await api.post(`iqac/${selectedReq.id}/`, data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert('IQAC Report Details Saved and Uploaded Successfully!');
      setSelectedReq(null);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || 'Failed to save report.');
    }
  };

  const downloadPdf = async (reqId) => {
    try {
      // Use standard fetch to get the blob with auth header
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${baseURL}iqac/${reqId}/generate-pdf/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to download PDF');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `IQAC_Report_${reqId}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (e) {
      console.error(e);
      alert('Failed to generate PDF. Make sure report is filled.');
    }
  };

  return (
    <Layout title="Request Reports & Directory">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem'}}>
          <div>
            <h2 style={{margin: 0}}>Request Reports</h2>
            <p style={{margin: 0, fontSize: '0.875rem', color: 'var(--text-secondary)'}}>View requests and generate IQAC Documentation</p>
          </div>
          <select 
            value={currentFilter} 
            onChange={(e) => setCurrentFilter(e.target.value)}
            className="form-input"
            style={{width: '200px'}}
          >
            <option value="ALL">All Requests</option>
            <option value="PENDING">Pending</option>
            <option value="APPROVED">Approved (IQAC)</option>
            <option value="REJECTED">Rejected</option>
          </select>
        </div>

        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>

          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading events...</div>
          ) : filteredRequests.length === 0 ? (
            <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
              <div style={{fontSize: '3rem', marginBottom: '1rem'}}>📊</div>
              <h3 style={{color: 'var(--text-primary)'}}>No Reports Found</h3>
              <p style={{color: 'var(--text-secondary)'}}>There are no requests matching the selected filter.</p>
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Event Name</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Date</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredRequests.map(req => (
                  <tr key={req.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '1rem', fontWeight: '500'}}>{req.function_name}</td>
                    <td style={{padding: '1rem'}}>{req.start_date || 'N/A'}</td>
                    <td style={{padding: '1rem', textAlign: 'center'}}>
                      {req.status === 'APPROVED' ? (
                        <div style={{display: 'flex', gap: '0.5rem', justifyContent: 'center'}}>
                          {(user?.role === 'FACULTY' || user?.role === 'HOD') && (
                            <button onClick={() => openReportForm(req)} className="btn btn-primary" style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem'}}>Fill Report</button>
                          )}
                          {['ADMIN', 'PRINCIPAL', 'MANAGEMENT', 'HOD', 'FACULTY'].includes(user?.role) && (
                            <button onClick={() => downloadPdf(req.id)} className="btn btn-outline" style={{padding: '0.4rem 0.8rem', fontSize: '0.875rem'}}>Download PDF</button>
                          )}
                        </div>
                      ) : (
                        <span style={{color: 'var(--text-secondary)', fontSize: '0.875rem'}}>N/A</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {selectedReq && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{background: 'white', padding: '2rem', borderRadius: '8px', width: '800px', maxWidth: '90%', maxHeight: '90vh', overflowY: 'auto'}}>
            <h3 style={{marginTop: 0, color: 'var(--primary-color)'}}>Generate IQAC Report: {selectedReq.function_name}</h3>
            
            {reportLoading ? (
              <div style={{padding: '2rem', textAlign: 'center'}}>Loading existing report data...</div>
            ) : (
            <form onSubmit={handleSubmit}>
              <h5 style={{borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem'}}>Event Details</h5>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '1.5rem'}}>
                <div>
                  <label className="form-label">Dept. Ref. No.</label>
                  <input type="text" className="form-input" value={formData.dept_ref_no} onChange={e => setFormData({...formData, dept_ref_no: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Funding Agency (Int / Ext)</label>
                  <input type="text" className="form-input" value={formData.funding_agency} onChange={e => setFormData({...formData, funding_agency: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Alumni Contribution</label>
                  <input type="text" className="form-input" value={formData.alumni_contribution} onChange={e => setFormData({...formData, alumni_contribution: e.target.value})} />
                </div>
                <div style={{gridColumn: '1 / -1'}}>
                  <label className="form-label">Objective of the event</label>
                  <textarea className="form-input" rows="2" value={formData.objective} onChange={e => setFormData({...formData, objective: e.target.value})}></textarea>
                </div>
              </div>

              <h5 style={{borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem'}}>Budget & Participants</h5>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem'}}>
                <div>
                  <label className="form-label">Proposed Budget</label>
                  <input type="text" className="form-input" value={formData.budget_proposed} onChange={e => setFormData({...formData, budget_proposed: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Actual Budget</label>
                  <input type="text" className="form-input" value={formData.budget_actual} onChange={e => setFormData({...formData, budget_actual: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">Internal Participants</label>
                  <input type="text" className="form-input" value={formData.participants_internal} onChange={e => setFormData({...formData, participants_internal: e.target.value})} />
                </div>
                <div>
                  <label className="form-label">External Participants</label>
                  <input type="text" className="form-input" value={formData.participants_external} onChange={e => setFormData({...formData, participants_external: e.target.value})} />
                </div>
              </div>

              <h5 style={{borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem'}}>Guest Details</h5>
              {guests.map((guest, index) => (
                <div key={index} style={{display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1rem', marginBottom: '1.5rem', background: '#f8fafc', padding: '1rem', borderRadius: '8px'}}>
                  <div>
                    <label className="form-label">Guest Name</label>
                    <input type="text" className="form-input" value={guest.name} onChange={e => { const newG = [...guests]; newG[index].name = e.target.value; setGuests(newG); }} />
                  </div>
                  <div>
                    <label className="form-label">Designation</label>
                    <input type="text" className="form-input" value={guest.designation} onChange={e => { const newG = [...guests]; newG[index].designation = e.target.value; setGuests(newG); }} />
                  </div>
                  <div>
                    <label className="form-label">Organization Address</label>
                    <input type="text" className="form-input" value={guest.organization_address} onChange={e => { const newG = [...guests]; newG[index].organization_address = e.target.value; setGuests(newG); }} />
                  </div>
                  <div>
                    <label className="form-label">Mobile</label>
                    <input type="text" className="form-input" value={guest.mobile} onChange={e => { const newG = [...guests]; newG[index].mobile = e.target.value; setGuests(newG); }} />
                  </div>
                  <div>
                    <label className="form-label">Email</label>
                    <input type="text" className="form-input" value={guest.email} onChange={e => { const newG = [...guests]; newG[index].email = e.target.value; setGuests(newG); }} />
                  </div>
                  <div>
                    <label className="form-label">Topic</label>
                    <input type="text" className="form-input" value={guest.topic} onChange={e => { const newG = [...guests]; newG[index].topic = e.target.value; setGuests(newG); }} />
                  </div>
                </div>
              ))}

              <h5 style={{borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem'}}>Outcome & Photos</h5>
              <div style={{marginBottom: '1.5rem'}}>
                <label className="form-label">Outcome of the event</label>
                <textarea className="form-input" rows="3" required value={formData.outcome} onChange={e => setFormData({...formData, outcome: e.target.value})}></textarea>
              </div>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
                <div>
                  <label className="form-label">Picture 1 (Image)</label>
                  <input type="file" className="form-input" accept="image/*" onChange={e => handleFileChange(e, 'photo_1')} />
                </div>
                <div>
                  <label className="form-label">Picture 2 (Image)</label>
                  <input type="file" className="form-input" accept="image/*" onChange={e => handleFileChange(e, 'photo_2')} />
                </div>
              </div>

              <h5 style={{borderBottom: '1px solid #e2e8f0', paddingBottom: '0.5rem', marginBottom: '1rem'}}>Enclosures (Images/PDFs)</h5>
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', marginBottom: '2rem'}}>
                <div>
                  <label className="form-label">Brochure</label>
                  <input type="file" className="form-input" onChange={e => handleFileChange(e, 'brochure')} />
                </div>
                <div>
                  <label className="form-label">Certificate</label>
                  <input type="file" className="form-input" onChange={e => handleFileChange(e, 'certificate')} />
                </div>
                <div>
                  <label className="form-label">Attendance Sheet</label>
                  <input type="file" className="form-input" onChange={e => handleFileChange(e, 'attendance_sheet')} />
                </div>
                <div>
                  <label className="form-label">Feedback Report</label>
                  <input type="file" className="form-input" onChange={e => handleFileChange(e, 'feedback_report')} />
                </div>
              </div>

              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
                <button type="button" onClick={() => setSelectedReq(null)} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary">Save Report Details</button>
              </div>
            </form>
            )}
          </div>
        </div>
      )}
    </Layout>
  );
}
