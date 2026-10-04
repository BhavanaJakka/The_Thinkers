import os
from backend.parsers.npm_parser import parse_npm_files
from backend.parsers.pypi_parser import parse_pypi_files
from backend.parsers.maven_parser import parse_maven_files
from backend.parsers.composer_parser import parse_composer_files
from backend.parsers.go_parser import parse_go_files
from backend.parsers.cargo_parser import parse_cargo_files

def parse_project_directory(root_dir: str):
    """
    Traverses extracted project directory and parses all detected manifests and lockfiles.
    Supports monorepos and multiple manifests across directories.
    Returns:
      dependencies: list of dicts {name, version, ecosystem, is_direct, depth, parent_name, license, scripts}
      edges: list of tuples (parent_name, parent_ver, child_name, child_ver)
      detected_ecosystems: list of strings
      project_metadata: dict {name, version, license}
    """
    dependencies = []
    edges = []
    detected_ecosystems = set()
    project_metadata = {'name': None, 'version': None, 'license': None}

    for dirpath, _, filenames in os.walk(root_dir):
        files_map = {f.lower(): os.path.join(dirpath, f) for f in filenames}

        # 1. npm / yarn
        if 'package-lock.json' in files_map or 'yarn.lock' in files_map or 'package.json' in files_map:
            res = parse_npm_files(dirpath, files_map)
            if len(res) == 3:
                d, e, meta = res
                if meta and meta.get('name'):
                    project_metadata = meta
            else:
                d, e = res
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('npm')

        # 2. PyPI / Python
        if 'requirements.txt' in files_map or 'poetry.lock' in files_map or 'pipfile.lock' in files_map:
            d, e = parse_pypi_files(dirpath, files_map)
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('PyPI')

        # 3. Maven / Gradle
        if 'pom.xml' in files_map or 'build.gradle' in files_map:
            d, e = parse_maven_files(dirpath, files_map)
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('Maven')

        # 4. Composer (PHP)
        if 'composer.json' in files_map or 'composer.lock' in files_map:
            d, e = parse_composer_files(dirpath, files_map)
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('Composer')

        # 5. Go
        if 'go.mod' in files_map:
            d, e = parse_go_files(dirpath, files_map)
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('Go')

        # 6. Cargo (Rust)
        if 'cargo.lock' in files_map:
            d, e = parse_cargo_files(dirpath, files_map)
            if d:
                dependencies.extend(d)
                edges.extend(e)
                detected_ecosystems.add('Cargo')

    # Deduplicate dependencies by (ecosystem, name, version) while keeping depth & direct metadata
    seen = {}
    unique_deps = []
    for dep in dependencies:
        key = (dep['ecosystem'], dep['name'].lower(), str(dep.get('version')))
        if key not in seen:
            seen[key] = dep
            unique_deps.append(dep)
        else:
            if dep.get('is_direct'):
                seen[key]['is_direct'] = True
                seen[key]['depth'] = min(seen[key]['depth'], dep.get('depth', 1))

    return unique_deps, edges, list(detected_ecosystems), project_metadata
