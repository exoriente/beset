from operator import itemgetter
from typing import TypeVar

T = TypeVar("T", covariant=True)

Bound = tuple[T, bool]
IntervalData = tuple[bool, tuple[tuple[T, bool], ...]]
UltimateBound = tuple[int, Bound[T]]


def interval_type(data: IntervalData) -> str:
    match data:
        case True, ():  # infinite
            return "Open"
        case False, ():  # empty
            return "Empty"
        case True, ((_, True),):
            return "OpenClosed"
        case True, ((_, False),):
            return "Open"
        case False, ((_, True),):
            return "Open"
        case False, ((_, False),):
            return "ClosedOpen"
        case False, ((_, False), (_, False)):
            return "ClosedOpen"
        case False, ((_, True), (_, False)):
            return "Open"
        case False, ((_, False), (_, True)):
            return "Closed"
        case False, ((_, True), (_, True)):
            return "OpenClosed"
        case odd, bounds:
            if not any(map(itemgetter(1), bounds)):
                return "ClosedOpenSet"
            if all(map(itemgetter(1), bounds)):
                return "OpenClosedSet"
            if alternating(map(itemgetter(1), bounds)):

"""
closedopen [3, inf> = F(3F)F
closed [3, inf] = T(3F)T =
closed [3, 7] = T(3F,7T)F =
closedopen [-inf, inf> = F()F
openclosed <-inf, inf] = 
"""