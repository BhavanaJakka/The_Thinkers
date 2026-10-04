import re

def parse_cargo_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []

    if 'cargo.lock' in files_map:
        try:
            with open(files_map['cargo.lock'], 'r', encoding='utf-8') as f:
                content = f.read()

            blocks = content.split('[[package]]')
            for block in blocks[1:]:
                name_match = re.search(r'name = "([^"]+)"', block)
                ver_match = re.search(r'version = "([^"]+)"', block)
                if name_match and ver_match:
                    name = name_match.group(1)
                    ver = ver_match.group(1)
                    dependencies.append({
                        'name': name,
                        'version': ver,
                        'ecosystem': 'Cargo',
                        'is_direct': True,
                        'depth': 1,
                        'parent_name': 'root'
                    })
        except Exception as e:
            print(f"[CARGO PARSER ERROR] Cargo.lock: {e}")

    return dependencies, edges
