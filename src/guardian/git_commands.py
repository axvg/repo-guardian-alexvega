import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Union
import logging

logger = logging.getLogger(__name__)


def run_git_command(
    repo_path: Union[str, Path], args: List[str]
) -> subprocess.CompletedProcess:
    """
    Run a git command in the specified repository path

    Args:
        repo_path: Path to the repository with Git
        args: List of arguments to pass to git

    Returns:
        CompletedProcess object with the command result
    """
    cmd = ["git", "-C", str(repo_path)] + args
    logger.debug(f"Running git command: {' '.join(cmd)}")
    return subprocess.run(cmd, capture_output=True, text=True)


def bisect_start(repo_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Start a bisect session

    Args:
        repo_path: Path to the repository with Git

    Returns:
        Tuple of (success, message)
    """
    result = run_git_command(repo_path, ["bisect", "start"])
    if result.returncode == 0:
        return True, "Bisect session started successfully"
    return False, f"Failed to start bisect session: {result.stderr}"


def bisect_good(repo_path: Union[str, Path], commit: str) -> Tuple[bool, str]:
    """
    Mark a commit as good in a bisect session

    Args:
        repo_path: Path to the repository with Git
        commit: Commit reference  with SHA, tag, branch

    Returns:
        Tuple of (success, message)
    """
    result = run_git_command(repo_path, ["bisect", "good", commit])
    if result.returncode == 0:
        return True, f"Marked commit {commit} as good\n{result.stdout}"
    return False, f"Failed to mark commit as good: {result.stderr}"


def bisect_bad(repo_path: Union[str, Path], commit: str) -> Tuple[bool, str]:
    """
    Mark a commit as bad in a bisect session

    Args:
        repo_path: Path to the repository with Git
        commit: Commit reference (SHA, tag, branch, etc.)

    Returns:
        Tuple of (success, message)
    """
    result = run_git_command(repo_path, ["bisect", "bad", commit])
    if result.returncode == 0:
        return True, f"Marked commit {commit} as bad\n{result.stdout}"
    return False, f"Failed to mark commit as bad: {result.stderr}"


def bisect_reset(repo_path: Union[str, Path]) -> Tuple[bool, str]:
    """
    Reset a bisect session

    Args:
        repo_path: Path to the repository with Git

    Returns:
        Tuple of (success, message)
    """
    result = run_git_command(repo_path, ["bisect", "reset"])
    if result.returncode == 0:
        return True, "Bisect session reset successfully"
    return False, f"Failed to reset bisect session: {result.stderr}"


def bisect_run(repo_path: Union[str, Path], command: str) -> Tuple[bool, str]:
    """
    Run an automated bisect session with the given test command

    Args:
        repo_path: Path to the repository with Git
        command: Shell command to run to test each commit

    Returns:
        Tuple of (success, message) containing the results
    """
    cmd_args = command.split()
    git_args = ["bisect", "run"] + cmd_args

    result = run_git_command(repo_path, git_args)

    if result.returncode < 128:  # Git error codes start at 128 # TODO: rewrite this
        output = result.stdout
        if result.stderr:
            output += "\n" + result.stderr
        return True, f"Bisect run completed:\n{output}"

    return False, f"Bisect run failed: {result.stderr}"


def bisect_log(repo_path: Union[str, Path]) -> Tuple[bool, str, Dict]:
    """
    Get the bisect log which shows the history of the bisect session

    Args:
        repo_path: Path to the repository with Git

    Returns:
        Tuple of (success, log_text, parsed_data)
    """
    result = run_git_command(repo_path, ["bisect", "log"])

    if result.returncode != 0:
        return False, f"Failed to get bisect log: {result.stderr}", {}

    good_commits = []
    bad_commits = []

    for line in result.stdout.splitlines():
        if "# good" in line:
            commit = line.split()[-1].strip()
            good_commits.append(commit)
        elif "# bad" in line:
            commit = line.split()[-1].strip()
            bad_commits.append(commit)

    parsed_data = {"good_commits": good_commits, "bad_commits": bad_commits}

    return True, result.stdout, parsed_data


def get_current_bisect_status(repo_path: Union[str, Path]) -> Optional[str]:
    """
    Get information about where we currently are in the bisect process

    Args:
        repo_path: Path to the repository with Git

    Returns:
        Current commit being tested or None if not in bisect
    """
    git_dir_result = run_git_command(repo_path, ["rev-parse", "--git-dir"])

    if git_dir_result.returncode != 0:
        return None

    git_dir = Path(git_dir_result.stdout.strip())
    if not (Path(repo_path) / git_dir / "BISECT_HEAD").exists():
        return None

    result = run_git_command(repo_path, ["rev-parse", "BISECT_HEAD"])

    if result.returncode != 0:
        return None

    return result.stdout.strip()
