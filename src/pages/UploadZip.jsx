import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import { FileArchive, UploadCloud, AlertCircle } from 'lucide-react';

export default function UploadZip() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [projectName, setProjectName] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setErrorMsg('Please select a .zip archive file.');
      return;
    }

    setLoading(true);
    setErrorMsg('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('project_name', projectName);

    try {
      const res = await api.post('/projects/upload-zip', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      navigate(`/scans/${res.data.scan_id}`);
    } catch (err) {
      if (err.response && err.response.data && err.response.data.error) {
        setErrorMsg(err.response.data.error);
      } else {
        setErrorMsg('Upload failed. Ensure the zip file is valid.');
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
            <FileArchive size={42} style={{ color: 'var(--accent-gold)' }} />
            <h2 style={{ fontSize: '1.75rem', marginTop: '0.5rem' }}>Upload ZIP Repository Archive</h2>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              Upload compressed project ZIP file. Safe unzip protection blocks zip-slip and code execution.
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
              <label className="form-label" htmlFor="zip-proj-name">Project Name (Optional)</label>
              <input
                id="zip-proj-name"
                type="text"
                value={projectName}
                onChange={(e) => setProjectName(e.target.value)}
                className="form-control"
                placeholder="e.g. My Express Microservice"
              />
            </div>

            <div className="form-group">
              <label className="form-label" htmlFor="zip-file">Select ZIP File (.zip)</label>
              <input
                id="zip-file"
                type="file"
                accept=".zip"
                onChange={(e) => setFile(e.target.files[0])}
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
              {loading ? 'Uploading & Extracting...' : <><UploadCloud size={18} /> Upload ZIP & Start Scan</>}
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}
