from operator import itemgetter
from typing import TypeVar

T = TypeVar("T", covariant=True)

Oddity = bool
Sinisterity = bool

Bound = tuple[T, Sinisterity]
IntervalData = tuple[Oddity, Sinisterity, tuple[tuple[T, Sinisterity], ...], Sinisterity]
UltimateBound = tuple[int, Bound[T]]


def interval_type(data: IntervalData) -> str:
    match data:
        case True, False, (), False:  # [None ; None)
            return "ClosedOpen"
        case True, False, (), True:  # [None ; None]
            return "Closed"
        case True, True, (), False:  # (None ; None)
            return "Open"
        case True, True, (), True:  # (None ; None]
            return "OpenClosed"
        case False, _, (), _:  # Empty
            return "Empty"
        case True, False, ((_, True),), _:  # [None ; x]
            return "Closed"
        case True, True, ((_, True),), _:  # (None ; x]
            return "OpenClosed"
        case True, False, ((_, False),):  # [None ; x)
            return "ClosedOpen"
        case True, False, ((_, False),):  # [None ; x)
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
