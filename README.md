# gistnb

> [!WARNING]
> This is currently a work in progress and may undergo breaking changes.

When sharing a Jupyter notebook, there are a few common ways of sharing dependencies:

| How dependencies are listed        | Advantages                                              | Disadvantages                                                       |
| ---------------------------------- | ------------------------------------------------------- | ------------------------------------------------------------------- |
| No dependencies listed             | Simple; no extra files needed                           | Users may struggle to identify and install required packages        |
| Accompanying requirements.txt file | Easy to create and maintain; widely used                | Requires users to install dependencies manually; no version pinning |
| Using conda environment file       | Easy to create and maintain; allows for version pinning | Burdensome; may not be as familiar to some users                    |
| "pip install" cell magic           | Users can install dependencies directly in notebook     | Requires arbitrary code execution                                   |

`gistnb` is a command line tool that embeds dependencies in the metadata of a Jupyter notebook. Behind the scenes, dependencies are then managed with `uv` and kept in a virtual environment. This allows users to run the notebook without needing to install dependencies manually.

## Usage

### Guess the dependencies of a notebook

```bash
$ gistnb notebook.ipynb guess
Installed packages: {numpy, networkx}
```

### Add a new dependency to a notebook

```bash
gistnb notebook.ipynb add <package>
```

### Remove a dependency from a notebook

```bash
gistnb notebook.ipynb remove <package>
```

### List dependencies in a notebook

```bash
gistnb notebook.ipynb list
```

### Install dependencies for a notebook, creating a virtual environment if necessary

```bash
gistnb notebook.ipynb install
```

### Run a notebook with its dependencies

```bash
gistnb notebook.ipynb run
```
