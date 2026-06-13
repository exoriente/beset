from collections.abc import Iterable
from heapq import heappop, heappush
from typing import TypeVar

from beset._interval_data import Bound, IntervalData
from beset._protocol import Sortable

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


def generate_union_edges(left_edges: Iterable[bool], right_edges: Iterable[bool]) -> tuple[bool, bool]:
    return not all(left_edges), any(right_edges)


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
    oddities, left_edges, bounds, right_edges = tuple(zip(*intervals)) or ((), (), (), ())
    active = list[bool](oddities)
    odd = any(active)
    all_bounds = iterate_bounds(bounds)

    new_bounds = tuple(close_seams(generate_union_bounds(active, all_bounds)))

    left_edge, right_edge = generate_union_edges(left_edges, right_edges)

    return odd, left_edge, new_bounds, right_edge


def bounds_to_str(start: Bound[object], stop: Bound[object]) -> str:
    left, left_sinister = start
    right, right_sinister = stop

    lower = ("(" if left_sinister else "[") + ("-inf" if left is None else str(left))
    upper = ("+inf" if right is None else str(right)) + ("]" if right_sinister else ")")
    return f"{lower} ; {upper}"
