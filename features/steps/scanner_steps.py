from behave import given, when, then
import subprocess
import shlex


@given('a repository with a packfile "{packfile_path}"')
def given_packfile(context, packfile_path):
    context.packfile_path = packfile_path


@when('I run "{command}"')
def when_run_command(context, command):
    context.result = subprocess.run(shlex.split(command), capture_output=True, text=True)


@then('the exit code should be {expected_exit_code:d}')
def then_exit_code(context, expected_exit_code):
    assert context.result.returncode == expected_exit_code, f"Expected {expected_exit_code}, got {context.result.returncode}"


@then('the output should contain "{expected_output}"')
def then_output_contains(context, expected_output):
    assert expected_output in context.result.stdout, f"Expected output to contain '{expected_output}', but got: {context.result.stdout}"
