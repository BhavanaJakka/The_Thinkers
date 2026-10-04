import React from 'react';

export default function Logo({ size = 32, className = '' }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Outer Shield Boundary Outline */}
      <path
        d="M50 12 L82 24 V52 C82 72 50 90 50 90 C50 90 18 72 18 52 V24 L50 12 Z"
        stroke="#ff001b"
        strokeWidth="6.5"
        strokeLinecap="round"
        strokeLinejoin="round"
        fill="none"
      />

      {/* Internal Graph Nodes & Network Edges */}
      <line x1="50" y1="12" x2="36" y2="72" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />
      <line x1="50" y1="12" x2="68" y2="48" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />
      <line x1="24" y1="30" x2="68" y2="48" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />
      <line x1="18" y1="52" x2="36" y2="52" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />
      <line x1="36" y1="72" x2="68" y2="48" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />
      <line x1="68" y1="48" x2="82" y2="52" stroke="#ff001b" strokeWidth="6.5" strokeLinecap="round" />

      {/* Connected Graph Node Circles */}
      <circle cx="50" cy="12" r="5" fill="#171210" stroke="#ff001b" strokeWidth="3.5" />
      <circle cx="18" cy="52" r="5" fill="#171210" stroke="#ff001b" strokeWidth="3.5" />
      <circle cx="82" cy="52" r="5" fill="#171210" stroke="#ff001b" strokeWidth="3.5" />
      <circle cx="68" cy="48" r="5" fill="#171210" stroke="#ff001b" strokeWidth="3.5" />
      <circle cx="36" cy="72" r="4.5" fill="#ff001b" />
    </svg>
  );
}
