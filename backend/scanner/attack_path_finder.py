import os
import re
from collections import deque

VULN_PATTERNS = {
    'lodash': [r'_\.merge', r'lodash\.merge', r'_\.template'],
    'axios': [r'axios\.get', r'axios\.post', r'axios\('],
    'node-fetch': [r'fetch\(', r'nodeFetch\('],
    'ejs': [r'ejs\.render', r'ejs\.compile'],
    'jsonwebtoken': [r'jsonwebtoken\.verify', r'jwt\.verify'],
    'moment': [r'moment\(']
}

def analyze_src_reachability(extract_dir: str) -> dict[str, str]:
    """
    Statically scans source files (.js, .ts, .jsx, .tsx) in extract_dir for imports and call sites.
    Returns map of package_name -> 'reachable' | 'imported only' | 'not detected'.
    """
    reachability_map = {}
    src_content = ""

    src_dir = os.path.join(extract_dir, "src")
    search_dir = src_dir if os.path.exists(src_dir) else extract_dir

    for root, _, files in os.walk(search_dir):
        for f in files:
            if f.endswith(('.js', '.ts', '.jsx', '.tsx')) and 'node_modules' not in root:
                fp = os.path.join(root, f)
                try:
                    with open(fp, 'r', encoding='utf-8', errors='ignore') as file:
                        src_content += file.read() + "\n"
                except Exception:
                    pass

    if not src_content.strip():
        return reachability_map

    # Check for require/import of packages
    all_imported = set(re.findall(r"(?:require\(['\"]|from\s+['\"])(@?[a-zA-Z0-9_\-\./]+)['\"]", src_content))
    
    for pkg, patterns in VULN_PATTERNS.items():
        is_imported = any(pkg in imp for imp in all_imported) or (pkg in src_content)
        if is_imported:
            call_detected = any(re.search(pat, src_content) for pat in patterns)
            if call_detected:
                reachability_map[pkg] = 'reachable'
            else:
                reachability_map[pkg] = 'imported only'
        else:
            reachability_map[pkg] = 'not detected'

    return reachability_map

def find_attack_paths(graph: dict, flagged_nodes: set[str], extract_dir: str = None, max_depth: int = 10) -> list[dict]:
    """
    Executes BFS graph traversal from 'root' application node to every flagged node.
    Performs static source reachability analysis if extract_dir contains source files.
    Ranks reachable paths above unreachable ones.
    """
    attack_paths = []
    if not flagged_nodes or 'root' not in graph:
        return attack_paths

    reachability_map = analyze_src_reachability(extract_dir) if extract_dir else {}

    for target in flagged_nodes:
        if target == 'root':
            continue

        # BFS to find shortest path from root to target
        queue = deque([['root']])
        visited = set(['root'])
        found_path = None

        while queue:
            path = queue.popleft()
            node = path[-1]

            if node == target:
                found_path = path
                break

            if len(path) > max_depth:
                continue

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])

        if found_path:
            depth = len(found_path) - 1
            reach_status = reachability_map.get(target, 'not detected')
            
            # Severity rank computation
            base_rank = max(1.0, 10.0 - depth)
            if reach_status == 'reachable':
                severity_rank = base_rank + 100.0  # Rank reachable above all
            elif reach_status == 'imported only':
                severity_rank = base_rank + 50.0
            else:
                severity_rank = base_rank

            attack_paths.append({
                'target_node': target,
                'path_nodes': found_path,
                'depth': depth,
                'reachability': reach_status,
                'severity_rank': severity_rank
            })

    # Sort attack paths by severity_rank descending (reachable & shallowest first)
    attack_paths.sort(key=lambda x: x['severity_rank'], reverse=True)
    return attack_paths
