from collections import defaultdict

def build_dependency_graph(dependencies: list[dict], edges: list[tuple]):
    """
    Constructs adjacency list representation of dependency tree and assigns computed depths.
    Returns graph: dict[parent] -> list[children]
    """
    graph = defaultdict(list)
    nodes = set()

    for dep in dependencies:
        nodes.add(dep['name'])

    for parent, p_ver, child, c_ver in edges:
        graph[parent].append(child)
        nodes.add(parent)
        nodes.add(child)

    # Attach direct dependencies as children of 'root'
    for dep in dependencies:
        if dep['is_direct']:
            if dep['name'] not in graph['root']:
                graph['root'].append(dep['name'])

    return graph
