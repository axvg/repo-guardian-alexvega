from dataclasses import dataclass
from typing import Literal, List, Dict
from pathlib import Path
from hashlib import sha1
import zlib
import struct


@dataclass
class GitObject:
    """Class representing a Git object and its metadata"""
    obj_type: Literal["blob", "tree", "commit", "tag"]
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

        obj_type, size_str = header.split(' ')
        if obj_type not in ["blob", "tree", "commit", "tag"]:
            raise ValueError(f"Unknown object obj_type -> {obj_type}")

        calculated_sha = sha1(decompressed_data).hexdigest()
        if calculated_sha != sha:
            raise ValueError(f"SHA mismatch! {sha} is not {calculated_sha}")

        size = int(size_str)
        if size != len(content):
            raise ValueError(f"Size mismatch! {size} != {len(content)}")

        return GitObject(
            obj_type=obj_type,
            sha=sha,
            size=size,
            content=content,
        )


def find_idx_path(packfile_path: Path) -> Path:
    """You give me packfile path I give you index path"""
    idx_path = packfile_path.with_suffix('.idx')
    if not idx_path.exists():
        raise ValueError(f"Index file not found: {idx_path}")
    return idx_path


def get_object_offsets(idx_path: Path) -> Dict[str, int]:
    """
    Extract SHA so we can find the object in the packfile
    using offsets
    """
    sha_to_offset = {}

    with open(idx_path, "rb") as f:
        if f.read(4) != b"\xff\x74\x4f\x63":  # magic number for idx files
            raise ValueError("Invalid index file header")
        if struct.unpack(">I", f.read(4))[0] != 2:  # Version
            raise ValueError("Only version 2 index files are supported")
        fanout = struct.unpack(">" + "I" * 256, f.read(4 * 256))
        object_count = fanout[255]
        shas = [f.read(20).hex() for _ in range(object_count)]
        f.seek(4 * object_count, 1)  # skip CRC32 values
        offsets = list(
            struct.unpack(">" + "I" * object_count, f.read(4 * object_count))
            )
        for i, sha in enumerate(shas):
            offset = offsets[i]
            # this is because the offset is
            # 0x80000000 + offset for delta objects
            # and we need to remove the MSB flag
            if offset & 0x80000000:
                pass
            sha_to_offset[sha] = offset & 0x7FFFFFFF  # remove MSB flag
    return sha_to_offset


def extract_object_at_offset(packfile_path: Path, offset: int) -> GitObject:
    """
    Extract Git object using offset
    """
    with open(packfile_path, "rb") as f:
        f.seek(offset, 0)
        byte = ord(f.read(1))
        obj_type_id = (byte >> 4) & 7  # extract bits 4-6
        size = byte & 15  # extract bottom 4 bits
        shift = 4
        while byte & 0x80:
            byte = ord(f.read(1))
            size |= (byte & 0x7f) << shift
            shift += 7
        type_map = {1: "commit", 2: "tree", 3: "blob", 4: "tag"}
        if obj_type_id not in type_map:
            raise ValueError(f"Unknown object type: {obj_type_id}")
        obj_type = type_map[obj_type_id]
        compressed_data = b""
        chunk = f.read(4096)
        while chunk:
            compressed_data += chunk
            try:
                content = zlib.decompress(compressed_data)
                break  # ok decompression
            except zlib.error:
                chunk = f.read(4096)
        header_str = f"{obj_type} {size}".encode('ascii') + b'\0'
        sha = sha1(header_str + content).hexdigest()
        return GitObject(
            obj_type=obj_type,
            sha=sha,
            size=size,
            content=content
        )


def read_packfile(packfile_path: Path) -> List[GitObject]:
    """
    Read objects from packfile
    """
    if not packfile_path.is_file():
        raise ValueError(f"Packfile doesn't exist: {packfile_path}")

    with open(packfile_path, "rb") as f:
        if f.read(4) != b"PACK":
            raise ValueError("Not a valid packfile")

    idx_path = find_idx_path(packfile_path)
    sha_to_offset = get_object_offsets(idx_path)

    objects = []
    for sha, offset in sha_to_offset.items():
        try:
            obj = extract_object_at_offset(packfile_path, offset)
            obj.sha = sha
            objects.append(obj)
        except Exception as e:
            print(f"Error! extracting obj {sha} at offset {offset}: {e}")
    return objects


def read_single_object(packfile_path: Path, target_sha: str) -> GitObject:
    """
    Read one object from packfile using its SHA
    """
    idx_path = find_idx_path(packfile_path)
    sha_to_offset = get_object_offsets(idx_path)
    if target_sha not in sha_to_offset:
        raise ValueError(f"Object with SHA {target_sha} not found in packfile")
    offset = sha_to_offset[target_sha]
    return extract_object_at_offset(packfile_path, offset)
