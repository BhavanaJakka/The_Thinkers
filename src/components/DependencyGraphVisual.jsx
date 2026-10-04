import React, { useState } from 'react';

export default function DependencyGraphVisual() {
  const [hoveredNode, setHoveredNode] = useState(null);

  const nodes = [
    { id: 'app', label: 'App Root', x: 200, y: 50, type: 'root', color: '#c49a6c' },
    { id: 'express', label: 'express v4.18.2', x: 100, y: 140, type: 'direct', color: '#30a46c' },
    { id: 'requests', label: 'requests v2.31.0', x: 300, y: 140, type: 'direct', color: '#30a46c' },
    { id: 'body-parser', label: 'body-parser', x: 60, y: 230, type: 'transitive', color: '#30a46c' },
    { id: 'qs', label: 'qs (CVE-2023-45)', x: 140, y: 230, type: 'vulnerable', color: '#e5484d' },
    { id: 'urllib3', label: 'urllib3', x: 260, y: 230, type: 'transitive', color: '#30a46c' },
    { id: 'reqeusts', label: 'reqeusts (Typosquat)', x: 340, y: 230, type: 'suspicious', color: '#f59e0b' },
  ];

  const edges = [
    { from: 'app', to: 'express' },
    { from: 'app', to: 'requests' },
    { from: 'express', to: 'body-parser' },
    { from: 'express', to: 'qs' },
    { from: 'requests', to: 'urllib3' },
    { from: 'requests', to: 'reqeusts' }
  ];

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-color-gold)',
      borderRadius: 'var(--radius-lg)',
      padding: '1.5rem',
      boxShadow: 'var(--shadow-card)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
        <h4 style={{ color: 'var(--accent-gold)', fontSize: '1.05rem', margin: 0 }}>Interactive Dependency Risk Graph</h4>
        <div style={{ display: 'flex', gap: '0.75rem', fontSize: '0.8rem' }}>
          <span style={{ color: '#30a46c' }}>● Safe</span>
          <span style={{ color: '#f59e0b' }}>● Suspicious</span>
          <span style={{ color: '#e5484d' }}>● Vulnerable</span>
        </div>
      </div>

      <svg width="100%" height="280" viewBox="0 0 400 280">
        {/* Render Edges */}
        {edges.map((edge, idx) => {
          const fromNode = nodes.find(n => n.id === edge.from);
          const toNode = nodes.find(n => n.id === edge.to);
          const isHighlighted = hoveredNode && (hoveredNode === edge.from || hoveredNode === edge.to);

          return (
            <line
              key={idx}
              x1={fromNode.x}
              y1={fromNode.y}
              x2={toNode.x}
              y2={toNode.y}
              stroke={isHighlighted ? 'var(--accent-gold)' : 'var(--border-color)'}
              strokeWidth={isHighlighted ? '2.5' : '1.5'}
              strokeDasharray={toNode.type === 'vulnerable' ? '4 4' : 'none'}
            />
          );
        })}

        {/* Render Nodes */}
        {nodes.map((node) => {
          const isHovered = hoveredNode === node.id;

          return (
            <g
              key={node.id}
              onMouseEnter={() => setHoveredNode(node.id)}
              onMouseLeave={() => setHoveredNode(null)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={node.x}
                cy={node.y}
                r={isHovered ? 16 : 12}
                fill={node.color}
                stroke={isHovered ? '#fff' : 'none'}
                strokeWidth="2"
                style={{ transition: 'all 0.2s ease' }}
              />
              <text
                x={node.x}
                y={node.y + 24}
                textAnchor="middle"
                fill={isHovered ? 'var(--accent-gold)' : 'var(--text-muted)'}
                fontSize="10.5"
                fontFamily="var(--font-ui)"
                fontWeight={isHovered ? '600' : '400'}
              >
                {node.label}
              </text>
            </g>
          );
        })}
      </svg>
      {hoveredNode && (
        <div style={{
          fontSize: '0.85rem',
          color: 'var(--text-light)',
          textAlign: 'center',
          backgroundColor: 'rgba(0,0,0,0.5)',
          padding: '0.4rem',
          borderRadius: '4px',
          marginTop: '0.5rem'
        }}>
          Hovering node: <strong style={{ color: 'var(--accent-gold)' }}>{hoveredNode}</strong>
        </div>
      )}
    </div>
  );
}
