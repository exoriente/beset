from collections.abc import Iterable
from heapq import heappop, heappush
from itertools import groupby
from operator import itemgetter
from typing import TypeVar

from beset._interval_data import Bound, IntervalData
from beset._protocol import Sortable

T = TypeVar("T", covariant=True, bound=Sortable)

TaggedBound = tuple[Bound[T], int]


def iterate_bounds_sequential(bounds: Iterable[Iterable[Bound[T]]]) -> Iterable[TaggedBound[T]]:
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


def iterate_bounds(bounds: Iterable[Iterable[Bound[T]]]) -> Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]:
    """
    Return all bounds, tagged with the index of their source interval, in ascending order
    If there are bounds with the same value, return them as a tuple
    Unique bounds are returned as a tuple of one
    """
    yield from groupby(iterate_bounds_sequential(bounds), key=itemgetter(0))


def generate_union_bounds(
    active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]
) -> Iterable[Bound[T]]:
    """
    Return the bound of a union given the input bounds of all intervals in the union
    """
    total = sum(active)

    for bound, changing in tagged_bounds:
        delta = 0
        for _, index in changing:
            active[index] = (a := not active[index])
            delta += -1 + 2 * a

        if delta < 0:
            total += delta
            if total == 0:
                yield bound
        elif delta > 0:
            if total == 0:
                yield bound
            total += delta


def union_data(intervals: Iterable[IntervalData[T]]) -> IntervalData[T]:
    """
    Return the data for a union of the given interval data sets
    """
    oddities, bounds = tuple(zip(*intervals)) or ((), ())
    active = list[bool](oddities)
    odd = any(active)

    new_bounds = tuple(generate_union_bounds(active, iterate_bounds(bounds)))

    return odd, new_bounds


def generate_intersection_bounds(
    active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]
) -> Iterable[Bound[T]]:
    """
    Return the bound of an intersection given the input bounds of all intervals in the intersection
    """
    total = sum(active)
    max_active = len(active)

    for bound, changing in tagged_bounds:
        delta = 0
        for _, index in changing:
            active[index] = (a := not active[index])
            delta += -1 + 2 * a

        if delta < 0:
            if total == max_active:
                yield bound
            total += delta
        elif delta > 0:
            total += delta
            if total == max_active:
                yield bound


def intersection_data(intervals: Iterable[IntervalData[T]]) -> IntervalData[T]:
    """
    Return the data for an intersection of the given interval data sets
    """
    oddities, bounds = tuple(zip(*intervals)) or ((), ())
    active = list[bool](oddities)
    odd = all(active)

    new_bounds = tuple(generate_intersection_bounds(active, iterate_bounds(bounds)))

    return odd, new_bounds


def check_is_disjoint(active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]) -> bool:
    """
    Return true if more than one interval is active at the same time while iterating over the bounds
    """
    total = sum(active)

    if total > 1:
        return False

    for bound, changing in tagged_bounds:
        for _, index in changing:
            active[index] = (a := not active[index])
            total += -1 + 2 * a

        if total > 1:
            return False
    else:
        return True


def is_disjoint(intervals: Iterable[IntervalData[T]]) -> bool:
    """
    Return True iff there is no overlap between any of the intervals
    """
    oddities, bounds = tuple(zip(*intervals)) or ((), ())
    active = list[bool](oddities)

    return check_is_disjoint(active, iterate_bounds(bounds))


def check_is_subset(active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]) -> bool:
    """
    Return False if interval 0 is active at any time when interval 1 isn't
    """
    if active[0] > active[1]:
        return False

    for bound, changing in tagged_bounds:
        for _, index in changing:
            active[index] = not active[index]

        if active[0] > active[1]:
            return False
    else:
        return True


def is_subset(a: IntervalData[T], b: IntervalData[T]) -> bool:
    """
    Return True iff a is a subset of b
    """
    a_odd, a_bounds = a
    b_odd, b_bounds = b

    return check_is_subset([a_odd, b_odd], iterate_bounds((a_bounds, b_bounds)))


def check_is_proper_subset(
    active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]
) -> bool:
    """
    Return False if interval 0 is active at any time when interval 1 isn't
    Return False if interval 1 was never active while interval 0 wasn't
    """
    if active[0] > active[1]:
        return False

    proper = active[1] > active[0]

    for bound, changing in tagged_bounds:
        for _, index in changing:
            active[index] = not active[index]

        if active[0] > active[1]:
            return False

        if active[1] > active[0]:
            proper = True
    else:
        return proper


def is_proper_subset(a: IntervalData[T], b: IntervalData[T]) -> bool:
    """
    Return True iff a is a proper subset of b (b is larger)
    """
    a_odd, a_bounds = a
    b_odd, b_bounds = b

    return check_is_proper_subset([a_odd, b_odd], iterate_bounds((a_bounds, b_bounds)))


def generate_difference_bounds(
    active: list[bool], tagged_bounds: Iterable[tuple[Bound[T], Iterable[TaggedBound[T]]]]
) -> Iterable[Bound[T]]:
    """
    Return the bounds where interval 0 and interval 1 is not
    """
    for bound, changing in tagged_bounds:
        old_active = active[0] and not active[1]
        for _, index in changing:
            active[index] = not active[index]
        if old_active != (active[0] and not active[1]):
            yield bound


def difference_data(a: IntervalData[T], b: IntervalData[T]) -> IntervalData[T]:
    """
    Return IntervalData for an IntervalSet that contains everything from a unless it's in b
    """
    a_odd, a_bounds = a
    b_odd, b_bounds = b
    active = [a_odd, b_odd]

    odd = a_odd and not b_odd

    bounds = tuple(generate_difference_bounds(active, iterate_bounds((a_bounds, b_bounds))))

    return odd, bounds


def complement_data(d: IntervalData[T]) -> IntervalData[T]:
    """
    Return IntervalData for the complement of d
    """
    odd, bounds = d
    return not odd, bounds


SINISTERITY_TO_CLASS_NAME = {
    (False, False): "ClosedOpen",
    (False, True): "ClosedOpen",
    (True, False): "Open",
    (True, True): "OpenClosed",
}


def bounds_to_repr(start: Bound[object], stop: Bound[object]) -> str:
    """
    Return the technical representation for a continuous interval between two bounds:
    Examples: Closed(3, 7), LeftClosed(-100), Unbounded(), ClosedOpen("abc", "bcd")
    """
    left, left_sinister = start
    right, right_sinister = stop

    if left is None:
        cls_name = "RightClosed" if right_sinister else "RightOpen"
        return f"{cls_name}({right!r})"

    if right is None:
        cls_name = "LeftOpen" if left_sinister else "LeftClosed"
        return f"{cls_name}({left!r})"

    return f"{SINISTERITY_TO_CLASS_NAME[left_sinister, right_sinister]}({left!r}, {right!r})"


def bounds_to_str(start: Bound[object], stop: Bound[object]) -> str:
    """
    Return a nice notation for a continuous interval between two bounds.
    Examples: (3 ; 7], [-100 ; +inf⟩, ⟨-inf ; +inf⟩, ["abc" ; "bcd")
    """
    left, left_sinister = start
    right, right_sinister = stop

    if left is None:
        lower = "⟨-inf"
    else:
        lower = ("(" if left_sinister else "[") + repr(left)

    if right is None:
        upper = "+inf⟩"
    else:
        upper = repr(right) + ("]" if right_sinister else ")")

    return f"{lower} ; {upper}"
