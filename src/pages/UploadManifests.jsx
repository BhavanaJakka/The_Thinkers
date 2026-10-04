import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { FileCode, UploadCloud } from 'lucide-react';

export default function UploadManifests() {
  const navigate = useNavigate();
  const [files, setFiles] = useState([]);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (files.length === 0) {
      setErrorMsg('Please select at least one manifest or lock file.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    formData.append('project_name', projectName);

    try {
      const res = await api.post('/projects/upload-manifests', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      navigate(`/scans/${res.data.scan_id}`);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorMsg(err.response.data.error);
      } else {
        setErrorMsg('Upload failed.');
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
            <FileCode size={42} style={{ color: 'var(--accent-gold)' }} />
            <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Upload Manifest & Lock Files</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Select package.json, requirements.txt, Cargo.lock, pom.xml, go.mod, etc.
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
              <label className="form-label" htmlFor="manifest-proj-name">Project Name (Optional)</label>
              <input
                id="manifest-proj-name"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="form-control"
                placeholder="e.g. Frontend App Lockfiles"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="manifest-files">Select Manifest Files (Multiple allowed)</label>
              <input
                id="manifest-files"
                type="file"
                multiple
                onChange={(e) => setFiles(e.target.files)}
                className="form-control"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
              style={{ width: '100%', marginTop: '1rem', padding: '0.8rem' }}
            >
              {loading ? 'Processing Files...' : <><UploadCloud size={18} /> Upload Manifests & Start Scan</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
