import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import api from '../services/api';
import RiskGauge from '../components/RiskGauge';
import AttackPathView from '../components/AttackPathView';
import {
  ShieldAlert, ShieldCheck, Download, RefreshCw, ChevronDown, ChevronRight,
  AlertTriangle, Scale, GitBranch, Cpu, FileText, CheckCircle2
} from 'lucide-react';

export default function ScanReport() {
  const { scanId } = useParams();
  const [reportData, setReportData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [polling, setPolling] = useState(false);
  const [activeTab, setActiveTab] = useState('summary');
  
  // Filters & Sorting for Vulnerabilities
  const [sevFilter, setSevFilter] = useState('ALL');
  const [sortByCvss, setSortByCvss] = useState(true);

  // Collapsible Dependency Tree state
  const [expandedNodes, setExpandedNodes] = useState({});

  const fetchReport = async () => {
    try {
      const res = await api.get(`/scans/${scanId}/report`);
      setReportData(res.data);
      if (res.data.status !== 'COMPLETED' && res.data.status !== 'FAILED') {
        setPolling(true);
      } else {
        setPolling(false);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
  }, [scanId]);

  useEffect(() => {
    let interval;
    if (polling) {
      interval = setInterval(fetchReport, 3000);
    }
    return () => clearInterval(interval);
  }, [polling]);

  const handleRescan = async () => {
    try {
      const res = await api.post(`/scans/${scanId}/rescan`);
      window.location.href = `/scans/${res.data.new_scan_id}`;
    } catch (err) {
      alert('Failed to trigger re-scan.');
    }
  };

  const handleExportPDF = () => {
    window.open(`/api/scans/${scanId}/pdf`, '_blank');
  };

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(reportData, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `deptrix-report-${scanId.slice(0, 8)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const toggleNode = (nodeId) => {
    setExpandedNodes(prev => ({ ...prev, [nodeId]: !prev[nodeId] }));
  };

  if (loading) {
    return (
      <div className="page-wrapper authenticated" style={{ textAlign: 'center', padding: '4rem 0' }}>
        <h2 style={{ color: 'var(--accent-gold)' }}>Loading Scan Analysis...</h2>
      </div>
    );
  }

  if (!reportData) {
    return (
      <div className="page-wrapper authenticated" style={{ textAlign: 'center', padding: '4rem 0' }}>
        <h2>Scan Report Not Found</h2>
      </div>
    );
  }

  // Scan still in progress state
  if (reportData.status !== 'COMPLETED' && reportData.status !== 'FAILED') {
    return (
      <div className="page-wrapper authenticated" style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
        <div className="card" style={{ padding: '3rem 2rem' }}>
          <RefreshCw size={48} className="spin-icon" style={{ color: 'var(--accent-gold)', marginBottom: '1.5rem' }} />
          <h2 style={{ fontSize: '1.8rem', marginBottom: '0.5rem' }}>Analysis In Progress</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
            Current Status: <strong style={{ color: 'var(--accent-gold)' }}>{reportData.status}</strong>
          </p>

          <div style={{
            backgroundColor: 'var(--bg-primary)',
            borderRadius: '10px',
            overflow: 'hidden',
            height: '10px',
            marginBottom: '1.5rem'
          }}>
            <div style={{
              width: `${reportData.status === 'PARSING' ? 25 : reportData.status === 'QUERYING_OSV' ? 60 : 85}%`,
              height: '100%',
              backgroundColor: 'var(--accent-gold)',
              transition: 'width 0.5s ease'
            }} />
          </div>

          <p style={{ fontSize: '0.85rem', color: 'var(--text-dim)' }}>
            Parsing manifests, batch querying OSV advisories, and evaluating attack paths...
          </p>
        </div>
      </div>
    );
  }

  const summary = reportData.summary || {};
  const recs = reportData.recommendations || {};

  // Filtered vulnerabilities
  let filteredFindings = reportData.findings || [];
  if (sevFilter !== 'ALL') {
    filteredFindings = filteredFindings.filter(f => f.severity === sevFilter);
  }
  if (sortByCvss) {
    filteredFindings.sort((a, b) => (b.cvss_score || 0) - (a.cvss_score || 0));
  }

  return (
    <div className="page-wrapper authenticated">
      <div style={{ maxWidth: '1250px', margin: '0 auto' }}>
        {/* Header Bar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '2rem' }}>
          <div>
            <h1 style={{ fontSize: reportData.project_name.length > 25 ? '1.5rem' : '2rem', margin: 0, wordBreak: 'break-all', overflowWrap: 'anywhere', maxWidth: '100%' }}>
              Scan Report: <span style={{ color: 'var(--accent-gold)' }}>{reportData.project_name}</span>
            </h1>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginTop: '0.25rem' }}>
              Scan ID: <span style={{ fontFamily: 'monospace' }}>{scanId}</span> | Scanned on {new Date(reportData.created_at).toLocaleString()}
            </p>
          </div>

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button onClick={handleRescan} className="btn btn-outline" style={{ padding: '0.55rem 1rem', fontSize: '0.88rem' }}>
              <RefreshCw size={15} /> Re-scan
            </button>
            <button onClick={handleExportPDF} className="btn btn-outline" style={{ padding: '0.55rem 1rem', fontSize: '0.88rem' }}>
              <FileText size={15} /> Export PDF
            </button>
            <button onClick={handleExportJSON} className="btn btn-primary" style={{ padding: '0.55rem 1rem', fontSize: '0.88rem' }}>
              <Download size={15} /> Export JSON
            </button>
          </div>
        </div>

        {/* Top Overview Grid: Risk Score Gauge + Severity Cards */}
        <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '1.5rem', marginBottom: '2rem' }}>
          <div className="card" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <RiskGauge score={reportData.risk_score} />
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))', gap: '1rem' }}>
            <div className="card" style={{ borderLeft: '4px solid var(--danger-red)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>CRITICAL VULNS</span>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--danger-red)', marginTop: '0.2rem' }}>
                {summary.critical_vulns || 0}
              </div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid var(--warning-orange)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>HIGH VULNS</span>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--warning-orange)', marginTop: '0.2rem' }}>
                {summary.high_vulns || 0}
              </div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #facc15' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>SUSPICIOUS PKGS</span>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#facc15', marginTop: '0.2rem' }}>
                {summary.suspicious_packages || 0}
              </div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid var(--accent-gold)' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>LICENSE CONFLICTS</span>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: 'var(--accent-gold)', marginTop: '0.2rem' }}>
                {summary.license_conflicts || 0}
              </div>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #30a46c' }}>
              <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL DEPS</span>
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#30a46c', marginTop: '0.2rem' }}>
                {summary.total_dependencies || 0}
              </div>
            </div>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          borderBottom: '1px solid var(--border-color)',
          marginBottom: '1.5rem',
          overflowX: 'auto',
          paddingBottom: '0.2rem'
        }}>
          {[
            { id: 'summary', label: 'Risk Summary' },
            { id: 'tree', label: 'Dependency Tree' },
            { id: 'vulns', label: `Vulnerabilities (${reportData.findings.length})` },
            { id: 'suspicious', label: `Suspicious (${reportData.suspicious_signals.length})` },
            { id: 'licenses', label: `License Conflicts (${reportData.license_findings.length})` },
            { id: 'paths', label: `Attack Paths (${reportData.attack_paths.length})` },
            { id: 'solutions', label: 'Solutions & Alternatives' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                backgroundColor: 'transparent',
                border: 'none',
                borderBottom: activeTab === tab.id ? '2px solid var(--accent-gold)' : '2px solid transparent',
                color: activeTab === tab.id ? 'var(--accent-gold)' : 'var(--text-muted)',
                padding: '0.65rem 1.1rem',
                fontWeight: 600,
                fontSize: '0.9rem',
                cursor: 'pointer',
                whiteSpace: 'nowrap'
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* TAB 1: RISK SUMMARY & POTENTIAL IMPACT */}
        {activeTab === 'summary' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '0.75rem' }}>Risk Overview</h3>
              <p style={{ color: 'var(--text-light)', fontSize: '1rem', lineHeight: 1.7 }}>
                {summary.description}
              </p>
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '0.75rem' }}>Potential Impact Analysis</h3>
              <ul style={{ color: 'var(--text-muted)', lineHeight: 1.8, paddingLeft: '1.2rem' }}>
                <li><strong>Remote Code Execution (RCE):</strong> High/Critical CVSS vulnerabilities in network parsing dependencies can allow unauthenticated attackers to execute commands.</li>
                <li><strong>Credential Exfiltration:</strong> Typosquatted packages and malicious install scripts threaten to steal environment variables, API tokens, and cloud secrets.</li>
                <li><strong>Legal & Compliance Exposure:</strong> Unwanted copyleft (GPL/AGPL) licenses can mandate public disclosure of host application source code.</li>
              </ul>
            </div>
          </div>
        )}

        {/* TAB 2: COLLAPSIBLE DEPENDENCY TREE */}
        {activeTab === 'tree' && (
          <div className="card">
            <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1.25rem' }}>
              Collapsible Dependency Tree
            </h3>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {reportData.dependencies.map((dep) => {
                const hasVuln = reportData.findings.some(f => f.dependency_name === dep.name);
                const hasSusp = reportData.suspicious_signals.some(s => s.dependency_name === dep.name);
                const isFlagged = hasVuln || hasSusp;
                const isExpanded = expandedNodes[dep.id];

                return (
                  <div key={dep.id} style={{
                    backgroundColor: isFlagged ? 'rgba(229, 72, 77, 0.08)' : 'var(--bg-primary)',
                    border: `1px solid ${isFlagged ? 'var(--danger-red)' : 'var(--border-color)'}`,
                    borderRadius: 'var(--radius-sm)',
                    padding: '0.75rem 1rem'
                  }}>
                    <div
                      onClick={() => toggleNode(dep.id)}
                      style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', cursor: 'pointer' }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {isExpanded ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                        <span style={{ fontWeight: 600, color: isFlagged ? 'var(--danger-red)' : 'var(--text-light)' }}>
                          {dep.name} @ {dep.version}
                        </span>
                        <span style={{
                          fontSize: '0.75rem',
                          padding: '0.15rem 0.5rem',
                          borderRadius: '3px',
                          backgroundColor: 'var(--bg-surface-hover)',
                          color: 'var(--text-muted)'
                        }}>
                          {dep.is_direct ? 'Direct' : `Transitive (Depth: ${dep.depth})`}
                        </span>
                      </div>

                      <div>
                        {isFlagged && (
                          <span style={{ color: 'var(--danger-red)', fontWeight: 700, fontSize: '0.8rem' }}>
                            ● FLAG RISK
                          </span>
                        )}
                      </div>
                    </div>

                    {isExpanded && (
                      <div style={{ marginTop: '0.75rem', paddingTop: '0.75rem', borderTop: '1px solid var(--border-color)', fontSize: '0.88rem', color: 'var(--text-muted)' }}>
                        <p>Ecosystem: <strong>{dep.ecosystem}</strong></p>
                        <p>Parent Node: <strong>{dep.parent_name || 'Root Application'}</strong></p>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* TAB 3: VULNERABILITIES */}
        {activeTab === 'vulns' && (
          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem', flexWrap: 'wrap', gap: '1rem' }}>
              <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', margin: 0 }}>
                OSV Vulnerability Findings
              </h3>

              <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
                <select
                  value={sevFilter}
                  onChange={(e) => setSevFilter(e.target.value)}
                  className="form-control"
                  style={{ padding: '0.4rem 0.75rem', fontSize: '0.85rem' }}
                >
                  <option value="ALL">All Severities</option>
                  <option value="CRITICAL">Critical Only</option>
                  <option value="HIGH">High Only</option>
                  <option value="MEDIUM">Medium Only</option>
                  <option value="LOW">Low Only</option>
                </select>
              </div>
            </div>

            {filteredFindings.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No vulnerabilities matching selected filter.</p>
            ) : (
              <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                      <th style={{ padding: '0.75rem' }}>Package</th>
                      <th style={{ padding: '0.75rem' }}>OSV ID</th>
                      <th style={{ padding: '0.75rem' }}>Severity / CVSS</th>
                      <th style={{ padding: '0.75rem' }}>Fixed Version</th>
                      <th style={{ padding: '0.75rem' }}>Summary</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredFindings.map((f) => (
                      <tr key={f.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                        <td style={{ padding: '0.75rem', fontWeight: 600 }}>{f.dependency_name} ({f.dependency_version})</td>
                        <td style={{ padding: '0.75rem', fontFamily: 'monospace', color: 'var(--accent-gold)' }}>{f.osv_id}</td>
                        <td style={{ padding: '0.75rem' }}>
                          <span style={{
                            color: f.severity === 'CRITICAL' ? 'var(--danger-red)' : f.severity === 'HIGH' ? 'var(--warning-orange)' : '#facc15',
                            fontWeight: 700
                          }}>
                            {f.severity} ({f.cvss_score || 'N/A'})
                          </span>
                        </td>
                        <td style={{ padding: '0.75rem', color: 'var(--success-green)', fontWeight: 600 }}>{f.fixed_version}</td>
                        <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{f.summary}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 4: SUSPICIOUS PACKAGES */}
        {activeTab === 'suspicious' && (
          <div className="card">
            <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1.25rem' }}>
              Suspicious Packages & Typosquatting Signals
            </h3>

            {reportData.suspicious_signals.length === 0 ? (
              <p style={{ color: 'var(--text-muted)' }}>No suspicious package lookalikes or malicious signals detected.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {reportData.suspicious_signals.map((s) => (
                  <div key={s.id} style={{
                    backgroundColor: '#16100e',
                    border: '1px solid var(--danger-red)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '1.25rem'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                      <span style={{ fontWeight: 700, color: 'var(--danger-red)', fontSize: '1.05rem' }}>
                        {s.dependency_name}
                      </span>
                      <span style={{
                        padding: '0.2rem 0.6rem',
                        borderRadius: '4px',
                        fontSize: '0.78rem',
                        fontWeight: 700,
                        backgroundColor: 'var(--danger-red-bg)',
                        color: 'var(--danger-red)'
                      }}>
                        {s.signal_type}
                      </span>
                    </div>
                    <p style={{ color: 'var(--text-light)', fontSize: '0.92rem' }}>{s.description}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* TAB 5: LICENSE CONFLICTS */}
        {activeTab === 'licenses' && (
          <div className="card">
            <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1.25rem' }}>
              SPDX License Compatibility Matrix
            </h3>

            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.9rem' }}>
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)' }}>
                    <th style={{ padding: '0.75rem' }}>Dependency</th>
                    <th style={{ padding: '0.75rem' }}>SPDX License</th>
                    <th style={{ padding: '0.75rem' }}>Status</th>
                    <th style={{ padding: '0.75rem' }}>Conflict With</th>
                    <th style={{ padding: '0.75rem' }}>Details</th>
                  </tr>
                </thead>
                <tbody>
                  {reportData.license_findings.map((l) => (
                    <tr key={l.id} style={{ borderBottom: '1px solid var(--border-color)' }}>
                      <td style={{ padding: '0.75rem', fontWeight: 600 }}>{l.dependency_name}</td>
                      <td style={{ padding: '0.75rem', fontFamily: 'monospace' }}>{l.license_spdx}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          color: l.status === 'CONFLICT' ? 'var(--danger-red)' : l.status === 'UNKNOWN' ? 'var(--warning-orange)' : 'var(--success-green)',
                          fontWeight: 700
                        }}>
                          {l.status}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{l.conflict_with || 'None'}</td>
                      <td style={{ padding: '0.75rem', color: 'var(--text-muted)' }}>{l.description}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 6: ATTACK PATHS */}
        {activeTab === 'paths' && (
          <div className="card">
            <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1.25rem' }}>
              Attack Path Analysis Chains
            </h3>
            <AttackPathView attackPaths={reportData.attack_paths} />
          </div>
        )}

        {/* TAB 7: SOLUTIONS & SAFER ALTERNATIVES */}
        {activeTab === 'solutions' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div className="card">
              <h3 style={{ fontSize: '1.3rem', color: 'var(--success-green)', marginBottom: '1rem' }}>
                Recommended Minimal Patch Upgrades
              </h3>
              {(!recs.upgrade_solutions || recs.upgrade_solutions.length === 0) ? (
                <p style={{ color: 'var(--text-muted)' }}>No required upgrades detected. Dependencies are up to date.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {recs.upgrade_solutions.map((sol, idx) => (
                    <div key={idx} style={{
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '1rem'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.4rem' }}>
                        <strong style={{ color: 'var(--text-light)' }}>{sol.package_name}</strong>
                        <span style={{ color: 'var(--success-green)', fontWeight: 700 }}>
                          Upgrade to: {sol.recommended_version}
                        </span>
                      </div>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>{sol.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="card">
              <h3 style={{ fontSize: '1.3rem', color: 'var(--accent-gold)', marginBottom: '1rem' }}>
                Safer Package Alternatives
              </h3>
              {(!recs.safer_alternatives || recs.safer_alternatives.length === 0) ? (
                <p style={{ color: 'var(--text-muted)' }}>No alternative replacements required.</p>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                  {recs.safer_alternatives.map((alt, idx) => (
                    <div key={idx} style={{
                      backgroundColor: 'var(--bg-primary)',
                      border: '1px solid var(--border-color)',
                      borderRadius: 'var(--radius-sm)',
                      padding: '1rem'
                    }}>
                      <p style={{ color: 'var(--danger-red)', fontWeight: 600 }}>Replace Flagged Package: {alt.flagged_package}</p>
                      <p style={{ color: 'var(--success-green)', fontWeight: 700 }}>Authentic Alternative: {alt.recommended_alternative}</p>
                      <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', marginTop: '0.4rem' }}>{alt.reason}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
