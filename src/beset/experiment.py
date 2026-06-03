from abc import abstractmethod, ABC
from functools import reduce
from itertools import chain
from operator import attrgetter
from typing import Iterable, Any, cast, overload

from beset.infinity import INF
from beset.sortable import Sortable


class Multiinterval[T: Sortable]:
    _intervals: tuple["Monointerval[T]", ...]

    def __init__(self, intervals: Iterable["Monointerval[T]"]) -> None:
        # object.__setattr__(self, "_intervals", tuple(Monointerval._iterable_union(*intervals)))
        object.__setattr__(self, "_intervals", tuple(intervals))

    def __setattr__(self, key: str, value: object) -> None:
        raise AttributeError(f"{self.__class__.__name__} is immutable. Cannot modify '{key}'.")

    @property
    def intervals(self) -> tuple["Monointerval[T]", ...]:
        return self._intervals

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

    def _binary_intersection[U: Sortable](
        self, other: "Multiinterval[U]"
    ) -> "Multiinterval[T | U]":
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
                if v1.stop < v2.stop:  # type:ignore[operator]
                    v1 = next(it1)
                else:
                    v2 = next(it2)
            except StopIteration:
                return Multiinterval(intervals)

    def union[U: Sortable](*others: "Multiinterval[U]") -> "Multiinterval[T | U]":
        return Multiinterval(chain.from_iterable(map(attrgetter("intervals"), others)))

    def intersection[U: Sortable](*others: "Multiinterval[U]") -> "Multiinterval[T | U]":
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
    _start: T
    _stop: T

    def __init__(self, start: T, stop: T) -> None:
        object.__setattr__(self, "_intervals", (self,))
        object.__setattr__(self, "_start", start)
        object.__setattr__(self, "_stop", stop)

    @property
    def start(self) -> T:
        return self._start

    @property
    def stop(self) -> T:
        return self._stop

    @abstractmethod
    def includes_lower_bound(self) -> bool: ...

    @abstractmethod
    def includes_upper_bound(self) -> bool: ...

    def empty(self) -> bool:
        return self.stop < self.start or (
            not self.start < self.stop
            and (not self.includes_lower_bound() or not self.includes_upper_bound())
        )

    def __eq__(self, other: object) -> bool:
        match other:
            case Multiinterval() as multi:
                if self.empty():
                    return multi.empty()

                match other:
                    case Monointerval() as mono:
                        try:
                            return (
                                self.includes_lower_bound() == mono.includes_lower_bound()
                                and self.includes_upper_bound() == mono.includes_upper_bound()
                                and not self.start < mono.start
                                and not mono.start < self.start
                                and not self.stop < mono.stop
                                and not mono.stop < self.stop
                            )
                        except TypeError:
                            return False
                    case Multiinterval():
                        return super().__eq__(other)
            case _:
                return NotImplemented

    def _binary_union[U: Sortable](
        self, other: "Monointerval[U]"
    ) -> tuple["Monointerval[T | U]"] | tuple["Monointerval[T | U]", "Monointerval[T | U]"]:
        """
        Returns a tuple with one or two monointervals in ascending order
        """
        if self.empty():
            return (other,)

        if other.empty():
            return (self,)

        if self.stop < other.start:  # type:ignore[operator]
            return self, other

        if other.stop < self.start:  # type:ignore[operator]
            return other, self

        if self.start < other.stop and other.start < self.stop:  # type:ignore[operator]
            start, include_lower_bound = min(
                (self.start, -self.includes_lower_bound()),
                (other.start, -other.includes_lower_bound()),
            )
            stop, include_upper_bound = max(
                (self.stop, self.includes_upper_bound()), (other.stop, other.includes_upper_bound())
            )
            return (
                new_monointerval(start, stop, bool(include_lower_bound), bool(include_upper_bound)),  # type:ignore[return-value]
            )

        if not self.stop < other.start and not other.start < self.start:  # type:ignore[operator]
            if self.includes_upper_bound() or other.includes_lower_bound():
                return (
                    new_monointerval(
                        self.start,
                        other.stop,
                        self.includes_lower_bound(),
                        other.includes_upper_bound(),
                    ),  # type:ignore[return-value]
                )
            else:
                return self, other

        if other.includes_upper_bound() or self.includes_lower_bound():
            return (
                new_monointerval(
                    other.start,
                    self.stop,
                    other.includes_lower_bound(),
                    self.includes_upper_bound(),
                ),  # type:ignore[return-value]
            )
        else:
            return other, self

    def _iterable_union[U: Sortable](*intervals: "Monointerval[U]") -> Iterable["Monointerval[U]"]:
        ordered = sorted(intervals, key=lambda x: (x.start, -x.includes_lower_bound()))

        last: Monointerval[U] = EMPTY_INTERVAL

        for interval in ordered:
            result = last._binary_union(interval)

            match result:
                case (interval_a,):
                    last = interval_a
                case (interval_a, interval_b):
                    yield interval_a
                    last = interval_b

        if not last.empty():
            yield last

    def _binary_intersection_mono[U: Sortable](
        self, other: "Monointerval[U]"
    ) -> "Monointerval[T | U]":
        start: T | U
        stop: T | U
        start, include_lower_bound = max(  # type:ignore[assignment]
            (self.start, -self.includes_lower_bound()), (other.start, -other.includes_lower_bound())
        )
        stop, include_upper_bound = min(  # type:ignore[assignment]
            (self.stop, self.includes_upper_bound()), (other.stop, other.includes_upper_bound())
        )
        return new_monointerval(start, stop, bool(include_lower_bound), include_upper_bound)

    def _binary_intersection[U: Sortable](self, other: Multiinterval[U]) -> Multiinterval[T | U]:
        match other:
            case Monointerval():
                return self._binary_intersection_mono(cast(Monointerval[U], other))
            case Multiinterval():
                return super()._binary_intersection(other)

    def intersection[U: Sortable](*others: Multiinterval[U]) -> Multiinterval[U]:
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


def new_monointerval[T: Sortable](
    start: T, stop: T, include_lower_bound: bool, include_upper_bound: bool
) -> Monointerval[T]:
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


Closed = ClosedInterval
Open = OpenInterval
ClosedOpen = ClosedOpenInterval
OpenClosed = OpenClosedInterval
Interval = ClosedOpenInterval


EMPTY_INTERVAL = OpenInterval[Any](INF, -INF)

open_multiinterval_1: Multiinterval[int] = OpenInterval[int](0, 1)
open_multiinterval_2: Multiinterval[int] = OpenInterval[bool](False, True)
open_monointerval: OpenInterval[int] = OpenInterval[bool](False, True)
