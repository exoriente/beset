from collections.abc import Iterable
from heapq import heappop, heappush
from typing import TypeVar

from beset.bound import Bound, IntervalData
from beset.sortable import Sortable

T = TypeVar("T", covariant=True, bound=Sortable)

TaggedBound = tuple[Bound[T], int]


def iterate_bounds(bounds: Iterable[Iterable[Bound[T]]]) -> Iterable[TaggedBound[T]]:
    """
    Return all bounds, tagged with the index of their source interval, in ascending order
    Do this as a generator reading the source tuples, without copying the data, by assuming the source bounds
    are sorted by interval and using heap sort to choose the right one to yield
    """
    iterators = list(map(iter, bounds))

    heap: list[TaggedBound[T]] = []

    for index, it in enumerate(iterators):
        try:
            heappush(heap, (next(it), index))  # pyrefly:ignore[bad-argument-type]
        except StopIteration:
            pass

    while heap:
        bound, index = heappop(heap)
        yield bound, index
        try:
            heappush(heap, (next(iterators[index]), index))
        except StopIteration:
            pass


def generate_union_bounds(active: list[bool], tagged_bounds: Iterable[TaggedBound[T]]) -> Iterable[Bound[T]]:
    """
    Return the bound of a union given the input bounds of all intervals in the union
    Can return duplicate values if one of the intervals ends when another starts
    """
    total = sum(active)

    for bound, index in tagged_bounds:
        if active[index]:
            total -= 1
            active[index] = False
            if total == 0:
                yield bound
        else:
            if total == 0:
                yield bound
            total += 1
            active[index] = True


def close_seams(bounds: Iterable[Bound[T]]) -> Iterable[Bound[T]]:
    """
    Returns the input stream, but without pairs of consecutive equal values
    """
    last = None

    for bound in bounds:
        if bound == last:
            last = None
        else:
            if last is not None:
                yield last
            last = bound

    if last is not None:
        yield last


def union_data(intervals: Iterable[IntervalData[T]]) -> IntervalData[T]:
    """
    Return the data for a union of the given interval data sets
    """
    intervals = list(intervals)
    active = [i[0] for i in intervals]
    odd = any(active)
    all_bounds = iterate_bounds(i[1] for i in intervals)

    new_bounds = tuple(close_seams(generate_union_bounds(active, all_bounds)))

    return odd, new_bounds
