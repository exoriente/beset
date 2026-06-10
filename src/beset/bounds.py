from collections.abc import Iterable
from typing import Generic, TypeVar, cast

from beset._operations import union_data
from beset.bound import Bound, IntervalData
from beset.sortable import Sortable

T = TypeVar("T", covariant=True, bound=Sortable | None)
U = TypeVar("U", covariant=True, bound=Sortable | None)


class IntervalSet(Generic[T]):
    def __init__(self, intervals: Iterable["Interval[T]"]):
        self._odd, self._bounds = union_data(i._data() for i in intervals)  # type:ignore[type-var]

    def _data(self) -> IntervalData[T]:
        return self._odd, self._bounds

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
    def __init__(self, start: T, stop: T, left_closed: bool, right_closed: bool):
        lower_bound: tuple[Bound[T], ...]
        upper_bound: tuple[Bound[T], ...]

        if start is None:
            self._odd = True
            lower_bound = ()
        else:
            self._odd = False
            lower_bound = ((start, not left_closed),)

        upper_bound = () if stop is None else ((stop, right_closed),)

        self._bounds = lower_bound + upper_bound

    @property
    def _start(self) -> Bound[T] | None:
        return ((0, True) * self._odd + self._bounds)[0]

    @property
    def start(self) -> T:
        return cast(T, (((None,),) * self._odd + self._bounds)[0][0])

    @property
    def stop(self) -> T:
        return cast(T, (((None,),) * self._odd + self._bounds + ((None,),))[1][0])

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"


print(repr(Interval(0, 5, True, False)))
print(repr(Interval(None, 5, True, False)))
print(repr(Interval(5, None, True, False)))

x = Interval(2, 5, True, False)
y = Interval(5, 8, True, False)
z = Interval(7, 10, True, False)

print(IntervalSet((x,)))
