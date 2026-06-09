from typing import TypeVar

T = TypeVar("T", covariant=True)

Bound = tuple[T, bool]
IntervalInternals = tuple[bool, tuple[tuple[T, bool], ...]]
