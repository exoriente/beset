from collections.abc import Iterable
from itertools import chain, batched, pairwise
from operator import itemgetter
from typing import TypeVar

T = TypeVar("T", covariant=True)

Oddity = bool
Sinisterity = bool

Bound = tuple[T, Sinisterity]
IntervalData = tuple[Oddity, Sinisterity, tuple[tuple[T, Sinisterity], ...], Sinisterity]
UltimateBound = tuple[int, Bound[T]]



def analyze_sinisterity(sinisterities: Iterable[Sinisterity]) -> str:
    it = iter(sinisterities)
    a = next(it)
    b = next(it)

    if a and b and all(it):
        return "ClosedOpen"
    elif not a and not b and not any(it):
        return "OpenClosed"
    elif a != b and all(x != y for x, y in pairwise(chain((b,), it))):
        return "alternating"
    else:
        return "arbitrary"


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
        case True, False, ((_, False),), _:  # [None ; x)
            return "ClosedOpen"
        case True, True, ((_, False),), _:  # [None ; x)
            return "Open"
        case False, _, ((_, True),), False:  # (x ; None)
            return "Open"
        case False, _, ((_, False),), False:  # [x ; None)
            return "ClosedOpen"
        case False, _, ((_, True),), True:  # (x ; None]
            return "OpenClosed"
        case False, _, ((_, False),), True:  # [x ; None]
            return "Closed"
        case False, _, ((_, False), (_, False)), _:  # [x ; y)
            return "ClosedOpen"
        case False, _, ((_, True), (_, False)), _:  # (x ; y)
            return "Open"
        case False, _, ((_, False), (_, True)), _:  # [x ; y]
            return "Closed"
        case False, _, ((_, True), (_, True)), _:  # (x ; y]
            return "OpenClosed"
        case odd, neg_inf_sinister, bounds, pos_inf_sinister:
            if not any(chain((neg_inf_sinister,), map(itemgetter(1), bounds), (pos_inf_sinister,))):
                return "ClosedOpenSet"
            if all(chain((neg_inf_sinister,), map(itemgetter(1), bounds), (pos_inf_sinister,))):
                return "OpenClosedSet"
            if alternating(chain((neg_inf_sinister,), map(itemgetter(1), bounds), (pos_inf_sinister,))):
