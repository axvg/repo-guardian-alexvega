import pytest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
from guardian.cli import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_git_repo():
    with patch("guardian.cli.get_git_dir") as mock_get_git_dir:
        mock_get_git_dir.return_value = Path("/repo/.git")
        yield mock_get_git_dir


def test_generate_script_non_git_repo(runner):
    with patch("guardian.cli.get_git_dir", return_value=None):
        result = runner.invoke(app, ["generate-script", "/not/a/git/repo"])
        assert result.exit_code == 2
        assert "not a git repository" in result.stdout.lower()
