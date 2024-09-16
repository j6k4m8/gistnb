import pathlib
import click
import nbformat as nbf
import tempfile


def _split_package_and_version(package: str) -> tuple[str, str | None]:
    # Split the package string into name and version
    if "==" in package:
        result = tuple(package.split("=="))
    elif ">=" in package:
        result = tuple(package.split(">="))
    elif "<=" in package:
        result = tuple(package.split("<="))
    elif ">" in package:
        result = tuple(package.split(">"))
    elif "<" in package:
        result = tuple(package.split("<"))
    else:
        result = (package, None)

    assert len(result) == 2, f"Expected 2 elements, got {len(result)}: {result}"
    return result


class DepContainer:

    def __init__(self):
        self._version_pins = {}

    def pin(self, package, version):
        self._version_pins[package] = version

    @classmethod
    def from_list(cls, packages: list[str]):
        container = cls()
        for package in packages:
            pkg, ver = _split_package_and_version(package)
            container.pin(pkg, ver)
        return container


@click.group()
@click.argument("notebook", type=click.Path())
@click.option("--venv-path", type=click.Path(), default=".venv")
@click.pass_context
def cli(ctx, notebook, venv_path):
    ctx.ensure_object(dict)

    notebook_path = pathlib.Path(notebook).with_suffix(".ipynb")
    venv_path = pathlib.Path(venv_path)

    ctx.obj["notebook"] = notebook_path
    ctx.obj["venv_path"] = venv_path
    # Confirm that the notebook exists:
    if not notebook_path.is_file():
        # Create a new notebook if it doesn't exist
        nbf.write(nbf.v4.new_notebook(), str(notebook_path))
    try:
        with open(notebook_path) as f:
            nbf.read(f, as_version=4)
    except Exception as e:
        click.echo(f"Error reading notebook: {e}")
        ctx.exit(1)


@cli.command()
@click.argument("packages", nargs=-1)
@click.pass_context
def add(ctx, packages):
    # Create a temp folder to store the requirements file
    for package in packages:




@cli.command()
@click.pass_context
def list(ctx):

    print(ctx.args)


if __name__ == "__main__":
    cli()
