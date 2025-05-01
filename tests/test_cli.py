from typer.testing import CliRunner
from guardian.cli import app

runner = CliRunner()


def test_scan_command():
    result = runner.invoke(app, ["scan"])
    assert result.exit_code == 0
    assert "Iniciando scaneo de" in result.output
    assert "TODO..." in result.output
