import typer
from guardian.object_scanner import read_loose, read_packfile
from pathlib import Path
from guardian.utils import get_git_dir, find_loose_object_dirs, find_packfiles

app = typer.Typer()


@app.command()
def scan(repo_path: str):
    """
    Scanea el directorio .git de tu repositorio
    """
    repo_path = Path(repo_path)
    git_repo_path = get_git_dir(repo_path)
    if not git_repo_path:
        typer.echo(f"Path {repo_path} is not a git repository!")
        raise typer.Exit(code=2)

    loose_dirs = find_loose_object_dirs(git_repo_path)
    pack_dirs = find_packfiles(git_repo_path)

    typer.secho(
        f"Tenemos {len(loose_dirs)} loose objects y {len(pack_dirs)} packs",
        fg=typer.colors.BLUE,
        bold=True,
        )

    if loose_dirs:
        try:
            for obj_dir in loose_dirs:
                obj = read_loose(obj_dir)
                typer.secho(
                    f"loose: tipo={obj.type}, sha={obj.sha}, size={obj.size}",
                    fg=typer.colors.BRIGHT_RED,
                    bold=True,
                    )
        except Exception as e:
            typer.echo(f"err en obj loose: {e}")

    if pack_dirs:
        try:
            for pack_dir in pack_dirs:
                pack = read_packfile(pack_dir)
                for obj in pack:
                    typer.secho(
                        f"pack: tipo={obj.type}, size={obj.size}",
                        fg=typer.colors.YELLOW,
                        bold=True,
                        )
        except Exception as e:
            typer.echo(f"err     packfile: {e}")


if __name__ == "__main__":
    app()
