import re

COPYLEFT_LICENSES = {
    'GPL-2.0', 'GPL-3.0', 'AGPL-1.0', 'AGPL-3.0', 'LGPL-2.1', 'LGPL-3.0',
    'GPL-2.0-ONLY', 'GPL-3.0-ONLY', 'AGPL-3.0-ONLY', 'AGPL-3.0-OR-LATER', 'MPL-2.0', 'AGPL'
}

PERMISSIVE_LICENSES = {
    'MIT', 'APACHE-2.0', 'BSD-2-CLAUSE', 'BSD-3-CLAUSE', 'ISC', 'UNLICENSE', 'CC0-1.0'
}

COMMON_LICENSE_GUESSES = {
    'mit': 'MIT',
    'apache 2.0': 'Apache-2.0',
    'apache-2.0': 'Apache-2.0',
    'bsd': 'BSD-3-Clause',
    'gpl': 'GPL-3.0',
    'gplv3': 'GPL-3.0',
    'gplv2': 'GPL-2.0',
    'agpl': 'AGPL-3.0',
    'agpl-3.0': 'AGPL-3.0',
    'isc': 'ISC'
}

def normalize_spdx(raw_license: str | None) -> str:
    """Normalizes raw license text to SPDX identifier."""
    if not raw_license or str(raw_license).strip().lower() in {'unknown', 'none', 'null', ''}:
        return 'UNKNOWN'
    
    clean = str(raw_license).strip()
    low = clean.lower()
    if low in COMMON_LICENSE_GUESSES:
        return COMMON_LICENSE_GUESSES[low]
    
    for key, val in COMMON_LICENSE_GUESSES.items():
        if key in low:
            return val

    return clean.upper()

def evaluate_license_risk(dep_license: str | None, deployment_model: str = 'HOSTED', project_license: str = 'MIT', is_root: bool = False) -> dict:
    """
    Evaluates SPDX license compatibility and risk according to deployment model:
    - HOSTED (SaaS): AGPL-3.0 is HIGH risk network copyleft.
    - Missing license: MEDIUM risk.
    - Root project's own license (e.g. UNLICENSED / private) is NEVER flagged.
    """
    spdx = normalize_spdx(dep_license)
    proj_spdx = normalize_spdx(project_license)

    if is_root:
        return {
            'license_spdx': spdx,
            'status': 'COMPATIBLE',
            'conflict_with': None,
            'risk_level': 'LOW',
            'description': 'Root project license. Excluded from license vulnerability findings.'
        }

    if spdx == 'UNKNOWN':
        return {
            'license_spdx': 'UNKNOWN',
            'status': 'UNKNOWN',
            'conflict_with': None,
            'risk_level': 'MEDIUM',
            'description': 'Dependency license field is missing or unparseable. Compliance check recommended.'
        }

    # AGPL check in HOSTED SaaS model
    if 'AGPL' in spdx and deployment_model == 'HOSTED':
        return {
            'license_spdx': spdx,
            'status': 'CONFLICT',
            'conflict_with': proj_spdx,
            'risk_level': 'HIGH',
            'description': f"AGPL license '{spdx}' in HOSTED (SaaS) deployment mode triggers network copyleft risk."
        }

    # General strong copyleft conflict check vs permissive project license
    if spdx in COPYLEFT_LICENSES and proj_spdx in PERMISSIVE_LICENSES:
        return {
            'license_spdx': spdx,
            'status': 'CONFLICT',
            'conflict_with': proj_spdx,
            'risk_level': 'HIGH',
            'description': f"Copyleft license '{spdx}' conflicts with permissive project license '{proj_spdx}'."
        }

    return {
        'license_spdx': spdx,
        'status': 'COMPATIBLE',
        'conflict_with': None,
        'risk_level': 'LOW',
        'description': f"License '{spdx}' is compatible with project license under {deployment_model} deployment."
    }
