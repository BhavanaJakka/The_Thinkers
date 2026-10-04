import os
from datetime import datetime, timezone
from backend.extensions import db
from backend.models import (
    Scan, Package, Dependency, DependencyEdge, Finding,
    SuspiciousSignal, LicenseFinding, AttackPath, Report, Project, Upload
)
from backend.parsers import parse_project_directory
from backend.scanner.extractor import cleanup_temp_dir
from backend.services.osv_service import query_osv_batch, process_and_cache_advisories
from backend.services.typosquat_service import analyze_suspicious_signals
from backend.services.spdx_service import evaluate_license_risk
from backend.scanner.graph_builder import build_dependency_graph
from backend.scanner.attack_path_finder import find_attack_paths
from backend.scanner.risk_engine import (
    calculate_risk_score, generate_risk_summary, generate_recommendations
)

def run_scan_pipeline(scan_id: str, extract_dir: str):
    """
    Full supply chain scanning pipeline execution.
    Can be run inside a Celery task or directly in-process synchronously.
    """
    scan = Scan.query.get(scan_id)
    if not scan:
        print(f"[SCAN PIPELINE ERROR] Scan {scan_id} not found.")
        return

    try:
        # Phase 1: PARSING
        scan.status = 'PARSING'
        scan.progress = 10
        db.session.commit()

        parsed_deps, edges, ecosystems, meta = parse_project_directory(extract_dir)
        scan.total_dependencies = len(parsed_deps)

        project = Project.query.get(scan.project_id)
        if project:
            if meta and meta.get('name'):
                project.name = meta['name']
            if ecosystems and not project.ecosystem:
                project.ecosystem = ecosystems[0]
            db.session.commit()

        # Bulk insert dependencies
        dep_records_map = {}  # (name, ver) -> Dependency model
        for dep in parsed_deps:
            ver_str = dep.get('version') or '0.0.0'
            pkg = Package.query.filter_by(
                ecosystem=dep['ecosystem'],
                name=dep['name'],
                version=ver_str
            ).first()
            if not pkg:
                pkg = Package(
                    ecosystem=dep['ecosystem'],
                    name=dep['name'],
                    version=ver_str,
                    license_spdx=dep.get('license')
                )
                db.session.add(pkg)
                db.session.commit()

            dep_rec = Dependency(
                scan_id=scan.id,
                package_id=pkg.id,
                name=dep['name'],
                version=ver_str,
                ecosystem=dep['ecosystem'],
                is_direct=dep.get('is_direct', True),
                depth=dep.get('depth', 1),
                parent_name=dep.get('parent_name', 'root')
            )
            db.session.add(dep_rec)
            dep_records_map[(dep['name'], ver_str)] = dep_rec
            # Fallback map for name without version
            dep_records_map[(dep['name'], '*')] = dep_rec

        db.session.commit()

        # Insert dependency edges
        for parent_pkg, parent_ver, child_pkg, child_ver in edges:
            edge = DependencyEdge(
                scan_id=scan.id,
                parent_package=parent_pkg,
                parent_version=str(parent_ver or '*'),
                child_package=child_pkg,
                child_version=str(child_ver or '*')
            )
            db.session.add(edge)
        db.session.commit()

        # Phase 2: QUERYING OSV VULNERABILITIES
        scan.status = 'QUERYING_OSV'
        scan.progress = 40
        db.session.commit()

        osv_raw_results = query_osv_batch(parsed_deps)
        cached_advisories = process_and_cache_advisories(osv_raw_results)

        vuln_counts = {'CRITICAL': 0, 'HIGH': 0, 'MEDIUM': 0, 'LOW': 0}
        findings_list_for_recs = []
        flagged_nodes = set()

        for (eco, pkg_name, ver), adv_list in cached_advisories.items():
            dep_rec = dep_records_map.get((pkg_name, ver)) or dep_records_map.get((pkg_name, '*'))
            if not dep_rec:
                continue

            for adv in adv_list:
                sev = adv['severity']
                vuln_counts[sev] = vuln_counts.get(sev, 0) + 1
                flagged_nodes.add(pkg_name)

                finding = Finding(
                    scan_id=scan.id,
                    dependency_id=dep_rec.id,
                    advisory_id=adv['advisory_id'],
                    severity=sev,
                    fixed_version=adv['fixed_version'],
                    summary=adv['summary']
                )
                db.session.add(finding)
                findings_list_for_recs.append({
                    'package_name': pkg_name,
                    'current_version': ver,
                    'fixed_version': adv['fixed_version'],
                    'severity': sev,
                    'summary': adv['summary']
                })
        db.session.commit()

        # Phase 3: ANALYZING RISK SIGNALS & LICENSES
        scan.status = 'ANALYZING_RISKS'
        scan.progress = 70
        db.session.commit()

        suspicious_signals_count = 0
        suspicious_signals_list_for_recs = []
        license_conflict_count = 0
        deployment_model = scan.deployment_model or 'HOSTED'

        for dep in parsed_deps:
            ver_str = dep.get('version') or '0.0.0'
            dep_rec = dep_records_map.get((dep['name'], ver_str)) or dep_records_map.get((dep['name'], '*'))
            if not dep_rec:
                continue

            # A. Suspicious Signals
            adv_list = cached_advisories.get((dep['ecosystem'], dep['name'], ver_str), [])
            signals = analyze_suspicious_signals(dep, adv_list)

            for sig in signals:
                # Count towards suspicious score & tab ONLY if CRITICAL, HIGH, or MEDIUM (INFO benign scripts excluded)
                if sig['severity'] in {'CRITICAL', 'HIGH', 'MEDIUM'}:
                    suspicious_signals_count += 1
                    flagged_nodes.add(dep['name'])

                ss = SuspiciousSignal(
                    scan_id=scan.id,
                    dependency_id=dep_rec.id,
                    signal_type=sig['signal_type'],
                    severity=sig['severity'],
                    description=sig['description'],
                    distance_target=sig['distance_target']
                )
                db.session.add(ss)
                if sig['severity'] in {'CRITICAL', 'HIGH', 'MEDIUM'}:
                    suspicious_signals_list_for_recs.append({
                        'dependency_name': dep['name'],
                        'signal_type': sig['signal_type'],
                        'distance_target': sig['distance_target']
                    })

            # B. License Compatibility Check
            lic_eval = evaluate_license_risk(
                dep.get('license'),
                deployment_model=deployment_model,
                project_license=meta.get('license') or 'MIT',
                is_root=False
            )
            if lic_eval['risk_level'] in {'HIGH', 'MEDIUM'}:
                license_conflict_count += 1

            lf = LicenseFinding(
                scan_id=scan.id,
                dependency_id=dep_rec.id,
                license_spdx=lic_eval['license_spdx'],
                status=lic_eval['status'],
                conflict_with=lic_eval['conflict_with'],
                risk_level=lic_eval['risk_level'],
                description=lic_eval['description']
            )
            db.session.add(lf)

        db.session.commit()

        # Phase 4: ATTACK PATH & REACHABILITY ANALYSIS
        dep_graph = build_dependency_graph(parsed_deps, edges)
        attack_paths = find_attack_paths(dep_graph, flagged_nodes, extract_dir=extract_dir)

        reachable_count = 0
        for ap in attack_paths:
            if ap.get('reachability') == 'reachable':
                reachable_count += 1

            target_dep = Dependency.query.filter_by(scan_id=scan.id, name=ap['target_node']).first()
            if target_dep:
                ap_rec = AttackPath(
                    scan_id=scan.id,
                    target_dependency_id=target_dep.id,
                    path_nodes_json=ap['path_nodes'],
                    depth=ap['depth'],
                    severity_rank=ap['severity_rank']
                )
                db.session.add(ap_rec)
        db.session.commit()

        # Phase 5: RISK SCORE & REPORT GENERATION
        risk_score = calculate_risk_score(
            vuln_counts=vuln_counts,
            suspicious_count=suspicious_signals_count,
            license_conflict_count=license_conflict_count,
            attack_path_count=len(attack_paths),
            reachable_count=reachable_count
        )

        summary_data = generate_risk_summary(
            risk_score=risk_score,
            vuln_counts=vuln_counts,
            suspicious_count=suspicious_signals_count,
            license_conflict_count=license_conflict_count,
            total_deps=len(parsed_deps),
            attack_paths=attack_paths
        )

        recommendations_data = generate_recommendations(
            findings=findings_list_for_recs,
            suspicious_signals=suspicious_signals_list_for_recs
        )

        report = Report(
            scan_id=scan.id,
            user_id=scan.user_id,
            risk_score=risk_score,
            summary_jsonb=summary_data,
            recommendations_jsonb=recommendations_data
        )
        db.session.add(report)

        # Finalize scan status
        scan.risk_score = risk_score
        scan.status = 'COMPLETED'
        scan.progress = 100
        scan.completed_at = datetime.now(timezone.utc)
        db.session.commit()

    except Exception as e:
        db.session.rollback()
        scan.status = 'FAILED'
        scan.error_message = str(e)
        scan.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        print(f"[SCAN ERROR] Scan {scan_id} failed: {e}")
    finally:
        cleanup_temp_dir(extract_dir)
