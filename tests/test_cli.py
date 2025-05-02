from typer.testing import CliRunner
from guardian.cli import app

runner = CliRunner()


def test_scan_command():
    result = runner.invoke(app)
    # Because not path provided
    assert result.exit_code == 2


def test_scan_valid_packfile():
    result = runner.invoke(app, ["fixtures/corrupt-blob.git"])
    assert result.exit_code == 0
    assert "Tenemos 8 loose objects y 0 packs" in result.output


def test_scan_invalid_packfile():
    result = runner.invoke(
        app, [
            "fixtures/corrupt-blob.git/objects/pack/invalid-pack.git"
            ])
    assert result.exit_code == 2
