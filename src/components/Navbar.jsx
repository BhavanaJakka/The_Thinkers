import React, { useContext } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import Logo from './Logo';
import { LayoutDashboard, Upload, History, LogOut } from 'lucide-react';

export default function Navbar() {
  const { user, logout } = useContext(AuthContext);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="sticky-navbar">
      <Link to={user ? "/dashboard" : "/"} className="nav-brand">
        <Logo size={32} className="text-danger-red" />
        <span style={{ color: 'var(--text-light)', fontWeight: 700, letterSpacing: '1px' }}>DEPTRIX</span>
      </Link>

      <ul className="nav-links">
        {!user ? (
          <>
            <li><Link to="/" className={`nav-link ${isActive('/') ? 'active' : ''}`}>Home</Link></li>
            <li><Link to="/about" className={`nav-link ${isActive('/about') ? 'active' : ''}`}>About Deptrix</Link></li>
            <li><Link to="/threats" className={`nav-link ${isActive('/threats') ? 'active' : ''}`}>Threats & Malware</Link></li>
            <li><Link to="/contact" className={`nav-link ${isActive('/contact') ? 'active' : ''}`}>Contact</Link></li>
            <li>
              <Link to="/login" className="btn btn-outline" style={{ padding: '0.45rem 1.1rem', fontSize: '0.9rem' }}>
                Sign In
              </Link>
            </li>
            <li>
              <Link to="/signup-step1" className="btn btn-primary" style={{ padding: '0.45rem 1.1rem', fontSize: '0.9rem' }}>
                Sign Up
              </Link>
            </li>
          </>
        ) : (
          <>
            <li>
              <Link to="/dashboard" className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <LayoutDashboard size={16} /> Dashboard
              </Link>
            </li>
            <li>
              <Link to="/upload" className={`nav-link ${isActive('/upload') ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <Upload size={16} /> Upload
              </Link>
            </li>
            <li>
              <Link to="/history" className={`nav-link ${isActive('/history') ? 'active' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <History size={16} /> History
              </Link>
            </li>
            <li>
              <button onClick={logout} className="btn btn-outline" style={{ padding: '0.4rem 0.9rem', fontSize: '0.88rem' }}>
                <LogOut size={15} /> Logout
              </button>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}
