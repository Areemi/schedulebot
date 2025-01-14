# Development guide

This is guide how to prepare development environment and use main tools

## Table of contents

- [Table of contents](#table-of-contents)
- [Preparations](#preparations)
- [Initialize your code](#initialize-your-code)
  - [Just created project?](#just-created-project)
  - [Cloned existing project](#cloned-existing-project)
- [Optional setup steps](#optional-setup-steps)
- [Some known issues](#some-known-issues)

## Preparations

1. Install make
    - Windows:

        Install [chocolatey](https://chocolatey.org/install) and install `make` with command:

    ```powershell
    choco install make
    ```

    - Linux:

    ```bash
    sudo apt-get install build-essential
    ```

    

1. Install python 3.8
    - Windows

        Install with [official executable](https://www.python.org/downloads/)

    - Linux

    ```bash
    sudo apt install python3.8-dev
    ```

1. Install poetry

   - Windows

        Use [official instructions](https://python-poetry.org/docs/#windows-powershell-install-instructions) or use `powershell` command:

    ```powershell
    (Invoke-WebRequest -Uri https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py -UseBasicParsing).Content | python -
    ```

   - Linux

    ```bash
    make poetry-download
    ```

1.  Attention

    For the correct work of the programme it is necessary to write and in the .env file
    - DB_DPATH="*path to the folder with the database*"
    - bot_token="*token of your bot*"


[Table of contents](#table-of-contents)

## Initialize your code

### Just created project?

0. Create repository on your favourite server (Bitbucket, Github or other) and obtain "Version control system URL" like this one:

```url
https://github.com/KaiL4eK/pyproject-cookiecutter.git
```

1. Initialize `git` inside your repo:

```bash
cd schedulebot && git init
```

2. Initialize poetry and install `pre-commit` hooks:

```bash
make install
```

3. Upload initial code to GitHub:

```bash
git add .
git commit -m ":tada: Initial commit"
git branch -M develop
git remote add origin <Version control system URL>
git push -u origin develop
```

[Table of contents](#table-of-contents)

### Cloned existing project

1. Initialize poetry and install `pre-commit` hooks:

```bash
make install
```

[Table of contents](#table-of-contents)

## Optional setup steps

1. Install VSCode Extensions
   - [EditorConfig for VS Code](https://marketplace.visualstudio.com/items?itemName=EditorConfig.EditorConfig)
      Open control panel (Ctrl+P) and enter `ext install EditorConfig.EditorConfig`



[Table of contents](#table-of-contents)

## Some known issues

- If you have issues with python version like:

    ```bash
    The currently activated Python version 3.9.7 is not supported by the project (~3.8.0)
    ...
    NoCompatiblePythonVersionFound
    ...
    ```

    Check version of your `python3` binary and make sure you have python3.8 installed.

[Table of contents](#table-of-contents)
