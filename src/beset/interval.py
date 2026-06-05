from functools import reduce
from itertools import chain
from operator import attrgetter
from typing import Iterable, Any, cast, overload

from beset.infinity import INF, InfinityTypes
from beset.sortable import Sortable


class IntervalSet[T: Sortable]:
    _intervals: tuple["Interval[T]", ...]

    def __init__(self, intervals: Iterable["Interval[T]"]) -> None:
        object.__setattr__(self, "_intervals", tuple(Interval._iterable_union(*intervals)))

    def __setattr__(self, key: str, value: object) -> None:
        raise AttributeError(f"{self.__class__.__name__} is immutable. Cannot modify '{key}'.")

    @property
    def intervals(self) -> tuple["Interval[T]", ...]:
        return self._intervals

    def empty(self) -> bool:
        return len(self.intervals) == 0

    def __eq__(self, other: object) -> bool:
        match other:
            case IntervalSet():
                try:
                    return all(a == b for a, b in zip(self.intervals, other.intervals, strict=True))
                except ValueError:
                    return False
            case _:
                return NotImplemented

    def _binary_intersection[U: Sortable](self, other: "IntervalSet[U]") -> "IntervalSet[T | U]":
        it1 = iter(self.intervals)
        it2 = iter(other.intervals)

        try:
            v1 = next(it1)
            v2 = next(it2)
        except StopIteration:
            return IntervalSet(())

        intervals = []

        while True:
            intervals.append(v1._binary_intersection_mono(v2))
            try:
                if v1.stop < v2.stop:  # type:ignore[operator]
                    v1 = next(it1)
                else:
                    v2 = next(it2)
            except StopIteration:
                return IntervalSet(intervals)

    def union[U: Sortable](*others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return IntervalSet(chain.from_iterable(map(attrgetter("intervals"), others)))

    def intersection[U: Sortable](*others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return reduce(IntervalSet._binary_intersection, others)

    def finite(self) -> bool:
        return len(self.intervals) == 0 or (self.intervals[0].start != -INF and self.intervals[-1].stop != INF)

    def infinite(self) -> bool:
        return len(self.intervals) > 0 and (self.intervals[0].start == -INF or self.intervals[-1].stop == INF)

    def bounded[U: Sortable](self: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[U]":
        if self.infinite():
            raise TypeError("Bounded cannot be called on infinite interval")

        return cast(IntervalSet[U], self)

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


def _extract_arguments(
    start: object,
    stop: object,
    include_lower_bound: object,
    include_upper_bound: object,
    *args: object,
    **kwargs: object,
) -> tuple[object, object, object, object, tuple[object, ...], dict[str, object]]:
    return start, stop, include_lower_bound, include_upper_bound, args, kwargs


class _IntervalMeta(type):
    def __call__(cls: "_IntervalMeta", *args: object, **kwargs: object) -> Any:
        if cls is Interval:
            start, stop, include_lower_bound, include_upper_bound, args, kwargs = _extract_arguments(*args, **kwargs)

            if include_lower_bound:
                cls = ClosedInterval if include_upper_bound else ClosedOpenInterval
            else:
                cls = OpenClosedInterval if include_upper_bound else OpenInterval

            return super(_IntervalMeta, cls).__call__(start, stop, *args, **kwargs)  # type:ignore[misc]

        else:
            return super(_IntervalMeta, cls).__call__(*args, **kwargs)


class Interval[T: Sortable](IntervalSet[T], metaclass=_IntervalMeta):
    _start: T
    _stop: T

    def __init__(self, start: T, stop: T, include_lower_bound: bool, include_upper_bound: bool) -> None:
        # never actually called
        raise NotImplementedError

    @property
    def start(self) -> T:
        return self._start

    @property
    def stop(self) -> T:
        return self._stop

    def includes_lower_bound(self) -> bool:
        raise NotImplementedError

    def includes_upper_bound(self) -> bool:
        raise NotImplementedError

    def empty(self) -> bool:
        return self.stop < self.start or (
            not self.start < self.stop and (not self.includes_lower_bound() or not self.includes_upper_bound())
        )

    def __eq__(self, other: object) -> bool:
        match other:
            case IntervalSet() as multi:
                if self.empty():
                    return multi.empty()

                match other:
                    case Interval() as mono:
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
                    case IntervalSet():
                        return super().__eq__(other)
            case _:
                return NotImplemented

    def _binary_union[U: Sortable](
        self, other: "Interval[U]"
    ) -> tuple["Interval[T | U]"] | tuple["Interval[T | U]", "Interval[T | U]"]:
        """
        Returns a tuple with one or two Intervals in ascending order
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
                new_interval(start, stop, bool(include_lower_bound), bool(include_upper_bound)),  # type:ignore[return-value]
            )

        if not self.stop < other.start and not other.start < self.start:  # type:ignore[operator]
            if self.includes_upper_bound() or other.includes_lower_bound():
                return (
                    new_interval(
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
                new_interval(
                    other.start,
                    self.stop,
                    other.includes_lower_bound(),
                    self.includes_upper_bound(),
                ),  # type:ignore[return-value]
            )
        else:
            return other, self

    def _iterable_union[U: Sortable](*intervals: "Interval[U]") -> Iterable["Interval[U]"]:
        ordered = iter(sorted(intervals, key=lambda x: (x.start, -x.includes_lower_bound())))

        try:
            last = next(ordered)
        except StopIteration:
            return

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

    def _binary_intersection_mono[U: Sortable](self, other: "Interval[U]") -> "Interval[T | U]":
        start: T | U
        stop: T | U
        start, include_lower_bound = max(  # type:ignore[assignment]
            (self.start, -self.includes_lower_bound()), (other.start, -other.includes_lower_bound())
        )
        stop, include_upper_bound = min(  # type:ignore[assignment]
            (self.stop, self.includes_upper_bound()), (other.stop, other.includes_upper_bound())
        )
        return new_interval(start, stop, bool(include_lower_bound), include_upper_bound)

    def _binary_intersection[U: Sortable](self, other: IntervalSet[U]) -> IntervalSet[T | U]:
        match other:
            case Interval():
                return self._binary_intersection_mono(cast(Interval[U], other))
            case IntervalSet():
                return super()._binary_intersection(other)

    @overload
    def intersection[U: Sortable](*others: "Interval[U]") -> "Interval[U]": ...

    @overload
    def intersection[U: Sortable](*others: IntervalSet[U]) -> IntervalSet[U]: ...

    def intersection[U: Sortable](*others: IntervalSet[U]) -> IntervalSet[U]:
        return reduce(lambda x, y: x._binary_intersection(y), others)

    @overload
    def __and__[U: Sortable](self, other: "Interval[U]") -> "Interval[U]": ...

    @overload
    def __and__[U: Sortable](self, other: IntervalSet[U]) -> IntervalSet[U]: ...

    def __and__[U: Sortable](self, other: IntervalSet[U]) -> IntervalSet[T | U]:
        return self._binary_intersection(other)

    def finite(self) -> bool:
        return self.start != -INF and self.stop != INF

    def infinite(self) -> bool:
        return self.start == -INF or self.stop == INF

    def bounded[U: Sortable](self: "Interval[U | InfinityTypes]") -> "Interval[U]":
        if self.infinite():
            raise TypeError("Bounded cannot be called on infinite interval")

        return cast(Interval[U], self)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"

    def __str__(self) -> str:
        open_bracket = "[" if self.includes_lower_bound() else "<"
        close_bracket = "]" if self.includes_upper_bound() else ">"

        if self.empty():
            return f"{open_bracket}:{close_bracket}"
        else:
            return f"{open_bracket}{self.start!s} : {self.stop!s}{close_bracket}"


class ConcreteInterval[T: Sortable](Interval[T]):
    def __init__(self, start: T, stop: T) -> None:
        object.__setattr__(self, "_intervals", (self,))
        object.__setattr__(self, "_start", start)
        object.__setattr__(self, "_stop", stop)


class ClosedInterval[T: Sortable](ConcreteInterval[T]):
    def includes_lower_bound(self) -> bool:
        return True

    def includes_upper_bound(self) -> bool:
        return True


class OpenInterval[T: Sortable](ConcreteInterval[T]):
    def includes_lower_bound(self) -> bool:
        return False

    def includes_upper_bound(self) -> bool:
        return False


class ClosedOpenInterval[T: Sortable](ConcreteInterval[T]):
    def includes_lower_bound(self) -> bool:
        return True

    def includes_upper_bound(self) -> bool:
        return False


class OpenClosedInterval[T: Sortable](ConcreteInterval[T]):
    def includes_lower_bound(self) -> bool:
        return False

    def includes_upper_bound(self) -> bool:
        return True


def new_interval[T: Sortable](start: T, stop: T, include_lower_bound: bool, include_upper_bound: bool) -> Interval[T]:
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


EMPTY_INTERVAL = OpenInterval[Any](INF, -INF)


print(Open(1, 2))
print(Interval(1, 2, False, False))
print(Interval(1, 2, True, True))
