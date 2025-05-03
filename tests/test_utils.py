import pytest
from pathlib import Path
from unittest.mock import patch
from guardian.utils import get_git_dir, find_loose_object_dirs, find_packfiles


@pytest.fixture
def mock_repo_path():
    return Path("/repo")


@pytest.fixture
def mock_git_dir():
    return Path("/repo/.git")


def test_get_git_dir_exists(mock_repo_path):
    with patch.object(Path, "is_dir", return_value=True):
        result = get_git_dir(mock_repo_path)
        assert result == mock_repo_path / ".git"


def test_get_git_dir_not_exists(mock_repo_path):
    with patch.object(Path, "is_dir", return_value=False):
        result = get_git_dir(mock_repo_path)
        assert result is None


def test_find_loose_object_dirs_none(mock_git_dir):
    with patch.object(Path, "is_dir", return_value=False):
        result = find_loose_object_dirs(mock_git_dir)
        assert result == []


def test_find_loose_object_dirs_empty(mock_git_dir):
    with patch.object(Path, "is_dir", return_value=True):
        with patch.object(Path, "iterdir", return_value=[]):
            result = find_loose_object_dirs(mock_git_dir)
            assert result == []


def test_find_packfiles_none(mock_git_dir):
    with patch.object(Path, "is_dir", return_value=False):
        result = find_packfiles(mock_git_dir)
        assert result == []


def test_find_packfiles_empty(mock_git_dir):
    with patch.object(Path, "is_dir", return_value=True):
        with patch.object(Path, "iterdir", return_value=[]):
            result = find_packfiles(mock_git_dir)
            assert result == []
