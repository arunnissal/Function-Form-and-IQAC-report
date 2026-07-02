import React, { useState, useEffect } from 'react';
import api from '../api';
import Layout from '../components/Layout';

export default function ManageHalls() {
  const [halls, setHalls] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editId, setEditId] = useState(null);
  const [formData, setFormData] = useState({
    hall_name: '',
    capacity: 0,
    has_projector: false,
    has_ac: false,
    has_audio_system: false
  });

  useEffect(() => {
    fetchHalls();
  }, []);

  const fetchHalls = async () => {
    try {
      const response = await api.get('halls/');
      setHalls(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
  };

  const openModal = (hall = null) => {
    if (hall) {
      setEditId(hall.id);
      setFormData(hall);
    } else {
      setEditId(null);
      setFormData({ hall_name: '', capacity: 0, has_projector: false, has_ac: false, has_audio_system: false });
    }
    setShowModal(true);
  };

  const closeModal = () => setShowModal(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editId) {
        await api.put(`halls/${editId}/`, formData);
      } else {
        await api.post('halls/', formData);
      }
      closeModal();
      fetchHalls();
    } catch (err) {
      console.error(err);
      alert('Error saving hall.');
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm("Are you sure you want to delete this hall?")) {
      try {
        await api.delete(`halls/${id}/`);
        fetchHalls();
      } catch (err) {
        console.error(err);
        alert('Error deleting hall.');
      }
    }
  };

  return (
    <Layout title="Manage Seminar Halls">
      <div style={{ maxWidth: '1000px', margin: '0 auto'}}>
        <div style={{ background: 'white', borderRadius: '8px', boxShadow: 'var(--shadow-md)', overflow: 'hidden'}}>
          <div style={{padding: '1.5rem', borderBottom: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center'}}>
            <h3 style={{margin: 0}}>Seminar Halls Directory</h3>
            <button onClick={() => openModal()} className="btn btn-primary" style={{padding: '0.5rem 1rem', fontSize: '0.875rem'}}>+ Add New Hall</button>
          </div>
          
          {loading ? (
            <div style={{padding: '2rem', textAlign: 'center', color: 'var(--text-secondary)'}}>Loading halls...</div>
          ) : halls.length === 0 ? (
            <div style={{padding: '4rem 2rem', textAlign: 'center'}}>
              <p style={{color: 'var(--text-secondary)'}}>No seminar halls found.</p>
            </div>
          ) : (
            <table style={{width: '100%', borderCollapse: 'collapse'}}>
              <thead style={{backgroundColor: 'var(--bg-color)', borderBottom: '1px solid var(--border-color)'}}>
                <tr>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Hall Name</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Capacity</th>
                  <th style={{padding: '1rem', textAlign: 'left', fontWeight: '600', color: 'var(--text-secondary)'}}>Facilities</th>
                  <th style={{padding: '1rem', textAlign: 'center', fontWeight: '600', color: 'var(--text-secondary)'}}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {halls.map(hall => (
                  <tr key={hall.id} style={{borderBottom: '1px solid var(--border-color)'}}>
                    <td style={{padding: '1rem', fontWeight: '500'}}>{hall.hall_name}</td>
                    <td style={{padding: '1rem'}}>{hall.capacity} Seats</td>
                    <td style={{padding: '1rem', color: 'var(--text-secondary)', fontSize: '0.875rem'}}>
                      {hall.has_projector ? 'Projector ' : ''}
                      {hall.has_ac ? 'A/C ' : ''}
                      {hall.has_audio_system ? 'Audio' : ''}
                    </td>
                    <td style={{padding: '1rem', textAlign: 'center'}}>
                      <button onClick={() => openModal(hall)} className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.75rem', marginRight: '0.5rem'}}>Edit</button>
                      <button onClick={() => handleDelete(hall.id)} className="btn btn-outline" style={{padding: '0.2rem 0.5rem', fontSize: '0.75rem', color: '#ef4444', borderColor: '#ef4444'}}>Delete</button>
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
            <h3 style={{marginTop: 0}}>{editId ? 'Edit Hall' : 'Add New Hall'}</h3>
            <form onSubmit={handleSubmit}>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Hall Name *</label>
                <input type="text" className="form-input" name="hall_name" value={formData.hall_name} onChange={handleInputChange} required />
              </div>
              <div style={{marginBottom: '1rem'}}>
                <label className="form-label">Capacity *</label>
                <input type="number" className="form-input" name="capacity" value={formData.capacity} onChange={handleInputChange} required min="1" />
              </div>
              <div style={{marginBottom: '1rem', display: 'flex', gap: '1rem'}}>
                <label><input type="checkbox" name="has_projector" checked={formData.has_projector} onChange={handleInputChange} /> Projector</label>
                <label><input type="checkbox" name="has_ac" checked={formData.has_ac} onChange={handleInputChange} /> A/C</label>
                <label><input type="checkbox" name="has_audio_system" checked={formData.has_audio_system} onChange={handleInputChange} /> Audio System</label>
              </div>
              <div style={{display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem'}}>
                <button type="button" onClick={closeModal} className="btn btn-outline">Cancel</button>
                <button type="submit" className="btn btn-primary">{editId ? 'Save Changes' : 'Create Hall'}</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </Layout>
  );
}
