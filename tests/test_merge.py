from unittest.mock import patch, MagicMock

from guardian.merge import (
    perform_three_way_merge,
)


def test_perform_three_way_merge():
    with patch("guardian.git_commands.run_git_command") as mock_run:
        checkout_result = MagicMock()
        checkout_result.returncode = 0

        merge_result = MagicMock()
        merge_result.returncode = 0
        merge_result.stdout = "Successfully merged branches"

        mock_run.side_effect = [checkout_result, merge_result]

        success, message = perform_three_way_merge(
            "/repo", "main", "feature", None, "recursive"
        )

        assert success is True
        assert "Successfully merged" in message

        assert mock_run.call_count == 2

        args1 = mock_run.call_args_list[0][0][1]
        assert "checkout" in args1
        assert "main" in args1

        args2 = mock_run.call_args_list[1][0][1]
        assert "merge" in args2
        assert "-s" in args2
        assert "recursive" in args2
        assert "feature" in args2


def test_perform_three_way_merge_with_conflict():
    with patch("guardian.git_commands.run_git_command") as mock_run:
        checkout_result = MagicMock()
        checkout_result.returncode = 0

        merge_result = MagicMock()
        merge_result.returncode = 1
        merge_result.stderr = "CONFLICT (content): Merge conflict in file.txt"

        mock_run.side_effect = [checkout_result, merge_result]

        success, message = perform_three_way_merge("/repo", "main", "feature")

        assert success is False
        assert "Merge conflicts detected" in message
        assert "file.txt" in message
