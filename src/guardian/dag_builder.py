import networkx as nx
from pathlib import Path
from collections import defaultdict, deque
from guardian.object_scanner import GitObject, read_loose, read_packfile
from typing import Dict, List
import re


def parse_commit_content(content: bytes) -> Dict[str, List[str]]:
    """
    Parse a commit object content to extract metadata including parent commits.
    Returns a dictionary with keys tree, parent, author, committer.
    """
    result = defaultdict(list)
    lines = content.split(b'\n')

    for line in lines:
        if not line:
            break

        try:
            key_value = line.split(b' ', 1)
            if len(key_value) == 2:
                key, value = key_value
                result[key.decode('utf-8')].append(value.decode('utf-8'))
        except Exception:
            continue

    return dict(result)


def get_parent_commits(commit_obj: GitObject) -> List[str]:
    """
    Extract parent commit SHAs from a commit object.
    Returns a list of parent commit SHAs.
    """
    if commit_obj.obj_type != "commit":
        return []

    metadata = parse_commit_content(commit_obj.content)
    return metadata.get('parent', [])


def build_graph(commits: List[GitObject]) -> nx.DiGraph:
    """
    Build a directed acyclic graph (DAG) from a list of Git commits.

    Args:
        commits: List of GitObject instances representing commits

    Returns:
        A Networkx digraph where nodes are commit SHAs
        and edges point from parent to child
    """
    dag = nx.DiGraph()

    for commit in commits:
        if commit.obj_type == "commit":
            dag.add_node(
                commit.sha,
                type=commit.obj_type,
                size=commit.size)

    commit_map = {
        commit.sha: commit for commit in commits
        if commit.obj_type == "commit"}

    for sha, commit_obj in commit_map.items():
        parents = get_parent_commits(commit_obj)
        for parent_sha in parents:
            if parent_sha in dag:
                dag.add_edge(parent_sha, sha)

    return dag


def build_dag_from_git_commits(repo_path: Path) -> nx.DiGraph:
    """
    Build a DAG from all Git commits in a repository.

    Args:
        repo_path: Path to the repository (with Git)

    Returns:
        A Networkx digraph where nodes are commit SHAs
        and edges represent parent-child relationships
    """
    commits = []

    git_dir = repo_path / ".git"
    if not git_dir.is_dir():
        git_dir = repo_path

    objects_dir = git_dir / "objects"
    if objects_dir.is_dir():
        hex_pattern = re.compile(r'^[0-9a-f]{2}$')
        for dir_path in objects_dir.iterdir():
            if dir_path.is_dir() and hex_pattern.match(dir_path.name):
                try:
                    obj = read_loose(dir_path)
                    commits.append(obj)
                except Exception as e:
                    print(f"Error reading loose object in {dir_path}: {e}")

    pack_dir = git_dir / "objects" / "pack"
    if pack_dir.is_dir():
        for pack_file in pack_dir.glob("*.pack"):
            try:
                pack_objects = read_packfile(pack_file)
                commits.extend(pack_objects)
            except Exception as e:
                print(f"Error reading packfile {pack_file}: {e}")
    return build_graph([obj for obj in commits if obj.obj_type == "commit"])


def calculate_generation_numbers(dag: nx.DiGraph) -> Dict[str, int]:
    """
    Calculate Generation Number (GN) for each commit in the DAG.
    GN is the maximum distance from any root node to this node.

    Args:
        dag: A Networkx digraph representing the commit history

    Returns:
        dict mapping commit SHA to its generation number
    """
    roots = [node for node in dag.nodes() if dag.in_degree(node) == 0]

    generation_numbers = {node: 0 for node in dag.nodes()}

    for root in roots:
        visited = set()
        queue = deque([(root, 0)])

        while queue:
            node, distance = queue.popleft()

            if node in visited:
                continue

            visited.add(node)

            generation_numbers[node] = max(generation_numbers[node], distance)

            for child in dag.successors(node):
                queue.append((child, distance + 1))

    return generation_numbers


def get_dag_stats(dag: nx.DiGraph) -> Dict[str, int]:
    """
    Calculate statistics for the DAG.

    Args:
        dag: A Networkx diGraph representing the commit history

    Returns:
        dict with statistics including node/edge counts, root nodes, leaf nodes
    """
    stats = {
        "nodes": dag.number_of_nodes(),
        "edges": dag.number_of_edges(),
        "roots": len([n for n in dag.nodes() if dag.in_degree(n) == 0]),
        "leaves": len([n for n in dag.nodes() if dag.out_degree(n) == 0]),
    }

    if stats["nodes"] > 0:
        stats["merges"] = len([n for n in dag.nodes() if dag.in_degree(n) > 1])

        try:
            # DAG topology
            if nx.is_directed_acyclic_graph(dag):
                stats["is_dag"] = 1
            else:
                stats["is_dag"] = 0
                stats["cycles"] = len(list(nx.simple_cycles(dag)))
        except Exception:
            stats["is_dag"] = -1

    return stats
