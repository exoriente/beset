from itertools import permutations

from beset.interval import (
    Closed,
    Open,
    ClosedOpen,
    OpenClosed,
    IntervalSet,
    EMPTY_INTERVAL,
    ConcreteInterval,
)
from pytest import mark, raises


def test_interval_set_immutable() -> None:
    with raises(AttributeError):
        IntervalSet(()).intervals = ()  # type:ignore[ty:invalid-assignment,unused-ignore,misc]


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_interval_set_eq(
    interval_type: type[ConcreteInterval[int]],
) -> None:
    assert IntervalSet(()) == IntervalSet(())
    assert not IntervalSet(()) == IntervalSet((interval_type(0, 1),))
    assert IntervalSet((interval_type(0, 1),)) == IntervalSet((interval_type(0, 1),))
    assert not IntervalSet((interval_type(0, 1),)) == IntervalSet((interval_type(0, 2),))
    assert not IntervalSet((interval_type(0, 1),)) == IntervalSet((interval_type(0, 1), interval_type(1, 2)))
    assert IntervalSet((interval_type(0, 1), interval_type(1, 2))) == IntervalSet(
        (interval_type(0, 1), interval_type(1, 2))
    )
    assert not IntervalSet((interval_type(0, 1), interval_type(1, 2))) == IntervalSet(
        (interval_type(0, 1), interval_type(1, 3))
    )


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_interval_set_eq_interval(
    interval_type: type[ConcreteInterval[int]],
) -> None:
    assert IntervalSet(()) == EMPTY_INTERVAL
    assert EMPTY_INTERVAL == IntervalSet(())
    assert IntervalSet((interval_type(0, 1),)) == interval_type(0, 1)


def test_interval_set_simplification() -> None:
    assert IntervalSet(()) == EMPTY_INTERVAL
    assert IntervalSet((EMPTY_INTERVAL,)) == EMPTY_INTERVAL
    assert IntervalSet((EMPTY_INTERVAL,) * 10) == EMPTY_INTERVAL

    # disjoint
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 1), Closed(2, 3), Open(4, 5)) * factor):
            assert IntervalSet(intervals) == IntervalSet((Open(0, 1), Closed(2, 3), Open(4, 5)))

    # overlapping
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Closed(1, 4), Open(3, 5)) * factor):
            assert IntervalSet(intervals) == IntervalSet((Open(0, 5),))

    # touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Closed(2, 3)) * factor):
            assert IntervalSet(intervals) == IntervalSet((Open(0, 4),))

    # not touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Open(2, 3)) * factor):
            assert IntervalSet(intervals) == IntervalSet((Open(0, 2), Open(2, 4)))
