from nox import Session, main, options
from nox_uv import session as uv_session

options.default_venv_backend = "uv"

python_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
python_source_dirs = ["src"]
python_test_dirs = ["test"]
python_dirs = python_source_dirs + python_test_dirs


@uv_session(python=python_versions, uv_groups=["test"])
def test(s: Session) -> None:
    s.run("python", "-m", "pytest")


@uv_session(python=python_versions, uv_groups=["test", "type-check"])
def type_check(s: Session) -> None:
    s.run("mypy", *python_dirs)
    s.run("ty", "check", *python_dirs)
    s.run("pyright", *python_dirs)
    s.run("pyrefly", "check", *python_dirs)


@uv_session(python=python_versions, uv_only_groups=["lint"])
def lint(s: Session) -> None:
    s.run("ruff", "check", *python_dirs)
    s.run("ruff", "format", "--check", *python_dirs)


if __name__ == "__main__":
    main()
