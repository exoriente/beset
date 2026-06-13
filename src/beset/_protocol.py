from typing import Protocol, TypeVar

S = TypeVar("S")


class Sortable(Protocol):
    def __lt__(self: S, other: S, /) -> bool: ...
