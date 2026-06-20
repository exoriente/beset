from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Literal, TypeVar, overload

T = TypeVar("T")


@overload
def batched(iterable: Iterable[T], n: Literal[2], *, strict: bool = False) -> Iterator[tuple[T, T] | tuple[T]]: ...


@overload
def batched(iterable: Iterable[T], n: Literal[1], *, strict: bool = False) -> Iterator[tuple[T]]: ...


def batched(iterable: Iterable[T], n: int, *, strict: bool = False) -> Iterator[tuple[T, ...]]:
    # batched('ABCDEFG', 3) → ABC DEF G
    # source: https://docs.python.org/3/library/itertools.html#itertools.batched
    if n < 1:
        raise ValueError("n must be at least one")
    iterator = iter(iterable)
    while batch := tuple(islice(iterator, n)):
        if strict and len(batch) != n:
            raise ValueError("batched(): incomplete batch")
        yield batch
