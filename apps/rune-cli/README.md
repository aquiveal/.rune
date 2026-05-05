# Rune CLI

Rune is a Git-like command-line tool designed to manage LLM coding agent context, rules, and skills.

## Installation

Rune is managed using PDM, a modern Python package and dependency manager.

### Prerequisites
1. Python 3.14 or higher.
2. PDM (Python Dependency Manager). Install it using pip:
   ```sh
   pip install pdm
   ```

### Installing the CLI

You can install Rune CLI globally in your system or use it within a virtual environment.

#### Option 1: Global Installation via pipx or uv (Recommended for WSL/Windows)
To install Rune globally on your system so you can use the `rune` command anywhere:
```sh
# Install globally using pipx from git
pipx install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"

# Or using uv from git
uv tool install "git+https://github.com/aquiveal/rune.git#subdirectory=apps/rune-cli"
```

You can also install it from a local clone:
```sh
# Navigate to the rune-cli directory
cd apps/rune-cli

# Install globally using pipx
pipx install .

# Or using uv
uv tool install .
```

Make sure your Python global scripts directory is in your `PATH` (typically `~/.local/bin` on WSL/Linux or `%APPDATA%\Python\Scripts` on Windows).

#### Option 2: Editable Installation (Development)
If you want to contribute to Rune or run it locally:
```sh
cd apps/rune-cli
pdm install
```
You can then run commands using:
```sh
pdm run rune --help
```

