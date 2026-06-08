from collections.abc import Iterable, Iterator
from heapq import heappop, heappush
from typing import cast

from beset.sortable import Sortable


class Interval[T: Sortable | None]:
    def __init__(self, intervals: Iterable["MonoInterval[T]"]):
        self._odd: bool
        self._bounds: tuple[tuple[T, bool], ...]

    @staticmethod
    def _iterate_bounds[U: Sortable](bounds: Iterable[Iterable[tuple[U, bool]]]) -> Iterator[tuple[U, bool, int]]:
        iterators = list(map(iter, bounds))

        heap: list[tuple[U, bool, int]] = []

        for i, it in enumerate(iterators):
            try:
                heappush(heap, next(it) + (i,))
            except StopIteration:
                pass

        while heap:
            value, left, index = heappop(heap)
            yield value, left, index
            try:
                heappush(heap, next(iterators[index]) + (index,))
            except StopIteration:
                pass

    @staticmethod
    def _bounds_union[U: Sortable](
        *bounds: tuple[bool, Iterable[tuple[U, bool]]],
    ) -> tuple[bool, tuple[tuple[U, bool], ...]]:
        active = [b[0] for b in bounds]
        odd = any(active)
        total = sum(active)

        new_bounds = []

        for value, left, index in Interval._iterate_bounds(b[1] for b in bounds):
            if active[index]:
                total -= 1
                active[index] = False
                if total == 0:
                    if new_bounds and new_bounds[-1] == (value, left):
                        del new_bounds[-1]
                    else:
                        new_bounds.append((value, left))
            else:
                if total == 0:
                    if new_bounds and new_bounds[-1] == (value, left):
                        del new_bounds[-1]
                    else:
                        new_bounds.append((value, left))
                total += 1
                active[index] = True

        return odd, tuple(new_bounds)


class MonoInterval[T: Sortable | None](Interval[T]):
    def __init__(self, start: T, stop: T, left_closed: bool, right_closed: bool):
        lower_bound: tuple[tuple[T, bool], ...]
        upper_bound: tuple[tuple[T, bool], ...]

        if start is None:
            self._odd = True
            lower_bound = ()
        else:
            self._odd = False
            lower_bound = ((start, not left_closed),)

        upper_bound = () if stop is None else ((stop, right_closed),)

        self._bounds = lower_bound + upper_bound

    @property
    def start(self) -> T:
        if self._odd:
            return cast(T, None)
        else:
            return self._bounds[0][0]

    @property
    def stop(self) -> T:
        try:
            return self._bounds[1 - self._odd][0]
        except IndexError:
            return cast(T, None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"


print(repr(MonoInterval(0, 5, True, False)))
print(repr(MonoInterval(None, 5, True, False)))
print(repr(MonoInterval(5, None, True, False)))

x = MonoInterval(2, 5, True, False)
y = MonoInterval(5, 8, True, False)
z = MonoInterval(4, 10, True, False)

print(Interval._bounds_union((x._odd, x._bounds), (y._odd, y._bounds), (z._odd, z._bounds)))
