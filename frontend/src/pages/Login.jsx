import React, { useState, useContext } from 'react';
import { AuthContext } from '../AuthContext';
import { useNavigate } from 'react-router-dom';
import { LogIn, Eye, EyeOff } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    if (!email.endsWith('@drngpit.ac.in')) {
      setError('Mail id must end with @drngpit.ac.in');
      return;
    }

    setSubmitting(true);
    try {
      const user = await login(email, password);
      // Optional: Add strict role checking here if required matching `position`
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid Mail id or password.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="auth-layout">
      <div className="auth-card animate-fade-in">
        <div className="auth-header">
          <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '64px',
            height: '64px',
            backgroundColor: 'rgba(13, 35, 64, 0.05)',
            borderRadius: '16px',
            marginBottom: '1rem',
            color: 'var(--primary-color)'
          }}>
            <LogIn size={32} />
          </div>
          <h1 className="auth-logo-text">Dr.NGPIT ERP</h1>
          <p style={{color: 'var(--text-secondary)', marginTop: '0.5rem'}}>Sign in to continue to Function Requirement System</p>
        </div>

        {error && (
          <div style={{
            padding: '0.75rem 1rem',
            backgroundColor: 'rgba(239, 68, 68, 0.1)',
            borderLeft: '4px solid var(--danger)',
            color: 'var(--danger)',
            borderRadius: '4px',
            marginBottom: '1.5rem',
            fontSize: '0.875rem'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>


          <div className="form-group">
            <label className="form-label">College Mail ID</label>
            <input 
              type="email" 
              className="form-input" 
              placeholder="name@drngpit.ac.in" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>

          <div className="form-group" style={{marginBottom: '2rem'}}>
            <label className="form-label">Password</label>
            <div style={{ position: 'relative' }}>
              <input 
                type={showPassword ? "text" : "password"} 
                className="form-input" 
                placeholder="••••••••" 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required 
                style={{ paddingRight: '2.5rem' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '0.75rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  alignItems: 'center',
                  padding: 0
                }}
              >
                {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
              </button>
            </div>
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{
              width: '100%', 
              padding: '0.875rem', 
              display: 'flex', 
              alignItems: 'center', 
              justifyContent: 'center', 
              gap: '0.5rem',
              opacity: submitting ? 0.8 : 1,
              cursor: submitting ? 'not-allowed' : 'pointer'
            }}
            disabled={submitting}
          >
            {submitting ? (
              <>
                <span className="spinner"></span>
                Signing In...
              </>
            ) : (
              "Sign In"
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
