import React, { useState } from 'react';

export default function ApprovalButtons({ onApprove, onReject, onReturn, isSubmitting, approveLabel }) {
  const [remarks, setRemarks] = useState('');

  const handleApprove = () => {
    onApprove(remarks);
    setRemarks('');
  };

  const handleReject = () => {
    if (!remarks.trim()) {
      alert("Please provide remarks explaining the reason for rejection.");
      return;
    }
    onReject(remarks);
    setRemarks('');
  };

  const handleReturn = () => {
    if (!remarks.trim()) {
      alert("Please provide remarks explaining what needs to be corrected.");
      return;
    }
    onReturn(remarks);
    setRemarks('');
  };

  return (
    <div style={{ background: '#f8fafc', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border-color)', margin: '2rem 0' }}>
      <h3 style={{ color: 'var(--primary-color)', margin: '0 0 1rem 0', fontSize: '1.25rem' }}>Review Decision</h3>
      
      <div style={{ marginBottom: '1.25rem' }}>
        <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', fontWeight: 'bold', color: 'var(--text-secondary)' }}>
          Review Remarks / Comments * (Required for rejection or correction)
        </label>
        <textarea
          className="form-input"
          rows="3"
          value={remarks}
          onChange={(e) => setRemarks(e.target.value)}
          placeholder="Enter comments for approval, rejection, or correction..."
          style={{ width: '100%', resize: 'vertical' }}
        />
      </div>

      <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
        <button
          type="button"
          onClick={handleApprove}
          className="btn"
          disabled={isSubmitting}
          style={{ background: '#10b981', color: 'white', flex: 1, minWidth: '150px' }}
        >
          {isSubmitting ? 'Processing...' : (approveLabel || '✅ Approve')}
        </button>
        <button
          type="button"
          onClick={handleReturn}
          className="btn btn-outline"
          disabled={isSubmitting}
          style={{ borderColor: '#f59e0b', color: '#f59e0b', flex: 1, minWidth: '150px' }}
        >
          {isSubmitting ? 'Processing...' : '⚠️ Return for Correction'}
        </button>
        <button
          type="button"
          onClick={handleReject}
          className="btn btn-outline"
          disabled={isSubmitting}
          style={{ borderColor: '#ef4444', color: '#ef4444', flex: 1, minWidth: '150px' }}
        >
          {isSubmitting ? 'Processing...' : '❌ Reject'}
        </button>
      </div>
    </div>
  );
}
