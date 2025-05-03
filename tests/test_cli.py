import pytest
from pathlib import Path
from unittest.mock import patch
from typer.testing import CliRunner
from guardian.cli import app
from guardian.object_scanner import GitObject


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_git_repo():
    with patch('guardian.cli.get_git_dir') as mock_get_git_dir:
        mock_get_git_dir.return_value = Path('/repo/.git')
        yield mock_get_git_dir


@pytest.fixture
def mock_loose_object():
    return GitObject(
        obj_type="blob",
        sha="abcd1234",
        size=42,
        content=b"fake content"
    )


@pytest.fixture
def mock_pack_object():
    return GitObject(
        obj_type="commit",
        sha="1234abcd",
        size=120,
        content=b"fake packed content"
    )


def test_scan_non_git_repo(runner):
    with patch('guardian.cli.get_git_dir', return_value=None):
        result = runner.invoke(app, ["/not/a/git/repo"])
        assert result.exit_code == 2


def test_scan_empty_repo(runner, mock_git_repo):
    with patch(
        'guardian.cli.find_loose_object_dirs', return_value=[]
              ) as mock_find_loose:
        with patch(
            'guardian.cli.find_packfiles', return_value=[]
                  ) as mock_find_packs:
            result = runner.invoke(app, ["/repo"])
            assert result.exit_code == 0
            assert "Tenemos 0 loose objects y 0 packs" in result.stdout
            mock_find_loose.assert_called_once()
            mock_find_packs.assert_called_once()


def test_scan_with_loose_error(runner, mock_git_repo):
    loose_dirs = [Path('/repo/.git/objects/ab/cd1234')]
    with patch(
            'guardian.cli.find_loose_object_dirs', return_value=loose_dirs
                ) as mock_find_loose:
        with patch(
            'guardian.cli.find_packfiles', return_value=[]
                ) as mock_find_packs:
            with patch(
                    'guardian.cli.read_loose', return_value=mock_loose_object,
                    side_effect=ValueError("Corrupted object")
                    ) as mock_read_loose:
                res = runner.invoke(app, ["/repo"])
                assert "Tenemos 1 loose objects y 0 packs" in res.stdout
                assert "err en obj loose: Corrupted object" in res.stdout
                mock_find_loose.assert_called_once()
                mock_find_packs.assert_called_once()
                mock_read_loose.assert_called_once()


def test_scan_with_packfile_error(runner, mock_git_repo):
    pack_files = [Path('/repo/.git/objects/pack/pack-abc123.pack')]
    with patch(
        'guardian.cli.find_loose_object_dirs', return_value=[]
              ) as mock_find_loose:
        with patch(
            'guardian.cli.find_packfiles', return_value=pack_files
                  ) as mock_find_packs:
            with patch(
                'guardian.cli.read_packfile',
                side_effect=ValueError("Corrupted packfile")
                      ) as mock_read_pack:
                result = runner.invoke(app, ["/repo"])
                assert "Tenemos 0 loose objects y 1 packs" in result.stdout
                assert "err     packfile: Corrupted packfile" in result.stdout
                mock_find_loose.assert_called_once()
                mock_find_packs.assert_called_once()
                mock_read_pack.assert_called_once()


def test_scan_with_objects_and_packfiles(runner, mock_git_repo, mock_loose_object, mock_pack_object):
    loose_dirs = [Path('/repo/.git/objects/ab/cd1234')]
    pack_files = [Path('/repo/.git/objects/pack/pack-abc123.pack')]
    with patch(
        'guardian.cli.find_loose_object_dirs',
        return_value=loose_dirs
              ) as mock_find_loose:
        with patch(
            'guardian.cli.find_packfiles',
            return_value=pack_files
                  ) as mock_find_packs:
            with patch(
                'guardian.cli.read_loose',
                return_value=mock_loose_object
                      ) as mock_read_loose:
                with patch(
                    'guardian.cli.read_packfile',
                    return_value=[mock_pack_object]
                          ) as mock_read_pack:
                    res = runner.invoke(app, ["/repo"])
                    assert "Tenemos 1 loose objects y 1 packs" in res.stdout
                    assert f"o: t={mock_loose_object.obj_type}" in res.stdout
                    assert f"p: t={mock_pack_object.obj_type}" in res.stdout
                    mock_find_loose.assert_called_once()
                    mock_find_packs.assert_called_once()
                    mock_read_loose.assert_called_once()
                    mock_read_pack.assert_called_once()
