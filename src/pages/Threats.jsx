import React from 'react';
import { 
  ShieldAlert, Terminal, AlertOctagon, RefreshCw, FileText, CheckSquare, 
  Lock, Key, Bug, GitFork, ShieldX, ServerCrash 
} from 'lucide-react';

export default function Threats() {
  const threats = [
    {
      icon: <ShieldAlert size={26} style={{ color: 'var(--danger-red)' }} />,
      title: '1. Typosquatting & Brandjacking Attacks',
      description: 'Attackers register package names on public registries (npm, PyPI) that closely mimic popular open-source libraries (e.g. `reqeusts` vs `requests`, `recat` vs `react`, `djanog` vs `django`). Developers accidentally install the typo package, which immediately executes malicious payloads during installation or at runtime.',
      impact: 'Remote code execution (RCE), credential harvesting, and backdoor installation on developer machines.',
      tips: [
        'Enforce lockfile verification (package-lock.json, poetry.lock, Cargo.lock) to pin exact package names and checksum hashes.',
        'Run automated Levenshtein distance checks during local build and CI/CD pipelines.',
        'Configure internal package proxy mirrors with strict name validation filters.'
      ]
    },
    {
      icon: <Terminal size={26} style={{ color: 'var(--accent-gold)' }} />,
      title: '2. Malicious Lifecycle Install Hooks (preinstall / postinstall)',
      description: 'Package managers allow lifecycle scripts like `preinstall`, `postinstall`, or `build` in `package.json` or `setup.py`. Malicious maintainers or compromised maintainer accounts embed obfuscated Node/Python scripts that exfiltrate environment variables (`.env`), SSH private keys, AWS tokens, and browser cookies during `npm install`.',
      impact: 'Secret exfiltration, cloud account compromise, and unauthorized CI/CD pipeline access.',
      tips: [
        'Run `npm install --ignore-scripts` inside build containers whenever feasible.',
        'Use isolated containerized sandboxes for dependency resolution.',
        'Inspect dependency diffs when updating third-party packages.'
      ]
    },
    {
      icon: <AlertOctagon size={26} style={{ color: 'var(--warning-orange)' }} />,
      title: '3. Dependency Confusion (Namespace Substitution)',
      description: 'Organizations frequently build internal private packages without reserving the same namespace on public registries. Attackers publish a public package with higher version numbers using the identical private package name. Build tooling configured with default settings fetches the malicious public package over internal feeds.',
      impact: 'Malicious code injection into corporate production software builds.',
      tips: [
        'Always use official scoped package namespaces (e.g. `@company/internal-pkg`).',
        'Explicitly configure package manager feed priorities in `.npmrc` or `pip.conf`.',
        'Reserve internal package names as private placeholders on public registries.'
      ]
    },
    {
      icon: <RefreshCw size={26} style={{ color: '#30a46c' }} />,
      title: '4. Abandoned & Unmaintained Package Hijacking',
      description: 'Open-source libraries that haven’t been updated for years often accumulate unpatched CVE vulnerabilities. Attackers track expired maintainer email domain names, re-register the domains, request password resets on registry accounts, and publish malicious patch releases to thousands of downstream applications.',
      impact: 'Silent takeover of popular unmaintained packages used in enterprise stacks.',
      tips: [
        'Audit dependency trees regularly for unmaintained or abandoned packages.',
        'Migrate from unmaintained libraries to active, community-backed alternatives.',
        'Monitor maintainer email domain expirations and registry ownership changes.'
      ]
    },
    {
      icon: <FileText size={26} style={{ color: '#60a5fa' }} />,
      title: '5. Deep Transitive Vulnerabilities (Multi-Level CVEs)',
      description: 'Modern applications have 50-100 direct dependencies, but over 1,000+ transitive dependencies 3 to 6 levels deep. Critical vulnerabilities like Log4Shell, ReDoS, and Prototype Pollution hide in sub-dependencies that developers never directly import or inspect.',
      impact: 'Zero-day vulnerability exposure in production servers without developer awareness.',
      tips: [
        'Perform N-level graph traversal on project lockfiles to map full execution chains.',
        'Automate OSV.dev advisory vulnerability matching across all transitive nodes.',
        'Apply minimal semantic version patch upgrades recommended by security advisories.'
      ]
    },
    {
      icon: <Bug size={26} style={{ color: '#c084fc' }} />,
      title: '6. Copyleft License Contamination (Legal & IP Risks)',
      description: 'Sub-dependencies carrying restrictive copyleft licenses (such as GPL-3.0, AGPL-3.0, or SSPL) can create severe legal exposure. Distributing or hosting SaaS applications containing copyleft code can legally mandate open-sourcing proprietary corporate intellectual property.',
      impact: 'Forced disclosure of proprietary codebase, copyright infringement lawsuits, and compliance audits.',
      tips: [
        'Audit all direct and transitive package licenses against SPDX standardized identifiers.',
        'Evaluate license compatibility against project deployment models (HOSTED vs DISTRIBUTED).',
        'Block unapproved license identifiers in CI/CD pipeline gates.'
      ]
    },
    {
      icon: <ShieldX size={26} style={{ color: '#f43f5e' }} />,
      title: '7. Maintainer Account Takeover & Compromised Tokens',
      description: 'Maintainer accounts on npm, PyPI, or RubyGems targeted via phishing or credential stuffing allow attackers to publish compromised updates to legitimate, highly trusted packages without modifying GitHub source code repositories.',
      impact: 'Mass compromise of trusted mainstream packages downloaded millions of times per day.',
      tips: [
        'Enforce Two-Factor Authentication (2FA) for all package publishing accounts.',
        'Verify package signature provenance and build attestations (SLSA / Sigstore).',
        'Use Deptrix graph analysis to detect sudden suspicious release behavior.'
      ]
    }
  ];

  return (
    <div className="page-wrapper">
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Page Header */}
        <section style={{ textAlign: 'center', marginBottom: '3.5rem' }}>
          <h1 style={{ fontSize: '2.8rem', marginBottom: '1rem' }}>
            Supply Chain <span style={{ color: 'var(--danger-red)' }}>Threats & Malware Analysis</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.15rem', maxWidth: '800px', margin: '0 auto', lineHeight: 1.8 }}>
            Understand critical software supply chain attack vectors, malicious package techniques, and actionable developer countermeasures to fortify your engineering pipeline.
          </p>
        </section>

        {/* Threat List Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          {threats.map((threat, idx) => (
            <div key={idx} className="card" style={{ padding: '1.8rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
                {threat.icon}
                <h2 style={{ fontSize: '1.45rem', margin: 0, color: 'var(--text-light)' }}>{threat.title}</h2>
              </div>
              
              <p style={{ color: 'var(--text-muted)', lineHeight: 1.8, fontSize: '0.96rem', marginBottom: '1rem' }}>
                {threat.description}
              </p>

              <div style={{ 
                backgroundColor: 'var(--danger-red-bg)', 
                border: '1px solid var(--danger-red)', 
                borderRadius: 'var(--radius-sm)', 
                padding: '0.75rem 1rem', 
                marginBottom: '1.25rem',
                fontSize: '0.88rem',
                color: 'var(--danger-red)'
              }}>
                <strong>Potential Impact:</strong> {threat.impact}
              </div>

              <div style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-color)',
                borderRadius: 'var(--radius-sm)',
                padding: '1.25rem'
              }}>
                <h4 style={{ fontSize: '0.95rem', color: 'var(--accent-gold)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <CheckSquare size={17} /> Recommended Prevention & Mitigation Steps:
                </h4>
                <ul style={{ color: 'var(--text-light)', fontSize: '0.9rem', lineHeight: 1.7, paddingLeft: '1.2rem' }}>
                  {threat.tips.map((tip, tIdx) => (
                    <li key={tIdx} style={{ marginBottom: '0.4rem' }}>{tip}</li>
                  ))}
                </ul>
              </div>
            </div>
          ))}
        </div>

        {/* Developer Security Checklist Box */}
        <section className="card" style={{ 
          marginTop: '3.5rem', 
          backgroundColor: '#14100e', 
          borderColor: 'var(--border-color-gold)', 
          padding: '2.5rem' 
        }}>
          <h2 style={{ fontSize: '1.8rem', color: 'var(--accent-gold)', marginBottom: '1rem', textAlign: 'center' }}>
            Software Supply Chain Security Best Practices Checklist
          </h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.25rem', marginTop: '1.5rem' }}>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1rem 1.25rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              <strong style={{ color: 'var(--success-green)' }}>✓ Commit Lockfiles</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Always check in lockfiles (package-lock.json, poetry.lock) to guarantee immutable dependency versions across environments.</p>
            </div>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1rem 1.25rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              <strong style={{ color: 'var(--success-green)' }}>✓ Automate Scanning</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Integrate Deptrix automated scans into pull request checks and CI/CD deployment pipelines.</p>
            </div>
            <div style={{ backgroundColor: 'var(--bg-primary)', padding: '1rem 1.25rem', borderRadius: '6px', border: '1px solid var(--border-color)' }}>
              <strong style={{ color: 'var(--success-green)' }}>✓ Audit Install Hooks</strong>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>Review third-party lifecycle install scripts before adding new direct dependencies to project manifests.</p>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
