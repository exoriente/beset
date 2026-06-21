source_path = src/
tests_path = test/
python_paths = $(source_path) $(tests_path)

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

slotscheck:
	slotscheck $(source_path)

    checks: ruff-check type-checks slotscheck

nice: format checks

tests:
	pytest

tox:
	tox

missing-coverage:
	pytest --cov --cov-report term-missing
