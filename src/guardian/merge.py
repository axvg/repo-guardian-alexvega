from pathlib import Path
from typing import Tuple, Union, Optional
import guardian.git_commands


def perform_three_way_merge(
    repo_path: Union[str, Path],
    ours_branch: str,
    theirs_branch: str,
    base_commit: Optional[str] = None,
    strategy: Optional[str] = None,
) -> Tuple[bool, str]:
    """
    Perform a three-way merge between two branches

    Args:
        repo_path: Path to the git repository
        ours_branch: Our branch name (the branch we are on)
        theirs_branch: Their branch name (the branch to merge in)
        base_commit: Optional base commit for the merge (common ancestor)
        strategy: Git merge strategy to use (recursive, resolve, octopus, ours, subtree)

    Returns:
        Tuple of (success, message)
    """
    result = guardian.git_commands.run_git_command(repo_path, ["checkout", ours_branch])
    if result.returncode != 0:
        return False, f"Failed to checkout branch {ours_branch}: {result.stderr}"

    merge_cmd = ["merge"]

    if strategy:
        merge_cmd.extend(["-s", strategy])

    if base_commit:
        merge_cmd.extend(["--onto", base_commit])

    merge_cmd.append(theirs_branch)

    result = guardian.git_commands.run_git_command(repo_path, merge_cmd)

    if result.returncode == 0:
        return True, f"Successfully merged {theirs_branch} into {ours_branch}"
    else:
        if "CONFLICT" in result.stderr or "Automatic merge failed" in result.stderr:
            return False, f"Merge conflicts detected: {result.stderr}"
        else:
            return False, f"Merge failed: {result.stderr}"
