from collections.abc import Iterable, Mapping
from itertools import pairwise, chain
from typing import Generic, TypeVar

from typing_extensions import Never

from beset._interval_data import IntervalData, UltimateBound, Sinisterity
from beset._operations import union_data
from beset.sortable import Sortable

T = TypeVar("T", covariant=True, bound=Sortable | None)
U = TypeVar("U", covariant=True, bound=Sortable | None)


def analyze_sinisterity(sinisterities: Iterable[Sinisterity]) -> str:
    it = iter(sinisterities)
    a = next(it)
    b = next(it)

    if a and b and all(it):
        return "ClosedOpenSet"
    elif not a and not b and not any(it):
        return "OpenClosedSet"
    elif a != b and all(x != y for x, y in pairwise(chain((b,), it))):
        return "alternating"
    else:
        return "arbitrary"


def _get_class(cls, interval_data: IntervalData) -> type["IntervalSet"]:
    if cls == Empty:
        return Empty

    odd, left_sinister, bounds, right_sinister = interval_data

    if cls in [Open, Closed, OpenClosed, ClosedOpen]:
        if not odd and not bounds:
            return Empty
        else:
            return cls






class _IntervalMeta(type):
    def __call__(cls: type["IntervalSet"], *args, **kwargs):  # type:ignore[no-untyped-def]
        interval_data, extra_data = cls._construct(*args, **kwargs)

        cls = _get_class(cls, interval_data)

        obj = object().__new__(cls)
        obj._odd, obj._left_sinister, obj._bounds, obj._right_sinister = interval_data

        for name, value in extra_data:
            object.__setattr__(obj, name, value)

        return obj


class IntervalSet(Generic[T], meta=_IntervalMeta):
    __slots__ = ["_odd", "_left_sinister", "_bounds", "_right_sinister"]

    def __init__(self, intervals: Iterable["Interval[T]"]):
        self._odd, self._left_sinister, self._bounds, self._right_sinister = union_data(i._data() for i in intervals)  # type:ignore[type-var]

    @staticmethod
    def _construct(intervals: Iterable["Interval[T]"]) -> tuple[IntervalData[T], Mapping[str, object]]:
        return union_data(i._data() for i in intervals), {}  # type:ignore[type-var]

    def _data(self) -> IntervalData[T]:
        return self._odd, self._left_sinister, self._bounds, self._right_sinister

    def __len__(self) -> int:
        return len(self._bounds) - 1 + self._odd

    # def intervals(self) -> Sequence["Interval[T]"]:
    #     bounds = chain((None,) * self._odd, self._bounds, (None,) * ((len(self._bounds) + self._odd) % 2))
    #     return tuple(
    #
    #         for index, ((start, start_left), (stop, stop_left)) in
    #         enumerate(batched(self._bounds, 2))
    #     )


class Interval(IntervalSet[T], Generic[T]):
    __slots__ = ["_start", "_stop"]
    _start: UltimateBound[T]
    _stop: UltimateBound[T]

    def __init__(self, start: T, stop: T, left_closed: bool, right_closed: bool):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

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


class _ConcreteInterval(Interval[T], Generic[T]):
    def __init__(self, start: T, stop: T):
        # not in use, metaclass handles initialization
        # signature provided for IDE detection
        raise NotImplementedError

    def _construct(self, start: T, stop: T) -> tuple[IntervalData, Mapping[str, object]]:
        far_left, left, right, far_right = self._sinister_template()

        if start is None:
            if stop is None:
                left_sinister = left
                right_sinister = right

                odd = True
                bounds = ()
                start = (-1, start, left)
                stop = (1, stop, right)
            else:
                left_sinister = left
                right_sinister = far_right

                odd = True
                bounds = ((stop, right),)
                start = (-1, start, left)
                stop = (0, stop, right)
        else:
            if stop is None:
                left_sinister = far_left
                right_sinister = right

                odd = False
                bounds = ((start, left),)
                start = (0, start, left)
                stop = (1, stop, right)
            else:
                lower_bound = (start, left)
                upper_bound = (stop, right)

                if not lower_bound < upper_bound:  # empty
                    return (False, left, (), right), {}
                else:
                    left_sinister = far_left
                    right_sinister = far_right

                    odd = False
                    bounds = (lower_bound, upper_bound)
                    start = (0, start, left)
                    stop = (0, stop, right)

        return (odd, left_sinister, bounds, right_sinister), {"_start": start, "_stop": stop}


    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        # abstract
        raise NotImplementedError


class Open(_ConcreteInterval[T], Generic[T]):
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return False, True, False, True


class Closed(_ConcreteInterval[T], Generic[T]):
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return True, False, True, False


class OpenClosed(_ConcreteInterval[T], Generic[T]):
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return True, True, True, True


class ClosedOpen(_ConcreteInterval[T], Generic[T]):
    @staticmethod
    def _sinister_template() -> tuple[bool, bool, bool, bool]:
        return False, False, False, False


class Empty(IntervalSet[Never]): ...
