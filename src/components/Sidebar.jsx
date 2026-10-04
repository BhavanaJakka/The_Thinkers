import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { FileArchive, Github, FileCode, History, Info, Mail } from 'lucide-react';

export default function Sidebar() {
  const location = useLocation();
  const isActive = (path) => location.pathname === path;

  return (
    <aside className="left-sidebar">
      <div className="sidebar-title">Scanning Workflows</div>
      
      <Link to="/upload/zip" className={`sidebar-item ${isActive('/upload/zip') ? 'active' : ''}`}>
        <FileArchive size={18} /> Upload file (zip)
      </Link>

      <Link to="/upload/github" className={`sidebar-item ${isActive('/upload/github') ? 'active' : ''}`}>
        <Github size={18} /> Upload by GitHub link
      </Link>

      <Link to="/upload/manifests" className={`sidebar-item ${isActive('/upload/manifests') ? 'active' : ''}`}>
        <FileCode size={18} /> Upload manifest/lock files
      </Link>

      <div className="sidebar-title">Analytics & Info</div>

      <Link to="/history" className={`sidebar-item ${isActive('/history') ? 'active' : ''}`}>
        <History size={18} /> History
      </Link>

      <Link to="/about" className={`sidebar-item ${isActive('/about') ? 'active' : ''}`}>
        <Info size={18} /> About Us
      </Link>

      <Link to="/contact" className={`sidebar-item ${isActive('/contact') ? 'active' : ''}`}>
        <Mail size={18} /> Contact Us
      </Link>
    </aside>
  );
}
