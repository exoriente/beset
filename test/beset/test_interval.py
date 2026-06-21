from typing import TypeVar

from pytest import fail, raises

from beset import (
    EMPTY,
    UNBOUNDED,
    Closed,
    ClosedOpen,
    ClosedOpenSet,
    ClosedSet,
    Empty,
    Interval,
    IntervalSet,
    LeftClosed,
    LeftOpen,
    Open,
    OpenClosed,
    OpenClosedSet,
    OpenSet,
    RightClosed,
    RightOpen,
    Sortable,
    Unbounded,
)

T = TypeVar("T", covariant=True, bound=Sortable | None)
IntervalType = Open[T] | Closed[T] | ClosedOpen[T] | OpenClosed[T]


def assert_exact_match(x: IntervalSet[Sortable | None], y: IntervalSet[Sortable | None]) -> None:
    __tracebackhide__ = True
    if not (type(x) is type(y) and x._odd == y._odd and x._bounds == y._bounds):
        problem = "Intervals not an exact match!\n"
        for name, a, b in [
            ("type", type(x), type(y)),
            ("odd", x._odd, y._odd),
            ("bounds", x._bounds, y._bounds),
        ]:
            problem += f"{name}: {a} {'==' if a == b else '!='} {b}  {'✅' if a == b else '❌'}\n"

        fail(problem)


def assert_not_exact_match(x: IntervalSet[Sortable | None], y: IntervalSet[Sortable | None]) -> None:
    __tracebackhide__ = True
    if type(x) is type(y) and x._odd == y._odd and x._bounds == y._bounds:
        fail("Intervals match exactly when the shouldn't!")


class TestIntervalCreation:
    def test_empty(self) -> None:
        assert type(Empty()) is Empty

    def test_interval_restricted(self) -> None:
        assert type(Open(0, 1)) is Open
        assert type(Open(0, None)) is LeftOpen
        assert type(Open(None, 0)) is RightOpen
        assert type(Open(None, None)) is Unbounded

    def test_interval_restricted_but_empty(self, interval_class: type[IntervalType[int]]) -> None:
        with raises(ValueError):
            type(interval_class(1, 0))

    def test_interval_but_zero_length(self) -> None:
        with raises(ValueError):
            Open(0, 0)
        with raises(ValueError):
            OpenClosed(0, 0)
        with raises(ValueError):
            ClosedOpen(0, 0)

        assert Closed(0, 0)

    def test_interval(self) -> None:
        assert type(Interval(0, 1, False, False)) is Open
        assert type(Interval(0, 1, False, True)) is OpenClosed
        assert type(Interval(0, 1, True, False)) is ClosedOpen
        assert type(Interval(0, 1, True, True)) is Closed

        assert type(Interval(None, 1, False, False)) is RightOpen
        assert type(Interval(None, 1, False, True)) is RightClosed
        assert type(Interval(None, 1, True, False)) is RightOpen
        assert type(Interval(None, 1, True, True)) is RightClosed

        assert type(Interval(0, None, False, False)) is LeftOpen
        assert type(Interval(0, None, False, True)) is LeftOpen
        assert type(Interval(0, None, True, False)) is LeftClosed
        assert type(Interval(0, None, True, True)) is LeftClosed

        assert type(Interval(None, None, False, False)) is Unbounded
        assert type(Interval(None, None, False, True)) is Unbounded
        assert type(Interval(None, None, True, False)) is Unbounded
        assert type(Interval(None, None, True, True)) is Unbounded

    def test_interval_but_empty(self) -> None:
        with raises(ValueError):
            Interval(1, 0, False, False)
        with raises(ValueError):
            Interval(1, 0, False, True)
        with raises(ValueError):
            Interval(1, 0, True, False)
        with raises(ValueError):
            Interval(1, 0, True, True)

    def test_interval_set_restricted(self) -> None:
        assert type(OpenSet([Open(0, 1), Open(2, 3)])) is OpenSet
        assert type(ClosedSet([Closed(0, 1), Closed(2, 3)])) is ClosedSet
        assert type(OpenClosedSet([OpenClosed(0, 1), OpenClosed(2, 3)])) is OpenClosedSet
        assert type(ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])) is ClosedOpenSet

    def test_interval_set_restricted_but_singular(self) -> None:
        assert type(OpenSet([Open(0, 1)])) is Open
        assert type(ClosedSet([Closed(0, 1)])) is Closed
        assert type(OpenClosedSet([OpenClosed(0, 1)])) is OpenClosed
        assert type(ClosedOpenSet([ClosedOpen(0, 1)])) is ClosedOpen

    def test_interval_set_restricted_but_empty(self) -> None:
        assert type(OpenSet()) is Empty
        assert type(ClosedSet()) is Empty
        assert type(OpenClosedSet()) is Empty
        assert type(ClosedOpenSet()) is Empty

    def test_interval_set(self) -> None:
        assert type(IntervalSet([Open(0, 1), Closed(2, 3)])) is IntervalSet

    def test_interval_set_but_restricted(self) -> None:
        assert type(IntervalSet([Open(0, 1), Open(2, 3)])) is OpenSet
        assert type(IntervalSet([Closed(0, 1), Closed(2, 3)])) is ClosedSet
        assert type(IntervalSet([OpenClosed(0, 1), OpenClosed(2, 3)])) is OpenClosedSet
        assert type(IntervalSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])) is ClosedOpenSet

    def test_interval_set_but_singular(self) -> None:
        assert type(IntervalSet([Open(0, 1)])) is Open
        assert type(IntervalSet([Closed(0, 1)])) is Closed
        assert type(IntervalSet([OpenClosed(0, 1)])) is OpenClosed
        assert type(IntervalSet([ClosedOpen(0, 1)])) is ClosedOpen

    def test_interval_set_but_empty(self) -> None:
        assert type(IntervalSet()) is Empty

    def test_interval_set_simplification(self) -> None:
        assert IntervalSet() == EMPTY
        assert IntervalSet([EMPTY, EMPTY]) == EMPTY
        assert IntervalSet([EMPTY, EMPTY, EMPTY]) == EMPTY
        assert IntervalSet([Open(0, 4), EMPTY]) == Open(0, 4)
        assert IntervalSet([Open(0, 4), Closed(2, 6)]) == OpenClosed(0, 6)
        assert IntervalSet([Open(None, 4), Closed(2, 6)]) == RightClosed(6)
        assert IntervalSet([Open(None, 4), Closed(2, 6), ClosedOpen(7, 9)]) == IntervalSet(
            [RightClosed(6), ClosedOpen(7, 9)]
        )
        assert_exact_match(
            IntervalSet([Open(None, 4), Closed(2, 6), OpenClosed(7, 9)]),
            OpenClosedSet([OpenClosed(None, 6), OpenClosed(7, 9)]),
        )


class TestIntervalCovariance:
    def test_interval(self) -> None:
        """
        type checkers should be satisfied result Interval[bool] is a valid Interval[int]
        since bools are ints
        """
        open: Open[int] = Open[bool](False, True)
        assert open
        closed: Closed[int] = Closed[bool](False, True)
        assert closed
        closed_open: ClosedOpen[int] = ClosedOpen[bool](False, True)
        assert closed_open
        open_closed: OpenClosed[int] = OpenClosed[bool](False, True)
        assert open_closed

    def test_interval_without_none(self) -> None:
        """
        type checkers should be satisfied that the start and stop of an Interval[int] are ints and not None
        """
        start_1: int = Open(1, 2).start
        assert start_1 == 1
        stop_1: int = Open(1, 2).stop
        assert stop_1 == 2

        start_2: int = Closed(1, 2).start
        assert start_2 == 1
        stop_2: int = Closed(1, 2).stop
        assert stop_2 == 2

        start_3: int = OpenClosed(1, 2).start
        assert start_3 == 1
        stop_3: int = OpenClosed(1, 2).stop
        assert stop_3 == 2

        start_4: int = ClosedOpen(1, 2).start
        assert start_4 == 1
        stop_4: int = ClosedOpen(1, 2).stop
        assert stop_4 == 2

    def test_interval_with_none(self) -> None:
        """
        type checkers should be satisfied that the start and stop of an Interval[int | None] should be optional ints
        """
        start_1: int | None = Open(None, 2).start
        assert start_1 is None
        stop_1: int | None = Open(None, 2).stop
        assert stop_1 == 2

        start_2: int | None = Closed(None, 2).start
        assert start_2 is None
        stop_2: int | None = Closed(None, 2).stop
        assert stop_2 == 2

        start_3: int | None = OpenClosed(None, 2).start
        assert start_3 is None
        stop_3: int | None = OpenClosed(None, 2).stop
        assert stop_3 == 2

        start_4: int | None = ClosedOpen(None, 2).start
        assert start_4 is None
        stop_4: int | None = ClosedOpen(None, 2).stop
        assert stop_4 == 2

    def test_half_bounded_interval(self) -> None:
        """
        type checkers should be satisfied that intervals with "missing" bounds are allowed
        as bounded intervals with None
        """
        open_left: Open[int | None] = LeftOpen(0)
        assert open_left
        open_right: Open[int | None] = RightOpen(0)
        assert open_right
        open_all: Open[int | None] = UNBOUNDED
        assert open_all

        closed_left: Closed[int | None] = LeftClosed(0)
        assert closed_left
        closed_right: Closed[int | None] = RightClosed(0)
        assert closed_right
        closed_all: Closed[int | None] = UNBOUNDED
        assert closed_all

        open_closed_left: OpenClosed[int | None] = LeftOpen(0)
        assert open_closed_left
        open_closed_right: OpenClosed[int | None] = RightClosed(0)
        assert open_closed_right
        open_closed_all: OpenClosed[int | None] = UNBOUNDED
        assert open_closed_all

        closed_open_left: ClosedOpen[int | None] = RightOpen(0)
        assert closed_open_left
        closed_open_right: ClosedOpen[int | None] = RightOpen(0)
        assert closed_open_right
        closed_open_all: ClosedOpen[int | None] = UNBOUNDED
        assert closed_open_all

    def test_interval_set(self) -> None:
        """
        type checkers should be satisfied result IntervalSet[int] is a valid IntervalSet[int | float]
        since ints are ints | floats
        """
        open: OpenSet[int | float] = OpenSet[int]((Open(0, 1), Open(2, 3)))
        assert open
        closed: ClosedSet[int | float] = ClosedSet[int]((Closed(0, 1), Closed(2, 3)))
        assert closed
        closed_open: ClosedOpenSet[int | float] = ClosedOpenSet[int]((ClosedOpen(0, 1), ClosedOpen(2, 3)))
        assert closed_open
        open_closed: OpenClosedSet[int | float] = OpenClosedSet[int]((OpenClosed(0, 1), OpenClosed(2, 3)))
        assert open_closed
        interval_set: IntervalSet[int | float] = IntervalSet[int]((Open(0, 1), Open(2, 3)))
        assert interval_set


class TestIntervalOrEmpty:
    def test_interval_reversed(self) -> None:
        assert Open.or_empty(1, 0) == EMPTY
        assert Closed.or_empty(1, 0) == EMPTY
        assert OpenClosed.or_empty(1, 0) == EMPTY
        assert ClosedOpen.or_empty(1, 0) == EMPTY

    def test_interval_reversed_exact_match(self) -> None:
        assert_exact_match(Open.or_empty(1, 0), ~Closed(None, None))
        assert_exact_match(Closed.or_empty(1, 0), ~Open(None, None))
        assert_exact_match(OpenClosed.or_empty(1, 0), ~OpenClosed(None, None))
        assert_exact_match(ClosedOpen.or_empty(1, 0), ~ClosedOpen(None, None))

    def test_interval(self) -> None:
        assert_exact_match(Open.or_empty(0, 1), Open(0, 1))
        assert_exact_match(Closed.or_empty(0, 1), Closed(0, 1))
        assert_exact_match(OpenClosed.or_empty(0, 1), OpenClosed(0, 1))
        assert_exact_match(ClosedOpen.or_empty(0, 1), ClosedOpen(0, 1))


class TestIntervalEquals:
    def test_interval(self, interval_class: type[IntervalType[int]]) -> None:
        assert interval_class(0, 1) == interval_class(0, 1)

    def test_interval_unbounded(self) -> None:
        assert Open(None, 0) == ClosedOpen(None, 0)
        assert Closed(None, 0) == OpenClosed(None, 0)
        assert Open(0, None) == OpenClosed(0, None)
        assert Closed(0, None) == ClosedOpen(0, None)
        assert Open(None, None) == ClosedOpen(None, None)

    def test_interval_set(self) -> None:
        assert OpenSet((Open(0, 1), Open(2, 3))) == OpenSet((Open(0, 1), Open(2, 3)))
        assert ClosedSet((Closed(0, 1), Closed(2, 3))) == ClosedSet((Closed(0, 1), Closed(2, 3)))
        assert ClosedOpenSet((ClosedOpen(0, 1), ClosedOpen(2, 3))) == ClosedOpenSet(
            (ClosedOpen(0, 1), ClosedOpen(2, 3))
        )
        assert OpenClosedSet((OpenClosed(0, 1), OpenClosed(2, 3))) == OpenClosedSet(
            (OpenClosed(0, 1), OpenClosed(2, 3))
        )
        assert IntervalSet((Open(0, 1), Open(2, 3))) == IntervalSet((Open(0, 1), Open(2, 3)))


class TestIntervalHash:
    def test_interval(self, interval_class: type[IntervalType[int]]) -> None:
        assert hash(interval_class(0, 1)) == hash(interval_class(0, 1))

    def test_interval_set(self) -> None:
        assert hash(OpenSet((Open(0, 1), Open(2, 3)))) == hash(OpenSet((Open(0, 1), Open(2, 3))))
        assert hash(ClosedSet((Closed(0, 1), Closed(2, 3)))) == hash(ClosedSet((Closed(0, 1), Closed(2, 3))))
        assert hash(ClosedOpenSet((ClosedOpen(0, 1), ClosedOpen(2, 3)))) == hash(
            ClosedOpenSet((ClosedOpen(0, 1), ClosedOpen(2, 3)))
        )
        assert hash(OpenClosedSet((OpenClosed(0, 1), OpenClosed(2, 3)))) == hash(
            OpenClosedSet((OpenClosed(0, 1), OpenClosed(2, 3)))
        )
        assert hash(IntervalSet((Open(0, 1), Open(2, 3)))) == hash(IntervalSet((Open(0, 1), Open(2, 3))))


class TestIntervalLen:
    def test_empty(self) -> None:
        assert len(EMPTY) == 0

    def test_interval(self, interval_class: type[IntervalType[int | None]]) -> None:
        assert len(interval_class(0, 1)) == 1
        assert len(interval_class(None, 0)) == 1
        assert len(interval_class(0, None)) == 1
        assert len(interval_class(None, None)) == 1

    def test_interval_set_two(self) -> None:
        assert len(OpenSet([Open(0, 1), Open(2, 3)])) == 2
        assert len(ClosedSet([Closed(0, 1), Closed(2, 3)])) == 2
        assert len(ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])) == 2
        assert len(OpenClosedSet([OpenClosed(0, 1), OpenClosed(2, 3)])) == 2
        assert len(IntervalSet([Open(0, 1), Open(2, 3)])) == 2

    def test_interval_set_three(self) -> None:
        assert len(OpenSet([Open(0, 1), Open(2, 3), Open(4, 5)])) == 3
        assert len(ClosedSet([Closed(0, 1), Closed(2, 3), Closed(4, 5)])) == 3
        assert len(ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3), ClosedOpen(4, 5)])) == 3
        assert len(OpenClosedSet([OpenClosed(0, 1), OpenClosed(2, 3), OpenClosed(4, 5)])) == 3
        assert len(IntervalSet([Open(0, 1), Open(2, 3), Open(4, 5)])) == 3

    def test_interval_set_three_unbounded(self) -> None:
        assert len(OpenSet([Open(0, 1), Open(2, 3), Open(4, None)])) == 3
        assert len(ClosedSet([Closed(0, 1), Closed(2, 3), Closed(4, None)])) == 3
        assert len(ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3), ClosedOpen(4, None)])) == 3
        assert len(OpenClosedSet([OpenClosed(0, 1), OpenClosed(2, 3), OpenClosed(4, None)])) == 3
        assert len(IntervalSet([Open(0, 1), Open(2, 3), Open(4, None)])) == 3


class TestIntervalBool:
    def test_empty(self) -> None:
        assert not EMPTY

    def test_interval(self, interval_class: type[IntervalType[int | None]]) -> None:
        assert interval_class(0, 1)
        assert interval_class(None, 0)
        assert interval_class(0, None)
        assert interval_class(None, None)

    def test_interval_set_two(self) -> None:
        assert OpenSet([Open(0, 1), Open(2, 3)])
        assert ClosedSet([Closed(0, 1), Closed(2, 3)])
        assert ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])
        assert OpenClosedSet([OpenClosed(0, 1), OpenClosed(2, 3)])
        assert IntervalSet([Open(0, 1), Open(2, 3)])


class TestIntervalIntervals:
    def test_empty(self) -> None:
        assert EMPTY.intervals == ()

    def test_interval(self, interval_class: type[IntervalType[int]]) -> None:
        assert interval_class(1, 2).intervals == (interval_class(1, 2),)

    def test_interval_set(self) -> None:
        assert IntervalSet([Open(0, 1), Closed(2, 3), Open(4, 5)]).intervals == (Open(0, 1), Closed(2, 3), Open(4, 5))

    def test_interval_set_unbounded(self) -> None:
        assert IntervalSet([Open(None, 1), Closed(2, 3), Open(4, None)]).intervals == (
            RightOpen(1),
            Closed(2, 3),
            LeftOpen(4),
        )


class TestIntervalContains:
    def test_empty(self) -> None:
        assert 1 not in EMPTY
        assert "a" not in EMPTY
        assert object() not in EMPTY
        assert None not in EMPTY

    def test_interval(self) -> None:
        assert 0 not in Open(1, 3)
        assert 1 not in Open(1, 3)
        assert 2 in Open(1, 3)
        assert 3 not in Open(1, 3)
        assert 4 not in Open(1, 3)

        assert 0 not in Closed(1, 3)
        assert 1 in Closed(1, 3)
        assert 2 in Closed(1, 3)
        assert 3 in Closed(1, 3)
        assert 4 not in Closed(1, 3)

        assert 0 not in OpenClosed(1, 3)
        assert 1 not in OpenClosed(1, 3)
        assert 2 in OpenClosed(1, 3)
        assert 3 in OpenClosed(1, 3)
        assert 4 not in OpenClosed(1, 3)

        assert 0 not in ClosedOpen(1, 3)
        assert 1 in ClosedOpen(1, 3)
        assert 2 in ClosedOpen(1, 3)
        assert 3 not in ClosedOpen(1, 3)
        assert 4 not in ClosedOpen(1, 3)

    def test_interval_zero_length(self) -> None:
        assert 0 not in Closed(1, 1)
        assert 1 in Closed(1, 1)
        assert 2 not in Closed(1, 1)

    def test_interval_different_types(self) -> None:
        assert 2.718281828 in Open(1, 3)
        assert "a" not in Open(1, 3)
        assert object() not in Open(1, 3)
        assert None not in Open(1, 3)

    def test_interval_unbounded(self) -> None:
        assert 5 in Open(None, 10)
        assert 10 not in Open(None, 10)
        assert 15 not in Open(None, 10)
        assert 5 not in Open(10, None)
        assert 10 not in Open(10, None)
        assert 15 in Open(10, None)
        assert 5 in Open(None, None)

    def test_interval_set(self) -> None:
        assert 0 not in (Open(1, 3) | Closed(5, 7))
        assert 1 not in (Open(1, 3) | Closed(5, 7))
        assert 2 in (Open(1, 3) | Closed(5, 7))
        assert 3 not in (Open(1, 3) | Closed(5, 7))
        assert 4 not in (Open(1, 3) | Closed(5, 7))
        assert 5 in (Open(1, 3) | Closed(5, 7))
        assert 6 in (Open(1, 3) | Closed(5, 7))
        assert 7 in (Open(1, 3) | Closed(5, 7))
        assert 8 not in (Open(1, 3) | Closed(5, 7))

        assert 0 in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 1 in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 2 not in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 3 in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 4 in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 5 not in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 6 not in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 7 not in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))
        assert 8 in (Closed(None, 1) | ClosedOpen(3, 5) | Open(7, None))


class TestIntervalIsDisjoint:
    def test_empty(self) -> None:
        assert EMPTY.isdisjoint()
        assert EMPTY.isdisjoint(EMPTY)
        assert EMPTY.isdisjoint(EMPTY, EMPTY)
        assert EMPTY.isdisjoint(Open(0, 1), Open(2, 3))
        assert EMPTY.isdisjoint(Open(None, None))

    def test_interval(self) -> None:
        assert Open(1, 2).isdisjoint()
        assert Open(1, 2).isdisjoint(EMPTY)
        assert Open(1, 2).isdisjoint(Open(3, 4))
        assert Open(1, 2).isdisjoint(Open(3, 4), Open(5, 6))
        assert Open(1, 2).isdisjoint(Open(2, 3), Open(3, 4))
        assert not Open(1, 3).isdisjoint(Open(2, 4))
        assert not Open(1, 2).isdisjoint(Open(3, 5), Open(4, 6))
        assert not Closed(1, 2).isdisjoint(Closed(2, 3))
        assert Closed(1, 2).isdisjoint(Open(2, 3))

    def test_interval_unbounded(self) -> None:
        assert Open(None, 0).isdisjoint(Open(1, None))
        assert not Open(None, 0).isdisjoint(Open(None, 1))
        assert not Open(None, None).isdisjoint(Open(0, 1))

    def test_interval_set(self) -> None:
        assert (Open(1, 2) | Open(3, 4)).isdisjoint()
        assert (Open(1, 2) | Open(3, 4)).isdisjoint(EMPTY)
        assert (Open(1, 2) | Open(5, 6)).isdisjoint(Open(3, 4))
        assert (Open(1, 2) | Open(5, 6)).isdisjoint(Open(3, 4) | Open(7, 8))
        assert (Open(1, 2) | Open(5, 6)).isdisjoint(Open(3, 4) | Open(7, 8), Open(2, 3) | Open(6, 7))
        assert not (Open(1, 2) | Open(5, 6)).isdisjoint(Open(3, 4) | Open(7, 8), Open(1, 3) | Open(6, 7))
        assert not (Open(1, 2) | Open(5, 6)).isdisjoint(Open(3, 4) | ClosedOpen(7, 8), Open(2, 3) | OpenClosed(6, 7))


class TestIntervalIsSubset:
    def test_empty(self) -> None:
        assert EMPTY <= EMPTY
        assert EMPTY <= Open(0, 1)

    def test_interval(self) -> None:
        assert Open(1, 2) <= Open(0, 3)
        assert Open(1, 2) <= Open(1, 2)
        assert Open(1, 2) <= Closed(1, 2)
        assert not Closed(1, 2) <= Open(1, 2)

    def test_interval_unbounded(self) -> None:
        assert Open(1, 2) <= Open(None, 3)
        assert Open(None, 2) <= Open(None, 3)
        assert not Open(None, 2) <= Open(0, 3)
        assert Open(None, 2) <= Open(None, None)

    def test_interval_set(self) -> None:
        assert Open(1, 2) <= Closed(1, 2) | Open(3, 4)
        assert Open(1, 2) | Open(3, 4) <= Closed(1, 2) | Open(3, 4)
        assert Open(1, 2) | Open(3, 4) <= Closed(None, 2) | Open(3, 4)
        assert not Open(1, 2) | Open(3, 5) <= Closed(None, 2) | Open(3, 4)


class TestIntervalIsProperSubset:
    def test_empty(self) -> None:
        assert not EMPTY < EMPTY
        assert EMPTY < Open(0, 1)

    def test_interval(self) -> None:
        assert Open(1, 2) < Open(0, 3)
        assert not Open(1, 2) < Open(1, 2)
        assert Open(1, 2) < Closed(1, 2)
        assert not Closed(1, 2) < Open(1, 2)

    def test_interval_unbounded(self) -> None:
        assert Open(1, 2) < Open(None, 3)
        assert Open(None, 2) < Open(None, 3)
        assert not Open(None, 2) < Open(None, 2)
        assert not Open(None, 2) < Open(0, 3)
        assert Open(None, 2) < Open(None, None)

    def test_interval_set(self) -> None:
        assert Open(1, 2) < Closed(1, 2) | Open(3, 4)
        assert Open(1, 2) | Open(3, 4) < Closed(1, 2) | Open(3, 4)
        assert not Open(1, 2) | Open(3, 4) < Open(1, 2) | Open(3, 4)
        assert Open(1, 2) | Open(3, 4) < Closed(None, 2) | Open(3, 4)
        assert not Open(1, 2) | Open(3, 5) < Closed(None, 2) | Open(3, 4)


class TestIntervalIsSuperset:
    def test_empty(self) -> None:
        assert EMPTY >= EMPTY
        assert Open(0, 1) >= EMPTY

    def test_interval(self) -> None:
        assert Open(0, 3) >= Open(1, 2)
        assert Open(1, 2) >= Open(1, 2)
        assert Closed(1, 2) >= Open(1, 2)
        assert not Open(1, 2) >= Closed(1, 2)

    def test_interval_unbounded(self) -> None:
        assert Open(None, 3) >= Open(1, 2)
        assert Open(None, 3) >= Open(None, 2)
        assert not Open(0, 3) >= Open(None, 2)
        assert Open(None, None) >= Open(None, 2)

    def test_interval_set(self) -> None:
        assert Closed(1, 2) | Open(3, 4) >= Open(1, 2)
        assert Closed(1, 2) | Open(3, 4) >= Open(1, 2) | Open(3, 4)
        assert Closed(None, 2) | Open(3, 4) >= Open(1, 2) | Open(3, 4)
        assert not Closed(None, 2) | Open(3, 4) >= Open(1, 2) | Open(3, 5)


class TestIntervalIsProperSuperset:
    def test_empty(self) -> None:
        assert not EMPTY > EMPTY
        assert Open(0, 1) > EMPTY

    def test_interval(self) -> None:
        assert Open(0, 3) > Open(1, 2)
        assert not Open(1, 2) > Open(1, 2)
        assert Closed(1, 2) > Open(1, 2)
        assert not Open(1, 2) > Closed(1, 2)

    def test_interval_unbounded(self) -> None:
        assert Open(None, 3) > Open(1, 2)
        assert Open(None, 3) > Open(None, 2)
        assert not Open(None, 2) > Open(None, 2)
        assert not Open(0, 3) > Open(None, 2)
        assert Open(None, None) > Open(None, 2)

    def test_interval_set(self) -> None:
        assert Closed(1, 2) | Open(3, 4) > Open(1, 2)
        assert Closed(1, 2) | Open(3, 4) > Open(1, 2) | Open(3, 4)
        assert not Open(1, 2) | Open(3, 4) > Open(1, 2) | Open(3, 4)
        assert Closed(None, 2) | Open(3, 4) > Open(1, 2) | Open(3, 4)
        assert not Closed(None, 2) | Open(3, 4) > Open(1, 2) | Open(3, 5)


class TestIntervalUnion:
    def test_empty(self) -> None:
        assert EMPTY | EMPTY == EMPTY
        assert Open(0, 1) | EMPTY == Open(0, 1)
        assert Closed(0, 2) | EMPTY == Closed(0, 2)
        assert Closed(0, 2) | Open(4, 6) | EMPTY == Closed(0, 2) | Open(4, 6)

    def test_interval(self) -> None:
        assert Open(0, 1) | Open(2, 3) == OpenSet([Open(0, 1), Open(2, 3)])
        assert Open(0, 1) | Open(1, 2) == OpenSet([Open(0, 1), Open(1, 2)])
        assert Open(0, 1) | ClosedOpen(1, 2) == Open(0, 2)
        assert Open(0, 2) | Open(1, 3) == Open(0, 3)
        assert Open(0, 3) | Open(1, 2) == Open(0, 3)
        assert Open(0, 3) | Open(1, 3) == Open(0, 3)
        assert Open(0, 3) | OpenClosed(1, 3) == OpenClosed(0, 3)

    def test_interval_unbounded(self) -> None:
        assert Open(None, None) | Open(2, 3) == Open(None, None)
        assert Open(None, None) | Open(1, 2) == Open(None, None)
        assert Open(None, None) | ClosedOpen(1, 2) == Open(None, None)
        assert Open(None, None) | Open(1, 3) == Open(None, None)
        assert Open(None, None) | Open(1, 2) == Open(None, None)
        assert Open(None, None) | Open(1, 3) == Open(None, None)
        assert Open(None, None) | OpenClosed(1, 3) == Open(None, None)

    def test_interval_set(self) -> None:
        assert IntervalSet([Open(0, 1), Open(4, 5)]) | IntervalSet([Open(2, 3), Open(6, 7)]) == IntervalSet(
            [Open(0, 1), Open(2, 3), Open(4, 5), Open(6, 7)]
        )
        assert IntervalSet([Open(0, 2), Open(3, 6)]) | IntervalSet([Open(1, 4), Open(5, 7)]) == Open(0, 7)
        assert IntervalSet([Closed(0, 2), Closed(3, 6)]) | IntervalSet([Closed(1, 4), Closed(5, 7)]) == Closed(0, 7)

    def test_multiple_arguments(self) -> None:
        assert Closed(0, 2).union(Open(1, 3), Open(4, 6), Closed(5, 7)) == IntervalSet(
            [ClosedOpen(0, 3), OpenClosed(4, 7)]
        )


class TestIntervalIntersection:
    def test_empty(self) -> None:
        assert EMPTY & EMPTY == EMPTY
        assert Open(0, 1) & EMPTY == EMPTY
        assert Closed(0, 2) & EMPTY == EMPTY
        assert Closed(0, 3) & Open(2, 4) & EMPTY == EMPTY

    def test_interval(self) -> None:
        assert Open(0, 1) & Open(2, 3) == EMPTY
        assert Open(0, 1) & Open(1, 2) == EMPTY
        assert OpenClosed(0, 1) & ClosedOpen(1, 2) == Closed(1, 1)
        assert Open(0, 2) & Open(1, 3) == Open(1, 2)
        assert Open(0, 3) & Open(1, 2) == Open(1, 2)
        assert Open(0, 3) & Open(1, 3) == Open(1, 3)
        assert Open(0, 3) & OpenClosed(1, 3) == Open(1, 3)

    def test_interval_unbounded(self) -> None:
        assert Open(None, None) & Open(2, 3) == Open(2, 3)
        assert Open(None, None) & Open(1, 2) == Open(1, 2)
        assert Open(None, None) & ClosedOpen(1, 2) == ClosedOpen(1, 2)
        assert Open(None, None) & Open(1, 3) == Open(1, 3)
        assert Open(None, None) & Open(1, 2) == Open(1, 2)
        assert Open(None, None) & Open(1, 3) == Open(1, 3)
        assert Open(None, None) & OpenClosed(1, 3) == OpenClosed(1, 3)

    def test_interval_set(self) -> None:
        assert IntervalSet([Open(0, 1), Open(4, 5)]) & IntervalSet([Open(2, 3), Open(6, 7)]) == EMPTY
        assert IntervalSet([Open(0, 2), Open(3, 6)]) & IntervalSet([Open(1, 4), Open(5, 7)]) == IntervalSet(
            [Open(1, 2), Open(3, 4), Open(5, 6)]
        )
        assert IntervalSet([Closed(0, 2), Closed(3, 6)]) & IntervalSet([Closed(1, 4), Closed(5, 7)]) == IntervalSet(
            [Closed(1, 2), Closed(3, 4), Closed(5, 6)]
        )

    def test_multiple_arguments(self) -> None:
        assert Closed(0, 10).intersection(Open(None, 6), Open(4, 7), Closed(2, 100)) == Open(4, 6)

    def test_type_narrowing(self) -> None:
        """
        type checkers should be satisfied that an intersection between and interval of [int | None] and of [int]
        should always return an interval of [int]
        """
        a: IntervalSet[int] = Open(None, 10) & Open(0, 100)
        assert a == Open(0, 10)

        # ty does not understand the reversed situation, but the other checkers do:

        b: IntervalSet[int] = Open(0, 100) & Open(None, 10)  # type:ignore[ty:invalid-assignment,unused-ignore]
        assert b == Open(0, 10)

        c: IntervalSet[int] = Open(None, 10).intersection(Closed(0, 100), Open(-50, 50))
        assert c == ClosedOpen(0, 10)

        # ty does not understand the reversed situation, but the other checkers do:

        d: IntervalSet[int] = Closed(0, 100).intersection(Open(None, 10), Open(-50, 50))  # type:ignore[ty:invalid-assignment,unused-ignore]
        assert d == ClosedOpen(0, 10)


class TestIntervalDifference:
    def test_empty(self) -> None:
        assert EMPTY - EMPTY == EMPTY
        assert Open(0, 1) - EMPTY == Open(0, 1)
        assert Open(0, None) - EMPTY == Open(0, None)
        assert Open(None, 0) - EMPTY == Open(None, 0)
        assert Open(None, None) - EMPTY == Open(None, None)
        assert EMPTY - Open(0, 1) == EMPTY
        assert EMPTY - Open(0, None) == EMPTY
        assert EMPTY - Open(None, 0) == EMPTY
        assert EMPTY - Open(None, None) == EMPTY

    def test_match_intersection_of_complement(self) -> None:
        assert_exact_match(Open(0, 1) - EMPTY, Open(0, 1) & ~EMPTY)
        assert_exact_match(Open(0, 1) - EMPTY, Open(0, 1) & ~EMPTY)
        assert_exact_match(Open(0, None) - EMPTY, Open(0, None) & ~EMPTY)
        assert_exact_match(Open(None, 0) - EMPTY, Open(None, 0) & ~EMPTY)
        assert_exact_match(Open(None, None) - EMPTY, Open(None, None) & ~EMPTY)
        assert_exact_match(EMPTY - Open(0, 1), EMPTY & ~Open(0, 1))
        assert_exact_match(EMPTY - Open(0, None), EMPTY & ~Open(0, None))
        assert_exact_match(EMPTY - Open(None, 0), EMPTY & ~Open(None, 0))
        assert_exact_match(EMPTY - Open(None, None), EMPTY & ~Open(None, None))


class TestIntervalComplement:
    def test_empty(self) -> None:
        assert_exact_match(~EMPTY, Open(None, None))
        assert_exact_match(EMPTY, ~Open(None, None))

    def test_interval(self) -> None:
        assert_exact_match(~Open(0, 1), Closed(None, 0) | Closed(1, None))
        assert_exact_match(Open(0, 1), ~(Closed(None, 0) | Closed(1, None)))
        assert_exact_match(~Closed(0, 1), Open(None, 0) | Open(1, None))
        assert_exact_match(Closed(0, 1), ~(Open(None, 0) | Open(1, None)))
        assert_exact_match(~OpenClosed(0, 1), OpenClosed(None, 0) | OpenClosed(1, None))
        assert_exact_match(OpenClosed(0, 1), ~(OpenClosed(None, 0) | OpenClosed(1, None)))
        assert_exact_match(~ClosedOpen(0, 1), ClosedOpen(None, 0) | ClosedOpen(1, None))
        assert_exact_match(ClosedOpen(0, 1), ~(ClosedOpen(None, 0) | ClosedOpen(1, None)))

    def test_interval_unbound(self) -> None:
        assert_exact_match(~Open(None, 0), Closed(0, None))
        assert_exact_match(Open(None, 0), ~Closed(0, None))
        assert_exact_match(~Closed(None, 0), Open(0, None))
        assert_exact_match(Closed(None, 0), ~Open(0, None))
        assert_exact_match(~OpenClosed(None, 0), OpenClosed(0, None))
        assert_exact_match(OpenClosed(None, 0), ~OpenClosed(0, None))
        assert_exact_match(~ClosedOpen(None, 0), ClosedOpen(0, None))
        assert_exact_match(ClosedOpen(None, 0), ~ClosedOpen(0, None))

    def test_interval_infinite(self) -> None:
        assert_exact_match(~UNBOUNDED, EMPTY)
        assert_exact_match(~EMPTY, UNBOUNDED)

    def test_interval_set(self) -> None:
        assert ~(Open(0, 1) | Open(2, 3) | Open(4, 5)) == Closed(None, 0) | Closed(1, 2) | Closed(3, 4) | Closed(
            5, None
        )
        assert Open(0, 1) | Open(2, 3) | Open(4, 5) == ~(
            Closed(None, 0) | Closed(1, 2) | Closed(3, 4) | Closed(5, None)
        )
        assert ~(Closed(0, 1) | Closed(2, 3) | Closed(4, 5)) == Open(None, 0) | Open(1, 2) | Open(3, 4) | Open(5, None)
        assert Closed(0, 1) | Closed(2, 3) | Closed(4, 5) == ~(Open(None, 0) | Open(1, 2) | Open(3, 4) | Open(5, None))
        assert ~(OpenClosed(0, 1) | OpenClosed(2, 3) | OpenClosed(4, 5)) == OpenClosed(None, 0) | OpenClosed(
            1, 2
        ) | OpenClosed(3, 4) | OpenClosed(5, None)
        assert OpenClosed(0, 1) | OpenClosed(2, 3) | OpenClosed(4, 5) == ~(
            OpenClosed(None, 0) | OpenClosed(1, 2) | OpenClosed(3, 4) | OpenClosed(5, None)
        )
        assert ~(ClosedOpen(0, 1) | ClosedOpen(2, 3) | ClosedOpen(4, 5)) == ClosedOpen(None, 0) | ClosedOpen(
            1, 2
        ) | ClosedOpen(3, 4) | ClosedOpen(5, None)
        assert ClosedOpen(0, 1) | ClosedOpen(2, 3) | ClosedOpen(4, 5) == ~(
            ClosedOpen(None, 0) | ClosedOpen(1, 2) | ClosedOpen(3, 4) | ClosedOpen(5, None)
        )


class TestIntervalGetItem:
    def test_index(self) -> None:
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[0] == Open(0, 1)
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[1] == Closed(2, 3)
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[2] == OpenClosed(4, 5)
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[-3] == Open(0, 1)
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[-2] == Closed(2, 3)
        assert (Open(0, 1) | Closed(2, 3) | OpenClosed(4, 5))[-1] == OpenClosed(4, 5)
        assert Open(0, 1)[0] == Open(0, 1)
        assert Open(0, 1)[-1] == Open(0, 1)

    def test_slice(self) -> None:
        a = Open(0, 1) | OpenClosed(2, 3) | ClosedOpen(4, 5) | Closed(6, 7) | Open(8, 9)

        assert a[:] == a[0:] == a[:6] == a[:10] == a
        assert a[1:] == OpenClosed(2, 3) | ClosedOpen(4, 5) | Closed(6, 7) | Open(8, 9)
        assert a[2:] == ClosedOpen(4, 5) | Closed(6, 7) | Open(8, 9)
        assert a[-1:] == Open(8, 9)
        assert a[-2:] == Closed(6, 7) | Open(8, 9)
        assert a[1:4] == OpenClosed(2, 3) | ClosedOpen(4, 5) | Closed(6, 7)
        assert a[2:10] == ClosedOpen(4, 5) | Closed(6, 7) | Open(8, 9)
        assert a[::2] == Open(0, 1) | ClosedOpen(4, 5) | Open(8, 9)
        assert a[1::2] == OpenClosed(2, 3) | Closed(6, 7)
        assert a[::-2] == Open(0, 1) | ClosedOpen(4, 5) | Open(8, 9)
        assert a[::-3] == OpenClosed(2, 3) | Open(8, 9)
        assert a[-2::-2] == OpenClosed(2, 3) | Closed(6, 7)
        assert a[-2:-4:-2] == Closed(6, 7)
        assert a[::-1] == a
        assert a[:-3:-1] == Closed(6, 7) | Open(8, 9)
        assert a[:-4:-2] == ClosedOpen(4, 5) | Open(8, 9)


class TestIntervalRepr:
    def test_empty(self) -> None:
        assert repr(EMPTY) == "Empty()"

    def test_interval(self) -> None:
        assert repr(Open(0, 1)) == "Open(0, 1)"
        assert repr(Closed(0, 1)) == "Closed(0, 1)"
        assert repr(OpenClosed(0, 1)) == "OpenClosed(0, 1)"
        assert repr(ClosedOpen(0, 1)) == "ClosedOpen(0, 1)"

    def test_interval_half_bounded(self) -> None:
        assert repr(LeftOpen(1)) == "LeftOpen(1)"
        assert repr(LeftClosed(1)) == "LeftClosed(1)"
        assert repr(RightOpen(1)) == "RightOpen(1)"
        assert repr(RightClosed(1)) == "RightClosed(1)"

    def test_interval_unbounded(self) -> None:
        assert repr(Unbounded()) == "Unbounded()"

    def test_interval_set(self) -> None:
        assert (
            repr(IntervalSet([ClosedOpen(0, 1), ClosedOpen(2, 3)]))
            == "ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])"
        )

    def test_interval_set_unbound(self) -> None:
        assert (
            repr(IntervalSet([ClosedOpen(None, 1), ClosedOpen(2, 3)]))
            == "ClosedOpenSet([RightOpen(1), ClosedOpen(2, 3)])"
        )
        assert (
            repr(IntervalSet([ClosedOpen(0, 1), ClosedOpen(2, None)]))
            == "ClosedOpenSet([ClosedOpen(0, 1), LeftClosed(2)])"
        )


class TestIntervalStr:
    def test_empty(self) -> None:
        assert str(EMPTY) == "⟨;⟩"

    def test_interval(self) -> None:
        assert str(Open(0, 1)) == "(0 ; 1)"
        assert str(Closed(0, 1)) == "[0 ; 1]"
        assert str(OpenClosed(0, 1)) == "(0 ; 1]"
        assert str(ClosedOpen(0, 1)) == "[0 ; 1)"

    def test_interval_unbounded(self) -> None:
        assert str(Open(None, 1)) == "⟨-inf ; 1)"
        assert str(Closed(None, 1)) == "⟨-inf ; 1]"
        assert str(OpenClosed(None, 1)) == "⟨-inf ; 1]"
        assert str(ClosedOpen(None, 1)) == "⟨-inf ; 1)"
        assert str(Open(0, None)) == "(0 ; +inf⟩"
        assert str(Closed(0, None)) == "[0 ; +inf⟩"
        assert str(OpenClosed(0, None)) == "(0 ; +inf⟩"
        assert str(ClosedOpen(0, None)) == "[0 ; +inf⟩"
        assert str(Open(None, None)) == "⟨-inf ; +inf⟩"
        assert str(Closed(None, None)) == "⟨-inf ; +inf⟩"
        assert str(OpenClosed(None, None)) == "⟨-inf ; +inf⟩"
        assert str(ClosedOpen(None, None)) == "⟨-inf ; +inf⟩"

    def test_interval_set(self) -> None:
        assert str(IntervalSet()) == "⟨;⟩"
        assert str(IntervalSet([Open(0, 1)])) == "(0 ; 1)"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3)])) == "(0 ; 1) | [2 ; 3]"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3), ClosedOpen(4, 5)])) == "(0 ; 1) | [2 ; 3] | [4 ; 5)"
        assert str(IntervalSet([Open(None, 1), Closed(2, 3), ClosedOpen(4, 5)])) == "⟨-inf ; 1) | [2 ; 3] | [4 ; 5)"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3), ClosedOpen(4, None)])) == "(0 ; 1) | [2 ; 3] | [4 ; +inf⟩"
        assert str(IntervalSet([Closed(0, 1), Open(2, 3), OpenClosed(4, None)])) == "[0 ; 1] | (2 ; 3) | (4 ; +inf⟩"
