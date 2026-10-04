import math

def calculate_harmfulness_percentage(
    vuln_counts: dict[str, int],
    suspicious_count: int,
    license_conflict_count: int,
    total_deps: int
) -> int:
    """
    Dedicated Harmfulness Percentage Calculation Function.
    Calculates weighted findings normalized by total dependencies (0% - 100%).
    """
    if not total_deps or total_deps <= 0:
        return 0

    crit = vuln_counts.get('CRITICAL', 0)
    high = vuln_counts.get('HIGH', 0)
    med = vuln_counts.get('MEDIUM', 0)
    low = vuln_counts.get('LOW', 0)

    weighted_impact = (crit * 40) + (high * 20) + (med * 10) + (low * 5) + (suspicious_count * 30) + (license_conflict_count * 15)
    max_impact = max(total_deps * 20, 40)
    percentage = int(min(100, max(0, round((weighted_impact / max_impact) * 100))))
    return percentage

def calculate_risk_score(
    vuln_counts: dict[str, int],
    suspicious_count: int,
    license_conflict_count: int,
    attack_path_count: int,
    reachable_count: int = 0
) -> float:
    """
    Calculates overall supply chain risk score on a 0.0 - 100.0 scale.
    Formula considers severity weights, reachability, depth, and supply chain behavior.
    """
    raw_score = (
        vuln_counts.get('CRITICAL', 0) * 25.0 +
        vuln_counts.get('HIGH', 0) * 12.0 +
        vuln_counts.get('MEDIUM', 0) * 5.0 +
        vuln_counts.get('LOW', 0) * 2.0 +
        suspicious_count * 22.0 +
        license_conflict_count * 12.0 +
        attack_path_count * 2.0 +
        reachable_count * 8.0
    )

    if raw_score == 0:
        return 0.0

    normalized = 100.0 * (1.0 - math.exp(-raw_score / 72.0))
    return round(min(100.0, max(0.0, normalized)), 1)

def generate_risk_summary(
    risk_score: float,
    vuln_counts: dict[str, int],
    suspicious_count: int,
    license_conflict_count: int,
    total_deps: int,
    attack_paths: list[dict]
) -> dict:
    """Builds structured risk summary overview with verdict level."""
    harmfulness = calculate_harmfulness_percentage(vuln_counts, suspicious_count, license_conflict_count, total_deps)
    if risk_score >= 75.0:
        level = "Critical"
        description = "High-risk supply chain profile. Multiple critical vulnerabilities or suspicious packages detected."
    elif risk_score >= 50.0:
        level = "High"
        description = "Elevated risk profile. Action required to resolve typosquatting malware or license conflicts."
    elif risk_score >= 25.0:
        level = "Medium"
        description = "Moderate risk profile. Minor advisory findings or unpatched transitive dependencies."
    elif risk_score > 0.0:
        level = "Low"
        description = "Low supply chain risk. Minor vulnerabilities with low reachability."
    else:
        level = "Safe"
        description = "Clean supply chain profile. No vulnerabilities, typosquats, or copyleft license risks."

    return {
        'risk_score': risk_score,
        'harmfulness_percent': harmfulness,
        'risk_level': level,
        'description': description,
        'total_dependencies': total_deps,
        'critical_vulns': vuln_counts.get('CRITICAL', 0),
        'high_vulns': vuln_counts.get('HIGH', 0),
        'medium_vulns': vuln_counts.get('MEDIUM', 0),
        'low_vulns': vuln_counts.get('LOW', 0),
        'suspicious_packages': suspicious_count,
        'license_conflicts': license_conflict_count,
        'attack_path_count': len(attack_paths)
    }

def generate_recommendations(findings: list[dict], suspicious_signals: list[dict]) -> dict:
    """
    Generates minimal upgrade recommendations and safer package alternatives.
    """
    upgrade_fixes = []
    safer_alternatives = []

    seen_packages = set()
    for f in findings:
        pkg_name = f.get('package_name')
        if pkg_name and pkg_name not in seen_packages:
            seen_packages.add(pkg_name)
            fixed_ver = f.get('fixed_version', 'latest patch version')
            if fixed_ver != 'N/A':
                upgrade_fixes.append({
                    'package_name': pkg_name,
                    'current_version': f.get('current_version', 'unknown'),
                    'recommended_version': fixed_ver,
                    'reason': f"Fixes {f.get('severity')} vulnerability ({f.get('summary', '')[:80]}...)"
                })

    for s in suspicious_signals:
        if s.get('signal_type') == 'TYPOSQUATTING' and s.get('distance_target'):
            safer_alternatives.append({
                'flagged_package': s.get('dependency_name'),
                'recommended_alternative': s.get('distance_target'),
                'reason': f"Flagged as typosquatting lookalike. Replace with authentic package '{s.get('distance_target')}'."
            })

    return {
        'upgrade_solutions': upgrade_fixes[:10],
        'safer_alternatives': safer_alternatives
    }
