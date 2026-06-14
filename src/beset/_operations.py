from collections.abc import Iterable
from heapq import heappop, heappush
from itertools import compress
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


def union_data(intervals: Iterable[IntervalData[T]]) -> IntervalData[T]:
    """
    Return the data for a union of the given interval data sets
    """
    oddities, left_edges, bounds, right_edges = tuple(zip(*intervals)) or ((), (), (), ())
    active = list[bool](oddities)
    odd = any(active)
    all_bounds = iterate_bounds(bounds)

    left_edge = all(compress(left_edges, active))

    new_bounds = tuple(close_seams(generate_union_bounds(active, all_bounds)))

    right_edge = any(compress(right_edges, active))

    return odd, left_edge, new_bounds, right_edge


def generate_intersection_bounds(active: list[bool], tagged_bounds: Iterable[TaggedBound[T]]) -> Iterable[Bound[T]]:
    """
    Return the bound of an intersection given the input bounds of all intervals in the intersection
    Can return duplicate values if one of the intervals ends when another starts
    """
    total = sum(active)
    max = len(active)

    for bound, index in tagged_bounds:
        if active[index]:
            if total == max:
                yield bound
            total -= 1
            active[index] = False
        else:
            total += 1
            active[index] = True
            if total == max:
                yield bound


def intersection_data(intervals: Iterable[IntervalData[T]]) -> IntervalData[T]:
    """
    Return the data for an intersection of the given interval data sets
    """
    oddities, left_edges, bounds, right_edges = tuple(zip(*intervals)) or ((), (), (), ())
    active = list[bool](oddities)
    odd = all(active)
    all_bounds = iterate_bounds(bounds)

    left_edge = any(compress(left_edges, active))

    new_bounds = tuple(close_seams(generate_intersection_bounds(active, all_bounds)))

    right_edge = all(compress(right_edges, active))

    return odd, left_edge, new_bounds, right_edge


SINISTERITY_TO_CLASS_NAME = {
    (False, False): "ClosedOpen",
    (False, True): "ClosedOpen",
    (True, False): "Open",
    (True, True): "OpenClosed",
}


def bounds_to_repr(start: Bound[object], stop: Bound[object]) -> str:
    """
    Return the technical representation for a continuous interval between two bounds:
    Examples: Closed(3, 7), Closed(-100, None), Open(None, None), ClosedOpen("abc", "bcd")
    """
    left, left_sinister = start
    right, right_sinister = stop
    return f"{SINISTERITY_TO_CLASS_NAME[left_sinister, right_sinister]}({left!r}, {right!r})"


def bounds_to_str(start: Bound[object], stop: Bound[object]) -> str:
    """
    Return a nice notation for a continuous interval between two bounds.
    Examples: [3 ; 7], [-100 ; +inf], (-inf ; + inf), ["abc" ; "bcd")
    """
    left, left_sinister = start
    right, right_sinister = stop

    lower = ("(" if left_sinister else "[") + ("-inf" if left is None else repr(left))
    upper = ("+inf" if right is None else repr(right)) + ("]" if right_sinister else ")")
    return f"{lower} ; {upper}"
