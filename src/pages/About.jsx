import React from 'react';
import { Shield, Database, AlertCircle, CheckCircle, Cpu, GitBranch, Scale, Server, UserCheck, Lock } from 'lucide-react';

export default function About() {
  return (
    <div className="page-wrapper">
      <div style={{ maxWidth: '960px', margin: '0 auto' }}>
        {/* Header */}
        <section style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <h1 style={{ fontSize: '2.8rem', marginBottom: '1rem' }}>
            About <span style={{ color: 'var(--accent-gold)' }}>Deptrix Security</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.15rem', maxWidth: '780px', margin: '0 auto', lineHeight: 1.8 }}>
            Deptrix is a next-generation Software Supply Chain Risk Analyzer engineered to protect open-source software dependencies through real-time vulnerability lookups, typosquatting malware detection, license compliance auditing, and graph traversal attack path analysis.
          </p>
        </section>

        {/* The Problem */}
        <section className="card" style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--accent-gold)', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <AlertCircle size={24} /> The Supply Chain Security Challenge
          </h2>
          <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem', fontSize: '0.98rem' }}>
            Modern software engineering relies heavily on thousands of open-source third-party dependencies. While open-source packages dramatically accelerate product development, they introduce severe security risks into application pipelines.
          </p>
          <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, marginBottom: '1rem', fontSize: '0.98rem' }}>
            Attackers increasingly target the supply chain rather than application code directly. They publish lookalike typosquatting packages, hijack unmaintained maintainer accounts, introduce lifecycle install scripts (`preinstall`/`postinstall`) that harvest secrets, or exploit zero-day CVE vulnerabilities buried deep inside transitive sub-dependencies.
          </p>
          <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, fontSize: '0.98rem' }}>
            Without full visibility into N-level transitive dependency trees, engineering teams unknowingly push vulnerable code or malicious backdoors directly into production deployments.
          </p>
        </section>

        {/* Our Mission */}
        <section className="card" style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--accent-gold)', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Shield size={24} /> Platform Mission & Core Objectives
          </h2>
          <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, fontSize: '0.98rem', marginBottom: '1.2rem' }}>
            Deptrix was developed to democratize software supply chain security for developers, DevOps engineers, and security teams. Our goal is to make deep graph inspection as effortless as running a simple build check.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.2rem' }}>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: 'var(--text-light)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle size={16} style={{ color: 'var(--success-green)' }} /> Automated Transparency
              </h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>Give developers complete visibility into direct and transitive dependencies across npm, PyPI, Maven, Go, and Cargo ecosystems.</p>
            </div>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: 'var(--text-light)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle size={16} style={{ color: 'var(--success-green)' }} /> Proactive Threat Defense
              </h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>Detect typosquatting lookalikes, suspicious install hooks, and copyleft license contamination before deployment.</p>
            </div>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1.2rem', borderRadius: 'var(--radius-sm)', border: '1px solid var(--border-color)' }}>
              <h4 style={{ color: 'var(--text-light)', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                <CheckCircle size={16} style={{ color: 'var(--success-green)' }} /> Actionable Patching
              </h4>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>Provide minimal non-breaking upgrade version recommendations and safe alternative package suggestions.</p>
            </div>
          </div>
        </section>

        {/* How Scanning Works & Data Sources */}
        <section className="card" style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.6rem', color: 'var(--accent-gold)', marginBottom: '1.2rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <Database size={24} /> Data Sources & Analysis Engine Pipeline
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            <div style={{ borderLeft: '3px solid var(--accent-gold)', paddingLeft: '1rem' }}>
              <h4 style={{ color: 'var(--text-light)', fontSize: '1.05rem', marginBottom: '0.3rem' }}>1. OSV.dev Database Integration</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.7 }}>
                Deptrix queries the Open Source Vulnerability (OSV.dev) batch API in real-time, matching package identifiers and version strings against authoritative CVE advisories across npm, PyPI, Go, Maven, Cargo, and Packagist.
              </p>
            </div>

            <div style={{ borderLeft: '3px solid var(--danger-red)', paddingLeft: '1rem' }}>
              <h4 style={{ color: 'var(--text-light)', fontSize: '1.05rem', marginBottom: '0.3rem' }}>2. Levenshtein Distance Typosquatting Engine</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.7 }}>
                Our distance heuristic algorithms evaluate dependency package names against top 100 ecosystem libraries (e.g. <code>react</code>, <code>requests</code>, <code>express</code>), flagging typosquatting squatters and lookalike malware risks.
              </p>
            </div>

            <div style={{ borderLeft: '3px solid var(--warning-orange)', paddingLeft: '1rem' }}>
              <h4 style={{ color: 'var(--text-light)', fontSize: '1.05rem', marginBottom: '0.3rem' }}>3. SPDX License Compliance Matrix</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.7 }}>
                Integrates SPDX standardized license identifiers to assess legal compatibility against specified project deployment models (HOSTED, INTERNAL, DISTRIBUTED), alerting teams to restrictive copyleft GPL/AGPL licenses.
              </p>
            </div>

            <div style={{ borderLeft: '3px solid var(--success-green)', paddingLeft: '1rem' }}>
              <h4 style={{ color: 'var(--text-light)', fontSize: '1.05rem', marginBottom: '0.3rem' }}>4. BFS/DFS Execution Chain Graph Traversal</h4>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.7 }}>
                Uses Breadth-First Search (BFS) and Depth-First Search (DFS) graph traversal to map execution paths from application entrypoints to flagged sub-dependencies, rating reachability and exposure impact.
              </p>
            </div>
          </div>
        </section>

        {/* Corporate & Author Governance */}
        <section className="card" style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', color: 'var(--accent-gold)', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <UserCheck size={22} /> Platform Ownership & Contact Details
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '1.5rem', marginTop: '1rem' }}>
            <div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}><strong>Lead Engineer & Creator:</strong> Omkar Nalawade</p>
              <p style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}><strong>Contact Email:</strong> <a href="mailto:nalawadeomkar0508@gmail.com" style={{ color: 'var(--accent-gold)' }}>nalawadeomkar0508@gmail.com</a></p>
              <p style={{ color: 'var(--text-muted)' }}><strong>Headquarters:</strong> Pune, Maharashtra, India</p>
            </div>
            <div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}><strong>Platform Version:</strong> v1.0.0 Production Release</p>
              <p style={{ color: 'var(--text-muted)', marginBottom: '0.5rem' }}><strong>Security Advisories Source:</strong> OSV.dev / GHSA / NVD</p>
              <p style={{ color: 'var(--text-muted)' }}><strong>Authentication:</strong> JWT + Security Q&A + SMTP Mail OTP</p>
            </div>
          </div>
        </section>

        {/* Limitations & Disclaimer */}
        <section className="card" style={{ backgroundColor: '#14100e', borderColor: 'var(--warning-orange)' }}>
          <h2 style={{ fontSize: '1.3rem', color: 'var(--warning-orange)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
            <AlertCircle size={20} /> System Boundaries & Responsibility Disclaimer
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.92rem', lineHeight: 1.7 }}>
            Deptrix provides security vulnerability matches, malware signals, and license compliance indicators based on static manifest analysis and public advisory databases. While Deptrix drastically reduces supply chain attack surface exposure, it does not replace runtime defenses, secure coding policies, or continuous zero-day monitoring.
          </p>
        </section>
      </div>
    </div>
  );
}
