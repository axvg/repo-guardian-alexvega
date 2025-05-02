from pathlib import Path


def get_git_dir(repo_path: Path) -> Path | None:
    """
    Returns path to the .git directory inside repo_path or not.
    """
    git_dir = repo_path / ".git"
    if git_dir.is_dir():
        return git_dir
    return None


def find_loose_object_dirs(git_dir: Path) -> list[Path]:
    """
    Returns a list of paths for loose object directories .
    """
    loose_dirs = []
    objects_dir = git_dir / "objects"
    if not objects_dir.is_dir():
        return loose_dirs
    for d in objects_dir.iterdir():
        if d.is_dir() and len(d.name) == 2:
            is_hex = True
            for c in d.name.lower():
                if c not in "0123456789abcdef":
                    is_hex = False
                    break
            if is_hex:
                loose_dirs.append(d)
    return loose_dirs


def find_packfiles(git_dir: Path) -> list[Path]:
    """
    Returns a list of paths for packfiles.
    """
    packfiles = []
    pack_dir = git_dir / "objects" / "pack"
    if not pack_dir.is_dir():
        return packfiles
    for f in pack_dir.iterdir():
        if f.is_file() and f.name.endswith(".pack"):
            packfiles.append(f)
    return packfiles
