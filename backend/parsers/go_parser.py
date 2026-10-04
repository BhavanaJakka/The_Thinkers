import re

def parse_go_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []

    if 'go.mod' in files_map:
        try:
            with open(files_map['go.mod'], 'r', encoding='utf-8') as f:
                content = f.read()

            in_require_block = False
            for line in content.splitlines():
                line = line.strip()
                if line.startswith('require ('):
                    in_require_block = True
                    continue
                if in_require_block and line == ')':
                    in_require_block = False
                    continue

                if in_require_block or line.startswith('require '):
                    clean_line = line.replace('require ', '').strip()
                    parts = clean_line.split()
                    if len(parts) >= 2:
                        name = parts[0]
                        ver = parts[1].lstrip('v')
                        is_indirect = '// indirect' in line
                        dependencies.append({
                            'name': name,
                            'version': ver,
                            'ecosystem': 'Go',
                            'is_direct': not is_indirect,
                            'depth': 2 if is_indirect else 1,
                            'parent_name': 'root'
                        })
        except Exception as e:
            print(f"[GO PARSER ERROR] go.mod: {e}")

    return dependencies, edges
