from guardian.object_scanner import GitObject, find_idx_path, read_packfile, \
    get_object_offsets, read_single_object
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, mock_open


def test_read_packfile_with_mocks():
    fake_pack_path = MagicMock()
    fake_idx_path = MagicMock()
    fake_sha = "a" * 40
    fake_offset = 123
    fake_obj = GitObject("blob", fake_sha, 6, b"foobar")

    m = mock_open(read_data=b"PACK")
    with patch("guardian.object_scanner.Path.is_file", return_value=True), \
         patch("guardian.object_scanner.open", m), \
         patch(
             "guardian.object_scanner.find_idx_path",
             return_value=fake_idx_path), \
         patch(
             "guardian.object_scanner.get_object_offsets",
             return_value={fake_sha: fake_offset}), \
         patch(
             "guardian.object_scanner.extract_object_at_offset",
             return_value=fake_obj):
        objs = read_packfile(fake_pack_path)
        assert len(objs) == 1
        assert objs[0].sha == fake_sha
        assert objs[0].content == b"foobar"


def test_find_idx_path_exists():
    fake_pack = Path("repo/packfile.pack")
    fake_idx = Path("repo/packfile.idx")
    with patch.object(Path, "with_suffix", return_value=fake_idx), \
         patch.object(Path, "exists", return_value=True):
        assert find_idx_path(fake_pack) == fake_idx


def test_find_idx_path_not_exists():
    fake_pack = Path("repo/packfile.pack")
    fake_idx = Path("repo/packfile.idx")
    with patch.object(Path, "with_suffix", return_value=fake_idx), \
         patch.object(Path, "exists", return_value=False):
        with pytest.raises(ValueError, match="Index file not found"):
            find_idx_path(fake_pack)


# TODO: rewrite this...
def test_get_object_offsets_valid_idx():
    fake_idx_path = MagicMock()
    fake_sha = b"\xaa" * 20
    fake_offset = 123
    fanout = (0,) * 255 + (1,)
    data = (
        b"\xff\x74\x4f\x63" +
        (2).to_bytes(4, "big") +
        b"".join((i).to_bytes(4, "big") for i in fanout) +
        fake_sha +
        (0).to_bytes(4, "big") +
        (fake_offset).to_bytes(4, "big")
    )
    m = mock_open(read_data=data)
    with patch("builtins.open", m):
        offsets = get_object_offsets(fake_idx_path)
        assert list(offsets.keys())[0] == fake_sha.hex()


def test_get_object_offsets_invalid_header():
    fake_idx_path = MagicMock()
    m = mock_open(read_data=b"BAD!")
    with patch("builtins.open", m):
        with pytest.raises(ValueError, match="Invalid index file header"):
            get_object_offsets(fake_idx_path)


def test_read_single_object_success():
    fake_pack_path = MagicMock()
    fake_idx_path = MagicMock()
    fake_sha = "a" * 40
    fake_offset = 123
    fake_obj = GitObject("blob", fake_sha, 6, b"foobar")
    with patch(
        "guardian.object_scanner.find_idx_path",
        return_value=fake_idx_path), \
        patch("guardian.object_scanner.get_object_offsets",
              return_value={fake_sha: fake_offset}), \
        patch("guardian.object_scanner.extract_object_at_offset",
              return_value=fake_obj):
        obj = read_single_object(fake_pack_path, fake_sha)
        assert obj.sha == fake_sha
        assert obj.content == b"foobar"


def test_read_single_object_not_found():
    fake_pack_path = MagicMock()
    fake_idx_path = MagicMock()
    fake_sha = "a" * 40
    with patch("guardian.object_scanner.find_idx_path",
               return_value=fake_idx_path), \
         patch("guardian.object_scanner.get_object_offsets", return_value={}):
        with pytest.raises(ValueError, match="Object with SHA"):
            read_single_object(fake_pack_path, fake_sha)
