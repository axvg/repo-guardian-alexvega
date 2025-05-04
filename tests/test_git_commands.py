import pytest
from unittest.mock import patch, MagicMock

from src.guardian.git_commands import (
    run_git_command,
    bisect_start,
    bisect_good,
    bisect_bad,
    bisect_reset,
    bisect_run,
    bisect_log,
    get_current_bisect_status
)


@pytest.fixture
def mock_subprocess_run():
    with patch('guardian.git_commands.subprocess.run') as mock_run:
        mock_process = MagicMock()
        mock_process.returncode = 0
        mock_process.stderr = ""
        mock_run.return_value = mock_process
        yield mock_run


def test_run_git_command(mock_subprocess_run):
    repo_path = "/repo"
    args = ["status", "--short"]
    result = run_git_command(repo_path, args)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "status", "--short"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0


def test_bisect_start(mock_subprocess_run):
    repo_path = "/repo"
    success, message = bisect_start(repo_path)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "start"],
        capture_output=True,
        text=True
    )
    assert success is True
    assert "successfully" in message


def test_bisect_start_failure(mock_subprocess_run):
    repo_path = "/repo"
    mock_subprocess_run.return_value.returncode = 1
    mock_subprocess_run.return_value.stderr = "Error starting bisect"
    success, message = bisect_start(repo_path)
    assert success is False
    assert "Failed" in message
    assert "Error starting bisect" in message


def test_bisect_good(mock_subprocess_run):
    repo_path = "/repo"
    commit = "abcd1234"
    success, message = bisect_good(repo_path, commit)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "good", commit],
        capture_output=True,
        text=True
    )
    assert success is True
    assert commit in message


def test_bisect_bad(mock_subprocess_run):
    repo_path = "/repo"
    commit = "abcd1234"
    success, message = bisect_bad(repo_path, commit)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "bad", commit],
        capture_output=True,
        text=True
    )
    assert success is True
    assert commit in message


def test_bisect_reset(mock_subprocess_run):
    repo_path = "/repo"
    success, message = bisect_reset(repo_path)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "reset"],
        capture_output=True,
        text=True
    )
    assert success is True
    assert "reset successfully" in message


def test_bisect_run(mock_subprocess_run):
    repo_path = "/repo"
    command = "python test.py"
    success, message = bisect_run(repo_path, command)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "run", "python", "test.py"],
        capture_output=True,
        text=True
    )
    assert success is True
    assert "completed" in message


def test_bisect_log(mock_subprocess_run):
    repo_path = "/repo"
    mock_subprocess_run.return_value.stdout = (
        "# bad: [abcd1234] Bad commit\n"
        "# good: [efgh5678] Good commit\n"
    )
    success, log_text, parsed = bisect_log(repo_path)
    mock_subprocess_run.assert_called_once_with(
        ["git", "-C", repo_path, "bisect", "log"],
        capture_output=True,
        text=True
    )
    assert success is True
    assert log_text == mock_subprocess_run.return_value.stdout


def test_get_current_bisect_status(mock_subprocess_run):
    repo_path = "/repo"
    mock_subprocess_run.side_effect = [
        MagicMock(returncode=0, stdout=".git"),
        MagicMock(returncode=0, stdout="abcd1234efgh5678")
    ]
    with patch('guardian.git_commands.Path.exists', return_value=True):
        result = get_current_bisect_status(repo_path)
    assert result == "abcd1234efgh5678"
