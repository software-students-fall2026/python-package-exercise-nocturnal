# Python Package Exercise

A little exercise to create a Python package, build it, test it, distribute it, and use it.

## Team repository

Your team works from a single shared GitHub repository.

To create it, exactly one member of the team - decide among yourselves who - clicks the `Fork` button on this repository to make a copy of it in their own GitHub account. That member then gives the rest of the team access to it: in the new repository's `Settings` tab, under `Collaborators and teams`, add each teammate and the course admins by their GitHub usernames. Everyone else clones that one shared repository, rather than making further copies of their own.

Share the web address of the team's repository using the messaging app specified by your instructor, posting it wherever the instructor has directed. That is how the work is submitted.

## Concept

A _package_ is software that has been built, tested, and distributed in a way that makes it easy for other developers to download, install, and configure to add extra functionality to their own programs. Your job is to create a Python package that brings a little bit of joy and levity to the lives of other developers. The package you create should be lighthearted and not "serious" software. However, you will create it following _rigorous_ software engineering practices.

## Inspiration

Some inspirational Python packages, for example:

- [pyjokes](https://pypi.org/project/pyjokes/)
- [pyfiglet](https://github.com/pwaller/pyfiglet)
- [pycowsay](https://pypi.org/project/pycowsay/)
- [emoji](https://pypi.org/project/emoji/)
- [python-lorem](https://pypi.org/project/python-lorem/)
- [horoscope](https://pypi.org/project/horoscope/)
- [freegames](https://pypi.org/project/freegames/)

## Requirements

Create a Python package with at least **four functions that accept arguments** which influence their behavior. The package must be distributed in the [PyPI](https://pypi.org/) repository and installable via [pip](https://pypi.org/project/pip/).

- Use [pipenv](https://packaging.python.org/en/latest/tutorials/managing-dependencies/) to manage the package dependencies and virtual environments with a `Pipfile`.
- Use [pytest](https://docs.pytest.org/en/latest/) to write and run tests to validate that your package code behaves as expected. Create as many assertions and test functions as necessary to thoroughly verify each function's expected behavior - this should be no fewer than three assertions per package function. But there is no magic number - your job is to make sure all possible function scenarios -- valid and invalid alike -- are tested.
- Use [build](https://pypa-build.readthedocs.io/en/stable/index.html) to create the package artifacts.
- Use [twine](https://pypi.org/project/twine/) to upload the package to PyPI.
- Use [GitHub Actions](https://github.com/actions) to build your package and run your tests on two different recent versions of Python with every pull request to the `main`/`master` branch of your GitHub repository.

Create an example program that uses all functions of your package and demonstrates its complete functionality.

## Developer workflow

All team members must have visibly contributed to the code using their own git & GitHub accounts in order to claim that they contributed to the project.

All code changes must be done in feature branches and not directly in the `main`/`master` branch.

To merge code from a feature branch into the `main`/`master` branch, do the following:

1. Create a pull request from the feature branch to the `main`/`master` branch. Because your team's repository is a fork of the instructor's, GitHub will set the `base repository` of the pull request to the instructor's repository - change it back to your own team's repository before creating it, or your teammates will not be able to review or merge your work.
1. Ask a fellow developer to review your code.
1. The reviewer must review the code and run unit tests to verify that the functions behave as expepcted.
1. If the reviewer has any concerns, discuss then and make any changes agreed upon.
1. Merge the pull request into the `main`/`master` branch.
1. Delete the feature branch.
1. Pull the latest changes from the remote `main`/`master` branch to your local `main`/`master` branch.

**Warning**: the longer you let code sit in a feature branch, the more likely your team is to end up in [merge hell](https://en.wikipedia.org/wiki/Merge_hell). . Merge feature branches into `main` often to avoid this fate.

## Documentation

Replace the contents of the [README.md](./README.md) file with a beautifully-formatted Markdown file including a plain-language **description** of your project and **clear instructions**, including exact **code examples**, for:

Replace the contents of the [README.md](./README.md) file with a beautifully-formatted Markdown file including

- a plain-language **description** of your project, including:
- a [badge](https://docs.github.com/en/actions/monitoring-and-troubleshooting-workflows/adding-a-workflow-status-badge) at the top of the `README.md` file showing the result of the latest build/test workflow run.
- a link to your package's page on the PyPI website.
- how a developer who wants to import your project into their own code can do so - include documentation and code examples for all functions in your package and a link to an example Python program that uses each of them.
- how a developer who wants to contribute to your project can set up the virtual environment, install dependencies, and build and test your package for themselves.
- the names of all teammates as links to their GitHub profiles in the `README.md` file.
- instructions for how to configure and run all parts of your project for any developer on any platform - these instructions must work!
- instructions for how to set up any environment variables and import any starter data into the database, as necessary, for the system to operate correctly when run.
- if there are any "secret" configuration files, such as `.env` or similar files, that are not included in the version control repository, examples of these files, such as `env.example`, with dummy data must be included in the repository and exact instructions for how to create the proper configuration files and what their contents should be must be supplied to the course admins by the due date.
