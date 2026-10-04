import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { ShieldCheck, Plus, History, ArrowRight, FileArchive, Github, FileCode } from 'lucide-react';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const res = await api.get('/projects');
        setProjects(res.data.projects);
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    fetchProjects();
  }, []);

  return (
    <div className="page-wrapper authenticated">
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', margin: 0 }}>Security Dashboard</h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Overview of your supply chain projects and recent risk assessments
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <Link to="/upload/zip" className="btn btn-primary">
              <Plus size={16} /> New Scan Upload
            </Link>
          </div>
        </div>

        {/* Quick Upload Workflows Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginBottom: '2.5rem' }}>
          <Link to="/upload/zip" className="card" style={{ textDecoration: 'none' }}>
            <FileArchive size={26} style={{ color: 'var(--accent-gold)', marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-light)', marginBottom: '0.25rem' }}>Upload ZIP Archive</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Scan packaged project repository zip archive safely.</p>
          </Link>

          <Link to="/upload/github" className="card" style={{ textDecoration: 'none' }}>
            <Github size={26} style={{ color: 'var(--accent-gold)', marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-light)', marginBottom: '0.25rem' }}>Public GitHub Repo</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Fetch and parse manifest files via GitHub API.</p>
          </Link>

          <Link to="/upload/manifests" className="card" style={{ textDecoration: 'none' }}>
            <FileCode size={26} style={{ color: 'var(--accent-gold)', marginBottom: '0.75rem' }} />
            <h3 style={{ fontSize: '1.1rem', color: 'var(--text-light)', marginBottom: '0.25rem' }}>Lockfiles / Manifests</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>Upload package-lock.json, requirements.txt, Cargo.lock, etc.</p>
          </Link>
        </div>

        {/* Recent Projects Table */}
        <div className="card">
          <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1.25rem' }}>
            Active Projects & Recent Scans
          </h3>

          {loading ? (
            <div style={{ color: 'var(--text-muted)', padding: '2rem 0', textAlign: 'center' }}>Loading projects...</div>
          ) : projects.length === 0 ? (
            <div style={{ textAlignment: 'center', padding: '3rem 1rem' }}>
              <ShieldCheck size={48} style={{ color: 'var(--text-dim)', marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', marginBottom: '1rem' }}>
                No supply chain projects scanned yet.
              </p>
              <Link to="/upload/zip" className="btn btn-primary">
                Upload Your First Project
              </Link>
            </div>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.92rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>Project Name</th>
                    <th style={{ padding: '0.75rem' }}>Ecosystem</th>
                    <th style={{ padding: '0.75rem' }}>Risk Score</th>
                    <th style={{ padding: '0.75rem' }}>Scan Status</th>
                    <th style={{ padding: '0.75rem' }}>Last Scanned</th>
                    <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {projects.map((proj) => {
                    const scan = proj.last_scan;
                    const score = scan ? scan.risk_score : 0;
                    const scoreColor = score >= 75 ? 'var(--danger-red)' : score >= 50 ? 'var(--warning-orange)' : 'var(--success-green)';

                    return (
                      <tr key={proj.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.85rem', fontWeight: 600 }}>{proj.name}</td>
                        <td style={{ padding: '0.85rem', color: 'var(--text-muted)' }}>{proj.ecosystem}</td>
                        <td style={{ padding: '0.85rem' }}>
                          {scan ? (
                            <span style={{ color: scoreColor, fontWeight: 700 }}>
                              {score} / 100
                            </span>
                          ) : 'N/A'}
                        </td>
                        <td style={{ padding: '0.85rem' }}>
                          <span style={{
                            padding: '0.25rem 0.6rem',
                            borderRadius: '4px',
                            fontSize: '0.8rem',
                            fontWeight: 600,
                            backgroundColor: scan?.status === 'COMPLETED' ? 'var(--success-green-bg)' : 'var(--accent-gold-glow)',
                            color: scan?.status === 'COMPLETED' ? 'var(--success-green)' : 'var(--accent-gold)'
                          }}>
                            {scan?.status || 'QUEUED'}
                          </span>
                        </td>
                        <td style={{ padding: '0.85rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                          {new Date(proj.created_at).toLocaleDateString()}
                        </td>
                        <td style={{ padding: '0.85rem', textAlign: 'right' }}>
                          {scan ? (
                            <Link to={`/scans/${scan.id}`} className="btn btn-outline" style={{ padding: '0.35rem 0.8rem', fontSize: '0.82rem' }}>
                              View Report <ArrowRight size={14} />
                            </Link>
                          ) : '-'}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
