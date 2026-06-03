from itertools import permutations

from beset.interval import (
    Closed,
    Open,
    ClosedOpen,
    OpenClosed,
    Multiinterval,
    EMPTY_INTERVAL,
    Monointerval,
)
from pytest import mark, raises


def test_multiinterval_immutable() -> None:
    with raises(AttributeError):
        Multiinterval(()).intervals = ()  # type:ignore[ty:invalid-assignment,unused-ignore,misc]


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_multiinterval_eq(
    interval_type: type[Monointerval[int]],
) -> None:
    assert Multiinterval(()) == Multiinterval(())
    assert not Multiinterval(()) == Multiinterval((interval_type(0, 1),))
    assert Multiinterval((interval_type(0, 1),)) == Multiinterval((interval_type(0, 1),))
    assert not Multiinterval((interval_type(0, 1),)) == Multiinterval((interval_type(0, 2),))
    assert not Multiinterval((interval_type(0, 1),)) == Multiinterval(
        (interval_type(0, 1), interval_type(1, 2))
    )
    assert Multiinterval((interval_type(0, 1), interval_type(1, 2))) == Multiinterval(
        (interval_type(0, 1), interval_type(1, 2))
    )
    assert not Multiinterval((interval_type(0, 1), interval_type(1, 2))) == Multiinterval(
        (interval_type(0, 1), interval_type(1, 3))
    )


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_multiinterval_eq_monointerval(
    interval_type: type[Monointerval[int]],
) -> None:
    assert Multiinterval(()) == EMPTY_INTERVAL
    assert EMPTY_INTERVAL == Multiinterval(())
    assert Multiinterval((interval_type(0, 1),)) == interval_type(0, 1)


def test_multiinterval_normalization() -> None:
    assert Multiinterval(()) == EMPTY_INTERVAL
    assert Multiinterval((EMPTY_INTERVAL,)) == EMPTY_INTERVAL
    assert Multiinterval((EMPTY_INTERVAL,) * 10) == EMPTY_INTERVAL

    # disjoint
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 1), Closed(2, 3), Open(4, 5)) * factor):
            assert Multiinterval(intervals) == Multiinterval((Open(0, 1), Closed(2, 3), Open(4, 5)))

    # overlapping
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Closed(1, 4), Open(3, 5)) * factor):
            assert Multiinterval(intervals) == Multiinterval((Open(0, 5),))

    # touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Closed(2, 3)) * factor):
            assert Multiinterval(intervals) == Multiinterval((Open(0, 4),))

    # not touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Open(2, 3)) * factor):
            assert Multiinterval(intervals) == Multiinterval((Open(0, 2), Open(2, 4)))
