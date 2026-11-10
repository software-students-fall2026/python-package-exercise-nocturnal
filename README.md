![CI](https://github.com/software-students-fall2026/python-package-exercise-nocturnal/actions/workflows/ci.yml/badge.svg?branch=main)
![CD](https://github.com/software-students-fall2026/python-package-exercise-nocturnal/actions/workflows/cd.yml/badge.svg?branch=main)

# Python Package Exercise

## Setup after cloning

After cloning this repository, run `pipenv install --dev` from the main project directory. This creates the project's virtual environment and installs everything listed in the `Pipfile`:

- `[dev-packages]` - tools needed only while developing the package, such as `pytest`, `coverage`, [build](https://packaging.python.org/en/latest/tutorials/packaging-projects/#generating-distribution-archives). The `--dev` flag installs these too.

Activating the virtual environment with `pipenv shell` does not install anything. If you skip `pipenv install --dev`, commands like `pytest` may silently run a copy installed elsewhere on your computer and fail with a `ModuleNotFoundError`.

## CD
When code is merged into main and CI passes, the CD pipeline sets the version number based on the date, builds the package and checks it with twine, and uploads it to TestPyPI.