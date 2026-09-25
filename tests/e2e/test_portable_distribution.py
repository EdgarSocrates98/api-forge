from typer.testing import CliRunner

from apiforge.cli import app


def test_cli_inspect_is_hostless(tmp_path):
    result = CliRunner().invoke(
        app, ["inspect", "--root", str(tmp_path), "--detail-level", "summary"]
    )
    assert result.exit_code == 0, result.stdout
    assert '"paths"' in result.stdout


def test_cli_init_creates_only_minimal_project_manifest(tmp_path):
    result = CliRunner().invoke(app, ["init", "--root", str(tmp_path)])
    assert result.exit_code == 0, result.stdout
    assert (tmp_path / ".apiforge" / "project.yaml").is_file()
    assert not (tmp_path / "CLAUDE.md").exists()
