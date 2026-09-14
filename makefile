source_path = src/
tests_path = test/
python_paths = $(source_path) $(tests_path)

all: nice tests nox

ruff-format:
	uv run ruff format

format: ruff-format

ruff-check:
	uv run ruff check --fix

mypy:
	uv run mypy $(python_paths)

ty:
	uv run ty check $(python_paths)

pyright:
	uv run pyright $(python_paths)

pyrefly:
	uv run pyrefly check $(python_paths)

type-checks: mypy ty pyright pyrefly

slotscheck:
	uv run slotscheck $(source_path)

checks: ruff-check type-checks slotscheck

nice: format checks

tests:
	uv run pytest

nox:
	uvx --with nox-uv nox

missing-coverage:
	uv run pytest --cov --cov-report term-missing
