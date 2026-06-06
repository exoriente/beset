python_paths = src/ test/

all: nice tests tox

ruff-format:
	ruff format

format: ruff-format

ruff-check:
	ruff check --fix

mypy:
	mypy $(python_paths)

ty:
	ty check $(python_paths)

pyright:
	pyright $(python_paths)

pyrefly:
	pyrefly check $(python_paths)

type-checks: mypy ty pyright pyrefly

checks: ruff-check type-checks

nice: format checks

tests:
	pytest

tox:
	tox

missing-coverage:
	pytest --cov --cov-report term-missing
