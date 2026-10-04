import React from 'react';
import { Link } from 'react-router-dom';
import DependencyGraphVisual from '../components/DependencyGraphVisual';
import { 
  ShieldCheck, Cpu, GitBranch, AlertTriangle, Scale, Lock, ArrowRight, 
  Layers, Search, FileCode, CheckCircle2, ShieldAlert, Zap, BookOpen 
} from 'lucide-react';

export default function Home() {
  return (
    <div className="page-wrapper">
      {/* Hero Section */}
      <section style={{ textAlign: 'center', padding: '3.5rem 1rem 3rem', maxWidth: '960px', margin: '0 auto' }}>
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '0.5rem',
          padding: '0.4rem 1.1rem',
          borderRadius: '20px',
          backgroundColor: 'var(--accent-gold-glow)',
          color: 'var(--accent-gold)',
          fontSize: '0.88rem',
          fontWeight: 600,
          marginBottom: '1.5rem',
          border: '1px solid var(--border-color-gold)'
        }}>
          <ShieldCheck size={18} /> Software Supply Chain Security & Risk Analyzer
        </div>

        <h1 style={{ fontSize: '3.2rem', lineHeight: 1.2, marginBottom: '1.5rem', letterSpacing: '-0.5px' }}>
          Your dependencies can become your <span style={{ color: 'var(--accent-gold)' }}>attack surface</span>
        </h1>

        <p style={{ color: 'var(--text-muted)', fontSize: '1.18rem', marginBottom: '2.5rem', lineHeight: 1.8, maxWidth: '850px', margin: '0 auto 2.5rem' }}>
          Deptrix automatically scans software supply chain manifests, lockfiles, and GitHub repositories in real-time. Detect CVE vulnerabilities, typosquatting malware, copyleft license risks, and compute execution attack paths before code enters production.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.2rem', flexWrap: 'wrap' }}>
          <Link to="/signup-step1" className="btn btn-primary" style={{ padding: '0.85rem 2.2rem', fontSize: '1.05rem', fontWeight: 700 }}>
            Start Free Security Scan <ArrowRight size={18} />
          </Link>
          <Link to="/threats" className="btn btn-outline" style={{ padding: '0.85rem 2rem', fontSize: '1.05rem' }}>
            Explore Supply Chain Threats
          </Link>
        </div>
      </section>

      {/* Key Metrics / Highlights Bar */}
      <section style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
        gap: '1.2rem', 
        margin: '1rem 0 3.5rem' 
      }}>
        {[
          { label: 'Indexed CVE Advisories', val: '100,000+', icon: <Cpu size={20} style={{ color: 'var(--accent-gold)' }} /> },
          { label: 'Ecosystems Supported', val: '6+ Major Platforms', icon: <Layers size={20} style={{ color: '#60a5fa' }} /> },
          { label: 'Graph Traversal Depth', val: 'Full Transitive', icon: <GitBranch size={20} style={{ color: 'var(--success-green)' }} /> },
          { label: 'Malware Engine', val: 'Levenshtein Heuristics', icon: <ShieldAlert size={20} style={{ color: 'var(--danger-red)' }} /> },
        ].map((stat, i) => (
          <div key={i} className="card" style={{ textAlign: 'center', padding: '1.25rem 1rem' }}>
            <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '0.4rem' }}>{stat.icon}</div>
            <div style={{ fontSize: '1.4rem', fontWeight: 'bold', color: 'var(--text-light)', fontFamily: 'var(--font-heading)' }}>{stat.val}</div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Interactive Graph Banner */}
      <section style={{ margin: '2rem 0 4rem' }}>
        <DependencyGraphVisual />
      </section>

      {/* How Deptrix Works in 4 Steps */}
      <section style={{ margin: '4.5rem 0' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2.4rem', marginBottom: '0.5rem' }}>
            How Deptrix Works in <span style={{ color: 'var(--accent-gold)' }}>4 Steps</span>
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
            From static manifest upload to deep graph analysis and actionable patch resolution.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
          {[
            { 
              step: '01', 
              title: 'Upload Manifests', 
              text: 'Upload ZIP project archives, paste GitHub repository URLs, or select lockfiles (package-lock.json, requirements.txt, yarn.lock, etc).' 
            },
            { 
              step: '02', 
              title: 'Dependency Graph Construction', 
              text: 'Deptrix automatically parses project lockfiles and builds a full direct and N-level transitive dependency tree.' 
            },
            { 
              step: '03', 
              title: 'Multi-Source Risk Audit', 
              text: 'Real-time OSV.dev advisory lookups, Levenshtein distance typosquatting checks, and SPDX legal compatibility matrix evaluation.' 
            },
            { 
              step: '04', 
              title: 'Actionable Audit Report', 
              text: 'Get an overall Risk Score (0-100), reachability attack paths, minimal version patch solutions, and printable PDF audit reports.' 
            }
          ].map((item, i) => (
            <div key={i} className="card" style={{ position: 'relative', overflow: 'hidden' }}>
              <span style={{ 
                fontSize: '2.5rem', 
                fontFamily: 'var(--font-heading)', 
                color: 'var(--accent-gold)', 
                display: 'block', 
                marginBottom: '0.5rem',
                opacity: 0.9 
              }}>
                {item.step}
              </span>
              <h3 style={{ fontSize: '1.25rem', marginBottom: '0.6rem' }}>{item.title}</h3>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.93rem', lineHeight: 1.7 }}>{item.text}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Core Security Protection Capabilities */}
      <section style={{ margin: '4.5rem 0' }}>
        <div style={{ textAlign: 'center', marginBottom: '3rem' }}>
          <h2 style={{ fontSize: '2.4rem', marginBottom: '0.5rem' }}>
            Comprehensive Supply Chain Risk Protection
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.05rem' }}>
            Shielding your application pipeline against known CVEs, malicious packages, and legal compliance traps.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '1.75rem' }}>
          <div className="card">
            <Cpu size={32} style={{ color: 'var(--accent-gold)', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>OSV.dev Vulnerability Detection</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Queries open-source vulnerability databases to identify direct and transitive CVE vulnerabilities with exact CVSS severity scores, affected version ranges, and fixed releases.
            </p>
          </div>

          <div className="card">
            <AlertTriangle size={32} style={{ color: 'var(--danger-red)', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>Typosquatting & Malware Engine</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Detects lookalike package names targeting popular libraries, unmaintained packages, lifecycle install hooks (`preinstall`/`postinstall`), and confirmed malicious packages.
            </p>
          </div>

          <div className="card">
            <Scale size={32} style={{ color: 'var(--warning-orange)', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>SPDX License Conflict Matrix</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Parses license tags across all direct and transitive dependencies and evaluates legal compatibility against project deployment models (HOSTED, INTERNAL, DISTRIBUTED) to prevent copyleft GPL/AGPL contamination.
            </p>
          </div>

          <div className="card">
            <GitBranch size={32} style={{ color: 'var(--success-green)', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>Attack Path Graph Traversal</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Executes BFS/DFS graph search algorithms to construct precise structural execution chains from your application root down to vulnerable target nodes, identifying reachable code paths.
            </p>
          </div>

          <div className="card">
            <Zap size={32} style={{ color: '#60a5fa', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>Minimal Patch Upgrade Engine</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Recommends the smallest safe semantic version increment required to resolve security vulnerabilities without breaking existing application APIs or introduces unnecessary major changes.
            </p>
          </div>

          <div className="card">
            <FileCode size={32} style={{ color: '#c084fc', marginBottom: '1rem' }} />
            <h3 style={{ marginBottom: '0.6rem', fontSize: '1.3rem' }}>Printable Audit Reports</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.94rem', lineHeight: 1.7 }}>
              Generate comprehensive, executive-ready PDF audit reports formatted with clean `@media print` CSS styling for compliance reviews, security team sharing, and stakeholder sign-off.
            </p>
          </div>
        </div>
      </section>

      {/* Why Supply Chain Security Matters */}
      <section className="card" style={{ 
        margin: '4.5rem 0', 
        backgroundColor: '#14100e', 
        borderColor: 'var(--border-color-gold)',
        padding: '2.5rem'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
          <ShieldAlert size={26} style={{ color: 'var(--danger-red)' }} />
          <h2 style={{ fontSize: '1.8rem', color: 'var(--accent-gold)' }}>Why Software Supply Chain Security Matters</h2>
        </div>
        <p style={{ color: 'var(--text-muted)', fontSize: '1rem', lineHeight: 1.8, marginBottom: '1.25rem' }}>
          Over <strong>80% of code in modern enterprise applications</strong> consists of open-source third-party dependencies. Traditional security tools analyze only your proprietary source code, completely ignoring the thousands of sub-dependencies imported behind the scenes.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.2rem', marginTop: '1.5rem' }}>
          <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <h4 style={{ color: 'var(--danger-red)', marginBottom: '0.4rem' }}>Typosquatting Risk</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>Developers accidentally install lookalike packages like <code>reqeusts</code> instead of <code>requests</code>, executing malware on developer laptops.</p>
          </div>
          <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <h4 style={{ color: 'var(--warning-orange)', marginBottom: '0.4rem' }}>Transitive Vulnerabilities</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>A zero-day CVE in a sub-dependency 5 levels deep can compromise your entire production cloud environment.</p>
          </div>
          <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
            <h4 style={{ color: 'var(--accent-gold)', marginBottom: '0.4rem' }}>Legal License Risks</h4>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)' }}>Incompatible copyleft licenses (GPL/AGPL) in transitive libraries can force organizations to open-source proprietary code.</p>
          </div>
        </div>
      </section>

      {/* Supported Ecosystems & Lockfiles */}
      <section className="card" style={{ textAlign: 'center', padding: '2.5rem', margin: '4.5rem 0' }}>
        <h3 style={{ fontSize: '1.6rem', color: 'var(--accent-gold)', marginBottom: '0.75rem' }}>
          Supported Ecosystems & Lockfile Formats
        </h3>
        <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', marginBottom: '1.5rem' }}>
          Deptrix parses manifest files across major programming ecosystems with deep transitive resolution.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '0.85rem' }}>
          {[
            'package.json', 'package-lock.json', 'yarn.lock',
            'requirements.txt', 'poetry.lock', 'Pipfile.lock',
            'pom.xml', 'build.gradle',
            'composer.json', 'composer.lock',
            'go.mod', 'Cargo.lock'
          ].map((file, idx) => (
            <span key={idx} style={{
              padding: '0.45rem 1.1rem',
              backgroundColor: 'var(--bg-surface-hover)',
              border: '1px solid var(--border-color)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.9rem',
              color: 'var(--text-light)',
              fontFamily: 'monospace'
            }}>
              {file}
            </span>
          ))}
        </div>
      </section>

      {/* Call To Action Box */}
      <section style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-color-gold)',
        borderRadius: 'var(--radius-md)',
        padding: '3.5rem 2rem',
        textAlign: 'center',
        margin: '4rem 0',
        boxShadow: 'var(--shadow-card)'
      }}>
        <h2 style={{ fontSize: '2.2rem', marginBottom: '1rem' }}>Ready to Secure Your Software Supply Chain?</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '2rem', maxWidth: '650px', margin: '0 auto 2rem', fontSize: '1.05rem', lineHeight: 1.7 }}>
          Join security-conscious engineering teams. Create your account in minutes and perform automated security scans across your repositories.
        </p>
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <Link to="/signup-step1" className="btn btn-primary" style={{ padding: '0.9rem 2.4rem', fontSize: '1.1rem', fontWeight: 700 }}>
            Create Account & Scan Now
          </Link>
          <Link to="/login" className="btn btn-outline" style={{ padding: '0.9rem 2rem', fontSize: '1.1rem' }}>
            Sign In to Dashboard
          </Link>
        </div>
      </section>
    </div>
  );
}
