import pytest
from pathlib import Path
from unittest.mock import patch
import networkx as nx
from typer.testing import CliRunner
from guardian.cli import app, build_dag
from guardian.object_scanner import GitObject


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_git_repo():
    with patch("guardian.cli.get_git_dir") as mock_get_git_dir:
        mock_get_git_dir.return_value = Path("/repo/.git")
        yield mock_get_git_dir


@pytest.fixture
def mock_loose_object():
    return GitObject(obj_type="blob", sha="abcd1234", size=42, content=b"fake content")


@pytest.fixture
def mock_pack_object():
    return GitObject(
        obj_type="commit", sha="1234abcd", size=120, content=b"fake packed content"
    )


def test_scan_non_git_repo(runner):
    with patch("guardian.cli.get_git_dir", return_value=None):
        result = runner.invoke(app, ["scan", "/not/a/git/repo"])
        assert result.exit_code == 2


def test_scan_empty_repo(runner, mock_git_repo):
    with patch(
        "guardian.cli.find_loose_object_dirs", return_value=[]
    ) as mock_find_loose:
        with patch("guardian.cli.find_packfiles", return_value=[]) as mock_find_packs:
            result = runner.invoke(app, ["scan", "/repo"])
            assert result.exit_code == 0
            assert "Tenemos 0 loose objects y 0 packs" in result.stdout
            mock_find_loose.assert_called_once()
            mock_find_packs.assert_called_once()


def test_scan_with_loose_error(runner, mock_git_repo):
    loose_dirs = [Path("/repo/.git/objects/ab/cd1234")]
    with patch(
        "guardian.cli.find_loose_object_dirs", return_value=loose_dirs
    ) as mock_find_loose:
        with patch("guardian.cli.find_packfiles", return_value=[]) as mock_find_packs:
            with patch(
                "guardian.cli.read_loose",
                return_value=mock_loose_object,
                side_effect=ValueError("Corrupted object"),
            ) as mock_read_loose:
                res = runner.invoke(app, ["scan", "/repo"])
                assert "Tenemos 1 loose objects y 0 packs" in res.stdout
                assert "err en obj loose: Corrupted object" in res.stdout
                mock_find_loose.assert_called_once()
                mock_find_packs.assert_called_once()
                mock_read_loose.assert_called_once()


def test_scan_with_packfile_error(runner, mock_git_repo):
    pack_files = [Path("/repo/.git/objects/pack/pack-abc123.pack")]
    with patch(
        "guardian.cli.find_loose_object_dirs", return_value=[]
    ) as mock_find_loose:
        with patch(
            "guardian.cli.find_packfiles", return_value=pack_files
        ) as mock_find_packs:
            with patch(
                "guardian.cli.read_packfile",
                side_effect=ValueError("Corrupted packfile"),
            ) as mock_read_pack:
                result = runner.invoke(app, ["scan", "/repo"])
                assert "Tenemos 0 loose objects y 1 packs" in result.stdout
                assert "err     packfile: Corrupted packfile" in result.stdout
                mock_find_loose.assert_called_once()
                mock_find_packs.assert_called_once()
                mock_read_pack.assert_called_once()


def test_scan_with_objects_and_packfiles(
    runner, mock_git_repo, mock_loose_object, mock_pack_object
):
    loose_dirs = [Path("/repo/.git/objects/ab/cd1234")]
    pack_files = [Path("/repo/.git/objects/pack/pack-abc123.pack")]
    with patch(
        "guardian.cli.find_loose_object_dirs", return_value=loose_dirs
    ) as mock_find_loose:
        with patch(
            "guardian.cli.find_packfiles", return_value=pack_files
        ) as mock_find_packs:
            with patch(
                "guardian.cli.read_loose", return_value=mock_loose_object
            ) as mock_read_loose:
                with patch(
                    "guardian.cli.read_packfile", return_value=[mock_pack_object]
                ) as mock_read_pack:
                    res = runner.invoke(app, ["scan", "/repo"])
                    assert "Tenemos 1 loose objects y 1 packs" in res.stdout
                    assert f"o: t={mock_loose_object.obj_type}" in res.stdout
                    assert f"p: t={mock_pack_object.obj_type}" in res.stdout
                    mock_find_loose.assert_called_once()
                    mock_find_packs.assert_called_once()
                    mock_read_loose.assert_called_once()
                    mock_read_pack.assert_called_once()


def test_build_dag_success():
    fake_repo_path = "fake_repo"
    fake_git_dir = Path("/dir")
    fake_dag = nx.DiGraph()
    fake_dag.add_node("commit1", type="commit", size=100)
    fake_dag.add_node("commit2", type="commit", size=200)
    fake_dag.add_edge("commit1", "commit2")
    fake_gen_numbers = {"commit1": 0, "commit2": 1}
    fake_stats = {
        "nodes": 2,
        "edges": 1,
        "roots": 1,
        "leaves": 1,
        "merges": 0,
        "is_dag": 1,
    }

    with (
        patch("guardian.cli.Path", return_value=Path(fake_repo_path)) as _,
        patch(
            "guardian.cli.get_git_dir", return_value=fake_git_dir
        ) as mock_get_git_dir,
        patch(
            "guardian.cli.build_dag_from_git_commits", return_value=fake_dag
        ) as mock_build_dag,
        patch(
            "guardian.cli.calculate_generation_numbers", return_value=fake_gen_numbers
        ) as mock_calc_gen,
        patch("guardian.cli.get_dag_stats", return_value=fake_stats) as mock_get_stats,
        patch("guardian.cli.nx.write_graphml") as mock_write_graphml,
        patch("guardian.cli.typer.secho") as mock_secho,
        patch("guardian.cli.typer.echo") as _,
        patch("builtins.print") as mock_print,
    ):
        build_dag(fake_repo_path)
        mock_get_git_dir.assert_called_once_with(Path(fake_repo_path))
        mock_build_dag.assert_called_once_with(fake_git_dir)
        mock_calc_gen.assert_called_once_with(fake_dag)
        mock_get_stats.assert_called_once_with(fake_dag)
        mock_write_graphml.assert_called_once_with(fake_dag, "dag.graphml")

        assert mock_print.call_count >= 2
        assert mock_secho.call_count >= 4
        assert "Building DAG" in mock_print.call_args_list[0][0][0]

        gen_nums_shown = False
        stats_shown = False
        for call in mock_secho.call_args_list:
            args = call[0]
            if args and "Generation numbers" in args[0]:
                gen_nums_shown = True
            if args and "DAG stats" in args[0]:
                stats_shown = True

        assert gen_nums_shown
        assert stats_shown


def test_detect_rewrites_no_rewrites(runner, mock_git_repo):
    fake_dag = nx.DiGraph()
    fake_dag.add_node("commit1")
    fake_dag.add_node("commit2")
    fake_dag.add_edge("commit1", "commit2")

    no_rewrites_result = {"rewrites": []}

    with (
        patch(
            "guardian.cli.build_dag_from_git_commits", return_value=fake_dag
        ) as mock_build_dag,
        patch(
            "guardian.cli.detect_history_rewrites", return_value=no_rewrites_result
        ) as mock_detect,
    ):
        result = runner.invoke(app, ["detect-rewrites", "/repo"])

        assert result.exit_code == 0
        assert "Building DAG" in result.stdout
        assert "No potential history rewrites detected" in result.stdout
        mock_build_dag.assert_called_once()
        mock_detect.assert_called_once_with(fake_dag)


def test_detect_rewrites_with_rewrites(runner, mock_git_repo):
    fake_dag = nx.DiGraph()
    fake_dag.add_node("abcdef1234567890")
    fake_dag.add_node("1234567890abcdef")

    rewrites_result = {
        "rewrites": [
            {
                "commit1": "abcdef1234567890",
                "commit2": "1234567890abcdef",
                "similarity": 0.95,
                "path1": "abcdef12→98765432",
                "path2": "12345678→98765432",
            }
        ]
    }

    with (
        patch(
            "guardian.cli.build_dag_from_git_commits", return_value=fake_dag
        ) as mock_build_dag,
        patch(
            "guardian.cli.detect_history_rewrites", return_value=rewrites_result
        ) as mock_detect,
    ):
        result = runner.invoke(app, ["detect-rewrites", "/repo"])

        assert "Building DAG" in result.stdout
        assert "Found 1 potential history rewrites" in result.stdout
        assert "Similarity: 0.9500" in result.stdout
        assert "Commit 1: abcdef12" in result.stdout
        assert "Commit 2: 12345678" in result.stdout
        mock_build_dag.assert_called_once()
        mock_detect.assert_called_once_with(fake_dag)


def test_detect_rewrites_invalid_repo(runner):
    with patch("guardian.cli.get_git_dir", return_value=None):
        result = runner.invoke(app, ["detect-rewrites", "/repo"])
        assert result.exit_code == 2
        assert "not a git repository" in result.stdout.lower()


def test_bisect_command_with_current_session(runner, mock_git_repo):
    with (
        patch(
            "guardian.cli.get_current_bisect_status", return_value="abcd1234"
        ) as mock_status,
        patch("guardian.cli.bisect_log") as mock_log,
    ):

        mock_log.return_value = (
            True,
            "log text",
            {"good_commits": ["commit1"], "bad_commits": ["commit2"]},
        )

        result = runner.invoke(app, ["bisect", "/repo"])

        assert result.exit_code == 0
        assert "abcd1234" in result.stdout
        assert "Good commits: 1" in result.stdout
        assert "Bad commits: 1" in result.stdout
        mock_status.assert_called_once()
        mock_log.assert_called_once()


def test_bisect_interactive_new_session(runner, mock_git_repo):
    with (
        patch(
            "guardian.cli.get_current_bisect_status", return_value=None
        ) as mock_status,
        patch(
            "guardian.cli.bisect_start", return_value=(True, "Bisect started")
        ) as mock_start,
        patch(
            "guardian.cli.bisect_good", return_value=(True, "Marked as good")
        ) as mock_good,
        patch(
            "guardian.cli.bisect_bad", return_value=(True, "Marked as bad")
        ) as mock_bad,
    ):

        # Simulate user input: good commit=HEAD~5, bad commit=HEAD
        result = runner.invoke(
            app,
            ["bisect", "/repo"],
            input="HEAD~5\nHEAD\nn\n",
        )

        assert result.exit_code == 0
        assert "Starting new bisect session" in result.stdout
        assert "Enter a commit known to be good" in result.stdout
        assert "Enter a commit known to be bad" in result.stdout
        mock_status.assert_called_once()
        mock_start.assert_called_once()
        mock_good.assert_called_once_with(Path("/repo"), "HEAD~5")
        mock_bad.assert_called_once_with(Path("/repo"), "HEAD")


def test_bisect_interactive_existing_session_terminate(runner, mock_git_repo):
    with (
        patch(
            "guardian.cli.get_current_bisect_status", return_value="abcd1234"
        ) as mock_status,
        patch("guardian.cli.bisect_log") as mock_log,
        patch(
            "guardian.cli.bisect_reset", return_value=(True, "Reset successful")
        ) as mock_reset,
    ):

        # Simulate user input: yes to terminate session
        result = runner.invoke(app, ["bisect", "/repo"], input="y\n")

        assert result.exit_code == 0
        assert "Found existing bisect session" in result.stdout
        assert "Do you want to terminate" in result.stdout
        assert "Bisect session terminated" in result.stdout
        mock_status.assert_called_once()
        mock_reset.assert_called_once_with(Path("/repo"))
        mock_log.assert_not_called()


def test_bisect_interactive_existing_session_continue(runner, mock_git_repo):
    with (
        patch(
            "guardian.cli.get_current_bisect_status", return_value="abcd1234"
        ) as mock_status,
        patch("guardian.cli.bisect_log") as mock_log,
        patch("guardian.cli.bisect_good") as mock_good,
    ):

        mock_log.return_value = (
            True,
            "log text",
            {"good_commits": ["commit1"], "bad_commits": ["commit2"]},
        )

        result = runner.invoke(app, ["bisect", "/repo"], input="n\ngood\nHEAD~3\n")

        assert result.exit_code == 1
        assert "Found existing bisect session" in result.stdout
        assert "Do you want to terminate" in result.stdout
        assert "Continuing with existing bisect session" in result.stdout
        assert "Enter commit to mark as good" in result.stdout
        mock_status.assert_called_once()
        mock_log.assert_called_once_with(Path("/repo"))
        mock_good.assert_called_once_with(Path("/repo"), "HEAD~3")


def test_merge_non_git_repo(runner):
    with patch("guardian.cli.get_git_dir", return_value=None):
        result = runner.invoke(app, ["merge", "/not/a/git/repo"])
        assert result.exit_code == 2
        assert "not a git repository" in result.stdout.lower()


def test_merge_success(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (True, "Successfully merged feature into main")

        result = runner.invoke(app, ["merge", "/repo"], input="main\nfeature\nn\nn\n")

        assert result.exit_code == 0
        assert "Three-way Merge Tool" in result.stdout
        assert "Merging feature into main" in result.stdout
        assert "Merge successful" in result.stdout

        mock_merge.assert_called_once_with(Path("/repo"), "main", "feature", None, None)


def test_merge_with_options(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (
            True,
            "Successfully merged feature into main using custom options",
        )

        result = runner.invoke(
            app,
            ["merge", "/repo"],
            input="main\nfeature\ny\ncommon-ancestor\ny\nrecursive\n",
        )

        assert result.exit_code == 0
        assert "Three-way Merge Tool" in result.stdout
        assert "Merge successful" in result.stdout

        mock_merge.assert_called_once_with(
            Path("/repo"), "main", "feature", "common-ancestor", "recursive"
        )


def test_merge_conflict(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (
            False,
            "Merge conflicts detected: CONFLICT (content): Merge conflict in file.txt",
        )

        result = runner.invoke(
            app, ["merge", "/repo"], input="main\nfeature\nn\nn\ny\nmanual\n"
        )

        assert result.exit_code == 1
        assert "Three-way Merge Tool" in result.stdout
        assert "Merge failed" in result.stdout
        assert "conflict" in result.stdout.lower()
        assert "Please resolve conflicts manually" in result.stdout

        mock_merge.assert_called_once_with(Path("/repo"), "main", "feature", None, None)


def test_merge_conflict_ours_strategy(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (
            False,
            "Merge conflicts detected: CONFLICT (content): Merge conflict in file.txt",
        )

        result = runner.invoke(
            app, ["merge", "/repo"], input="main\nfeature\nn\nn\ny\nours\n"
        )

        assert result.exit_code == 1
        assert "Resolving with 'ours' strategy" in result.stdout
        assert "git checkout --ours" in result.stdout


def test_merge_conflict_theirs_strategy(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (
            False,
            "Merge conflicts detected: CONFLICT (content): Merge conflict in file.txt",
        )

        result = runner.invoke(
            app, ["merge", "/repo"], input="main\nfeature\nn\nn\ny\ntheirs\n"
        )

        assert result.exit_code == 1
        assert "Resolving with 'theirs' strategy" in result.stdout
        assert "git checkout --theirs" in result.stdout


def test_merge_failure_not_conflict(runner, mock_git_repo):
    with patch("guardian.cli.perform_three_way_merge") as mock_merge:
        mock_merge.return_value = (False, "Merge failed: not a valid branch")

        result = runner.invoke(
            app, ["merge", "/repo"], input="main\ninvalid-branch\nn\nn\n"
        )

        assert result.exit_code == 1
        assert "Merge failed" in result.stdout
        assert "not a valid branch" in result.stdout
