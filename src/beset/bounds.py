from collections.abc import Iterable
from typing import Generic, TypeVar, cast

from beset._operations import union_bounds
from beset.bound import IntervalInternals

T = TypeVar("T", covariant=True)


class IntervalSet(Generic[T]):
    def __init__(self, intervals: Iterable["MonoInterval[T]"]):
        self._odd, self._bounds = union_bounds(i._internals() for i in intervals)  # type:ignore[type-var]

    def _internals(self) -> IntervalInternals[T]:
        return self._odd, self._bounds

    def __len__(self) -> int:
        return len(self._bounds) - 1 + self._odd

    # def intervals(self) -> Sequence["MonoInterval[T]"]:
    #     bounds = chain((None,) * self._odd, self._bounds, (None,) * ((len(self._bounds) + self._odd) % 2))
    #     return tuple(
    #
    #         for index, ((start, start_left), (stop, stop_left)) in
    #         enumerate(batched(self._bounds, 2))
    #     )


class MonoInterval(IntervalSet[T], Generic[T]):
    def __init__(self, start: T, stop: T, left_closed: bool, right_closed: bool):
        lower_bound: tuple[tuple[T, bool], ...]
        upper_bound: tuple[tuple[T, bool], ...]

        if start is None:
            self._odd = True
            lower_bound = ()
        else:
            self._odd = False
            lower_bound = ((start, not left_closed),)

        upper_bound = () if stop is None else ((stop, right_closed),)

        self._bounds = lower_bound + upper_bound

    @property
    def start(self) -> T:
        if self._odd or not self._bounds:
            return cast(T, None)
        else:
            return self._bounds[0][0]

    @property
    def stop(self) -> T:
        try:
            return self._bounds[1 - self._odd][0]
        except IndexError:
            return cast(T, None)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.start!r}, {self.stop!r})"


print(repr(MonoInterval(0, 5, True, False)))
print(repr(MonoInterval(None, 5, True, False)))
print(repr(MonoInterval(5, None, True, False)))

x = MonoInterval(2, 5, True, False)
y = MonoInterval(5, 8, True, False)
z = MonoInterval(7, 10, True, False)

print(IntervalSet((x,)))
