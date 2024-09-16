import datetime
import pathlib
import subprocess
import click
import nbformat as nbf
import tempfile

_METADATA_DIR = "gistnb"
_METADATA_DEPLIST_PATH = "dependencies"


def _split_package_and_version(package: str) -> tuple[str, str | None, str | None]:
    # Split the package string into name and version
    for operator in ["==", ">=", "<=", ">", "<"]:
        if operator in package:
            result = (*tuple(package.split(operator)), operator)
    # The package name is alone I guess?
    else:
        result = (package, None, None)

    assert len(result) == 3, f"Expected 2 elements, got {len(result)}: {result}"
    return result


class DepContainer:

    def __init__(self):
        self._version_pins = {}

    def pin(self, package, version: tuple[str, str]):
        self._version_pins[package] = version

    def as_list(self):
        return [
            (f"{pkg}{op}{ver}" if ver else pkg)
            for pkg, (op, ver) in self._version_pins.items()
        ]

    @classmethod
    def from_list(cls, packages: list[str]):
        container = cls()
        for package in packages:
            pkg, ver, operator = _split_package_and_version(package)
            container.pin(pkg, (operator, ver))
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
@click.argument("package")
@click.pass_context
def add(ctx, package):
    """Add packages to the notebook metadata."""
    notebook_path = ctx.obj["notebook"]

    # Load the notebook
    with open(notebook_path) as f:
        nb = nbf.read(f, as_version=4)

    # Create or load the metadata
    if _METADATA_DIR not in nb.metadata:
        nb.metadata[_METADATA_DIR] = {}
    if _METADATA_DEPLIST_PATH not in nb.metadata[_METADATA_DIR]:
        nb.metadata[_METADATA_DIR][_METADATA_DEPLIST_PATH] = []

    # Add the packages to the metadata
    dep_container = DepContainer.from_list(
        nb.metadata[_METADATA_DIR][_METADATA_DEPLIST_PATH] + [package]
    )
    nb.metadata[_METADATA_DIR][_METADATA_DEPLIST_PATH] = dep_container.as_list()

    # Save the notebook
    with open(notebook_path, "w") as f:
        nbf.write(nb, f)


@cli.command()
@click.pass_context
def guess(ctx):
    """Guess package dependencies from the notebook code."""
    notebook_path = ctx.obj["notebook"]

    # Load the notebook
    with open(notebook_path) as f:
        nb = nbf.read(f, as_version=4)

    # Read all the cells and find any line with `import` in it:
    imports = set()
    for cell in nb.cells:
        if cell.cell_type == "code":
            for line in cell.source.splitlines():
                if line.startswith("import "):
                    imports.add(line.split()[1])
                elif line.startswith("from "):
                    imports.add(line.split()[1])

    # Save the imports as dependencies
    print("Guessed dependencies:", imports)


@cli.command()
@click.pass_context
def list(ctx):
    """List packages in the notebook metadata."""
    notebook_path = ctx.obj["notebook"]

    # Load the notebook
    with open(notebook_path, "r") as f:
        nb = nbf.read(f, as_version=4)

    # List the dependencies
    dependencies = nb.metadata.get(_METADATA_DIR, {}).get(_METADATA_DEPLIST_PATH, [])
    now = datetime.datetime.now().isoformat()
    click.echo(f"# Dependencies as of {now}")
    for dep in dependencies:
        click.echo(f"{dep}")


@cli.command()
@click.pass_context
@click.argument("package")
def remove(ctx, package):
    """Remove a package from the notebook metadata."""
    notebook_path = ctx.obj["notebook"]

    # Load the notebook
    with open(notebook_path) as f:
        nb = nbf.read(f, as_version=4)

    # Remove the package from the metadata
    dependencies = nb.metadata.get(_METADATA_DIR, {}).get(_METADATA_DEPLIST_PATH, [])
    # TODO: Handle case where version is specified
    dependencies = [dep for dep in dependencies if dep != package]
    nb.metadata[_METADATA_DIR][_METADATA_DEPLIST_PATH] = dependencies

    # Save the notebook
    with open(notebook_path, "w") as f:
        nbf.write(nb, f)


@cli.command()
@click.pass_context
def clear(ctx):
    """Clear all packages from the notebook metadata."""
    notebook_path = ctx.obj["notebook"]

    # Load the notebook
    with open(notebook_path, "r") as f:
        nb = nbf.read(f, as_version=4)

    # Clear the dependencies
    nb.metadata[_METADATA_DIR] = {}

    # Save the notebook
    with open(notebook_path, "w") as f:
        nbf.write(nb, f)


@cli.command()
@click.pass_context
def install(ctx):
    """Install packages listed in the notebook metadata."""
    notebook_path = ctx.obj["notebook"]
    venv_path = ctx.obj["venv_path"]
    venv_pip = pathlib.Path(venv_path) / "bin" / "pip"

    # Load the notebook
    with open(notebook_path, "r") as f:
        nb = nbf.read(f, as_version=4)

    # Get the dependencies
    dependencies = nb.metadata.get(_METADATA_DIR, {}).get(_METADATA_DEPLIST_PATH, [])

    # Install the dependencies using pip
    for dep in dependencies:
        click.echo(f"Installing {dep}...")
        subprocess.run([str(venv_pip), "install", dep], check=True)


@cli.command()
@click.pass_context
def run(ctx):
    """Run the notebook."""
    notebook_path = ctx.obj["notebook"]
    venv_path = ctx.obj["venv_path"]
    jupyter_path = pathlib.Path(venv_path) / "bin" / "jupyter"

    # Run the notebook using jupyter
    click.echo(f"Running notebook {notebook_path}...")
    subprocess.run(
        [
            str(jupyter_path),
            "notebook",
            str(notebook_path),
        ],
        check=True,
    )
