from typing import Protocol, Any


class Sortable(Protocol):
    def __lt__(self, other: Any) -> bool:
        ...
