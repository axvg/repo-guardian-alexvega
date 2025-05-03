import typer
from pathlib import Path
import networkx as nx

from guardian.object_scanner import read_loose, read_packfile
from guardian.utils import (
    get_git_dir,
    find_loose_object_dirs,
    find_packfiles
)

from guardian.dag_builder import (
    build_dag_from_git_commits,
    calculate_generation_numbers,
    get_dag_stats,
    detect_history_rewrites
)


app = typer.Typer()


@app.command()
def scan(repo_path: str):
    """
    Scan a Git repository for loose objects and packfiles.
    Prints the type, SHA, and size of each object found.
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
                    f"o: t={obj.obj_type}, sha={obj.sha}, size={obj.size}",
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
                        f"p: t={obj.obj_type}, sha={obj.sha}, size={obj.size}",
                        fg=typer.colors.YELLOW,
                        bold=True,
                        )
        except Exception as e:
            typer.echo(f"err     packfile: {e}")


@app.command()
def build_dag(repo_path: str):
    """
    Build a DAG from Git commits in a repository.
    Prints the number of nodes and edges in the DAG,
    and the generation numbers of each commit.
    Also writes the DAG to a graphML file.
    """
    print("Building DAG from Git commits...")
    repo_path = Path(repo_path)
    git_repo_path = get_git_dir(repo_path)
    print(f"Repo path: {git_repo_path}")

    typer.secho(
        f"Building DAG from {git_repo_path}...",
        fg=typer.colors.MAGENTA,
        bold=True,
    )
    dag = build_dag_from_git_commits(git_repo_path)
    typer.echo(
        f"DAG with {len(dag.nodes())} nodes and {len(dag.edges())} edges"
    )

    typer.secho("Calculating generation numbers...", fg=typer.colors.BLUE)

    gen_numbers = calculate_generation_numbers(dag)

    typer.secho(
        f"Generation numbers: {gen_numbers}",
        fg=typer.colors.GREEN,
        bold=True,
    )

    stats = get_dag_stats(dag)

    typer.secho(
        f"DAG stats: {stats}",
        fg=typer.colors.CYAN,
        bold=True,
    )

    nx.write_graphml(dag, "dag.graphml")
    typer.secho(
        "DAG written to dag.graphml",
        fg=typer.colors.GREEN,
        bold=True,
    )


@app.command()
def detect_rewrites(repo_path: str):
    """
    Detect potential history rewrites using Jaro-Winkler distance
    """
    repo_path = Path(repo_path)
    git_repo_path = get_git_dir(repo_path)
    if not git_repo_path:
        typer.echo(f"Path {repo_path} is not a git repository!")
        raise typer.Exit(code=2)

    typer.secho(
        f"Building DAG from {git_repo_path}...",
        fg=typer.colors.BLUE,
        bold=True)
    dag = build_dag_from_git_commits(git_repo_path)

    typer.secho(
        "Detecting potential history rewrites...",
        fg=typer.colors.BLUE)
    results = detect_history_rewrites(dag)

    if not results["rewrites"]:
        typer.secho(
            "No potential history rewrites detected.",
            fg=typer.colors.GREEN)
    else:
        typer.secho(
            f"Found {len(results['rewrites'])} potential history rewrites:",
            fg=typer.colors.YELLOW, bold=True)

        for rewrite in results["rewrites"]:
            typer.echo("")
            typer.secho(
                f"Similarity: {rewrite['similarity']:.4f}",
                fg=typer.colors.YELLOW)
            typer.echo(f"Commit 1: {rewrite['commit1'][:8]}")
            typer.echo(f"Path 1  : {rewrite['path1']}")
            typer.echo(f"Commit 2: {rewrite['commit2'][:8]}")
            typer.echo(f"Path 2  : {rewrite['path2']}")
    return 3 if results["rewrites"] else 0


if __name__ == "__main__":
    app()
