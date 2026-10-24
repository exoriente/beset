from typing import Generic, Iterable, TypeVar

from beset._interval import Interval, IntervalSet
from beset._protocol import Sortable

T = TypeVar("T", covariant=True, bound=Sortable | None)
V = TypeVar("V")


class NoValue: ...


NO_VALUE = NoValue()

Sinisterity = bool

BoundWithValue = tuple[T, Sinisterity, V]
UltimateBoundWithValue = tuple[int, T, Sinisterity, V]
MapData = tuple[V, tuple[BoundWithValue[T, V], ...]]


class IntervalMap(Generic[T, V]):
    def __init__(self, items: Iterable[tuple[IntervalSet[T], V]]):
        _map_data = self._overlay_items(items)

    @classmethod
    def _overlay_items(cls, items: Iterable[tuple[IntervalSet[T], V]]) -> MapData:
        bounds_with_value = tuple(cls._overlay_items_generator(items))