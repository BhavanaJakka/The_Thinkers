import re
import json

def parse_pypi_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []

    # A. requirements.txt
    if 'requirements.txt' in files_map:
        try:
            with open(files_map['requirements.txt'], 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#') or line.startswith('-'):
                        continue
                    # Parse line like requests==2.31.0 or flask>=2.0
                    match = re.match(r'^([A-Za-z0-9_.\-]+)\s*([~=><!]=?)\s*([A-Za-z0-9_.\-]+)', line)
                    if match:
                        name = match.group(1).lower()
                        version = match.group(3)
                        dependencies.append({
                            'name': name,
                            'version': version,
                            'ecosystem': 'PyPI',
                            'is_direct': True,
                            'depth': 1,
                            'parent_name': 'root'
                        })
                    else:
                        # Simple package name without explicit version
                        name_match = re.match(r'^([A-Za-z0-9_.\-]+)', line)
                        if name_match:
                            dependencies.append({
                                'name': name_match.group(1).lower(),
                                'version': '0.0.0',
                                'ecosystem': 'PyPI',
                                'is_direct': True,
                                'depth': 1,
                                'parent_name': 'root'
                            })
        except Exception as e:
            print(f"[PYPI PARSER ERROR] requirements.txt: {e}")

    # B. poetry.lock
    if 'poetry.lock' in files_map:
        try:
            with open(files_map['poetry.lock'], 'r', encoding='utf-8') as f:
                content = f.read()

            blocks = content.split("[[package]]")
            for block in blocks[1:]:
                name_match = re.search(r'name = "([^"]+)"', block)
                ver_match = re.search(r'version = "([^"]+)"', block)
                if name_match and ver_match:
                    name = name_match.group(1).lower()
                    ver = ver_match.group(1)
                    dependencies.append({
                        'name': name,
                        'version': ver,
                        'ecosystem': 'PyPI',
                        'is_direct': True,
                        'depth': 1,
                        'parent_name': 'root'
                    })
        except Exception as e:
            print(f"[POETRY PARSER ERROR] poetry.lock: {e}")

    # C. Pipfile.lock
    if 'pipfile.lock' in files_map:
        try:
            with open(files_map['pipfile.lock'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            default_deps = data.get('default', {})
            for name, info in default_deps.items():
                ver = info.get('version', '').replace('==', '') or '0.0.0'
                dependencies.append({
                    'name': name.lower(),
                    'version': ver,
                    'ecosystem': 'PyPI',
                    'is_direct': True,
                    'depth': 1,
                    'parent_name': 'root'
                })
        except Exception as e:
            print(f"[PIPFILE PARSER ERROR] Pipfile.lock: {e}")

    return dependencies, edges
