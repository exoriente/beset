from bisect import bisect_left, bisect_right
from collections.abc import Iterable
from itertools import tee
from operator import itemgetter
from typing import TypeVar, Protocol, Any, Generic

from src.beset.sortable import Sortable

T_co = TypeVar("T_co", bound=Sortable, covariant=True)


class MultiInterval(Generic[T_co]):
    def __init__(self, bounds: Iterable[tuple[T_co, bool]], odd: bool):
        for_bounds, for_inclusive = tee(bounds)
        self.bounds = tuple(map(itemgetter(0), for_bounds))
        self.inclusive = tuple(map(itemgetter(1), for_inclusive))
        self.odd = odd

    def __contains__(self, item: T_co) -> bool:
        i = bisect_right(self.bounds, item)

        return i % 2 == self.odd
