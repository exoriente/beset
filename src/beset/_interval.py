from bisect import bisect_right
from collections.abc import Iterable, Iterator, Mapping
from itertools import chain, pairwise, starmap
from operator import itemgetter
from sys import version_info
from typing import Any, Generic, Literal, TypeVar, cast, overload

if version_info >= (3, 11):  # pragma: no cover
    from typing import Never, Self  # type:ignore[attr-defined,unused-ignore]
else:
    from typing_extensions import Never, Self

if version_info >= (3, 12):  # pragma: no cover
    from itertools import batched  # type:ignore[attr-defined,unused-ignore]
else:
    from beset._itertools import batched  # type:ignore[assignment,unused-ignore]

from beset._interval_data import Bound, IntervalData, Sinisterity, UltimateBound
from beset._operations import (
    bounds_to_repr,
    bounds_to_str,
    complement_data,
    difference_data,
    intersection_data,
    is_disjoint,
    is_proper_subset,
    is_subset,
    union_data,
)
from beset._protocol import Sortable

T = TypeVar("T", covariant=True, bound=Sortable | None)
U = TypeVar("U", covariant=True, bound=Sortable | None)
V = TypeVar("V", bound=Sortable | None)
W = TypeVar("W", covariant=True, bound=Sortable)


def analyze_sinisterity(sinisterities: Iterable[Sinisterity]) -> Literal["co", "oc", "alt", "misc"]:
    it = iter(sinisterities)
    a = next(it)
    b = next(it)

    if a and b and all(it):
        return "oc"  # OpenClosed
    elif not a and not b and not any(it):
        return "co"  # ClosedOpen
    elif a != b and all(x != y for x, y in pairwise(chain((b,), it))):
        return "alt"  # alternating
    else:
        return "misc"  # something else


def choose_class(
    interval_data: IntervalData[T], interval_type: type["IntervalSet[T]"] | None
) -> type["IntervalSet[T]"]:
    if interval_type is not None and interval_type is not IntervalSet:
        if interval_type in [Empty, Unbounded]:
            return cast(type["IntervalSet[T]"], interval_type)

        odd, bounds = interval_data

        if not odd and len(bounds) == 2 and interval_type in [Open, Closed, OpenClosed, ClosedOpen]:
            return interval_type  # type:ignore[return-value]

        if len(bounds) + odd > 2 and interval_type in [OpenSet, ClosedSet, OpenClosedSet, ClosedOpenSet]:
            return interval_type  # type:ignore[return-value]

        if len(bounds) == 1 and interval_type in [LeftOpen, LeftClosed, RightOpen, RightClosed]:
            return interval_type  # type:ignore[return-value]

    match interval_data:
        case False, ():  # <;>
            return Empty
        case True, ():  # <-inf ; +inf>
            return cast(type["IntervalSet[T]"], Unbounded)
        case True, ((_, True),):  # <-inf ; x]
            return cast(type["IntervalSet[T]"], RightClosed)
        case True, ((_, False),):  # <-inf ; x)
            return cast(type["IntervalSet[T]"], RightOpen)
        case False, ((_, True),):  # (x ; +inf>
            return cast(type["IntervalSet[T]"], LeftOpen)
        case False, ((_, False),):  # [x ; +inf>
            return cast(type["IntervalSet[T]"], LeftClosed)
        case False, ((_, False), (_, False)):  # [x ; y)
            return ClosedOpen
        case False, ((_, True), (_, False)):  # (x ; y)
            return Open
        case False, ((_, False), (_, True)):  # [x ; y]
            return Closed
        case False, ((_, True), (_, True)):  # (x ; y]
            return OpenClosed
        case odd, bounds:
            match analyze_sinisterity(map(itemgetter(1), bounds)):
                case "co":
                    return ClosedOpenSet
                case "oc":
                    return OpenClosedSet
                case "alt":
                    if odd == bounds[0][1]:
                        return ClosedSet
                    else:
                        return OpenSet
                case _:
                    return IntervalSet

    return IntervalSet  # pragma: no cover  # added to satisfy type checkers, even though the match covers every case


def create_instance(
    interval_data: IntervalData[T], interval_type: type["IntervalSet[T]"] | None = None
) -> "IntervalSet[T]":
    cls = choose_class(interval_data, interval_type)
    obj = object().__new__(cls)
    obj._odd, obj._bounds = interval_data
    obj._post_construct()
    return obj


def create_singular_instance(start: Bound[T], stop: Bound[T]) -> "Interval[T]":
    left, left_sinister = start
    right, right_sinister = stop

    cls = SINISTERITY_TO_CLASS[left_sinister, right_sinister]

    new_left_bound: tuple[Bound[T], ...]
    new_right_bound: tuple[Bound[T], ...]

    if left is None:
        new_odd = True
        new_left_bound = ()
    else:
        new_odd = False
        new_left_bound = (start,)

    if right is None:
        new_right_bound = ()
    else:
        new_right_bound = (stop,)

    new_bounds = new_left_bound + new_right_bound

    obj = object().__new__(cls)

    obj._odd = new_odd
    obj._bounds = new_bounds

    obj._post_construct()

    return obj


class IntervalMeta(type):
    """Metaclass that normalizes interval construction to the most specific type."""

    def __call__(cls: type["IntervalSet[T]"], *args, **kwargs):  # type:ignore[no-untyped-def,misc,ty:invalid-method-override,unused-ignore]
        """Construct and normalize an interval-set instance."""
        interval_data = cls._construct(*args, **kwargs)
        return create_instance(interval_data, cls)


class IntervalSet(Generic[T], metaclass=IntervalMeta):
    """
    The `IntervalSet` type represents intervals and interval unions of any kind, including the empty interval.
    Unbounded intervals can also be represented when an `IntervalSet` has `None` or a union with `None` as its type argument.
    """
    __slots__ = ["_odd", "_bounds", "_intervals_cached"]
    _odd: bool
    _bounds: tuple[Bound[T], ...]

    def __init__(self, intervals: Iterable["IntervalSet[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        """
        Construct the simplified union of an iterable of interval sets.

        Args:
            intervals: The interval sets to combine. Defaults to an empty
                iterable.

        Note:
            The returned object may be a more specific `IntervalSet`
            subclass when the combined intervals have a simpler
            representation.

        Examples:
            Disjoint open intervals produce an `OpenSet`:

            >>> IntervalSet([Open(1, 2), Open(3, 4)])
            OpenSet([Open(1, 2), Open(3, 4)])

            Overlapping closed intervals produce a `Closed` interval:

            >>> IntervalSet([Closed(1, 3), Closed(2, 4)])
            Closed(1, 4)
        """
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls, intervals: Iterable["IntervalSet[T]"] = ()) -> IntervalData[T]:  # type:ignore[ty:invalid-generic-class,unused-ignore]
        return union_data(map(IntervalSet._data, intervals))  # type:ignore[arg-type]

    def _post_construct(self) -> None:
        pass

    def _data(self) -> IntervalData[T]:
        return self._odd, self._bounds

    def _bound_pairs(self) -> Iterator[tuple[Bound[T], Bound[T]]]:
        bounds = chain(self._odd * ((None, True),), self._bounds, ((None, False),))
        for pair in batched(bounds, 2):
            if len(pair) == 2:
                yield cast(tuple[Bound[T], Bound[T]], pair)

    def _bound_pairs_reversed(self) -> Iterator[tuple[Bound[T], Bound[T]]]:
        bounds = chain(
            ((len(self._bounds) + self._odd) % 2 * ((None, False),)), reversed(self._bounds), ((None, True),)
        )
        for pair in batched(bounds, 2):
            if len(pair) == 2:
                yield cast(tuple[Bound[T], Bound[T]], (pair[1], pair[0]))

    def _interval(self, index: int) -> "Interval[T]":
        a = 2 * index - self._odd
        b = a + 1
        if a == -1:
            if b == len(self._bounds):
                return cast(Interval[T], UNBOUNDED)
            else:
                return cast(Interval[T], create_singular_instance((None, True), self._bounds[b]))
        else:
            if b == len(self._bounds):
                return cast(Interval[T], create_singular_instance(self._bounds[a], (None, False)))
            else:
                return create_singular_instance(self._bounds[a], self._bounds[b])

    def __eq__(self, other: object, /) -> bool:
        """Return whether this interval set has the same members as `other`.

        Args:
            other (object): The object to compare with this interval set.

        Examples:
            >>> Open(1, 3) == Open(1, 3)
            True
        """
        return (self._odd, self._bounds) == (other._odd, other._bounds) if isinstance(other, IntervalSet) else False

    def __hash__(self) -> int:
        """Return a hash based on the interval set's bounds.

        Examples:
            >>> len({Open(1, 3), Open(1, 3)})
            1
        """
        return hash((self._odd, self._bounds))

    def __len__(self) -> int:
        """Return the number of disjoint intervals in this set.

        Examples:
            >>> len(OpenSet([Open(1, 2), Open(3, 4)]))
            2
        """
        b = len(self._bounds)
        return b // 2 + (b % 2 or self._odd)

    def __bool__(self) -> bool:
        """Return `False` when this is the empty interval set.

        Examples:
            >>> bool(Empty())
            False
        """
        return self._odd or bool(self._bounds)

    def __contains__(self, item: object) -> bool:
        """Return whether `item` belongs to this interval set.

        Objects that cannot be compared with the interval bounds are not
        contained.

        Examples:
            >>> 2 in Open(1, 3)
            True
        """
        value = (item, False)

        try:
            index = bisect_right(self._bounds, value)
        except TypeError:
            return False

        return index % 2 != self._odd

    def isdisjoint(self, *others: "IntervalSet[U]") -> bool:
        """Return whether this set has no members in common with `others`.

        Args:
            *others (IntervalSet[U]): The interval sets to compare with this set.
        """
        return is_disjoint(map(IntervalSet._data, chain((self,), others)))  # type:ignore[type-var]

    def issubset(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether every member of this set belongs to `other`.

        Args:
            other (IntervalSet[U]): The interval set that may contain this set.
        """
        return is_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __le__(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether this set is a subset of `other`.

        Args:
            other (IntervalSet[U]): The interval set that may contain this set.

        Examples:
            >>> Open(1, 2) <= Open(0, 3)
            True
        """
        return is_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __lt__(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether this set is a proper subset of `other`.

        Args:
            other (IntervalSet[U]): The interval set that may contain this set.

        Examples:
            >>> Open(1, 2) < Open(0, 3)
            True
        """
        return is_proper_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def issuperset(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether this set contains every member of `other`.

        Args:
            other (IntervalSet[U]): The interval set that may be contained by this set.
        """
        return is_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __ge__(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether this set is a superset of `other`.

        Args:
            other (IntervalSet[U]): The interval set that may be contained by this set.

        Examples:
            >>> Open(0, 3) >= Open(1, 2)
            True
        """
        return is_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __gt__(self, other: "IntervalSet[U]", /) -> bool:
        """Return whether this set is a proper superset of `other`.

        Args:
            other (IntervalSet[U]): The interval set that may be contained by this set.

        Examples:
            >>> Open(0, 3) > Open(1, 2)
            True
        """
        return is_proper_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def union(self, *others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        """Return the union of this set and `others`.

        Args:
            *others (IntervalSet[U]): The interval sets to combine with this set.
        """
        return create_instance(union_data(map(IntervalSet._data, chain((self,), others))))  # type:ignore[arg-type,type-var]

    def __or__(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        """Return the union of this set and `other` using `|`.

        Args:
            other (IntervalSet[U]): The interval set to combine with this set.

        Examples:
            >>> Open(1, 3) | Open(2, 4)
            Open(1, 4)
        """
        return create_instance(union_data(map(IntervalSet._data, (self, other))))  # type:ignore[arg-type,type-var]

    @overload
    def intersection(self: "IntervalSet[V | None]", *others: "IntervalSet[W]") -> "IntervalSet[V | W]": ...

    @overload
    def intersection(self: "IntervalSet[V]", *others: "IntervalSet[U | None]") -> "IntervalSet[V | U]": ...

    def intersection(self: "IntervalSet[V | None]", *others: "IntervalSet[U]") -> "IntervalSet[V | U]":
        """Return the intersection of this set and `others`.

        Args:
            *others (IntervalSet[U]): The interval sets to intersect with this set.
        """
        return create_instance(intersection_data(map(IntervalSet._data, chain((self,), others))))  # type:ignore[arg-type,type-var]

    @overload
    def __and__(self: "IntervalSet[V | None]", other: "IntervalSet[W]", /) -> "IntervalSet[V | W]": ...

    @overload
    def __and__(self: "IntervalSet[V]", other: "IntervalSet[U | None]", /) -> "IntervalSet[V | U]": ...

    def __and__(self: "IntervalSet[V | None]", other: "IntervalSet[U]", /) -> "IntervalSet[V | U]":
        """Return the intersection of this set and `other` using `&`.

        Args:
            other (IntervalSet[U]): The interval set to intersect with this set.

        Examples:
            >>> Open(1, 3) & Open(2, 4)
            Open(2, 3)
        """
        return create_instance(intersection_data(map(IntervalSet._data, (self, other))))  # type:ignore[arg-type,type-var]

    def difference(self: "IntervalSet[V]", other: "IntervalSet[U  | None]", /) -> "IntervalSet[V | U]":
        """Return the members of this set that are not in `other`.

        Args:
            other (IntervalSet[U | None]): The interval set to remove from this set.
        """
        return create_instance(difference_data(self._data(), other._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,arg-type,type-var]

    def __sub__(self: "IntervalSet[V]", other: "IntervalSet[U  | None]", /) -> "IntervalSet[V | U]":
        """Return the difference between this set and `other` using `-`.

        Args:
            other (IntervalSet[U | None]): The interval set to remove from this set.

        Examples:
            >>> Open(1, 4) - Closed(2, 3)
            OpenSet([Open(1, 2), Open(3, 4)])
        """
        return create_instance(difference_data(self._data(), other._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,arg-type,type-var]

    def complement(self) -> "IntervalSet[T | None]":
        """Return the values outside this set in the extended ordered domain."""
        return create_instance(complement_data(self._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __invert__(self) -> "IntervalSet[T | None]":
        """Return the complement of this set using `~`.

        Examples:
            >>> ~ClosedOpen(1, 3)
            ClosedOpenSet([RightOpen(1), LeftClosed(3)])
        """
        return create_instance(complement_data(self._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __getitem__(self, index_or_slice: int | slice, /) -> "Interval[T] | IntervalSet[T]":
        """Return a component interval by index or a set of components by slice.

        Integer indexing follows the usual sequence rules. A slice produces a
        normalized interval set containing the selected component intervals.

        Args:
            index_or_slice: The component index or slice.

        Raises:
            ValueError: If the slice step is zero.

        Examples:
            >>> OpenSet([Open(1, 2), Open(3, 4)])[1]
            Open(3, 4)
        """
        match index_or_slice:
            case int() as i:
                return self._interval(i)
            case slice() as s:
                length = len(self)
                step = 1 if s.step is None else s.step

                if step > 0:
                    start = 0 if s.start is None else max(length + s.start if s.start < 0 else s.start, 0)
                    stop = length if s.stop is None else min(length + s.stop if s.stop < 0 else s.stop, length)

                elif step < 0:
                    step = -step
                    start = 0 if s.stop is None else min(length + s.stop if s.stop < 0 else s.stop, length) + 1
                    stop = length if s.start is None else max(length + s.start if s.start < 0 else s.start, 0) + 1
                    start += (stop - 1 - start) % step

                else:
                    raise ValueError("slice step cannot be zero")

                no_of_bounds = len(self._bounds)
                new_bounds = tuple(
                    chain.from_iterable(
                        self._bounds[max(b := (i * 2 - self._odd), 0) : min(b + 2, no_of_bounds)]
                        for i in range(start, stop, step)
                    )
                )

                new_odd = self._odd and start == 0

                return create_instance((new_odd, new_bounds))

    def __iter__(self) -> "Iterator[Interval[T]]":
        """Iterate over this set's disjoint component intervals in ascending order.

        Examples:
            >>> list(OpenSet([Open(1, 2), Open(3, 4)]))
            [Open(1, 2), Open(3, 4)]
        """
        yield from starmap(create_singular_instance, self._bound_pairs())  # pyrefly:ignore[invalid-yield]

    def __reversed__(self) -> "Iterator[Interval[T]]":
        """Iterate over this set's disjoint component intervals in descending order.

        Examples:
            >>> list(reversed(OpenSet([Open(1, 2), Open(3, 4)])))
            [Open(3, 4), Open(1, 2)]
        """
        yield from starmap(create_singular_instance, self._bound_pairs_reversed())  # pyrefly:ignore[invalid-yield]

    def enclosure(self) -> "Interval[T]":
        """Return the smallest interval that contains every member of this set."""
        start = (None, True) if self._odd else self._bounds[0]
        stop = (None, False) if (len(self._bounds) + self._odd) % 2 else self._bounds[-1]
        return create_singular_instance(cast(Bound[T], start), cast(Bound[T], stop))

    def __repr__(self) -> str:
        """Return a constructor-style representation of this interval set.

        Examples:
            >>> repr(OpenSet([Open(1, 2), Open(3, 4)]))
            'OpenSet([Open(1, 2), Open(3, 4)])'
        """
        contents = ", ".join(bounds_to_repr(a, b) for a, b in self._bound_pairs())
        return f"{type(self).__name__}([{contents}])"

    def __str__(self) -> str:
        """Return a mathematical representation of this interval set.

        Examples:
            >>> str(Open(1, 3))
            '(1 ; 3)'
        """
        return " | ".join(bounds_to_str(a, b) for a, b in self._bound_pairs())


class OpenSet(IntervalSet[T], Generic[T]):
    """A union of zero or more open intervals."""
    _left_sinister = True
    _right_sinister = False

    def __init__(self, intervals: Iterable["Open[T]"] = ()):
        """Construct the simplified union of open intervals.

        Args:
            intervals: The open intervals to combine.

        Examples:
            >>> OpenSet([Open(1, 2), Open(3, 4)])
            OpenSet([Open(1, 2), Open(3, 4)])
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover


class ClosedSet(IntervalSet[T], Generic[T]):
    """A union of zero or more closed intervals."""
    _left_sinister = False
    _right_sinister = True

    def __init__(self, intervals: Iterable["Closed[T]"] = ()):
        """Construct the simplified union of closed intervals.

        Args:
            intervals: The closed intervals to combine.

        Examples:
            >>> ClosedSet([Closed(1, 2), Closed(3, 4)])
            ClosedSet([ClosedOpen(1, 2), ClosedOpen(3, 4)])
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover


class ClosedOpenSet(IntervalSet[T], Generic[T]):
    """A union of zero or more half-open, half-closed intervals: `[start ; stop)`."""
    _left_sinister = False
    _right_sinister = False

    def __init__(self, intervals: Iterable["ClosedOpen[T]"] = ()):
        """Construct the simplified union of closed-open intervals.

        Args:
            intervals: The closed-open intervals to combine.

        Examples:
            >>> ClosedOpenSet([ClosedOpen(1, 2), ClosedOpen(3, 4)])
            ClosedOpenSet([ClosedOpen(1, 2), ClosedOpen(3, 4)])
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover


class OpenClosedSet(IntervalSet[T], Generic[T]):
    """A union of zero or more half-open, half-closed intervals: `(start ; stop]`."""
    _left_sinister = True
    _right_sinister = True

    def __init__(self, intervals: Iterable["OpenClosed[T]"] = ()):
        """Construct the simplified union of open-closed intervals.

        Args:
            intervals: The open-closed intervals to combine.

        Examples:
            >>> OpenClosedSet([OpenClosed(1, 2), OpenClosed(3, 4)])
            OpenClosedSet([OpenClosed(1, 2), OpenClosed(3, 4)])
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover


class Interval(IntervalSet[T], Generic[T]):
    """A single interval with configurable open or closed endpoints."""
    _left_sinister: bool
    _right_sinister: bool
    __slots__ = ["_start", "_stop"]
    _start: UltimateBound[T]
    _stop: UltimateBound[T]

    def __init__(self, start: T, stop: T, start_closed: bool, stop_closed: bool):
        """Construct an interval with independently configurable endpoints.

        Args:
            start: The lower endpoint, or `None` for negative infinity.
            stop: The upper endpoint, or `None` for positive infinity.
            start_closed: Whether to include `start`.
            stop_closed: Whether to include `stop`.

        Raises:
            ValueError: If the interval is empty.

        Examples:
            >>> Interval(1, 3, start_closed=True, stop_closed=False)
            ClosedOpen(1, 3)
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls, start: V, stop: V, start_closed: bool, stop_closed: bool) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        if start_closed:
            if stop_closed:
                return Closed._construct(start, stop)
            else:
                return ClosedOpen._construct(start, stop)
        else:
            if stop_closed:
                return OpenClosed._construct(start, stop)
            else:
                return Open._construct(start, stop)

    @property
    def start(self) -> T:
        """Return the lower endpoint, or `None` when the interval is unbounded below."""
        return self._start[1]

    @property
    def stop(self) -> T:
        """Return the upper endpoint, or `None` when the interval is unbounded above."""
        return self._stop[1]


    def __contains__(self, item: object) -> bool:
        """Return whether `item` belongs to this interval.

        Examples:
            >>> 1 in Closed(1, 3)
            True
        """
        value = (0, item, False)
        try:
            return not value < self._start and value < self._stop  # type:ignore[ty:unsupported-operator,unused-ignore]
        except TypeError:
            return False

    def enclosure(self) -> Self:  # pyright:ignore[reportIncompatibleMethodOverride]
        """Return this interval, which already encloses itself."""
        return self

    def __repr__(self) -> str:
        """Return a constructor-style representation of this interval.

        Examples:
            >>> repr(Open(1, 3))
            'Open(1, 3)'
        """
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"

    def __str__(self) -> str:
        """Return a mathematical representation of this interval.

        Examples:
            >>> str(Closed(1, 3))
            '[1 ; 3]'
        """
        return bounds_to_str(self._start[1:], self._stop[1:])


class _ConcreteInterval(Interval[T], Generic[T]):
    def __init__(self, start: T, stop: T):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls, start: V, stop: V, allow_empty: bool = False) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        bounds: tuple[Bound[V], ...]
        if start is None:
            if stop is None:
                odd = True
                bounds = ()
            else:
                odd = True
                bounds = ((stop, cls._right_sinister),)
        else:
            if stop is None:
                odd = False
                bounds = ((start, cls._left_sinister),)
            else:
                lower_bound = (start, cls._left_sinister)
                upper_bound = (stop, cls._right_sinister)

                if not lower_bound < upper_bound:  # empty
                    if allow_empty:
                        return False, ()
                    else:
                        raise ValueError("Empty interval! Start must be before stop.")
                else:
                    odd = False
                    bounds = (lower_bound, upper_bound)

        return odd, bounds

    def _post_construct(self) -> None:
        match self._odd, self._bounds:
            case True, ((stop, stop_sinister),):
                self._start = (-1, None, True)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
                self._stop = (0, stop, stop_sinister)
            case True, ():
                self._start = (-1, None, True)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
                self._stop = (1, None, False)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            case False, ((start, start_sinister),):
                self._start = (0, start, start_sinister)
                self._stop = (1, None, False)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            case False, ((start, start_sinister), (stop, stop_sinister)):
                self._start = (0, start, start_sinister)
                self._stop = (0, stop, stop_sinister)

    @staticmethod
    def or_empty(start: V, stop: V) -> "Interval[V] | Empty":
        """Construct an interval, returning `Empty` if the endpoints form no interval.

        Args:
            start: The lower endpoint.
            stop: The upper endpoint.
        """
        raise NotImplementedError  # pragma: no cover

class Open(_ConcreteInterval[T], OpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """A single interval that excludes both endpoints: `(start ; stop)`."""

    @staticmethod
    def or_empty(start: V, stop: V) -> "Open[V] | Empty":
        """Construct an open interval, returning `Empty` when it is empty.

        Args:
            start: The excluded lower endpoint.
            stop: The excluded upper endpoint.
        """
        return cast(
            Open[V] | Empty, create_instance(Open._construct(start, stop, allow_empty=True), interval_type=Open)
        )


class Closed(_ConcreteInterval[T], ClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """A single interval that includes both endpoints: `[start ; stop]`."""

    @staticmethod
    def or_empty(start: V, stop: V) -> "Closed[V] | Empty":
        """Construct a closed interval, returning `Empty` when it is empty.

        Args:
            start: The included lower endpoint.
            stop: The included upper endpoint.
        """
        return cast(
            Closed[V] | Empty, create_instance(Closed._construct(start, stop, allow_empty=True), interval_type=Closed)
        )


class OpenClosed(_ConcreteInterval[T], OpenClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """A single interval that excludes `start` and includes `stop`: `(start ; stop]`."""

    @staticmethod
    def or_empty(start: V, stop: V) -> "OpenClosed[V] | Empty":
        """Construct an open-closed interval, returning `Empty` when it is empty.

        Args:
            start: The excluded lower endpoint.
            stop: The included upper endpoint.
        """
        return cast(
            OpenClosed[V] | Empty,
            create_instance(OpenClosed._construct(start, stop, allow_empty=True), interval_type=OpenClosed),
        )


class ClosedOpen(_ConcreteInterval[T], ClosedOpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """A single interval that includes `start` and excludes `stop`: `[start ; stop)`."""

    @staticmethod
    def or_empty(start: V, stop: V) -> "ClosedOpen[V] | Empty":
        """Construct a closed-open interval, returning `Empty` when it is empty.

        Args:
            start: The included lower endpoint.
            stop: The excluded upper endpoint.
        """
        return cast(
            ClosedOpen[V] | Empty,
            create_instance(ClosedOpen._construct(start, stop, allow_empty=True), interval_type=ClosedOpen),
        )


class _LeftBounded(_ConcreteInterval[T], Generic[T]):
    # abstract

    def __init__(self, start: T) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls, start: V) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        if start is None:
            return True, ()
        else:
            return False, ((start, cls._left_sinister),)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._bounds[0][0]!r})"


class _RightBounded(_ConcreteInterval[T], Generic[T]):
    # abstract

    def __init__(self, stop: T) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls, stop: V) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        if stop is None:
            return True, ()
        else:
            return True, ((stop, cls._right_sinister),)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._bounds[0][0]!r})"


class LeftOpen(_LeftBounded[T | None], Open[T | None], OpenClosed[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """An interval unbounded above with an excluded lower endpoint: `(start ; +inf⟩`."""

    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        """Raise `NotImplementedError`; unbounded intervals cannot be empty."""
        raise NotImplementedError  # pragma: no cover


class RightOpen(_RightBounded[T | None], Open[T | None], ClosedOpen[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """An interval unbounded below with an excluded upper endpoint: `⟨-inf ; stop)`."""

    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        """Raise `NotImplementedError`; unbounded intervals cannot be empty."""
        raise NotImplementedError  # pragma: no cover


class LeftClosed(_LeftBounded[T | None], Closed[T | None], ClosedOpen[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """An interval unbounded above with an included lower endpoint: `[start ; +inf⟩`."""

    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        """Raise `NotImplementedError`; unbounded intervals cannot be empty."""
        raise NotImplementedError  # pragma: no cover


class RightClosed(_RightBounded[T | None], Closed[T | None], OpenClosed[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    """An interval unbounded below with an included upper endpoint: `⟨-inf ; stop]`."""

    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        """Raise `NotImplementedError`; unbounded intervals cannot be empty."""
        raise NotImplementedError  # pragma: no cover


class Unbounded(LeftOpen[None], RightOpen[None], LeftClosed[None], RightClosed[None]):  # type:ignore[misc,unused-ignore]
    """The interval containing every value: `⟨-inf ; +inf⟩`."""

    def __init__(self) -> None:
        """Construct the unbounded interval.

        Examples:
            >>> Unbounded()
            Unbounded()
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls) -> IntervalData[None]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        return True, ()

    def __repr__(self) -> str:
        """Return `Unbounded()`.

        Examples:
            >>> repr(Unbounded())
            'Unbounded()'
        """
        return f"{type(self).__name__}()"


class Empty(OpenSet[Never], ClosedSet[Never], OpenClosedSet[Never], ClosedOpenSet[Never]):
    """The interval set containing no values."""

    def __init__(self) -> None:
        """Construct the empty interval set.

        Examples:
            >>> Empty()
            Empty()
        """
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _construct(cls) -> IntervalData[Never]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        return False, ()

    def enclosure(self) -> "Empty":  # type:ignore[ty:invalid-method-override,override,unused-ignore]
        """Return this empty set."""
        return self

    def __repr__(self) -> str:
        """Return `Empty()`.

        Examples:
            >>> repr(Empty())
            'Empty()'
        """
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
        """Return the mathematical representation of the empty set.

        Examples:
            >>> str(Empty())
            '⟨;⟩'
        """
        return "⟨;⟩"


PLURAL_TO_SINGULAR = {OpenSet: Open, ClosedSet: Closed, OpenClosedSet: OpenClosed, ClosedOpenSet: ClosedOpen}

SINISTERITY_TO_CLASS: Mapping[tuple[bool, bool], type[Interval[Any]]] = {
    (False, False): ClosedOpen,
    (False, True): ClosedOpen,
    (True, False): Open,
    (True, True): OpenClosed,
}

UNBOUNDED = Unbounded()
EMPTY = Empty()
