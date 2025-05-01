from src.guardian import object_scanner
import pytest
from pathlib import Path
import tempfile
import zlib

OBJECT_DIR_PATH = Path("features/corrupt-blob.git/objects/1d")


def test_valid_object_from_features():
    git_object = object_scanner.read_loose(OBJECT_DIR_PATH)
    assert git_object.size > 0
    assert git_object.type == "tree"
    assert git_object.content is not None
    assert len(git_object.sha) > 0


def test_empty_directory():
    with tempfile.TemporaryDirectory() as temp_dir:
        empty_dir = Path(temp_dir) / "00"
        empty_dir.mkdir()

        with pytest.raises(StopIteration):
            object_scanner.read_loose(empty_dir)


def test_object_dir_not_found():
    with pytest.raises(
            ValueError,
            match="Path must be a directory with 2 digits"):
        test_path = Path("tests/test_data/objects/00")
        object_scanner.read_loose(test_path)


def test_object_dir_not_file():
    with pytest.raises(ValueError):
        test_path = Path("tests/test_data/objects/00/00")
        object_scanner.read_loose(test_path)


def test_unknown_object_type():
    with tempfile.TemporaryDirectory() as temp_dir:
        unknown_dir = Path(temp_dir) / "11"
        unknown_dir.mkdir()
        obj_file = unknown_dir / "unknown_object"
        with open(obj_file, "wb") as f:
            f.write(zlib.compress(b"unknown 10\0content"))

        with pytest.raises(ValueError, match="Unknown object type"):
            object_scanner.read_loose(unknown_dir)


def test_hash_mismatch():
    with tempfile.TemporaryDirectory() as temp_dir:
        hash_mismatch_dir = Path(temp_dir) / "00"
        hash_mismatch_dir.mkdir()
        obj_file = hash_mismatch_dir / "hash_1"
        valid_data = b"blob 11\0foo"
        tampered_data = valid_data[:-1] + b"!"
        compressed = zlib.compress(tampered_data)

        with open(obj_file, "wb") as f:
            f.write(compressed)

        with pytest.raises(ValueError, match="SHA mismatch"):
            object_scanner.read_loose(hash_mismatch_dir)
