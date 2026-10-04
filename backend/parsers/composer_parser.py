import json

def parse_composer_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []

    if 'composer.lock' in files_map:
        try:
            with open(files_map['composer.lock'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            packages = data.get('packages', [])
            for pkg in packages:
                dependencies.append({
                    'name': pkg.get('name', ''),
                    'version': pkg.get('version', '0.0.0').lstrip('v'),
                    'ecosystem': 'Packagist',
                    'is_direct': True,
                    'depth': 1,
                    'parent_name': 'root'
                })
        except Exception as e:
            print(f"[COMPOSER PARSER ERROR] composer.lock: {e}")
    elif 'composer.json' in files_map:
        try:
            with open(files_map['composer.json'], 'r', encoding='utf-8') as f:
                data = json.load(f)
            require = data.get('require', {})
            for name, ver in require.items():
                if name == 'php':
                    continue
                dependencies.append({
                    'name': name,
                    'version': ver.lstrip('^~v'),
                    'ecosystem': 'Packagist',
                    'is_direct': True,
                    'depth': 1,
                    'parent_name': 'root'
                })
        except Exception as e:
            print(f"[COMPOSER PARSER ERROR] composer.json: {e}")

    return dependencies, edges
