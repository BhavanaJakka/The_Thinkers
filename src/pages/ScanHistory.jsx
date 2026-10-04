import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { History, ArrowRight, ShieldAlert, BarChart2, Trash2, Search, AlertCircle } from 'lucide-react';

export default function ScanHistory() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [deletingId, setDeletingId] = useState(null);
  const [clearing, setClearing] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [feedback, setFeedback] = useState(null);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const res = await api.get('/scans/history');
      setHistory(res.data.history || []);
    } catch (err) {
      console.error('Error fetching scan history:', err);
      showFeedback('Failed to load scan history.', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const showFeedback = (msg, type = 'success') => {
    setFeedback({ msg, type });
    setTimeout(() => setFeedback(null), 4000);
  };

  const handleDeleteScan = async (scanId, projectName) => {
    try {
      setDeletingId(scanId);
      await api.delete(`/scans/${scanId}`);
      setHistory(prev => prev.filter(s => s.id !== scanId));
      showFeedback(`Scan history for "${projectName}" deleted successfully.`);
    } catch (err) {
      console.error('Error deleting scan log:', err);
      showFeedback(err.response?.data?.error || 'Failed to delete scan log.', 'error');
    } finally {
      setDeletingId(null);
    }
  };

  const handleClearAllHistory = async () => {
    try {
      setClearing(true);
      const res = await api.delete('/scans/history');
      setHistory([]);
      showFeedback(res.data.message || 'All scan history logs cleared successfully.');
    } catch (err) {
      console.error('Error clearing scan history:', err);
      showFeedback(err.response?.data?.error || 'Failed to clear scan history.', 'error');
    } finally {
      setClearing(false);
    }
  };

  const filteredHistory = history.filter(s => 
    s.project_name?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.ecosystem?.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.id?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="page-wrapper authenticated">
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
          <div>
            <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <History size={28} style={{ color: 'var(--accent-gold)' }} />
              Scan History & Trend Analysis
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem' }}>
              Historical record of supply chain scans and risk score comparisons saved in database.
            </p>
          </div>

          {history.length > 0 && (
            <button
              onClick={handleClearAllHistory}
              disabled={clearing}
              className="btn btn-outline"
              style={{
                borderColor: 'var(--danger-red)',
                color: 'var(--danger-red)',
                fontSize: '0.85rem',
                padding: '0.5rem 1rem'
              }}
            >
              <Trash2 size={16} />
              {clearing ? 'Clearing History...' : 'Clear All History'}
            </button>
          )}
        </div>

        {/* Feedback Alert Banner */}
        {feedback && (
          <div style={{
            padding: '0.85rem 1.2rem',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '1.5rem',
            backgroundColor: feedback.type === 'error' ? 'var(--danger-red-bg)' : 'var(--success-green-bg)',
            border: `1px solid ${feedback.type === 'error' ? 'var(--danger-red)' : 'var(--success-green)'}`,
            color: feedback.type === 'error' ? '#ff6b6b' : '#30a46c',
            display: 'flex',
            alignItems: 'center',
            justify: 'space-between',
            fontSize: '0.9rem'
          }}>
            <span>{feedback.msg}</span>
            <button
              onClick={() => setFeedback(null)}
              style={{ background: 'none', border: 'none', color: 'inherit', cursor: 'pointer', fontWeight: 'bold' }}
            >
              ✕
            </button>
          </div>
        )}

        {/* Risk Trend Visual List */}
        {!loading && history.length > 0 && (
          <div className="card" style={{ marginBottom: '2rem' }}>
            <h3 style={{ fontSize: '1.2rem', color: 'var(--accent-gold)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <BarChart2 size={18} /> Risk Score Trend Comparison
            </h3>

            <div style={{ display: 'flex', alignItems: 'flex-end', gap: '1rem', height: '150px', paddingTop: '1rem', borderBottom: '1px solid var(--border-color)', paddingBottom: '0.5rem', overflowX: 'auto' }}>
              {history.slice(0, 10).reverse().map((scan, idx) => {
                const heightPct = Math.max(10, scan.risk_score);
                const color = scan.risk_score >= 75 ? 'var(--danger-red)' : scan.risk_score >= 50 ? 'var(--warning-orange)' : 'var(--success-green)';

                return (
                  <div key={scan.id || idx} style={{ flex: 1, minWidth: '45px', display: 'flex', flexDirection: 'column', alignItems: 'center', height: '100%', justifyContent: 'flex-end' }}>
                    <span style={{ fontSize: '0.75rem', fontWeight: 700, color: color, marginBottom: '0.25rem' }}>
                      {scan.risk_score}
                    </span>
                    <div style={{
                      width: '100%',
                      maxWidth: '36px',
                      height: `${heightPct}%`,
                      backgroundColor: color,
                      borderRadius: '4px 4px 0 0',
                      transition: 'height 0.5s ease'
                    }} />
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', marginTop: '0.4rem', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', maxWidth: '65px' }} title={scan.project_name}>
                      {scan.project_name}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* History Table */}
        <div className="card">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.25rem' }}>
            <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', margin: 0 }}>
              Scan History Logs ({filteredHistory.length})
            </h3>

            {history.length > 0 && (
              <div style={{ position: 'relative', width: '250px' }}>
                <Search size={15} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-dim)' }} />
                <input
                  type="text"
                  placeholder="Search history..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.45rem 0.75rem 0.45rem 2.2rem',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                    backgroundColor: 'var(--bg-primary)',
                    color: 'var(--text-light)',
                    fontSize: '0.85rem'
                  }}
                />
              </div>
            )}
          </div>

          {loading ? (
            <p style={{ color: 'var(--text-muted)', padding: '1.5rem 0', textAlign: 'center' }}>Loading scan history...</p>
          ) : history.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
              <ShieldAlert size={44} style={{ color: 'var(--text-dim)', marginBottom: '1rem' }} />
              <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem', marginBottom: '1rem' }}>
                No scan history logged yet.
              </p>
              <Link to="/upload/zip" className="btn btn-primary">
                Run Your First Security Scan
              </Link>
            </div>
          ) : filteredHistory.length === 0 ? (
            <p style={{ color: 'var(--text-muted)', padding: '1.5rem 0', textAlign: 'center' }}>
              No scan logs matching "{searchQuery}".
            </p>
          ) : (
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>Scan ID</th>
                    <th style={{ padding: '0.75rem' }}>Project Name</th>
                    <th style={{ padding: '0.75rem' }}>Risk Score</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                    <th style={{ padding: '0.75rem' }}>Total Deps</th>
                    <th style={{ padding: '0.75rem' }}>Created At</th>
                    <th style={{ padding: '0.75rem', textAlign: 'right' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredHistory.map((s) => {
                    const scoreColor = s.risk_score >= 75 ? 'var(--danger-red)' : s.risk_score >= 50 ? 'var(--warning-orange)' : 'var(--success-green)';
                    const formattedDate = s.created_at ? new Date(s.created_at).toLocaleString() : 'N/A';
                    const isDeleting = deletingId === s.id;

                    return (
                      <tr key={s.id} style={{ borderBottom: '1px solid var(--border-color)', opacity: isDeleting ? 0.5 : 1 }}>
                        <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: 'var(--accent-gold)' }}>
                          {s.id ? s.id.slice(0, 8) : 'N/A'}...
                        </td>
                        <td style={{ padding: '0.75rem', fontWeight: 600 }}>{s.project_name || 'Unnamed Project'}</td>
                        <td style={{ padding: '0.75rem', fontWeight: 700, color: scoreColor }}>{s.risk_score} / 100</td>
                        <td style={{ padding: '0.75rem' }}>
                          <span style={{
                            padding: '0.2rem 0.5rem',
                            borderRadius: '4px',
                            fontSize: '0.78rem',
                            backgroundColor: s.status === 'COMPLETED' ? 'var(--success-green-bg)' : 'var(--bg-surface-hover)',
                            color: s.status === 'COMPLETED' ? 'var(--success-green)' : 'var(--text-light)',
                            fontWeight: 600
                          }}>
                            {s.status}
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem' }}>{s.total_dependencies || 0}</td>
                        <td style={{ padding: '0.75rem', color: 'var(--text-dim)', fontSize: '0.85rem' }}>
                          {formattedDate}
                        </td>
                        <td style={{ padding: '0.75rem', textAlign: 'right' }}>
                          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem' }}>
                            <Link to={`/scans/${s.id}`} className="btn btn-outline" style={{ padding: '0.35rem 0.65rem', fontSize: '0.8rem' }}>
                              View <ArrowRight size={13} />
                            </Link>
                            <button
                              onClick={() => handleDeleteScan(s.id, s.project_name)}
                              disabled={isDeleting || clearing}
                              title="Delete Scan Log"
                              style={{
                                padding: '0.35rem 0.55rem',
                                borderRadius: 'var(--radius-sm)',
                                border: '1px solid var(--border-color)',
                                backgroundColor: 'transparent',
                                color: 'var(--danger-red)',
                                cursor: 'pointer',
                                transition: 'all 0.2s'
                              }}
                              onMouseEnter={(e) => e.currentTarget.style.backgroundColor = 'var(--danger-red-bg)'}
                              onMouseLeave={(e) => e.currentTarget.style.backgroundColor = 'transparent'}
                            >
                              <Trash2 size={14} />
                            </button>
                          </div>
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

