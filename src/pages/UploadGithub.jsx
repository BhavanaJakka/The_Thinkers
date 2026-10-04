import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { Github, UploadCloud } from 'lucide-react';

export default function UploadGithub() {
  const navigate = useNavigate();
  const [githubUrl, setGithubUrl] = useState('');
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMsg('');

    try {
      const res = await api.post('/projects/upload-github', {
        github_url: githubUrl,
        project_name: projectName
      });
      navigate(`/scans/${res.data.scan_id}`);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorMsg(err.response.data.error);
      } else {
        setErrorMsg('Failed to fetch GitHub repository.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page-wrapper authenticated">
      <div style={{ maxWidth: '650px', margin: '0 auto' }}>
        <div className="card">
          <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
            <Github size={42} style={{ color: 'var(--accent-gold)' }} />
            <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Upload Public GitHub Repo Link</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Fetches manifest files directly from GitHub API without executing code.
            </p>
          </div>

          {errorMsg && (
            <div style={{
              backgroundColor: 'var(--danger-red-bg)',
              border: '1px solid var(--danger-red)',
              color: 'var(--danger-red)',
              padding: '0.75rem',
              borderRadius: 'var(--radius-sm)',
              marginBottom: '1.25rem',
              fontSize: '0.88rem'
            }}>
              {errorMsg}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label className="form-label" htmlFor="gh-url">GitHub Repository URL</label>
              <input
                id="gh-url"
                type="url"
                value={githubUrl}
                onChange={(e) => setGithubUrl(e.target.value)}
                className="form-control"
                placeholder="https://github.com/owner/repository"
                required
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="gh-proj-name">Project Name (Optional)</label>
              <input
                id="gh-proj-name"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="form-control"
                placeholder="Custom project title"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem', padding: '0.8rem' }}
            >
              {loading ? 'Fetching Repository...' : <><UploadCloud size={18} /> Fetch & Scan Repository</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
