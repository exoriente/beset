python_paths = src/ test/

all: nice tests

ruff-format:
	ruff format

format: ruff-format

ruff-check:
	ruff check --fix

mypy:
	mypy $(python_paths)

ty:
	ty check $(python_paths)

checks: ruff-check mypy ty

nice: format checks

tests:
	pytest
