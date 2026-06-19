from bisect import bisect_right
from collections.abc import Iterable, Mapping
from itertools import chain, pairwise
from operator import itemgetter
from sys import version_info
from typing import Any, Generic, Literal, TypeVar, cast, overload

if version_info >= (3, 11):
    from typing import Never  # type:ignore[attr-defined,unused-ignore]
else:
    from typing_extensions import Never

if version_info >= (3, 12):
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
            return interval_type

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

    return IntervalSet


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
    def __call__(cls: type["IntervalSet[T]"], *args, **kwargs):  # type:ignore[no-untyped-def,misc]
        interval_data = cls._construct(*args, **kwargs)
        return create_instance(interval_data, cls)


class IntervalSet(Generic[T], metaclass=IntervalMeta):
    __slots__ = ["_odd", "_bounds", "_intervals_cached"]
    _odd: bool
    _bounds: tuple[Bound[T], ...]
    _intervals_cached: tuple["Interval[T]", ...] | None

    def __init__(self, intervals: Iterable["IntervalSet[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    @classmethod
    def _construct(cls, intervals: Iterable["IntervalSet[T]"] = ()) -> IntervalData[T]:
        return union_data(map(IntervalSet._data, intervals))  # type:ignore[arg-type]

    def _post_construct(self) -> None:
        self._intervals_cached = None

    def _data(self) -> IntervalData[T]:
        return self._odd, self._bounds

    def _bound_pairs(self) -> Iterable[tuple[Bound[T], Bound[T]]]:
        bounds = chain(self._odd * ((None, True),), self._bounds, ((None, False),))
        for pair in batched(bounds, 2):
            if len(pair) == 2:
                yield cast(tuple[Bound[T], Bound[T]], pair)

    def __eq__(self, other: object, /) -> bool:
        return (self._odd, self._bounds) == (other._odd, other._bounds) if isinstance(other, IntervalSet) else False

    def __hash__(self) -> int:
        return hash((self._odd, self._bounds))

    def __len__(self) -> int:
        b = len(self._bounds)
        return b // 2 + (b % 2 or self._odd)

    def __bool__(self) -> bool:
        return self._odd or bool(self._bounds)

    @property
    def intervals(self) -> tuple["Interval[T]", ...]:
        if self._intervals_cached is None:
            self._intervals_cached = tuple(create_singular_instance(start, stop) for start, stop in self._bound_pairs())

        return self._intervals_cached

    def __contains__(self, item: object) -> bool:
        value = (item, False)

        try:
            index = bisect_right(self._bounds, value)
        except TypeError:
            return False

        return index % 2 != self._odd

    def isdisjoint(self, *others: "IntervalSet[U]") -> bool:
        return is_disjoint(map(IntervalSet._data, chain((self,), others)))  # type:ignore[type-var]

    def issubset(self, other: "IntervalSet[U]", /) -> bool:
        return is_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __le__(self, other: "IntervalSet[U]", /) -> bool:
        return is_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __lt__(self, other: "IntervalSet[U]", /) -> bool:
        return is_proper_subset(self._data(), other._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def issuperset(self, other: "IntervalSet[U]", /) -> bool:
        return is_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __ge__(self, other: "IntervalSet[U]", /) -> bool:
        return is_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __gt__(self, other: "IntervalSet[U]", /) -> bool:
        return is_proper_subset(other._data(), self._data())  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def union(self, *others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return create_instance(union_data(map(IntervalSet._data, chain((self,), others))))  # type:ignore[arg-type,type-var]

    def __or__(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        return create_instance(union_data(map(IntervalSet._data, (self, other))))  # type:ignore[arg-type,type-var]

    @overload
    def intersection(self: "IntervalSet[V | None]", *others: "IntervalSet[U]") -> "IntervalSet[V | U]": ...

    @overload
    def intersection(self: "IntervalSet[V]", *others: "IntervalSet[U | None]") -> "IntervalSet[V | U]": ...  # type:ignore[overload-cannot-match]

    def intersection(self: "IntervalSet[V | None]", *others: "IntervalSet[U]") -> "IntervalSet[V | U]":
        return create_instance(intersection_data(map(IntervalSet._data, chain((self,), others))))  # type:ignore[arg-type,type-var]

    @overload
    def __and__(self: "IntervalSet[V | None]", other: "IntervalSet[U]", /) -> "IntervalSet[V | U]": ...

    @overload
    def __and__(self: "IntervalSet[V]", other: "IntervalSet[U | None]", /) -> "IntervalSet[V | U]": ...  # type:ignore[overload-cannot-match]

    def __and__(self: "IntervalSet[V | None]", other: "IntervalSet[U]", /) -> "IntervalSet[V | U]":
        return create_instance(intersection_data(map(IntervalSet._data, (self, other))))  # type:ignore[arg-type,type-var]

    def difference(self: "IntervalSet[V]", other: "IntervalSet[U  | None]", /) -> "IntervalSet[V | U]":
        return create_instance(difference_data(self._data(), other._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,arg-type,type-var]

    def __sub__(self: "IntervalSet[V]", other: "IntervalSet[U  | None]", /) -> "IntervalSet[V | U]":
        return create_instance(difference_data(self._data(), other._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,arg-type,type-var]

    def complement(self) -> "IntervalSet[T | None]":
        return create_instance(complement_data(self._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __invert__(self) -> "IntervalSet[T | None]":
        return create_instance(complement_data(self._data()))  # type:ignore[ty:invalid-argument-type,unused-ignore,type-var]

    def __getitem__(self, index_or_slice: int | slice, /) -> "Interval[T] | IntervalSet[T]":
        match index_or_slice:
            case int() as i:
                return self.intervals[i]
            case slice() as s:



    def __repr__(self) -> str:
        contents = ", ".join(bounds_to_repr(a, b) for a, b in self._bound_pairs())
        return f"{type(self).__name__}([{contents}])"

    def __str__(self) -> str:
        return " | ".join(bounds_to_str(a, b) for a, b in self._bound_pairs())


class OpenSet(IntervalSet[T], Generic[T]):
    _left_sinister = True
    _right_sinister = False

    def __init__(self, intervals: Iterable["Open[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class ClosedSet(IntervalSet[T], Generic[T]):
    _left_sinister = False
    _right_sinister = True

    def __init__(self, intervals: Iterable["Closed[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class ClosedOpenSet(IntervalSet[T], Generic[T]):
    _left_sinister = False
    _right_sinister = False

    def __init__(self, intervals: Iterable["ClosedOpen[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class OpenClosedSet(IntervalSet[T], Generic[T]):
    _left_sinister = True
    _right_sinister = True

    def __init__(self, intervals: Iterable["OpenClosed[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class Interval(IntervalSet[T], Generic[T]):
    _left_sinister: bool
    _right_sinister: bool
    __slots__ = ["_start", "_stop"]
    _start: UltimateBound[T]
    _stop: UltimateBound[T]

    def __init__(self, start: T, stop: T, start_closed: bool, stop_closed: bool):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

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
        return self._start[1]

    @property
    def stop(self) -> T:
        return self._stop[1]

    @staticmethod
    def or_empty(start: V, stop: V) -> "Interval[V] | Empty":
        # abstract
        raise NotImplementedError

    def __contains__(self, item: object) -> bool:
        value = (0, item, False)
        try:
            return not value < self._start and value < self._stop  # type:ignore[ty:unsupported-operator,unused-ignore]
        except TypeError:
            return False

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"

    def __str__(self) -> str:
        return bounds_to_str(self._start[1:], self._stop[1:])


class _ConcreteInterval(Interval[T], Generic[T]):
    def __init__(self, start: T, stop: T):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

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

        self._intervals_cached = (self,)


class Open(_ConcreteInterval[T], OpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: V, stop: V) -> "Open[V] | Empty":
        return cast(
            Open[V] | Empty, create_instance(Open._construct(start, stop, allow_empty=True), interval_type=Open)
        )


class Closed(_ConcreteInterval[T], ClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: V, stop: V) -> "Closed[V] | Empty":
        return cast(
            Closed[V] | Empty, create_instance(Closed._construct(start, stop, allow_empty=True), interval_type=Closed)
        )


class OpenClosed(_ConcreteInterval[T], OpenClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: V, stop: V) -> "OpenClosed[V] | Empty":
        return cast(
            OpenClosed[V] | Empty,
            create_instance(OpenClosed._construct(start, stop, allow_empty=True), interval_type=OpenClosed),
        )


class ClosedOpen(_ConcreteInterval[T], ClosedOpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: V, stop: V) -> "ClosedOpen[V] | Empty":
        return cast(
            ClosedOpen[V] | Empty,
            create_instance(ClosedOpen._construct(start, stop, allow_empty=True), interval_type=ClosedOpen),
        )


class _LeftBounded(_ConcreteInterval[T], Generic[T]):
    # abstract

    def __init__(self, start: T) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

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
        raise NotImplementedError

    @classmethod
    def _construct(cls, stop: V) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        if stop is None:
            return True, ()
        else:
            return True, ((stop, cls._right_sinister),)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._bounds[0][0]!r})"


class LeftOpen(_LeftBounded[T | None], Open[T | None], OpenClosed[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        raise NotImplementedError


class RightOpen(_RightBounded[T | None], Open[T | None], ClosedOpen[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        raise NotImplementedError


class LeftClosed(_LeftBounded[T | None], Closed[T | None], ClosedOpen[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        raise NotImplementedError


class RightClosed(_RightBounded[T | None], Closed[T | None], OpenClosed[T | None], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def or_empty(start: Never, stop: Never) -> Never:  # type:ignore[override,unused-ignore]
        raise NotImplementedError


class Unbounded(LeftOpen[None], RightOpen[None], LeftClosed[None], RightClosed[None]):  # type:ignore[misc,unused-ignore]
    def __init__(self) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    @classmethod
    def _construct(cls) -> IntervalData[None]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        return True, ()

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"


class Empty(OpenSet[Never], ClosedSet[Never], OpenClosedSet[Never], ClosedOpenSet[Never]):
    def __init__(self) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    @classmethod
    def _construct(cls) -> IntervalData[Never]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        return False, ()

    def _post_construct(self) -> None:
        self._intervals_cached = ()

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
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
