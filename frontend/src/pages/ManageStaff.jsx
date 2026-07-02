import React, { useState, useEffect } from 'react';
import api from '../api';
import Layout from '../components/Layout';

export default function ManageStaff() {
  const [users, setUsers] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    email: '',
    position: 'Staff',
    department: ''
  });
  const [filterDept, setFilterDept] = useState('');
  const [showBulkModal, setShowBulkModal] = useState(false);
  const [fileToUpload, setFileToUpload] = useState(null);
  const fileInputRef = React.useRef(null);

  useEffect(() => {
    fetchUsers();
    fetchDepartments();
  }, []);

  const fetchUsers = async () => {
    try {
      const response = await api.get('users/');
      setUsers(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDepartments = async () => {
    try {
      const response = await api.get('departments/');
      setDepartments(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const openModal = (userObj = null) => {
    if (userObj) {
      setEditId(userObj.id);
      // The old system mapped position text 'Staff' -> 'FACULTY' in backend
      const posMap = { 'FACULTY': 'Staff', 'HOD': 'HOD' };
      setFormData({ 
        email: userObj.email, 
        position: posMap[userObj.role] || 'Staff', 
        department: '' // Requires backend to return dept for editing, simplified for demo
      });
    } else {
      setEditId(null);
      setFormData({ email: '', position: 'Staff', department: '' });
    }
    setShowModal(true);
  };

  const closeModal = () => setShowModal(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editId) {
        await api.put(`users/${editId}/`, formData);
      } else {
        await api.post('users/', formData);
      }
      closeModal();
      fetchUsers();
    } catch (err) {
      console.error(err);
      alert('Error saving staff member.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to completely remove this user?")) {
      try {
        await api.delete(`users/${id}/`);
        fetchUsers();
      } catch (err) {
        console.error(err);
        alert('Error deleting user.');
      }
    }
  };

  const handleResetPassword = async (id) => {
    if (window.confirm("Are you sure you want to reset this user's password to their default?")) {
      try {
        const response = await api.post(`users/${id}/reset_password/`);
        alert(response.data.detail);
      } catch (err) {
        console.error(err);
        alert('Error resetting password.');
      }
    }
  };

  const handleBulkUpload = async (e) => {
    e.preventDefault();
    if (!fileToUpload) return;
    
    const data = new FormData();
    data.append('excel_file', fileToUpload);
    
    try {
      const response = await api.post('users/bulk_add/', data, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert(`Bulk upload complete! ${response.data.detail}`);
      fetchUsers();
      setShowBulkModal(false);
      setFileToUpload(null);
      if (fileInputRef.current) fileInputRef.current.value = '';
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || 'Failed to bulk upload staff');
    }
  };

  const getRoleBadge = (role) => {
    const badges = {
      'FACULTY': { color: '#4f46e5', bg: '#e0e7ff' },
      'HOD': { color: '#0891b2', bg: '#cffafe' },
      'MANAGEMENT': { color: '#9333ea', bg: '#f3e8ff' },
      'PRINCIPAL': { color: '#b91c1c', bg: '#fee2e2' },
      'ADMIN': { color: '#111827', bg: '#f3f4f6' }
    };
    const b = badges[role] || badges['FACULTY'];
    return (
      <span style={{
        padding: '0.25rem 0.5rem',
        borderRadius: '4px',
        fontSize: '0.75rem',
        fontWeight: 'bold',
        color: b.color,
        backgroundColor: b.bg
      }}>
        {role}
      </span>
    );
  };

  return (
    <Layout title="Manage Staff Directory">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>
          <div style={{padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <h3 style={{margin: 0}}>Staff & Roles</h3>
            <div style={{display: 'flex', gap: '1rem'}}>
              <button onClick={() => setShowBulkModal(true)} className="btn btn-outline" style={{padding: '0.5rem 1rem', fontSize: '0.875rem', borderColor: '#10b981', color: '#10b981'}}>
                <span style={{marginRight: '0.5rem'}}>x</span> Bulk Add
              </button>
              <button onClick={() => openModal()} className="btn btn-primary" style={{padding: '0.5rem 1rem', fontSize: '0.875rem'}}>+ Add Staff</button>
            </div>
          </div>
          
          <div style={{padding: '1rem', borderBottom: '1px solid var(--border-color)', background: '#f8fafc'}}>
            <label style={{fontSize: '0.875rem', fontWeight: 'bold', color: 'var(--text-secondary)', marginRight: '0.5rem'}}>▼ Filter by Department:</label>
            <select 
              value={filterDept} 
              onChange={(e) => setFilterDept(e.target.value)} 
              style={{padding: '0.4rem', borderRadius: '4px', border: '1px solid var(--border-color)', minWidth: '200px'}}
            >
              <option value="">All Departments</option>
              <option value="N/A">N/A (No Department)</option>
              {departments.map(d => (
                <option key={d.id} value={d.department_name}>{d.department_name}</option>
              ))}
            </select>
          </div>

          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading staff directory...</div>
          ) : users.length === 0 ? (
            <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
              <p style={{color: 'var(--text-secondary)'}}>No staff found.</p>
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Mail ID</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Role</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Department</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Status</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users
                  .filter(u => filterDept === '' || (filterDept === 'N/A' && !u.department) || u.department === filterDept)
                  .map(user => (
                  <tr key={user.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '1rem'}}>
                      <div style={{fontWeight: '500'}}>{user.email}</div>
                    </td>
                    <td style={{padding: '1rem'}}>{getRoleBadge(user.role)}</td>
                    <td style={{padding: '1rem', color: 'var(--text-secondary)'}}>{user.department || 'N/A'}</td>
                    <td style={{padding: '1rem', textAlign: 'center'}}>
                      <span style={{background: user.is_active ? '#10b981' : '#ef4444', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold'}}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td style={{padding: '1rem'}}>
                      <div style={{display: 'flex', justifyContent: 'center', gap: '0.5rem', flexWrap: 'nowrap'}}>
                        <button onClick={() => openModal(user)} className="btn btn-outline" style={{padding: '0.4rem', fontSize: '1rem', color: '#3b82f6', borderColor: '#bfdbfe'}} title="Edit Staff">
                          ✏️
                        </button>
                        <button onClick={() => handleDelete(user.id)} className="btn btn-outline" style={{padding: '0.4rem', fontSize: '1rem', color: '#ef4444', borderColor: '#fecaca'}} title="Delete Staff">
                          🗑️
                        </button>
                        <button onClick={() => handleResetPassword(user.id)} className="btn btn-outline" style={{padding: '0.4rem', fontSize: '1rem', color: '#f59e0b', borderColor: '#fde68a'}} title="Reset Password">
                          🔑
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>

      {showModal && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{background: 'white', padding: '2rem', borderRadius: '8px', width: '500px', maxWidth: '90%'}}>
            <h3 style={{marginTop: 0}}>{editId ? 'Edit Staff Role' : 'Add New Staff Member'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">College Email ID *</label>
                <input type="email" className="form-input" name="email" value={formData.email} onChange={handleInputChange} required disabled={!!editId} placeholder="e.g. name@drngpit.ac.in" />
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Position *</label>
                <select className="form-input" name="position" value={formData.position} onChange={handleInputChange} required>
                  <option value="Staff">Faculty / Staff</option>
                  <option value="HOD">Head of Department (HOD)</option>
                </select>
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Department *</label>
                <select className="form-input" name="department" value={formData.department} onChange={handleInputChange} required>
                  <option value="">Select Department...</option>
                  {departments.map(d => (
                    <option key={d.id} value={d.id}>{d.department_code} - {d.department_name}</option>
                  ))}
                </select>
              </div>
              
              <div style={{background: '#f8fafc', padding: '1rem', borderRadius: '4px', fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem'}}>
                <strong>Note:</strong> Password will automatically be set to the first part of their email address (before the @).
              </div>

              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
                <button type="button" onClick={closeModal} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary">{editId ? 'Update Role' : 'Create Account'}</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showBulkModal && (
        <div style={{position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000}}>
          <div style={{background: 'white', padding: '2rem', borderRadius: '8px', width: '600px', maxWidth: '90%'}}>
            <h3 style={{marginTop: 0}}>Bulk Import Staff</h3>
            
            <div style={{background: '#f8fafc', padding: '1rem', borderRadius: '4px', marginBottom: '1.5rem', border: '1px solid var(--border-color)'}}>
              <h4 style={{margin: '0 0 0.5rem 0', color: 'var(--primary-color)'}}>Required Excel Format</h4>
              <p style={{fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1rem'}}>
                Please upload an Excel file (`.xlsx` or `.xls`) containing the following exact column headers in the first row:
              </p>
              <table style={{width: '100%', fontSize: '0.875rem', borderCollapse: 'collapse', marginBottom: '1rem'}}>
                <thead>
                  <tr style={{background: '#e2e8f0'}}>
                    <th style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Full Name</th>
                    <th style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Email</th>
                    <th style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Department Code</th>
                    <th style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Position</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Dr. John Doe</td>
                    <td style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>johndoe@drngpit.ac.in</td>
                    <td style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>CSE</td>
                    <td style={{padding: '0.5rem', border: '1px solid #cbd5e1'}}>Staff / HOD</td>
                  </tr>
                </tbody>
              </table>
              <p style={{fontSize: '0.75rem', color: 'var(--text-secondary)', margin: 0}}>
                * Default passwords will be set to the email prefix (e.g. `johndoe`).
              </p>
            </div>

            <form onSubmit={handleBulkUpload}>
              <div style={{marginBottom: '2rem'}}>
                <label className="form-label">Upload File</label>
                <input 
                  type="file" 
                  ref={fileInputRef} 
                  onChange={(e) => setFileToUpload(e.target.files[0])} 
                  accept=".xlsx, .xls" 
                  className="form-input"
                  required
                />
              </div>

              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem'}}>
                <button type="button" onClick={() => {setShowBulkModal(false); setFileToUpload(null);}} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={!fileToUpload} style={{background: '#10b981', borderColor: '#10b981'}}>Upload & Import</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
