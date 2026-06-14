from collections.abc import Iterable
from itertools import chain, pairwise
from operator import itemgetter
from sys import version_info
from typing import Generic, Literal, TypeVar, cast

if version_info >= (3, 11):
    from typing import Never  # type:ignore[attr-defined,unused-ignore]
else:
    from typing_extensions import Never

if version_info >= (3, 12):
    from itertools import batched  # type:ignore[attr-defined,unused-ignore]
else:
    from beset._itertools import batched  # type:ignore[assignment,unused-ignore]

from beset._interval_data import Bound, IntervalData, Sinisterity, UltimateBound
from beset._operations import bounds_to_repr, bounds_to_str, union_data
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
    if interval_type == Empty:
        return Empty

    odd, left_sinister, bounds, right_sinister = interval_data

    if not odd and not bounds:
        return Empty

    if interval_type in [Open, Closed, OpenClosed, ClosedOpen]:
        return interval_type  # type:ignore[return-value]

    if interval_type in PLURAL_TO_SINGULAR:
        if len(bounds) + odd <= 2:
            return PLURAL_TO_SINGULAR[interval_type]  # type:ignore[ty:invalid-argument-type,unused-ignore,return-value]
        else:
            return interval_type  # pyright:ignore[reportReturnType]

    match odd, left_sinister, bounds, right_sinister:
        case True, False, (), False:  # [None ; None)
            return ClosedOpen
        case True, False, (), True:  # [None ; None]
            return Closed
        case True, True, (), False:  # (None ; None)
            return Open
        case True, True, (), True:  # (None ; None]
            return OpenClosed
        case False, _, (), _:  # Empty
            return Empty
        case True, False, ((_, True),), _:  # [None ; x]
            return Closed
        case True, True, ((_, True),), _:  # (None ; x]
            return OpenClosed
        case True, False, ((_, False),), _:  # [None ; x)
            return ClosedOpen
        case True, True, ((_, False),), _:  # [None ; x)
            return Open
        case False, _, ((_, True),), False:  # (x ; None)
            return Open
        case False, _, ((_, False),), False:  # [x ; None)
            return ClosedOpen
        case False, _, ((_, True),), True:  # (x ; None]
            return OpenClosed
        case False, _, ((_, False),), True:  # [x ; None]
            return Closed
        case False, _, ((_, False), (_, False)), _:  # [x ; y)
            return ClosedOpen
        case False, _, ((_, True), (_, False)), _:  # (x ; y)
            return Open
        case False, _, ((_, False), (_, True)), _:  # [x ; y]
            return Closed
        case False, _, ((_, True), (_, True)), _:  # (x ; y]
            return OpenClosed
        case odd, _, bounds, _:
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
    obj._odd, obj._left_sinister, obj._bounds, obj._right_sinister = interval_data
    obj._post_construct()
    return obj


class IntervalMeta(type):
    def __call__(cls: type["IntervalSet[T]"] | type["Empty"], *args, **kwargs):  # type:ignore[no-untyped-def,misc]
        interval_data = cls._construct(*args, **kwargs)
        return create_instance(interval_data, cls)


class IntervalSet(Generic[T], metaclass=IntervalMeta):
    __slots__ = ["_odd", "_left_sinister", "_bounds", "_right_sinister"]
    _odd: bool
    _left_sinister: bool
    _bounds: tuple[Bound[T], ...]
    _right_sinister: bool

    def __init__(self, intervals: Iterable["IntervalSet[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    @classmethod
    def _construct(cls, intervals: Iterable["IntervalSet[T]"] = ()) -> IntervalData[T]:
        return union_data(map(IntervalSet._data, intervals))  # type:ignore[arg-type]

    def _post_construct(self) -> None:
        pass

    def _data(self) -> IntervalData[T]:
        return self._odd, self._left_sinister, self._bounds, self._right_sinister

    def _bound_pairs(self) -> Iterable[tuple[Bound[T], Bound[T]]]:
        bounds = chain(self._odd * ((None, self._left_sinister),), self._bounds, ((None, self._right_sinister),))
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

    def union(self, *others: "IntervalSet[U]") -> "IntervalSet[T | U]":
        return create_instance(union_data(map(IntervalSet._data, chain((self,), others))))  # type:ignore[arg-type,type-var]

    def __or__(self, other: "IntervalSet[U]", /) -> "IntervalSet[T | U]":
        return create_instance(union_data(map(IntervalSet._data, (self, other))))  # type:ignore[arg-type,type-var]

    # def intervals(self) -> Sequence["Interval[T]"]:
    #     bounds = chain((None,) * self._odd, self._bounds, (None,) * ((len(self._bounds) + self._odd) % 2))
    #     return tuple(
    #
    #         for index, ((start, start_left), (stop, stop_left)) in
    #         enumerate(batched(self._bounds, 2))
    #     )

    def __repr__(self) -> str:
        contents = ", ".join(bounds_to_repr(a, b) for a, b in self._bound_pairs())
        return f"{type(self).__name__}([{contents}])"

    def __str__(self) -> str:
        return " | ".join(bounds_to_str(a, b) for a, b in self._bound_pairs())


class OpenSet(IntervalSet[T], Generic[T]):
    def __init__(self, intervals: Iterable["Open[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class ClosedSet(IntervalSet[T], Generic[T]):
    def __init__(self, intervals: Iterable["Closed[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class ClosedOpenSet(IntervalSet[T], Generic[T]):
    def __init__(self, intervals: Iterable["ClosedOpen[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class OpenClosedSet(IntervalSet[T], Generic[T]):
    def __init__(self, intervals: Iterable["OpenClosed[T]"] = ()):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError


class Interval(IntervalSet[T], Generic[T]):
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
    def _construct(cls, start: V, stop: V) -> IntervalData[V]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        far_left, left, right, far_right = cls._sinister_template()

        bounds: tuple[Bound[V], ...]
        if start is None:
            if stop is None:
                left_sinister = left
                right_sinister = right

                odd = True
                bounds = ()
            else:
                left_sinister = left
                right_sinister = far_right

                odd = True
                bounds = ((stop, right),)
        else:
            if stop is None:
                left_sinister = far_left
                right_sinister = right

                odd = False
                bounds = ((start, left),)
            else:
                lower_bound = (start, left)
                upper_bound = (stop, right)

                if not lower_bound < upper_bound:  # empty
                    raise ValueError("Empty interval! Start must be before stop.")
                else:
                    left_sinister = far_left
                    right_sinister = far_right

                    odd = False
                    bounds = (lower_bound, upper_bound)

        return odd, left_sinister, bounds, right_sinister

    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        # abstract
        raise NotImplementedError

    def _post_construct(self) -> None:
        far_left, left, right, far_right = self._sinister_template()
        match self._odd, self._bounds:
            case True, ((stop, stop_sinister),):
                self._start = (-1, None, left)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
                self._stop = (0, stop, stop_sinister)
            case True, ():
                self._start = (-1, None, left)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
                self._stop = (1, None, right)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            case False, ((start, start_sinister),):
                self._start = (0, start, start_sinister)
                self._stop = (1, None, right)  # type:ignore[ty:invalid-assignment,unused-ignore,assignment]
            case False, ((start, start_sinister), (stop, stop_sinister)):
                self._start = (0, start, start_sinister)
                self._stop = (0, stop, stop_sinister)


class Open(_ConcreteInterval[T], OpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return False, True, False, True


class Closed(_ConcreteInterval[T], ClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return True, False, True, False


class OpenClosed(_ConcreteInterval[T], OpenClosedSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return True, True, True, True


class ClosedOpen(_ConcreteInterval[T], ClosedOpenSet[T], Generic[T]):  # pyright:ignore[reportIncompatibleMethodOverride]
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return False, False, False, False


PLURAL_TO_SINGULAR = {OpenSet: Open, ClosedSet: Closed, OpenClosedSet: OpenClosed, ClosedOpenSet: ClosedOpen}


class Empty(OpenSet[Never], ClosedSet[Never], OpenClosedSet[Never], ClosedOpenSet[Never]):
    def __init__(self) -> None:
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    @classmethod
    def _construct(cls) -> IntervalData[Never]:  # type:ignore[ty:invalid-method-override,unused-ignore,override]
        return False, True, (), False

    def __repr__(self) -> str:
        return f"{type(self).__name__}()"

    def __str__(self) -> str:
        left = "(" if self._right_sinister else "["
        right = "]" if self._left_sinister else ")"
        return f"{left};{right}"


EMPTY = Empty()
