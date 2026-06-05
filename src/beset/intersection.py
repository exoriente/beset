from typing import overload

from beset.infinity import InfinityTypes
from beset.interval import IntervalSet, Interval
from beset.sortable import Sortable


# @overload
# def intersection[T: Sortable](
#     a: Interval[T | InfinityTypes], b: Interval[T]
# ) -> Interval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: Interval[T | InfinityTypes], b: IntervalSet[T]
# ) -> Interval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: Interval[T], b: IntervalSet[T | InfinityTypes]
# ) -> Interval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: IntervalSet[T | InfinityTypes], b: Interval[T]
# ) -> Interval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: IntervalSet[T], b: Interval[T | InfinityTypes]
# ) -> Interval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: IntervalSet[T | InfinityTypes], b: IntervalSet[T]
# ) -> IntervalSet[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: IntervalSet[T], b: IntervalSet[T | InfinityTypes]
# ) -> IntervalSet[T]: ...


@overload
def intersection[A: Sortable, B: Sortable](a: Interval[A], b: Interval[B | InfinityTypes]) -> Interval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Interval[A | InfinityTypes], b: Interval[B]
) -> Interval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Interval[A], b: Interval[B]
) -> Interval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](
    a: IntervalSet[A | InfinityTypes], b: IntervalSet[B]
) -> IntervalSet[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: IntervalSet[A], b: IntervalSet[B | InfinityTypes]
) -> IntervalSet[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: IntervalSet[A], b: IntervalSet[B]
) -> IntervalSet[A | B]: ...


def intersection[A: Sortable, B: Sortable](a: IntervalSet[A], b: IntervalSet[B]) -> IntervalSet[A | B]:
    return a.intersection(b)
