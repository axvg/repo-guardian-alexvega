from dataclasses import dataclass
from typing import Literal
from pathlib import Path
import zlib
import hashlib


@dataclass
class GitObject:
    """Class representing a Git object and its metadata"""
    type: Literal["blob", "tree", "commit", "tag"]
    sha: str
    size: int
    content: bytes


def read_loose(object_dir: Path) -> GitObject:
    """Read a loose Git object given its path"""
    if not object_dir.is_dir() or len(object_dir.stem) != 2:
        raise ValueError(
            f"Path must be a directory with 2 digits {object_dir.stem}"
            )

    object_file_path = next(object_dir.iterdir())
    # print(f"Object file path: {object_file_path}")

    # This should never happen but just in case
    if not object_file_path.is_file():
        raise ValueError("Path must be a file!")

    sha_parent = object_dir.name
    sha_child = object_file_path.name
    sha = sha_parent + sha_child

    with open(object_file_path, "rb") as f:
        compressed_data = f.read()
        decompressed_data = zlib.decompress(compressed_data)

        null_pos = decompressed_data.find(b'\0')
        if null_pos == -1:
            raise ValueError("Malformed header!!")

        header = decompressed_data[:null_pos].decode('ascii')
        content = decompressed_data[null_pos+1:]

        type, size_str = header.split(' ')
        if type not in ["blob", "tree", "commit", "tag"]:
            raise ValueError(f"Unknown object type -> {type}")

        calculated_sha = hashlib.sha1(decompressed_data).hexdigest()
        if calculated_sha != sha:
            raise ValueError(f"SHA mismatch! {sha} is not {calculated_sha}")

        size = int(size_str)
        if size != len(content):
            raise ValueError(f"Size mismatch! {size} != {len(content)}")

        return GitObject(
            type=type,
            sha=sha,
            size=size,
            content=content,
        )
