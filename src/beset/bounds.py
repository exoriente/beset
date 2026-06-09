from collections.abc import Iterable, Iterator, Sequence
from heapq import heappop, heappush
from itertools import batched, chain
from typing import cast

from beset.sortable import Sortable


class Interval[T: Sortable | None]:
    def __init__(self, intervals: Iterable["MonoInterval[T]"]):
        self._odd, self._bounds = Interval._union_bounds(intervals)

    def __len__(self) -> int:
        return len(self._bounds) - 1 + self._odd

    def intervals(self) -> Sequence["MonoInterval[T]"]:
        bounds = chain((None,) * self._odd, self._bounds, (None,) * ((len(self._bounds) + self._odd) % 2))
        return tuple(

            for index, ((start, start_left), (stop, stop_left)) in
            enumerate(batched(self._bounds, 2))
        )

    @staticmethod
    def _iterate_bounds[U: Sortable](bounds: Iterable[Iterable[tuple[U, bool]]]) -> Iterable[tuple[U, bool, int]]:
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
    def _generate_union_bounds[U: Sortable](active: list[bool], indexed_bounds: Iterable[tuple[U, bool, int]]) -> Iterable[tuple[U, bool]]:
        total = sum(active)

        for value, left, index in indexed_bounds:
            if active[index]:
                total -= 1
                active[index] = False
                if total == 0:
                    yield value, left
            else:
                if total == 0:
                    yield value, left
                total += 1
                active[index] = True

    @staticmethod
    def _deduplicate_bounds[U](bounds: Iterable[U]) -> Iterable[U]:
        last = None

        for bound in bounds:
            if bound == last:
                last = None
            else:
                if last is not None:
                    yield last
                last = bound

        if last is not None:
            yield last


    @staticmethod
    def _union_bounds[U: Sortable](intervals: "Iterable[MonoInterval[U]]"
    ) -> tuple[bool, tuple[tuple[U, bool], ...]]:
        intervals = list(intervals)
        active = [i._odd for i in intervals]
        odd = any(active)
        streams = Interval._iterate_bounds(i._bounds for i in intervals)

        new_bounds = tuple(Interval._deduplicate_bounds(Interval._generate_union_bounds(active, streams)))

        return odd, new_bounds




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
        if self._odd or not self._bounds:
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
z = MonoInterval(7, 10, True, False)

print(Interval((x, y, z)))
