from pathlib import Path
import networkx as nx
from guardian.dag_builder import (
    build_dag_from_git_commits,
    build_graph,
    parse_commit_content,
    get_parent_commits,
    calculate_generation_numbers,
    get_dag_stats
)
from guardian.object_scanner import GitObject

from unittest.mock import patch, MagicMock


def test_build_dag_from_git_commits_simple():
    commit_a = MagicMock(spec=Path)
    commit_a.is_dir.return_value = True
    commit_a.name = "A"
    commit_b = MagicMock(spec=Path)
    commit_b.is_dir.return_value = True
    commit_b.name = "B"
    fake_repo = MagicMock(spec=Path)
    fake_repo.iterdir.return_value = [commit_a, commit_b]

    def fake_get_parents(commit):
        if commit.name == "B":
            return ["A"]
        return []

    with patch(
        "guardian.dag_builder.get_parent_commits",
        side_effect=fake_get_parents
              ):
        dag = build_dag_from_git_commits(fake_repo)
        dag.size() > 0

    fake_repo = MagicMock(spec=Path)
    fake_git_dir = MagicMock(spec=Path)
    fake_git_dir.is_dir.return_value = False
    fake_repo.__truediv__.return_value = fake_git_dir

    with patch("src.guardian.dag_builder.build_graph") as mock_build_graph:
        build_dag_from_git_commits(fake_repo)
        assert not mock_build_graph.called


def test_parse_commit_content():
    commit_content = (
        b"tree 123456\n"
        b"parent abc123\n"
        b"author Test user <test@test.com> 1800 +0000\n"
        b"committer Test user <test@test.com> 1800 +0000\n"
        b"\n"
        b"Test commit message"
    )
    result = parse_commit_content(commit_content)

    assert "tree" in result
    assert "parent" in result
    assert "author" in result
    assert "committer" in result
    assert result["tree"] == ["123456"]
    assert result["parent"] == ["abc123"]

    commit_content_2 = (
        b"tree 123456\n"
        b"parent\n"     # error !!!
        b"author Test user <test@test.com> 1800 +0000\n"
    )
    result_2 = parse_commit_content(commit_content_2)
    assert "tree" in result_2


def test_get_parent_commits():
    commit_obj = MagicMock(spec=GitObject)
    commit_obj.obj_type = "commit"
    commit_obj.content = (
        b"tree 123456\n"
        b"parent sha1_p1\n"
        b"parent sha1_p2\n"
        b"author Test user <test@test.com> 1800 +0000\n"
    )

    parents = get_parent_commits(commit_obj)
    assert len(parents) == 2
    assert "sha1_p1" in parents
    assert "sha1_p2" in parents

    blob_obj = MagicMock(spec=GitObject)
    blob_obj.obj_type = "blob"      # no commit
    blob_obj.content = b"foobar"

    parents = get_parent_commits(blob_obj)
    assert parents == []


def test_build_graph():
    commit1 = MagicMock(spec=GitObject)
    commit1.obj_type = "commit"
    commit1.sha = "sha1"
    commit1.size = 100
    commit1.content = b"tree tree1\n"

    commit2 = MagicMock(spec=GitObject)
    commit2.obj_type = "commit"
    commit2.sha = "sha2"
    commit2.size = 200
    commit2.content = b"tree tree2\nparent sha1\n"

    commit3 = MagicMock(spec=GitObject)
    commit3.obj_type = "commit"
    commit3.sha = "sha3"
    commit3.size = 300
    commit3.content = b"tree tree3\nparent sha2\n"

    blob = MagicMock(spec=GitObject)
    blob.obj_type = "blob"
    blob.sha = "blob_sha"

    commits = [commit1, commit2, commit3, blob]

    dag = build_graph(commits)

    assert len(dag.nodes()) == 3
    assert "sha1" in dag.nodes()
    assert "sha2" in dag.nodes()
    assert "sha3" in dag.nodes()
    assert "blob_sha" not in dag.nodes()

    assert list(dag.edges()) == [("sha1", "sha2"), ("sha2", "sha3")]

    assert dag.nodes["sha1"]["type"] == "commit"
    assert dag.nodes["sha1"]["size"] == 100


def test_calculate_generation_numbers():
    dag = nx.DiGraph()

    # This graph is used to
    # test this function
    # A -> B -> C
    #  \
    #   -> D -> E
    #        \
    #         -> F
    dag.add_node("A")
    dag.add_node("B")
    dag.add_node("C")
    dag.add_node("D")
    dag.add_node("E")
    dag.add_node("F")
    dag.add_edge("A", "B")
    dag.add_edge("B", "C")
    dag.add_edge("A", "D")
    dag.add_edge("D", "E")
    dag.add_edge("D", "F")
    gen_numbers = calculate_generation_numbers(dag)

    assert len(gen_numbers) == 6
    assert gen_numbers["A"] == 0
    assert gen_numbers["B"] == 1
    assert gen_numbers["C"] == 2
    assert gen_numbers["D"] == 1
    assert gen_numbers["E"] == 2
    assert gen_numbers["F"] == 2


def test_get_dag_stats():
    dag = nx.DiGraph()
    # A -> B -> D
    # |    |
    # v    v
    # C -> E
    dag.add_node("A")
    dag.add_node("B")
    dag.add_node("C")
    dag.add_node("D")
    dag.add_node("E")
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("B", "D")
    dag.add_edge("B", "E")
    dag.add_edge("C", "E")
    stats = get_dag_stats(dag)

    assert stats["nodes"] == 5
    assert stats["edges"] == 5
    assert stats["roots"] == 1
    assert stats["leaves"] == 2
    assert stats["merges"] == 1
    assert stats["is_dag"] == 1


def test_get_dag_stats_with_cycle():
    graph = nx.DiGraph()

    graph.add_node("A")
    graph.add_node("B")
    graph.add_node("C")

    graph.add_edge("A", "B")
    graph.add_edge("B", "C")
    graph.add_edge("C", "A")

    stats = get_dag_stats(graph)

    assert stats["nodes"] == 3
    assert stats["edges"] == 3
    assert stats["roots"] == 0
    assert stats["leaves"] == 0
    assert stats["is_dag"] == 0
    assert stats["cycles"] == 1


def test_get_dag_stats_with_exception():
    dag = nx.DiGraph()
    dag.add_node("A")
    with patch(
        "networkx.is_directed_acyclic_graph",
        side_effect=Exception("DAG error")
            ):
        stats = get_dag_stats(dag)

        assert stats["is_dag"] == -1
