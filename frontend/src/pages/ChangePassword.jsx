import React, { useState } from 'react';
import api from '../api';
import Layout from '../components/Layout';

export default function ChangePassword() {
  const [formData, setFormData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage('');
    setError('');

    if (formData.new_password !== formData.confirm_password) {
      setError("New passwords do not match.");
      return;
    }

    try {
      await api.post('users/change_password/', {
        current_password: formData.current_password,
        new_password: formData.new_password
      });
      setMessage("Password updated successfully!");
      setFormData({ current_password: '', new_password: '', confirm_password: '' });
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to change password. Ensure your current password is correct.");
    }
  };

  return (
    <Layout title="Change Password">
      <div style={{ maxWidth: '600px', margin: '0 auto', background: 'white', padding: '2rem', borderRadius: '8px', boxShadow: 'var(--shadow-md)'}}>
        <h2 style={{marginTop: 0, marginBottom: '1.5rem'}}>Update Security Settings</h2>
        
        {message && <div style={{padding: '1rem', background: '#dcfce3', color: '#15803d', borderRadius: '4px', marginBottom: '1rem'}}>{message}</div>}
        {error && <div style={{padding: '1rem', background: '#fee2e2', color: '#b91c1c', borderRadius: '4px', marginBottom: '1rem'}}>{error}</div>}

        <form onSubmit={handleSubmit}>
          <div style={{marginBottom: '1rem'}}>
            <label className="form-label">Current Password *</label>
            <input type="password" name="current_password" value={formData.current_password} onChange={handleInputChange} className="form-input" required />
          </div>
          <div style={{marginBottom: '1rem'}}>
            <label className="form-label">New Password *</label>
            <input type="password" name="new_password" value={formData.new_password} onChange={handleInputChange} className="form-input" required minLength={6} />
          </div>
          <div style={{marginBottom: '1.5rem'}}>
            <label className="form-label">Confirm New Password *</label>
            <input type="password" name="confirm_password" value={formData.confirm_password} onChange={handleInputChange} className="form-input" required minLength={6} />
          </div>
          <button type="submit" className="btn btn-primary" style={{width: '100%'}}>Update Password</button>
        </form>
      </div>
    </Layout>
  );
}
