# Deptrix - Software Supply Chain Risk Analyzer

**Deptrix** is a production-grade Software Supply Chain Security & Risk Analysis application designed to detect open-source vulnerabilities (CVEs via OSV.dev), typosquatting malware, copyleft license risks, and compute full transitive attack paths before code deployment.

---

## Brand Theme & Color Palette

- **Background:** Near-black brown (`#0d0a08`)
- **Card Surfaces:** Dark brown/charcoal (`#171210`)
- **Accent:** Copper / Gold (`#c49a6c`)
- **Light Text:** Soft Sand (`#efe6dc`)
- **Muted Text:** Soft Muted Grey-Brown (`#a89a8c`)
- **Danger:** Deep Red (`#e5484d`)
- **Success:** Emerald Green (`#30a46c`)

---

## How results are calculated

Deptrix uses a transparent, empirical static analysis pipeline to compute all metrics directly from uploaded project manifests, lockfiles (`package-lock.json` v3/v2/v1), and source code (`src/`). **Zero sample or fallback data is used.**

### 1. Dependency Counts & Topology
- **Total Dependencies**: Computed from exact non-root entries in `package-lock.json`'s `packages` map (or lockfile v1 `dependencies`).
- **Direct Dependencies**: Dependencies declared in root `package.json` (`dependencies` and `devDependencies`).
- **Transitive Dependencies**: Nested sub-dependencies (`depth > 1`).

### 2. Vulnerability Identification & OSV.dev Lookup
- Each parsed dependency `(ecosystem, name, version)` is queried against the live OSV.dev batch API (`https://api.osv.dev/v1/querybatch`).
- Full advisory IDs (`GHSA-...`, `CVE-...`) are preserved and stored without truncation.
- CVSS v3 scores map to severity buckets:
  - `CRITICAL` (CVSS >= 9.0)
  - `HIGH` (CVSS 7.0 - 8.9)
  - `MEDIUM` (CVSS 4.0 - 6.9)
  - `LOW` (CVSS 0.1 - 3.9)
- **Null/Missing Versions**: Dependencies lacking version information display `"Vulnerability check not possible (no versions found)"` rather than falsely claiming 0 safe status.

### 3. Typosquatting & Install Script Static Analysis
- **Typosquatting Engine**: Compares package names against an official top-packages registry (`express`, `lodash`, `lodash.merge`, `date-fns`, `react`, etc.) using pure Python Levenshtein distance.
  - Flagged as `CRITICAL` if Levenshtein distance is `<= 2` and the package is not on the official top-packages list (e.g. `expresss` -> `express`).
  - **Zero False Positives**: Official packages (`express`, `lodash.merge`, `date-fns`) are never flagged.
- **Install Script Inspection**: Statically analyzes `preinstall`, `install`, and `postinstall` hooks in `package.json`:
  - `CRITICAL`/`HIGH`: Script contains dangerous commands (`curl|sh`, `base64` decode, `child_process.exec`, reading `process.env`/`.npmrc`, or remote data exfiltration).
  - `INFO`: Benign scripts (e.g. `mkdir -p build` local directory creation) are marked as `INFO` and **not counted** towards the Suspicious finding count.

### 4. SPDX License Compatibility
- Evaluates package SPDX identifiers against host project license under a user-selected deployment model:
  - `HOSTED` (SaaS): `AGPL-3.0` licenses trigger `HIGH` risk network copyleft flags.
  - Missing/unknown license fields trigger `MEDIUM` risk compliance findings.
  - Root project's own license (`UNLICENSED` / `private: true`) is **never flagged**.

### 5. Static Source Reachability & Attack Path Ranking
- Executes Breadth-First Search (BFS) graph traversal from `root` to every flagged target dependency.
- Statically scans `src/` files for imports (`require`/`import`) and call sites of vulnerable functions (`lodash.merge`, `axios.get`, `node-fetch`, `ejs.render`, `jsonwebtoken.verify`, `moment`).
- Labels paths as `reachable`, `imported only`, or `not detected`. Reachable attack paths are ranked **above** unreachable ones.

### 6. Transparent 0-100 Risk Score & Verdict Scale
Raw weighted impact points are mapped to a 0.0 - 100.0 score via logarithmic normalization:
```
raw_score = (
    Critical_Vulns * 25.0 +
    High_Vulns * 12.0 +
    Medium_Vulns * 5.0 +
    Low_Vulns * 2.0 +
    Suspicious_Signals * 22.0 +
    License_Conflicts * 12.0 +
    Attack_Paths * 2.0 +
    Reachable_Paths * 8.0
)

risk_score = round(100.0 * (1.0 - math.exp(-raw_score / 72.0)), 1)
```
- **Verdict Mapping**:
  - `0.0`: **Safe**
  - `0.1 - 24.9`: **Low**
  - `25.0 - 49.9`: **Medium**
  - `50.0 - 74.9`: **High**
  - `75.0 - 100.0`: **Critical**

---

## Acceptance Test Results Matrix

| Sample Fixture | Total Deps | Vulns | Suspicious | License | Verdict | Pytest Result |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| `p1-clean-app` | 70 | 0 | 0 | 0 | **Safe** | **PASSED** |
| `p2-low-risk-app` | 70 | 2 (`moment`, `lodash`) | 0 | 0 | **Low/Medium** (`moment` ranked above `lodash`) | **PASSED** |
| `p3-high-risk-app` | 79 | 15 (2 Critical: `ejs`, `minimist`; 10 High; 3 Low; 6 Transitive) | 0 | 0 | **Critical** (5 reachable attack paths) | **PASSED** |
| `p4-trap-app` | 80 | 0 | 2 (`expresss`, `lodassh`) | 2 (`acme-agpl-lib`, `acme-nolicense-lib`) | **High** (zero false positives for `express`, `lodash.merge`, `date-fns`; `safe-setup-tool` INFO) | **PASSED** |

**Extra Tests Passed:**
- `(a) Extra Dependency`: Adding 1 dependency to p1 lock increases Total Deps to 71.
- `(b) Null Version`: Manifest with missing version displays `"Vulnerability check not possible (no versions found)"`.
- `(c) User Isolation`: User A cannot access User B's scan report (HTTP 403 Forbidden).
- `(d) Safe Execution Isolation`: Uploaded code is never executed (ZIP slip protection & zero process evaluation).

---

## Security Architecture & Checklist

- [x] **No Hardcoded Secrets:** All credentials loaded via `.env`.
- [x] **No Seeded Accounts:** Every user account is explicitly created through multi-step signup.
- [x] **Argon2 / PBKDF2 Password & Answer Hashing:** Passwords and normalized security answers stored as cryptographic hashes.
- [x] **HTTP-Only JWT Cookies:** Secure token handling (`httpOnly`, `SameSite=Lax`, `Secure`).
- [x] **Zip Bomb & Path Traversal Protection:** Validates zip entries against Zip-Slip traversal, rejects symlinks, enforces max 100MB uncompressed size limit & 5000 max files.
- [x] **Safe Code Execution Isolation:** Never executes uploaded code or scripts during analysis.
- [x] **Rate Limiting & Account Lockout:** Enforces Flask-Limiter limits on auth/OTP routes and locks accounts after 5 consecutive failed logins for 15 minutes.
- [x] **Security Headers:** Enforces CSP, HSTS, X-Frame-Options (`DENY`), and X-Content-Type-Options (`nosniff`).
- [x] **Resource Ownership Access Control:** User projects, scans, and reports are protected by ownership verification on every endpoint.

---

## Quick Start & Installation Guide

### Prerequisites
- Python 3.10+
- Node.js 18+
- Docker & Docker Compose (for PostgreSQL & Redis)

### Step 1: Clone & Configure Environment
```bash
cp .env.example .env
```

### Step 2: Setup Backend Environment & Dependencies
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
```

### Step 3: Run Flask Backend API Server
```bash
python -m backend.app
```
*Backend runs on `http://127.0.0.1:5000`*

---

## Running Acceptance Tests

Run the full pytest suite across all 4 sample fixtures and extra test cases:
```bash
python -m pytest tests/test_acceptance.py backend/tests
```

---

## Contact & Author Information

- **Author:** Omkar Nalawade
- **Email:** `nalawadeomkar0508@gmail.com`
- **Location:** Pune, Maharashtra, India
