import networkx as nx
from pathlib import Path


def get_parent_commits(commit_path: Path):
    return []


def build_dag_from_git_commits(repo_path: Path) -> nx.DiGraph:
    dag = nx.DiGraph()
    commits = list(repo_path.iterdir())
    for commit in commits:
        if commit.is_dir():
            commit_hash = commit.name
            dag.add_node(commit_hash)
            parent_commits = get_parent_commits(commit)
            for parent_commit in parent_commits:
                dag.add_edge(parent_commit, commit_hash)
    return dag
