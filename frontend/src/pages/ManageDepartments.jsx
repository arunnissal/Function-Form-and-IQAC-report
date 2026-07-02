import React, { useState, useEffect } from 'react';
import api from '../api';
import Layout from '../components/Layout';

export default function ManageDepartments() {
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    department_code: '',
    department_name: ''
  });

  useEffect(() => {
    fetchDepartments();
  }, []);

  const fetchDepartments = async () => {
    try {
      const response = await api.get('departments/');
      setDepartments(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const openModal = (dept = null) => {
    if (dept) {
      setEditId(dept.id);
      setFormData({ department_code: dept.department_code, department_name: dept.department_name });
    } else {
      setEditId(null);
      setFormData({ department_code: '', department_name: '' });
    }
    setShowModal(true);
  };

  const closeModal = () => setShowModal(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editId) {
        await api.put(`departments/${editId}/`, formData);
      } else {
        await api.post('departments/', formData);
      }
      closeModal();
      fetchDepartments();
    } catch (err) {
      console.error(err);
      alert('Error saving department.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this department?")) {
      try {
        await api.delete(`departments/${id}/`);
        fetchDepartments();
      } catch (err) {
        console.error(err);
        alert('Error deleting department. It might be in use.');
      }
    }
  };

  return (
    <Layout title="Manage Departments">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>
          <div style={{padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <h3 style={{margin: 0}}>Departments Directory</h3>
            <button onClick={() => openModal()} className="btn btn-primary" style={{padding: '0.5rem 1rem', fontSize: '0.875rem'}}>+ Add Department</button>
          </div>
          
          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading departments...</div>
          ) : departments.length === 0 ? (
            <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
              <p style={{color: 'var(--text-secondary)'}}>No departments found.</p>
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Code</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Department Name</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {departments.map(dept => (
                  <tr key={dept.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '1rem', fontWeight: '600', color: 'var(--primary-color)'}}>{dept.department_code}</td>
                    <td style={{padding: '1rem'}}>{dept.department_name}</td>
                    <td style={{padding: '1rem', textAlign: 'center'}}>
                      <button onClick={() => openModal(dept)} className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.75rem', marginRight: '0.5rem'}}>Edit</button>
                      <button onClick={() => handleDelete(dept.id)} className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.75rem', color: '#ef4444', borderColor: '#ef4444'}}>Delete</button>
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
            <h3 style={{marginTop: 0}}>{editId ? 'Edit Department' : 'Add New Department'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Department Code *</label>
                <input type="text" className="form-input" name="department_code" value={formData.department_code} onChange={handleInputChange} required placeholder="e.g. CSE" />
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Department Name *</label>
                <input type="text" className="form-input" name="department_name" value={formData.department_name} onChange={handleInputChange} required placeholder="e.g. Computer Science Engineering" />
              </div>
              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem'}}>
                <button type="button" onClick={closeModal} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary">{editId ? 'Save Changes' : 'Create Department'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
