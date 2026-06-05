from functools import reduce
from itertools import chain, pairwise
from operator import attrgetter
from typing import Iterable, Any, cast, overload

from beset.infinity import INF, InfinityTypes, NegativeInfinity, Infinity
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

    def _binary_intersection[U: Sortable](self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        it1 = iter(self.intervals)
        it2 = iter(other.intervals)

        try:
            v1 = next(it1)
            v2 = next(it2)
        except StopIteration:
            return IntervalSet(())

        intervals: list[Interval[T | U]] = []

        while True:
            intervals.append(v1._binary_intersection_elementary(v2))
            try:
                if v1.stop < v2.stop:  # type:ignore[operator]
                    v1 = next(it1)
                else:
                    v2 = next(it2)
            except StopIteration:
                return IntervalSet(intervals)

    def union[U: Sortable](self, *others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return IntervalSet(chain.from_iterable(map(attrgetter("intervals"), chain((self,), others))))

    def __or__[U: Sortable](self, other: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return self.union(other)

    def intersection[U: Sortable](self, *others: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return reduce(lambda x, y: x._binary_intersection(y), others, self)

    def __and__[U: Sortable](self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return self._binary_intersection(other)

    def _include_infinity(self) -> bool:
        try:
            return not self.intervals[0].includes_lower_bound()
        except IndexError:
            return False

    def _include_negative_infinity(self) -> bool:
        try:
            return not self.intervals[-1].includes_upper_bound()
        except IndexError:
            return False

    def _complement_iterable(self) -> Iterable["Interval[T | InfinityTypes]"]:
        start: T | NegativeInfinity
        stop: T | Infinity
        for a, b in pairwise(chain((None,), self.intervals, (None,))):
            if a is None:
                start = -INF
                start_included = self._include_negative_infinity()
            else:
                start = a.stop
                start_included = not a.includes_upper_bound()

            if b is None:
                stop = INF
                stop_included = self._include_infinity()
            else:
                stop = b.start
                stop_included = not b.includes_lower_bound()

            yield Interval(start, stop, start_included, stop_included)

    def complement(self) -> "IntervalSet[T | InfinityTypes]":
        return IntervalSet(self._complement_iterable())

    def __invert__(self) -> "IntervalSet[T | InfinityTypes]":
        return self.complement()

    def _binary_difference[U: Sortable](self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return self.intersection(other.complement())

    def difference[U: Sortable](self, *others: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return reduce(lambda x, y: x._binary_difference(y), others, self)

    def __sub__[U: Sortable](self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return self.difference(other)

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
    def __call__(cls, *args, **kwargs):  # type:ignore[no-untyped-def]
        if cls is Interval:
            try:
                start, stop, include_lower_bound, include_upper_bound, args, kwargs = _extract_arguments(
                    *args, **kwargs
                )
            except TypeError as e:
                raise TypeError(str(e).replace(_extract_arguments.__name__, cls.__name__)) from None

            if include_lower_bound:
                cls = ClosedInterval if include_upper_bound else ClosedOpenInterval
            else:
                cls = OpenClosedInterval if include_upper_bound else OpenInterval

            return super(_IntervalMeta, cls).__call__(start, stop, *args, **kwargs)  # type:ignore[misc]

        elif cls is ConcreteInterval:
            raise TypeError("'ConcreteInterval' is abstract and cannot be instantiated")

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
        return (
            self.stop < self.start
            or (not self.start < self.stop and (not self.includes_lower_bound() or not self.includes_upper_bound()))
            or not -INF < self.stop
            or not self.start < INF
        )

    def __eq__(self, other: object) -> bool:
        match other:
            case IntervalSet() as interval_set:
                if self.empty():
                    return interval_set.empty()

                match other:
                    case Interval() as interval:
                        try:
                            return (
                                self.includes_lower_bound() == interval.includes_lower_bound()
                                and self.includes_upper_bound() == interval.includes_upper_bound()
                                and not self.start < interval.start
                                and not interval.start < self.start
                                and not self.stop < interval.stop
                                and not interval.stop < self.stop
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
        Returns a tuple with one or two intervals in ascending order
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
                Interval(start, stop, bool(include_lower_bound), bool(include_upper_bound)),  # type:ignore[return-value]
            )

        if not self.stop < other.start and not other.start < self.start:  # type:ignore[operator]
            if self.includes_upper_bound() or other.includes_lower_bound():
                return (
                    Interval(
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
                Interval(
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

    def _binary_intersection_elementary[U: Sortable](self, other: "Interval[U | InfinityTypes]") -> "Interval[T | U]":
        start: T | U
        stop: T | U

        # max eliminates -INF from U unless -INF ∈ T
        start, include_lower_bound = max(  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            (self.start, -self.includes_lower_bound()), (other.start, -other.includes_lower_bound())
        )

        # min eliminates INF from U unless INF ∈ T
        stop, include_upper_bound = min(  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            (self.stop, self.includes_upper_bound()), (other.stop, other.includes_upper_bound())
        )
        return Interval(start, stop, bool(include_lower_bound), include_upper_bound)

    def _binary_intersection[U: Sortable](self, other: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]:  # pyrefly:ignore[bad-override]
        match other:
            case Interval():
                return self._binary_intersection_elementary(cast(Interval[U], other))
            case IntervalSet():
                return super()._binary_intersection(other)

    @overload
    def intersection[U: Sortable](self, *others: "Interval[U | InfinityTypes]") -> "Interval[T | U]": ...  # pyrefly:ignore[bad-override]

    @overload
    def intersection[U: Sortable](self, *others: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]: ...

    def intersection[U: Sortable](self, *others: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]:
        return reduce(lambda x, y: x._binary_intersection(y), others, self)

    @overload
    def __and__[U: Sortable](self, other: "Interval[U | InfinityTypes]") -> "Interval[T | U]": ...  # pyrefly:ignore[bad-override]

    @overload
    def __and__[U: Sortable](self, other: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]: ...

    def __and__[U: Sortable](self, other: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]:
        return self._binary_intersection(other)

    def complement(self) -> "IntervalSet[T | InfinityTypes]":
        return IntervalSet(
            (
                Interval(-INF, self.start, not self.includes_upper_bound(), not self.includes_lower_bound()),
                Interval(self.stop, INF, not self.includes_upper_bound(), not self.includes_lower_bound()),
            )
        )

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


Closed = ClosedInterval
Open = OpenInterval
ClosedOpen = ClosedOpenInterval
OpenClosed = OpenClosedInterval


EMPTY_INTERVAL = OpenInterval[Any](INF, -INF)
