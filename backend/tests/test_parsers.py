from backend.parsers.npm_parser import parse_npm_files
from backend.parsers.pypi_parser import parse_pypi_files
from backend.scanner.risk_engine import calculate_risk_score
from backend.services.spdx_service import evaluate_license_risk
from backend.services.typosquat_service import check_typosquatting

def test_npm_package_json_parsing(tmp_path):
    pkg_json = tmp_path / "package.json"
    pkg_json.write_text('{"dependencies": {"react": "^18.2.0", "axios": "~1.4.0"}}')

    files_map = {'package.json': str(pkg_json)}
    res = parse_npm_files(str(tmp_path), files_map)
    deps, edges = res[0], res[1]

    assert len(deps) == 2
    names = [d['name'] for d in deps]
    assert 'react' in names
    assert 'axios' in names

def test_pypi_requirements_parsing(tmp_path):
    req_txt = tmp_path / "requirements.txt"
    req_txt.write_text("flask==3.0.0\nrequests>=2.31.0\n# comment\n")

    files_map = {'requirements.txt': str(req_txt)}
    deps, edges = parse_pypi_files(str(tmp_path), files_map)

    assert len(deps) == 2
    assert deps[0]['name'] == 'flask'

def test_risk_score_calculation():
    vuln_counts = {'CRITICAL': 1, 'HIGH': 2, 'MEDIUM': 1, 'LOW': 0}
    score = calculate_risk_score(vuln_counts, suspicious_count=1, license_conflict_count=1, attack_path_count=2)
    assert 50.0 <= score <= 100.0

def test_typosquatting_detection():
    signal = check_typosquatting('reqeusts', 'pypi')
    assert signal is not None
    assert signal['signal_type'] == 'TYPOSQUATTING'
    assert signal['distance_target'] == 'requests'

def test_license_conflict_detection():
    eval_res = evaluate_license_risk('GPL-3.0', deployment_model='HOSTED', project_license='MIT')
    assert eval_res['status'] == 'CONFLICT'
    assert eval_res['risk_level'] == 'HIGH'
