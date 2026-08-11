import React from 'react';
import StatusBadge from './StatusBadge';

export default function Timeline({ logs }) {
  if (!logs || logs.length === 0) {
    return (
      <div style={{ padding: '1.5rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
        No approval history recorded yet.
      </div>
    );
  }

  return (
    <div style={{ position: 'relative', paddingLeft: '2.5rem', margin: '2rem 0' }}>
      {/* Central vertical track line */}
      <div style={{
        position: 'absolute',
        top: '8px',
        bottom: '8px',
        left: '15px',
        width: '2px',
        background: 'linear-gradient(to bottom, #3b82f6, #10b981)'
      }} />

      {logs.map((log, idx) => {
        const formattedDate = new Date(log.timestamp).toLocaleString();
        return (
          <div key={log.id || idx} style={{ position: 'relative', marginBottom: '2.5rem' }}>
            {/* Timeline Dot Indicator */}
            <div style={{
              position: 'absolute',
              left: '-32px',
              top: '4px',
              width: '16px',
              height: '16px',
              borderRadius: '50%',
              background: '#fff',
              border: '3px solid #3b82f6',
              boxShadow: '0 0 0 4px rgba(59, 130, 246, 0.15)',
              zIndex: 1
            }} />

            {/* Content card */}
            <div className="card animate-fade-in" style={{ padding: '1.25rem', border: '1px solid var(--border-color)', margin: 0 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                  <span style={{ fontWeight: '700', fontSize: '1.05rem', color: 'var(--primary-color)' }}>
                    {log.stage === 'MANAGEMENT' ? 'Management (AO)' : log.stage}
                  </span>
                  <StatusBadge status={log.status} />
                </div>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {formattedDate}
                </span>
              </div>

              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)' }}>
                <div style={{ marginBottom: '0.25rem' }}>
                  <strong>Action by:</strong> {log.approver_name || 'System / Auto'}
                </div>
                {log.remarks && (
                  <div style={{ 
                    marginTop: '0.5rem', 
                    padding: '0.75rem', 
                    background: '#f8fafc', 
                    borderRadius: '6px', 
                    borderLeft: '3px solid #cbd5e1',
                    fontStyle: 'italic'
                  }}>
                    &ldquo;{log.remarks}&rdquo;
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
