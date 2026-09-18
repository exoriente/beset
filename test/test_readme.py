import doctest
from pathlib import Path


def _reveal_type(value: object) -> None:
    pass


def _python_examples(markdown: str) -> str:
    in_python_block = False
    examples: list[str] = []

    for line in markdown.splitlines():
        if line == "```python":
            in_python_block = True
            examples.append("")
        elif line == "```" and in_python_block:
            in_python_block = False
            examples.append("")
        else:
            examples.append(line if in_python_block else "")

    return "\n".join(examples)


def test_readme_examples() -> None:
    readme = Path(__file__).parents[1] / "readme.md"
    examples = _python_examples(readme.read_text(encoding="utf-8"))
    test = doctest.DocTestParser().get_doctest(
        examples,
        {"reveal_type": _reveal_type},
        "readme.md",
        str(readme),
        0,
    )
    runner = doctest.DocTestRunner()
    runner.run(test)
    result = runner.summarize()

    assert result.failed == 0
