from abc import ABC, abstractmethod
from collections.abc import Iterable
from functools import reduce
from itertools import chain
from operator import attrgetter
from typing import Any, overload

from beset.infinity import INF
from beset.sortable import Sortable


class Multiinterval[T: Sortable]:
    intervals: tuple["Monointerval[T]", ...]

    def __init__(self, intervals: Iterable["Monointerval[T]"]) -> None:
        object.__setattr__(self, "intervals", tuple(Monointerval._iterable_union(*intervals)))

    def __setattr__(self, key: str, value: object) -> None:
        raise AttributeError(f"{self.__class__.__name__} is immutable. Cannot modify '{key}'.")

    def empty(self) -> bool:
        return len(self.intervals) == 0

    def __eq__(self, other: object) -> bool:
        match other:
            case Multiinterval():
                try:
                    return all(a == b for a, b in zip(self.intervals, other.intervals, strict=True))
                except ValueError:
                    return False
            case _:
                return NotImplemented

    def _binary_intersection(self, other: "Multiinterval[T]") -> "Multiinterval[T]":
        it1 = iter(self.intervals)
        it2 = iter(other.intervals)

        try:
            v1 = next(it1)
            v2 = next(it2)
        except StopIteration:
            return Multiinterval(())

        intervals = []

        while True:
            intervals.append(v1._binary_intersection_mono(v2))
            try:
                if v1.stop < v2.stop:
                    v1 = next(it1)
                else:
                    v2 = next(it2)
            except StopIteration:
                return Multiinterval(intervals)

    def union(*others: "Multiinterval[T]") -> "Multiinterval[T]":
        return Multiinterval(chain.from_iterable(map(attrgetter("intervals"), others)))

    def intersection(*others: "Multiinterval[T]") -> "Multiinterval[T]":
        return reduce(Multiinterval._binary_intersection, others)

    def __repr__(self) -> str:
        intervals_str = ", ".join(map(repr, self.intervals))

        if len(self.intervals) == 1:
            extra_comma = ","
        else:
            extra_comma = ""

        return f"{type(self).__name__}(({intervals_str}{extra_comma}))"

    def __str__(self) -> str:
        if self.empty():
            return "<:>"
        return " U ".join(map(str, self.intervals))


class Monointerval[T: Sortable](Multiinterval[T], ABC):
    start: T
    stop: T

    def __init__(self, start: T, stop: T) -> None:
        object.__setattr__(self, "intervals", (self,))
        object.__setattr__(self, "start", start)
        object.__setattr__(self, "stop", stop)

    def empty(self) -> bool:
        return self.stop < self.start or (
            not self.start < self.stop
            and (not self.includes_lower_bound() or not self.includes_upper_bound())
        )

    @abstractmethod
    def includes_lower_bound(self) -> bool: ...

    @abstractmethod
    def includes_upper_bound(self) -> bool: ...

    @classmethod
    def create(
        cls, start: T, stop: T, include_lower_bound: bool, include_upper_bound: bool
    ) -> "Monointerval[T]":
        if include_lower_bound:
            if include_upper_bound:
                return ClosedInterval(start, stop)
            else:
                return ClosedOpenInterval(start, stop)
        else:
            if include_upper_bound:
                return OpenClosedInterval(start, stop)
            else:
                return OpenInterval(start, stop)

    def __eq__(self, other: object) -> bool:
        match other:
            case Multiinterval():
                if self.empty():
                    return other.empty()

                match other:
                    case Monointerval():
                        try:
                            return (
                                self.includes_lower_bound() == other.includes_lower_bound()
                                and self.includes_upper_bound() == other.includes_upper_bound()
                                and not self.start < other.start
                                and not other.start < self.start
                                and not self.stop < other.stop
                                and not other.stop < self.stop
                            )
                        except TypeError:
                            return False
                    case Multiinterval():
                        return super().__eq__(other)
            case _:
                return NotImplemented

    def _binary_union(
        self, other: "Monointerval[T]"
    ) -> tuple["Monointerval[T]"] | tuple["Monointerval[T]", "Monointerval[T]"]:
        """
        Returns a tuple with one or two monointervals in ascending order
        """
        if self.empty():
            return (other,)

        if other.empty():
            return (self,)

        if self.stop < other.start:
            return self, other

        if other.stop < self.start:
            return other, self

        if self.start < other.stop and other.start < self.stop:
            start, include_lower_bound = min(
                (self.start, -self.includes_lower_bound()),
                (other.start, -other.includes_lower_bound()),
            )
            stop, include_upper_bound = max(
                (self.stop, self.includes_upper_bound()), (other.stop, other.includes_upper_bound())
            )
            return (
                Monointerval.create(
                    start, stop, bool(include_lower_bound), bool(include_upper_bound)
                ),
            )

        if not self.stop < other.start and not other.start < self.start:
            if self.includes_upper_bound() or other.includes_lower_bound():
                return (
                    Monointerval.create(
                        self.start,
                        other.stop,
                        self.includes_lower_bound(),
                        other.includes_upper_bound(),
                    ),
                )
            else:
                return self, other

        if other.includes_upper_bound() or self.includes_lower_bound():
            return (
                Monointerval.create(
                    other.start,
                    self.stop,
                    other.includes_lower_bound(),
                    self.includes_upper_bound(),
                ),
            )
        else:
            return other, self

    def _iterable_union(*intervals: "Monointerval[T]") -> Iterable["Monointerval[T]"]:
        ordered = sorted(intervals, key=lambda x: (x.start, -x.includes_lower_bound()))

        last: Monointerval[T] = EMPTY_INTERVAL

        for interval in ordered:
            result = last._binary_union(interval)
            if len(result) == 1:
                (last,) = result
            else:
                confirmed, last = result
                yield confirmed

        if not last.empty():
            yield last

    def _binary_intersection_mono(self, other: "Monointerval[T]") -> "Monointerval[T]":
        start, include_lower_bound = max(
            (self.start, -self.includes_lower_bound()), (other.start, -other.includes_lower_bound())
        )
        stop, include_upper_bound = min(
            (self.stop, self.includes_upper_bound()),
            (other.stop, other.includes_upper_bound()),
        )
        return Monointerval.create(start, stop, bool(include_lower_bound), include_upper_bound)

    def _binary_intersection(self, other: Multiinterval[T]) -> Multiinterval[T]:
        match other:
            case Monointerval():
                return self._binary_intersection_mono(other)
            case Multiinterval():
                return super()._binary_intersection(other)

    @overload
    def intersection(*others: "Monointerval[T]") -> "Monointerval[T]": ...

    @overload
    def intersection(*others: Multiinterval[T]) -> Multiinterval[T]: ...

    def intersection(*others: Multiinterval[T]) -> Multiinterval[T]:
        return reduce(lambda x, y: x._binary_intersection(y), others)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"

    def __str__(self) -> str:
        open_bracket = "[" if self.includes_lower_bound() else "<"
        close_bracket = "]" if self.includes_upper_bound() else ">"

        if self.empty():
            return f"{open_bracket}:{close_bracket}"
        else:
            return f"{open_bracket}{self.start!s} : {self.stop!s}{close_bracket}"


class ClosedInterval[T: Sortable](Monointerval[T]):
    def includes_lower_bound(self) -> bool:
        return True

    def includes_upper_bound(self) -> bool:
        return True


class OpenInterval[T: Sortable](Monointerval[T]):
    def includes_lower_bound(self) -> bool:
        return False

    def includes_upper_bound(self) -> bool:
        return False


class ClosedOpenInterval[T: Sortable](Monointerval[T]):
    def includes_lower_bound(self) -> bool:
        return True

    def includes_upper_bound(self) -> bool:
        return False


class OpenClosedInterval[T: Sortable](Monointerval[T]):
    def includes_lower_bound(self) -> bool:
        return False

    def includes_upper_bound(self) -> bool:
        return True


Closed = ClosedInterval
Open = OpenInterval
ClosedOpen = ClosedOpenInterval
OpenClosed = OpenClosedInterval
Interval = ClosedOpenInterval

EMPTY_INTERVAL = OpenInterval[Any](INF, -INF)
