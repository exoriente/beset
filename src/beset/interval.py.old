from bisect import bisect_right
from functools import reduce
from itertools import chain, pairwise
from operator import attrgetter
from typing import Any, Generic, Iterable, TypeVar, cast, overload

from beset.infinity import INF, Infinity, InfinityTypes, NegativeInfinity
from beset.sortable import Sortable


def _eq(a: object, b: object) -> bool:
    return not a < b and not b < a  # type:ignore[ty:unsupported-operator,unused-ignore,operator]


def _le(a: object, b: object) -> bool:
    return a < b or not b < a  # type:ignore[ty:unsupported-operator,unused-ignore,operator]


T = TypeVar("T", covariant=True, bound=Sortable)
U = TypeVar("U", covariant=True, bound=Sortable)


class IntervalSet(Generic[T]):
    __slots__ = ("_intervals",)

    def __init__(self, intervals: Iterable["Interval[T]"] = ()) -> None:
        self._intervals: tuple["Interval[T]", ...] = tuple(Interval._iterable_union(*intervals))

    @property
    def intervals(self) -> tuple["Interval[T]", ...]:
        return self._intervals

    def empty(self) -> bool:
        return len(self.intervals) == 0

    def __bool__(self) -> bool:
        return not self.empty()

    def __eq__(self, other: object, /) -> bool:
        match other:
            case IntervalSet():
                try:
                    return all(a == b for a, b in zip(self.intervals, other.intervals, strict=True))
                except ValueError:
                    return False
            case _:
                return NotImplemented

    def __hash__(self) -> int:
        return hash((IntervalSet, *filter(None, map(Interval._hash_data, self.intervals))))

    def __contains__(self, item: object, /) -> bool:
        try:
            index = bisect_right(self.intervals, item, key=lambda x: x.stop)  # type:ignore[ty:no-matching-overload,unused-ignore,call-overload]
        except TypeError:
            return False

        if self.intervals and index > 0 and item in self.intervals[index - 1]:
            return True

        if len(self.intervals) > index and item in self.intervals[index]:
            return True

        return False

    def _binary_intersection(self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
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

    def union(self, *others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return IntervalSet(chain.from_iterable(map(attrgetter("intervals"), chain((self,), others))))

    def __or__(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        return self.union(other)

    def intersection(self, *others: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return reduce(lambda x, y: x._binary_intersection(y), others, self)

    def __and__(self, other: "IntervalSet[U | InfinityTypes]", /) -> "IntervalSet[T | U]":
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

    def _binary_difference(self, other: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return self.intersection(other.complement())

    def difference(self, *others: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[T | U]":
        return reduce(lambda x, y: x._binary_difference(y), others, self)

    def __sub__(self, other: "IntervalSet[U | InfinityTypes]", /) -> "IntervalSet[T | U]":
        return self.difference(other)

    def isdisjoint(self, other: "IntervalSet[U]", /) -> bool:
        return (self & other).empty()

    def issubset(self, other: "IntervalSet[U]", /) -> bool:
        return (self - other).empty()

    def __le__(self, other: "IntervalSet[U]", /) -> bool:
        return self.issubset(other)

    def __lt__(self, other: "IntervalSet[U]", /) -> bool:
        return self.issubset(other) and self != other

    def issuperset(self, other: "IntervalSet[U]", /) -> bool:
        return (other - self).empty()

    def __ge__(self, other: "IntervalSet[U]", /) -> bool:
        return self.issuperset(other)

    def __gt__(self, other: "IntervalSet[U]", /) -> bool:
        return self.issuperset(other) and self != other

    def symmetric_difference(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        return (self | other) - (self & other)  # pyrefly:ignore[bad-return]

    def __xor__(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        return self.symmetric_difference(other)

    def isbounded(self) -> bool:
        return len(self.intervals) == 0 or (self.intervals[0].start != -INF and self.intervals[-1].stop != INF)

    def isunbounded(self) -> bool:
        return len(self.intervals) > 0 and (self.intervals[0].start == -INF or self.intervals[-1].stop == INF)

    def bounded(self: "IntervalSet[U | InfinityTypes]") -> "IntervalSet[U]":
        if self.isunbounded():
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
        return " | ".join(map(str, self.intervals))


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
                cls = Closed if include_upper_bound else ClosedOpen
            else:
                cls = OpenClosed if include_upper_bound else Open

            return super(_IntervalMeta, cls).__call__(start, stop, *args, **kwargs)  # type:ignore[misc]

        elif cls is ConcreteInterval:
            raise TypeError("'ConcreteInterval' is abstract and cannot be instantiated")

        else:
            return super(_IntervalMeta, cls).__call__(*args, **kwargs)


class Interval(IntervalSet[T], Generic[T], metaclass=_IntervalMeta):
    __slots__ = "_start", "_stop"
    _start: T
    _stop: T

    def __init__(self, start: T, stop: T, include_lower_bound: bool, include_upper_bound: bool) -> None:
        """
        Interval is an abstract class representing a continuous interval and does not consist
        of disjoint subintervals. Being abstract, it does not return objects of type Interval,
        but instead of one of its four subclasses (OpenInterval, ClosedInterval,
        OpenClosedInterval, ClosedOpenInterval) depending on the values of the
        include_lower_bound and include_upper_bound arguments.

        :param start: the lower bound
        :param stop: the upper bound
        :param include_lower_bound: true if the interval is closed on the left, false if open
        :param include_upper_bound: true if the interval is closed on the right, false if open
        """

        # Implementation is effectively located in the metaclass
        raise NotImplementedError

    @property
    def start(self) -> T:
        return self._start

    @property
    def stop(self) -> T:
        return self._stop

    @staticmethod
    def includes_lower_bound() -> bool:
        # abstract method
        raise NotImplementedError

    @staticmethod
    def includes_upper_bound() -> bool:
        # abstract method
        raise NotImplementedError

    def empty(self) -> bool:
        return (
            self.stop < self.start
            or (not self.start < self.stop and (not self.includes_lower_bound() or not self.includes_upper_bound()))
            or not -INF < self.stop
            or not self.start < INF
        )

    def __eq__(self, other: object, /) -> bool:
        match other:
            case IntervalSet() as interval_set:
                if self.empty():
                    return interval_set.empty()

                match other:
                    case Interval() as interval:
                        try:
                            return (
                                _eq(self.start, interval.start)
                                and _eq(self.stop, interval.stop)
                                and (
                                    self.includes_lower_bound() == interval.includes_lower_bound() or self.start == -INF
                                )
                                and (self.includes_upper_bound() == interval.includes_upper_bound() or self.stop == INF)
                            )
                        except TypeError:
                            return False
                    case IntervalSet():
                        return super().__eq__(other)
            case _:
                return NotImplemented

    def __hash__(self) -> int:
        return super().__hash__()

    def _hash_data(self) -> tuple[T, T, bool | None, bool | None] | None:
        if self.empty():
            return None
        else:
            return (
                self.start,
                self.stop,
                None if self.start == -INF else self.includes_lower_bound(),
                None if self.stop == INF else self.includes_upper_bound(),
            )

    def __contains__(self, item: object, /) -> bool:
        # abstract method
        raise NotImplementedError

    def _binary_union(
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

    def _iterable_union(*intervals: "Interval[U]") -> Iterable["Interval[U]"]:
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

    def _binary_intersection_elementary(self, other: "Interval[U | InfinityTypes]") -> "Interval[T | U]":
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

    def _binary_intersection(self, other: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]:  # pyrefly:ignore[bad-override]
        match other:
            case Interval():
                return self._binary_intersection_elementary(cast(Interval[U], other))
            case IntervalSet():
                return super()._binary_intersection(other)

    @overload
    def intersection(self, *others: "Interval[U | InfinityTypes]") -> "Interval[T | U]": ...  # pyrefly:ignore[bad-override]

    @overload
    def intersection(self, *others: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]: ...

    def intersection(self, *others: IntervalSet[U | InfinityTypes]) -> IntervalSet[T | U]:
        return reduce(lambda x, y: x._binary_intersection(y), others, self)

    @overload
    def __and__(self, other: "Interval[U | InfinityTypes]", /) -> "Interval[T | U]": ...  # pyrefly:ignore[bad-override]

    @overload
    def __and__(self, other: IntervalSet[U | InfinityTypes], /) -> IntervalSet[T | U]: ...

    def __and__(self, other: IntervalSet[U | InfinityTypes], /) -> IntervalSet[T | U]:
        return self._binary_intersection(other)

    def complement(self) -> "IntervalSet[T | InfinityTypes]":
        return IntervalSet(
            (
                Interval(-INF, self.start, not self.includes_upper_bound(), not self.includes_lower_bound()),
                Interval(self.stop, INF, not self.includes_upper_bound(), not self.includes_lower_bound()),
            )
        )

    def isbounded(self) -> bool:
        return self.start != -INF and self.stop != INF

    def isunbounded(self) -> bool:
        return self.start == -INF or self.stop == INF

    def bounded(self: "Interval[U | InfinityTypes]") -> "Interval[U]":
        if self.isunbounded():
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
            return f"{open_bracket}{self.start!r} : {self.stop!r}{close_bracket}"


class ConcreteInterval(Interval[T], Generic[T]):
    def __init__(self, start: T, stop: T) -> None:
        self._intervals = (self,)
        self._start = start
        self._stop = stop


class Closed(ConcreteInterval[T], Generic[T]):
    @staticmethod
    def includes_lower_bound() -> bool:
        return True

    @staticmethod
    def includes_upper_bound() -> bool:
        return True

    def __contains__(self, item: object) -> bool:
        try:
            return _le(self.start, item) and _le(item, self.stop)
        except TypeError:
            return False


class Open(ConcreteInterval[T], Generic[T]):
    @staticmethod
    def includes_lower_bound() -> bool:
        return False

    @staticmethod
    def includes_upper_bound() -> bool:
        return False

    def __contains__(self, item: object) -> bool:
        try:
            return self.start < item < self.stop  # type:ignore[ty:unsupported-operator,unused-ignore,operator,no-any-return]
        except TypeError:
            return False


class ClosedOpen(ConcreteInterval[T], Generic[T]):
    @staticmethod
    def includes_lower_bound() -> bool:
        return True

    @staticmethod
    def includes_upper_bound() -> bool:
        return False

    def __contains__(self, item: object) -> bool:
        try:
            return _le(self.start, item) and item < self.stop  # type:ignore[ty:unsupported-operator,unused-ignore,operator]
        except TypeError:
            return False


class OpenClosed(ConcreteInterval[T], Generic[T]):
    @staticmethod
    def includes_lower_bound() -> bool:
        return False

    @staticmethod
    def includes_upper_bound() -> bool:
        return True

    def __contains__(self, item: object) -> bool:
        try:
            return self.start < item and _le(item, self.stop)  # type:ignore[operator]
        except TypeError:
            return False


EMPTY = Open[Any](INF, -INF)
