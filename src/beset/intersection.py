from typing import overload

from beset.infinity import InfinityTypes
from beset.interval import Multiinterval, Monointerval
from beset.sortable import Sortable


# @overload
# def intersection[T: Sortable](
#     a: Monointerval[T | InfinityTypes], b: Monointerval[T]
# ) -> Monointerval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: Monointerval[T | InfinityTypes], b: Multiinterval[T]
# ) -> Monointerval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: Monointerval[T], b: Multiinterval[T | InfinityTypes]
# ) -> Monointerval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: Multiinterval[T | InfinityTypes], b: Monointerval[T]
# ) -> Monointerval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: Multiinterval[T], b: Monointerval[T | InfinityTypes]
# ) -> Monointerval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](
#     a: Multiinterval[T | InfinityTypes], b: Multiinterval[T]
# ) -> Multiinterval[T]: ...
#
#
# @overload
# def intersection[T: Sortable](  # type:ignore[overload-cannot-match]
#     a: Multiinterval[T], b: Multiinterval[T | InfinityTypes]
# ) -> Multiinterval[T]: ...


@overload
def intersection[A: Sortable, B: Sortable](
    a: Monointerval[A], b: Monointerval[B | InfinityTypes]
) -> Monointerval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Monointerval[A | InfinityTypes], b: Monointerval[B]
) -> Monointerval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Monointerval[A], b: Monointerval[B]
) -> Monointerval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](
    a: Multiinterval[A | InfinityTypes], b: Multiinterval[B]
) -> Multiinterval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Multiinterval[A], b: Multiinterval[B | InfinityTypes]
) -> Multiinterval[A | B]: ...


@overload
def intersection[A: Sortable, B: Sortable](  # type:ignore[overload-cannot-match]
    a: Multiinterval[A], b: Multiinterval[B]
) -> Multiinterval[A | B]: ...


def intersection[A: Sortable, B: Sortable](
    a: Multiinterval[A], b: Multiinterval[B]
) -> Multiinterval[A | B]:
    return a.intersection(b)
