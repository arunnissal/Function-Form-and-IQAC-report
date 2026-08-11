import React from 'react';

export default function Stepper({ step, maxSteps = 7 }) {
  const steps = [
    'Basic Info',
    'Guest House',
    'Refreshments',
    'Power & Sound',
    'Memento',
    'Transport',
    'Review'
  ];

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '2.5rem', position: 'relative', overflowX: 'auto', paddingBottom: '0.5rem' }}>
      {/* Progress track line */}
      <div style={{
        position: 'absolute',
        top: '16px',
        left: '20px',
        right: '20px',
        height: '2px',
        background: '#e2e8f0',
        zIndex: 0
      }} />

      {steps.map((name, idx) => {
        const num = idx + 1;
        const isActive = step === num;
        const isCompleted = step > num;
        
        return (
          <div key={num} style={{ zIndex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', minWidth: '80px', flex: 1 }}>
            <div style={{
              width: '32px',
              height: '32px',
              borderRadius: '50%',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: isActive ? 'var(--primary-color)' : (isCompleted ? '#10b981' : '#e2e8f0'),
              color: isActive || isCompleted ? 'white' : 'var(--text-secondary)',
              fontWeight: 'bold',
              marginBottom: '0.5rem',
              transition: 'all 0.3s ease',
              boxShadow: isActive ? '0 0 0 4px rgba(59, 130, 246, 0.2)' : 'none'
            }}>
              {isCompleted ? '✓' : num}
            </div>
            <span style={{
              fontSize: '0.75rem',
              fontWeight: isActive ? '700' : '500',
              color: isActive ? 'var(--primary-color)' : (isCompleted ? '#10b981' : 'var(--text-secondary)'),
              textAlign: 'center',
              whiteSpace: 'nowrap'
            }}>
              {name}
            </span>
          </div>
        );
      })}
    </div>
  );
}
