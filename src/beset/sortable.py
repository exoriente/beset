from typing import Protocol, Self


class Sortable(Protocol):
    def __lt__(self, other: Self, /) -> bool: ...
