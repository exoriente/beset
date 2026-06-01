from abc import ABC, abstractmethod
from collections.abc import Iterable
from typing import Any

from beset.sortable import Sortable


class Multiinterval[T: Sortable]:
    intervals: tuple["Monointerval[T]", ...]

    def __init__(self, intervals: Iterable["Monointerval[T]"]) -> None:
        object.__setattr__(self, "intervals", intervals)

    def __setattr__(self, key, value):
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


class Monointerval[T: Sortable](Multiinterval[T], ABC):
    start: T
    stop: T

    def __init__(self, start: T, stop: T) -> None:
        super().__init__((self,))
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

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"


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


def monointerval_union[T: Sortable](
    a: Monointerval[T], b: Monointerval[T]
) -> tuple[Monointerval[T]] | tuple[Monointerval[T], Monointerval[T]]:
    """
    Returns a single monointerval or two separate ones in ascending order
    """
    if a.empty():
        return (b,)

    if b.empty():
        return (a,)

    if a.stop < b.start:
        return a, b

    if b.stop < a.start:
        return b, a

    if a.start < b.stop and b.start < a.stop:
        start, include_lower_bound = min(
            (a.start, -a.includes_lower_bound()), (b.start, -b.includes_lower_bound())
        )
        stop, include_upper_bound = max(
            (a.stop, a.includes_upper_bound()), (b.stop, b.includes_upper_bound())
        )
        return (
            Monointerval.create(start, stop, bool(include_lower_bound), bool(include_upper_bound)),
        )

    if not a.stop < b.start and not b.start < a.start:
        if a.includes_upper_bound() or b.includes_lower_bound():
            return (
                Monointerval.create(
                    a.start, b.stop, a.includes_lower_bound(), b.includes_upper_bound()
                ),
            )
        else:
            return a, b

    if b.includes_upper_bound() or a.includes_lower_bound():
        return (
            Monointerval.create(
                b.start, a.stop, b.includes_lower_bound(), a.includes_upper_bound()
            ),
        )
    else:
        return b, a


def monointervals_union[T: Sortable](intervals: Iterable[Monointerval[T]]) -> Iterable[Monointerval[T]]:
    ordered = sorted(intervals, key=lambda x: (x.start, -x.includes_lower_bound()))

    last = OpenInterval(0, 0)  # empty

    for interval in ordered:
        result = monointerval_union(last, interval)
        if len(result) == 1:
            (last,) = result
        else:
            confirmed, last = result
            yield confirmed

    yield last


Closed = ClosedInterval
Open = OpenInterval
ClosedOpen = ClosedOpenInterval
OpenClosed = OpenClosedInterval
Interval = ClosedOpenInterval

EMPTY_INTERVAL = Multiinterval[Any](())
