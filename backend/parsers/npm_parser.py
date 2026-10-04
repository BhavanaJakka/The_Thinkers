import json
import os
import re

def parse_npm_files(dirpath: str, files_map: dict):
    dependencies = []
    edges = []
    project_metadata = {'name': None, 'version': None, 'license': None}

    root_direct_names = set()
    root_pkg_json_path = files_map.get('package.json')
    
    if root_pkg_json_path and os.path.exists(root_pkg_json_path):
        try:
            with open(root_pkg_json_path, 'r', encoding='utf-8') as f:
                root_pkg_data = json.load(f)
                project_metadata['name'] = root_pkg_data.get('name')
                project_metadata['version'] = root_pkg_data.get('version')
                project_metadata['license'] = root_pkg_data.get('license')
                
                deps = root_pkg_data.get('dependencies', {})
                dev_deps = root_pkg_data.get('devDependencies', {})
                if isinstance(deps, dict):
                    root_direct_names.update(deps.keys())
                if isinstance(dev_deps, dict):
                    root_direct_names.update(dev_deps.keys())
        except Exception as e:
            print(f"[NPM PARSER ERROR] root package.json: {e}")

    # A. package-lock.json (v1, v2, v3)
    if 'package-lock.json' in files_map:
        try:
            with open(files_map['package-lock.json'], 'r', encoding='utf-8') as f:
                data = json.load(f)

            if not project_metadata['name']:
                project_metadata['name'] = data.get('name')

            # Lockfile v2 / v3 has "packages" map
            if "packages" in data and isinstance(data["packages"], dict):
                packages_map = data["packages"]
                root_info = packages_map.get("")
                if root_info and isinstance(root_info, dict):
                    if not project_metadata['name']:
                        project_metadata['name'] = root_info.get("name")
                    if not project_metadata['version']:
                        project_metadata['version'] = root_info.get("version")
                    root_deps = root_info.get("dependencies", {})
                    root_dev = root_info.get("devDependencies", {})
                    if isinstance(root_deps, dict):
                        root_direct_names.update(root_deps.keys())
                    if isinstance(root_dev, dict):
                        root_direct_names.update(root_dev.keys())

                for pkg_path, pkg_info in packages_map.items():
                    if not pkg_path:  # Skip root project entry
                        continue

                    # Extract name
                    name = pkg_info.get("name")
                    if not name:
                        name = pkg_path.replace("node_modules/", "").split("node_modules/")[-1]

                    version = pkg_info.get("version")
                    license_spdx = pkg_info.get("license")
                    scripts = pkg_info.get("scripts", {})
                    resolved = pkg_info.get("resolved", "")
                    is_link = pkg_info.get("link", False)

                    # Inspect linked/vendor packages for license & scripts
                    if is_link or (resolved and resolved.startswith("file:")):
                        vendor_rel_path = resolved.replace("file:", "") if resolved.startswith("file:") else name
                        vendor_pkg_json = os.path.join(dirpath, vendor_rel_path, "package.json")
                        if not os.path.exists(vendor_pkg_json):
                            vendor_pkg_json = os.path.join(dirpath, "vendor", name, "package.json")
                        
                        if os.path.exists(vendor_pkg_json):
                            try:
                                with open(vendor_pkg_json, 'r', encoding='utf-8') as vf:
                                    vdata = json.load(vf)
                                    if not license_spdx:
                                        license_spdx = vdata.get("license")
                                    if not scripts:
                                        scripts = vdata.get("scripts", {})
                                    if not version:
                                        version = vdata.get("version", "1.0.0")
                            except Exception as err:
                                print(f"[VENDOR PKG ERROR] {vendor_pkg_json}: {err}")

                    depth = pkg_path.count("node_modules/")
                    is_direct = (depth == 1 and name in root_direct_names) or (depth == 1 and not root_direct_names)

                    dependencies.append({
                        'name': name,
                        'version': version,
                        'ecosystem': 'npm',
                        'is_direct': is_direct,
                        'depth': depth,
                        'parent_name': 'root' if is_direct else 'transitive',
                        'license': license_spdx,
                        'scripts': scripts
                    })

                    # Add edges from child dependencies
                    child_deps = pkg_info.get("dependencies", {})
                    if isinstance(child_deps, dict):
                        for child_name, child_spec in child_deps.items():
                            edges.append((name, version or "*", child_name, child_spec or "*"))

            # Lockfile v1 fallback
            elif "dependencies" in data and isinstance(data["dependencies"], dict):
                def parse_v1_deps(deps_dict, parent="root", current_depth=1):
                    for name, info in deps_dict.items():
                        ver = info.get("version")
                        lic = info.get("license")
                        is_direct = (current_depth == 1 and name in root_direct_names) or current_depth == 1
                        dependencies.append({
                            'name': name,
                            'version': ver,
                            'ecosystem': 'npm',
                            'is_direct': is_direct,
                            'depth': current_depth,
                            'parent_name': parent,
                            'license': lic,
                            'scripts': info.get("scripts", {})
                        })
                        if parent != "root":
                            edges.append((parent, "*", name, ver or "*"))
                        if "dependencies" in info and isinstance(info["dependencies"], dict):
                            parse_v1_deps(info["dependencies"], name, current_depth + 1)
                parse_v1_deps(data["dependencies"])

        except Exception as e:
            print(f"[NPM PARSER ERROR] package-lock.json: {e}")

    # B. package.json direct parsing if no lockfile
    elif root_pkg_json_path:
        try:
            with open(root_pkg_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            deps = data.get('dependencies', {})
            dev_deps = data.get('devDependencies', {})
            all_deps = {**deps, **dev_deps} if isinstance(deps, dict) and isinstance(dev_deps, dict) else (deps or dev_deps or {})

            for pkg_name, spec in all_deps.items():
                clean_ver = re.sub(r'[\^~>=<]', '', str(spec)).split()[0] if spec else None
                dependencies.append({
                    'name': pkg_name,
                    'version': clean_ver,
                    'ecosystem': 'npm',
                    'is_direct': True,
                    'depth': 1,
                    'parent_name': 'root',
                    'license': None,
                    'scripts': {}
                })
        except Exception as e:
            print(f"[NPM PARSER ERROR] package.json: {e}")

    return dependencies, edges, project_metadata
