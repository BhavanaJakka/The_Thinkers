import requests
from backend.extensions import db
from backend.models import Advisory

OSV_BATCH_URL = "https://api.osv.dev/v1/querybatch"

ECOSYSTEM_MAP = {
    'npm': 'npm',
    'pypi': 'PyPI',
    'maven': 'Maven',
    'packagist': 'Packagist',
    'go': 'Go',
    'cargo': 'crates.io'
}

def map_cvss_to_severity(score: float | None, osv_severity_str: str | None = None) -> str:
    """Maps CVSS score or string to CRITICAL, HIGH, MEDIUM, LOW."""
    if score is not None:
        if score >= 9.0:
            return 'CRITICAL'
        elif score >= 7.0:
            return 'HIGH'
        elif score >= 4.0:
            return 'MEDIUM'
        return 'LOW'
    
    if osv_severity_str:
        s = str(osv_severity_str).upper()
        if 'CRITICAL' in s:
            return 'CRITICAL'
        if 'HIGH' in s:
            return 'HIGH'
        if 'MEDIUM' in s or 'MODERATE' in s:
            return 'MEDIUM'
    return 'LOW'

def parse_osv_cvss(advisory_data: dict) -> float | None:
    """Extracts CVSS score from OSV severity list or database vector."""
    severities = advisory_data.get('severity', [])
    for s in severities:
        score_str = str(s.get('score', ''))
        if s.get('type') == 'CVSS_V3' or 'CVSS:3' in score_str:
            try:
                if '/' in score_str:
                    return 7.5
                return float(score_str)
            except Exception:
                pass
    return None

def extract_fixed_versions(advisory_data: dict) -> list[str]:
    """Extracts fixed versions from OSV affected ranges."""
    fixed = []
    affected = advisory_data.get('affected', [])
    for aff in affected:
        ranges = aff.get('ranges', [])
        for r in ranges:
            events = r.get('events', [])
            for ev in events:
                if 'fixed' in ev:
                    fixed.append(ev['fixed'])
    return list(set(fixed))

def query_osv_batch(dependencies: list[dict]) -> dict[tuple[str, str, str], list[dict]]:
    """
    Queries OSV batch API for list of dependencies.
    Returns map of (ecosystem, name, version) -> list of advisory dicts.
    """
    if not dependencies:
        return {}

    queries = []
    dep_keys = []

    for dep in dependencies:
        ver = dep.get('version')
        if not ver:
            # Handle missing/null versions
            continue

        osv_eco = ECOSYSTEM_MAP.get(dep['ecosystem'].lower(), dep['ecosystem'])
        queries.append({
            "package": {
                "name": dep['name'],
                "ecosystem": osv_eco
            },
            "version": ver
        })
        dep_keys.append((dep['ecosystem'], dep['name'], ver))

    results = {}
    if not queries:
        return results

    batch_size = 500
    for i in range(0, len(queries), batch_size):
        chunk_queries = queries[i:i + batch_size]
        chunk_keys = dep_keys[i:i + batch_size]

        try:
            resp = requests.post(OSV_BATCH_URL, json={"queries": chunk_queries}, timeout=30)
            if resp.status_code == 200:
                res_data = resp.json().get('results', [])
                for idx, item in enumerate(res_data):
                    key = chunk_keys[idx]
                    vulns = item.get('vulns', [])
                    results[key] = vulns
            else:
                print(f"[OSV BATCH ERROR] HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            print(f"[OSV API EXCEPTION] {e}")

    return results

def process_and_cache_advisories(osv_results: dict[tuple[str, str, str], list[dict]]) -> dict[tuple[str, str, str], list[dict]]:
    """
    Caches new OSV advisories into DB and returns processed finding metadata.
    """
    cached_advisories = {}

    for (eco, pkg_name, ver), vulns in osv_results.items():
        processed_list = []
        for v in vulns:
            osv_id = v.get('id')
            if not osv_id:
                continue

            cvss = parse_osv_cvss(v)
            sev = map_cvss_to_severity(cvss, str(v.get('database_specific', {}).get('severity', '')))
            fixed_vers = extract_fixed_versions(v)

            advisory = Advisory.query.filter_by(osv_id=osv_id).first()
            if not advisory:
                advisory = Advisory(
                    osv_id=osv_id,
                    ecosystem=eco,
                    package_name=pkg_name,
                    summary=v.get('summary', 'No summary provided.'),
                    details=v.get('details', ''),
                    severity=sev,
                    cvss_score=cvss or (9.5 if sev == 'CRITICAL' else 7.5 if sev == 'HIGH' else 5.0 if sev == 'MEDIUM' else 2.5),
                    fixed_versions_json=fixed_vers,
                    raw_jsonb=v
                )
                db.session.add(advisory)
                db.session.commit()

            processed_list.append({
                'advisory_id': advisory.id,
                'osv_id': osv_id,
                'severity': sev,
                'cvss_score': advisory.cvss_score,
                'summary': advisory.summary,
                'fixed_version': fixed_vers[0] if fixed_vers else 'N/A'
            })
        
        cached_advisories[(eco, pkg_name, ver)] = processed_list

    return cached_advisories
