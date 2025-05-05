import pytest
from pathlib import Path
import os
import tempfile
from guardian.repair import (
    generate_repair_script,
    generate_rebase_todo,
    RepairAction,
    create_cherry_pick_script,
    create_rebase_script,
    create_reset_recovery_script,
)


@pytest.fixture
def temp_repo_path():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)


def test_generate_repair_script(temp_repo_path):
    actions = [
        RepairAction(
            action_type="cherry-pick",
            source_commit="abcd1234",
            description="Apply commit from feature branch",
        ),
        RepairAction(
            action_type="rebase",
            source_commit="efgh5678",
            target_branch="main",
            description="Rebase commit onto main",
        ),
    ]

    success, _, script_path = generate_repair_script(
        temp_repo_path, actions, temp_repo_path
    )

    assert success
    assert script_path.exists()
    assert script_path.is_file()

    with open(script_path, "r") as f:
        content = f.read()
        assert "#!/bin/bash" in content
        assert "git cherry-pick abcd1234" in content
        assert "git rebase --onto main efgh5678^ efgh5678" in content

    assert os.access(script_path, os.X_OK)


def test_generate_rebase_todo(temp_repo_path):
    commits = ["abcd1234", "efgh5678", "ijkl9012"]

    success, _, todo_path = generate_rebase_todo(
        temp_repo_path, commits, temp_repo_path
    )

    assert success
    assert todo_path.exists()
    assert todo_path.is_file()

    with open(todo_path, "r") as f:
        content = f.read()
        assert "pick abcd1234" in content
        assert "pick efgh5678" in content
        assert "pick ijkl9012" in content


def test_create_cherry_pick_script(temp_repo_path):
    commits = ["abcd1234", "efgh5678"]

    success, _, script_path = create_cherry_pick_script(
        temp_repo_path, commits, "feature-branch", temp_repo_path
    )

    assert success
    assert script_path.exists()
    assert script_path.is_file()

    with open(script_path, "r") as f:
        content = f.read()
        assert "git cherry-pick abcd1234" in content
        assert "git cherry-pick efgh5678" in content


def test_create_rebase_script(temp_repo_path):
    success, _, script_path = create_rebase_script(
        temp_repo_path, "feature-branch", "main", False, temp_repo_path
    )

    assert success
    assert script_path.exists()

    with open(script_path, "r") as f:
        content = f.read()
        assert "git checkout feature-branch" in content
        assert "git rebase main" in content


def test_create_rebase_script_interactive(temp_repo_path):
    success, _, script_path = create_rebase_script(
        temp_repo_path, "feature-branch", "main", True, temp_repo_path
    )

    assert success
    assert script_path.exists()

    with open(script_path, "r") as f:
        content = f.read()
        assert "git rebase -i main feature-branch" in content


def test_create_reset_recovery_script(temp_repo_path):
    success, _, script_path = create_reset_recovery_script(
        temp_repo_path, "abcd1234", True, temp_repo_path
    )

    assert success
    assert script_path.exists()

    with open(script_path, "r") as f:
        content = f.read()
        assert "Creating backup branch" in content
        assert "git reset --hard abcd1234" in content
