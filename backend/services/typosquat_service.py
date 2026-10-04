def levenshtein_distance(s1: str, s2: str) -> int:
    """Pure Python Levenshtein distance implementation requiring no C++ compilers."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)

    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]

TOP_PACKAGES = {
    'npm': [
        'react', 'react-dom', 'express', 'lodash', 'lodash.merge', 'date-fns', 'axios',
        'async', 'chalk', 'commander', 'debug', 'moment', 'request', 'bluebird', 'cors',
        'dotenv', 'fs-extra', 'glob', 'mongoose', 'nodemailer', 'redis', 'socket.io',
        'typescript', 'webpack', 'next', 'vue', 'tailwindcss', 'rxjs', 'tslib', 'babel',
        'core-js', 'prettier', 'eslint', 'ejs', 'minimist', 'jsonwebtoken', 'node-fetch'
    ],
    'pypi': [
        'requests', 'urllib3', 'numpy', 'pandas', 'flask', 'django', 'pytest', 'scipy',
        'scikit-learn', 'matplotlib', 'boto3', 'pillow', 'pydantic', 'setuptools', 'wheel',
        'pip', 'certifi', 'idna', 'charset-normalizer', 'jinja2', 'sqlalchemy', 'celery',
        'redis', 'cryptography', 'pyyaml', 'beautifulsoup4', 'joblib', 'psycopg2'
    ],
    'maven': [
        'org.springframework:spring-core', 'org.springframework.boot:spring-boot-starter-web',
        'com.fasterxml.jackson.core:jackson-databind', 'org.apache.commons:commons-lang3',
        'log4j:log4j', 'org.slf4j:slf4j-api', 'com.google.guava:guava', 'junit:junit'
    ]
}

def check_typosquatting(package_name: str, ecosystem: str) -> dict | None:
    """
    Checks if a package name is a lookalike of a top popular package using Levenshtein distance.
    Distance <= 2 is flagged as potential typosquatting attack unless package is itself on top list.
    """
    eco_key = ecosystem.lower() if ecosystem else 'npm'
    targets = TOP_PACKAGES.get(eco_key, TOP_PACKAGES['npm'])
    pkg_lower = package_name.lower().strip()

    # Never flag official packages on the top packages list
    if pkg_lower in targets:
        return None

    for target in targets:
        dist = levenshtein_distance(pkg_lower, target)
        if 1 <= dist <= 2 and len(pkg_lower) >= 4:
            return {
                'signal_type': 'TYPOSQUATTING',
                'severity': 'CRITICAL',
                'description': f"Package '{package_name}' resembles popular library '{target}' (Levenshtein distance: {dist}). Potential typosquatting supply chain attack.",
                'distance_target': target
            }
    return None

def analyze_install_scripts(scripts: dict | None) -> list[dict]:
    """
    Statically inspects install scripts (preinstall, install, postinstall) for suspicious behavior.
    Dangerous commands (curl|sh, base64, exec, process.env, remote fetch) = CRITICAL/HIGH.
    Benign commands (mkdir local folders) = INFO (not counted in Suspicious tab count).
    """
    signals = []
    if not scripts or not isinstance(scripts, dict):
        return signals

    hook_keys = {'preinstall', 'install', 'postinstall'}
    for hook, command in scripts.items():
        if hook.lower() in hook_keys and command:
            cmd_str = str(command).lower()
            
            # Dangerous patterns
            if any(pattern in cmd_str for pattern in ['curl', 'wget']) and ('|' in cmd_str or 'sh' in cmd_str or 'bash' in cmd_str):
                signals.append({
                    'signal_type': 'INSTALL_SCRIPT',
                    'severity': 'CRITICAL',
                    'description': f"Dangerous install hook '{hook}' uses remote script pipe (curl|sh / wget|bash): '{command}'.",
                    'distance_target': None
                })
            elif 'base64' in cmd_str or 'atob(' in cmd_str:
                signals.append({
                    'signal_type': 'INSTALL_SCRIPT',
                    'severity': 'CRITICAL',
                    'description': f"Suspicious install hook '{hook}' uses obfuscated base64 command: '{command}'.",
                    'distance_target': None
                })
            elif 'child_process' in cmd_str or 'execsync(' in cmd_str:
                signals.append({
                    'signal_type': 'INSTALL_SCRIPT',
                    'severity': 'HIGH',
                    'description': f"Install hook '{hook}' spawns process execution: '{command}'.",
                    'distance_target': None
                })
            elif 'process.env' in cmd_str or '.npmrc' in cmd_str:
                signals.append({
                    'signal_type': 'INSTALL_SCRIPT',
                    'severity': 'HIGH',
                    'description': f"Install hook '{hook}' accesses environment or npm credentials: '{command}'.",
                    'distance_target': None
                })
            else:
                # Benign script (e.g. mkdir local folders) -> INFO severity
                signals.append({
                    'signal_type': 'INSTALL_SCRIPT',
                    'severity': 'INFO',
                    'description': f"Standard install hook detected ({hook}): '{command}'. Benign build script.",
                    'distance_target': None
                })
    return signals

def analyze_suspicious_signals(dep: dict, osv_advisories: list[dict] = None) -> list[dict]:
    """
    Performs multi-heuristic suspicious package checks:
    1. Typosquatting lookalike check
    2. OSV Malicious package advisories
    3. Install script static analysis
    """
    signals = []
    pkg_name = dep['name']
    ecosystem = dep.get('ecosystem', 'npm')

    # 1. Typosquatting
    typo_signal = check_typosquatting(pkg_name, ecosystem)
    if typo_signal:
        signals.append(typo_signal)

    # 2. Install scripts analysis
    script_signals = analyze_install_scripts(dep.get('scripts'))
    signals.extend(script_signals)

    # 3. OSV Malicious advisories check
    if osv_advisories:
        for adv in osv_advisories:
            osv_id = adv.get('osv_id', '')
            if osv_id.startswith('MAL-') or 'malicious' in adv.get('summary', '').lower():
                signals.append({
                    'signal_type': 'MALICIOUS_OSV',
                    'severity': 'CRITICAL',
                    'description': f"Package '{pkg_name}' has confirmed malicious advisory ({osv_id}): {adv.get('summary')}",
                    'distance_target': None
                })

    # 4. Dependency confusion version strings
    ver = str(dep.get('version', ''))
    if ver in ['0.0.0-security', '99.99.99', '9.9.9']:
        signals.append({
            'signal_type': 'DEPENDENCY_CONFUSION',
            'severity': 'CRITICAL',
            'description': f"Suspicious version '{ver}' detected for '{pkg_name}'. Potential dependency confusion artifact.",
            'distance_target': None
        })

    return signals
