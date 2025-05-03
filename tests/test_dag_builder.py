from pathlib import Path
from guardian.dag_builder import build_dag_from_git_commits

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
        assert set(dag.nodes) == {"A", "B"}
        assert ("A", "B") in dag.edges
