import React from 'react';
import { ShieldAlert, ArrowRight } from 'lucide-react';

export default function AttackPathView({ attackPaths = [] }) {
  if (!attackPaths || attackPaths.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
        No critical attack paths detected in this scan graph.
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {attackPaths.map((ap, idx) => (
        <div key={ap.id || idx} style={{
          backgroundColor: '#120d0b',
          border: '1px solid var(--border-color)',
          borderRadius: 'var(--radius-sm)',
          padding: '1.25rem'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
            <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--danger-red)', fontWeight: 600, fontSize: '0.92rem' }}>
              <ShieldAlert size={16} /> Target Node: {ap.target_node}
            </span>
            <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
              Depth: {ap.depth} hop(s) | Severity Rank: {ap.severity_rank}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '0.5rem' }}>
            {ap.path_nodes.map((node, nIdx) => {
              const isRoot = nIdx === 0;
              const isTarget = nIdx === ap.path_nodes.length - 1;

              return (
                <React.Fragment key={nIdx}>
                  <span style={{
                    padding: '0.35rem 0.75rem',
                    borderRadius: '4px',
                    fontSize: '0.85rem',
                    fontWeight: 600,
                    backgroundColor: isRoot ? 'var(--accent-gold-glow)' : isTarget ? 'var(--danger-red-bg)' : 'var(--bg-surface-hover)',
                    color: isRoot ? 'var(--accent-gold)' : isTarget ? 'var(--danger-red)' : 'var(--text-light)',
                    border: `1px solid ${isRoot ? 'var(--accent-gold)' : isTarget ? 'var(--danger-red)' : 'var(--border-color)'}`
                  }}>
                    {node}
                  </span>
                  {nIdx < ap.path_nodes.length - 1 && (
                    <ArrowRight size={14} style={{ color: 'var(--text-dim)' }} />
                  )}
                </React.Fragment>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
}
