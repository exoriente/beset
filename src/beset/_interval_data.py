from typing import TypeVar

T = TypeVar("T", covariant=True)

Oddity = bool
Sinisterity = bool

Bound = tuple[T, Sinisterity]
IntervalData = tuple[Oddity, Sinisterity, tuple[tuple[T, Sinisterity], ...], Sinisterity]
UltimateBound = tuple[int, T, Sinisterity]
