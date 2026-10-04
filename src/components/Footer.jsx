import React from 'react';
import { Link } from 'react-router-dom';
import Logo from './Logo';

export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-col" style={{ flex: '1 1 300px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '1rem' }}>
            <Logo size={28} className="text-danger-red" />
            <h4 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--text-light)', letterSpacing: '1px' }}>DEPTRIX</h4>
          </div>
          <p>
            Production-grade Software Supply Chain Risk Analyzer. Detect vulnerabilities, typosquatting malware, copyleft license conflicts, and compute dependency attack paths before deployment.
          </p>
        </div>

        <div className="footer-col">
          <h4>Navigation</h4>
          <ul style={{ listStyle: 'none' }}>
            <li><Link to="/">Home Overview</Link></li>
            <li><Link to="/about">About Deptrix</Link></li>
            <li><Link to="/threats">Threats & Malware</Link></li>
            <li><Link to="/contact">Contact Support</Link></li>
          </ul>
        </div>

        <div className="footer-col">
          <h4>Security Analysis</h4>
          <ul style={{ listStyle: 'none' }}>
            <li>Vulnerability Lookup (OSV.dev)</li>
            <li>Typosquatting Malware Detection</li>
            <li>SPDX License Compatibility</li>
            <li>BFS/DFS Attack Path Traversal</li>
          </ul>
        </div>

        <div className="footer-col">
          <h4>Author & Contact</h4>
          <p>
            <strong>Omkar Nalawade</strong><br />
            Email: nalawadeomkar0508@gmail.com<br />
            Location: Pune, Maharashtra, India
          </p>
        </div>
      </div>

      <div className="footer-bottom">
        &copy; {new Date().getFullYear()} Deptrix Supply Chain Risk Analyzer. All rights reserved. Built for security-first engineering.
      </div>
    </footer>
  );
}
