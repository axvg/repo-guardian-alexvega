import typer

app = typer.Typer()


@app.command()
def scan(repo_path: str = typer.Argument(
            ".", help="Ruta al directorio .git de tu repositorio"
        )):
    """
    Scanea el directorio .git de tu repositorio
    """
    typer.echo(f"Iniciando scaneo de {repo_path}...")
    typer.echo("TODO...")


def main():
    app()


if __name__ == "__main__":
    main()
