import React from 'react';

export default function StatusBadge({ status }) {
  const config = {
    'DRAFT': { bg: 'rgba(107, 114, 128, 0.1)', color: '#6b7280', text: 'Draft' },
    'PENDING_HOD': { bg: 'rgba(59, 130, 246, 0.1)', color: '#3b82f6', text: 'Pending HOD' },
    'PENDING_DEAN': { bg: 'rgba(139, 92, 246, 0.1)', color: '#8b5cf6', text: 'Pending Dean' },
    'PENDING_MANAGEMENT': { bg: 'rgba(245, 158, 11, 0.1)', color: '#f59e0b', text: 'Pending AO' },
    'PENDING_PRINCIPAL': { bg: 'rgba(236, 72, 153, 0.1)', color: '#ec4899', text: 'Pending Principal' },
    'PENDING_FINAL_CONFIRMATION': { bg: 'rgba(244, 63, 94, 0.1)', color: '#f43f5e', text: 'Pending Confirmation' },
    'RETURNED_FOR_CORRECTION': { bg: 'rgba(239, 68, 68, 0.1)', color: '#ef4444', text: 'Returned' },
    'APPROVED': { bg: 'rgba(16, 185, 129, 0.1)', color: '#10b981', text: 'Approved' },
    'REJECTED': { bg: 'rgba(220, 38, 38, 0.1)', color: '#dc2626', text: 'Rejected' },
    'CANCELLED': { bg: 'rgba(127, 29, 29, 0.1)', color: '#7f1d1d', text: 'Cancelled' },
  };

  const style = config[status] || { bg: 'rgba(107, 114, 128, 0.1)', color: '#6b7280', text: status };

  return (
    <span style={{
      display: 'inline-flex',
      alignItems: 'center',
      padding: '0.25rem 0.75rem',
      borderRadius: '9999px',
      fontSize: '0.875rem',
      fontWeight: '600',
      backgroundColor: style.bg,
      color: style.color,
      textTransform: 'uppercase',
      letterSpacing: '0.05em'
    }}>
      {style.text}
    </span>
  );
}
