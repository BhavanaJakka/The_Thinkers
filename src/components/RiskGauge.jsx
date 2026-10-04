import React from 'react';

export default function RiskGauge({ score = 0 }) {
  let color = 'var(--success-green)';
  let label = 'LOW RISK';

  if (score >= 75) {
    color = 'var(--danger-red)';
    label = 'CRITICAL RISK';
  } else if (score >= 50) {
    color = 'var(--warning-orange)';
    label = 'HIGH RISK';
  } else if (score >= 25) {
    color = '#facc15';
    label = 'MEDIUM RISK';
  }

  const radius = 60;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <div style={{ position: 'relative', width: '160px', height: '160px' }}>
        <svg width="160" height="160" viewBox="0 0 160 160">
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke="var(--bg-surface-hover)"
            strokeWidth="12"
          />
          <circle
            cx="80"
            cy="80"
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth="12"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            strokeLinecap="round"
            transform="rotate(-90 80 80)"
            style={{ transition: 'stroke-dashoffset 1s ease-in-out' }}
          />
        </svg>
        <div style={{
          position: 'absolute',
          top: 0, left: 0, right: 0, bottom: 0,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center'
        }}>
          <span style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--text-light)', lineHeight: 1 }}>
            {score}
          </span>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>/ 100</span>
        </div>
      </div>
      <div style={{
        marginTop: '0.75rem',
        fontWeight: 700,
        fontSize: '0.9rem',
        color: color,
        letterSpacing: '1px'
      }}>
        {label}
      </div>
    </div>
  );
}
