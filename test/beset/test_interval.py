from typing import TypeVar

from pytest import raises

from beset import (
    EMPTY,
    Closed,
    ClosedOpen,
    ClosedOpenSet,
    ClosedSet,
    Empty,
    Interval,
    IntervalSet,
    Open,
    OpenClosed,
    OpenClosedSet,
    OpenSet,
    Sortable,
)

T = TypeVar("T", covariant=True, bound=Sortable | None)
IntervalType = Open[T] | Closed[T] | ClosedOpen[T] | OpenClosed[T]


def matches(x: IntervalSet[Sortable | None], y: IntervalSet[Sortable | None]) -> bool:
    return (
        type(x) is type(y)
        and x._odd == y._odd
        and x._left_sinister == y._left_sinister
        and x._bounds == y._bounds
        and x._right_sinister == y._right_sinister
    )


class TestIntervalCreation:
    def test_empty(self) -> None:
        assert type(Empty()) is Empty

    def test_interval_restricted(self, interval_class: type[IntervalType[int | None]]) -> None:
        assert type(interval_class(0, 1)) is interval_class
        assert type(interval_class(0, None)) is interval_class
        assert type(interval_class(None, 0)) is interval_class
        assert type(interval_class(None, None)) is interval_class

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
        assert IntervalSet([Open(None, 4), Closed(2, 6)]) == OpenClosed(None, 6)
        assert IntervalSet([Open(None, 4), Closed(2, 6), ClosedOpen(7, 9)]) == IntervalSet(
            [OpenClosed(None, 6), ClosedOpen(7, 9)]
        )
        assert matches(
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


class TestIntervalRepr:
    def test_empty(self) -> None:
        assert repr(EMPTY) == "Empty()"

    def test_interval(self) -> None:
        assert repr(Open(0, 1)) == "Open(0, 1)"
        assert repr(Closed(0, 1)) == "Closed(0, 1)"
        assert repr(OpenClosed(0, 1)) == "OpenClosed(0, 1)"
        assert repr(ClosedOpen(0, 1)) == "ClosedOpen(0, 1)"

    def test_interval_unbounded(self) -> None:
        assert repr(Open(None, 1)) == "Open(None, 1)"
        assert repr(Closed(None, 1)) == "Closed(None, 1)"
        assert repr(OpenClosed(None, 1)) == "OpenClosed(None, 1)"
        assert repr(ClosedOpen(None, 1)) == "ClosedOpen(None, 1)"
        assert repr(Open(0, None)) == "Open(0, None)"
        assert repr(Closed(0, None)) == "Closed(0, None)"
        assert repr(OpenClosed(0, None)) == "OpenClosed(0, None)"
        assert repr(ClosedOpen(0, None)) == "ClosedOpen(0, None)"
        assert repr(Open(None, None)) == "Open(None, None)"
        assert repr(Closed(None, None)) == "Closed(None, None)"
        assert repr(OpenClosed(None, None)) == "OpenClosed(None, None)"
        assert repr(ClosedOpen(None, None)) == "ClosedOpen(None, None)"

    def test_interval_set(self) -> None:
        assert (
            repr(IntervalSet([ClosedOpen(0, 1), ClosedOpen(2, 3)]))
            == "ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, 3)])"
        )

    def test_interval_set_unbound(self) -> None:
        assert (
            repr(IntervalSet([ClosedOpen(None, 1), ClosedOpen(2, 3)]))
            == "ClosedOpenSet([ClosedOpen(None, 1), ClosedOpen(2, 3)])"
        )
        assert (
            repr(IntervalSet([ClosedOpen(0, 1), ClosedOpen(2, None)]))
            == "ClosedOpenSet([ClosedOpen(0, 1), ClosedOpen(2, None)])"
        )


class TestIntervalStr:
    def test_empty(self) -> None:
        assert str(EMPTY) == "[;]"

    def test_interval(self) -> None:
        assert str(Open(0, 1)) == "(0 ; 1)"
        assert str(Closed(0, 1)) == "[0 ; 1]"
        assert str(OpenClosed(0, 1)) == "(0 ; 1]"
        assert str(ClosedOpen(0, 1)) == "[0 ; 1)"

    def test_interval_unbounded(self) -> None:
        assert str(Open(None, 1)) == "(-inf ; 1)"
        assert str(Closed(None, 1)) == "[-inf ; 1]"
        assert str(OpenClosed(None, 1)) == "(-inf ; 1]"
        assert str(ClosedOpen(None, 1)) == "[-inf ; 1)"
        assert str(Open(0, None)) == "(0 ; +inf)"
        assert str(Closed(0, None)) == "[0 ; +inf]"
        assert str(OpenClosed(0, None)) == "(0 ; +inf]"
        assert str(ClosedOpen(0, None)) == "[0 ; +inf)"
        assert str(Open(None, None)) == "(-inf ; +inf)"
        assert str(Closed(None, None)) == "[-inf ; +inf]"
        assert str(OpenClosed(None, None)) == "(-inf ; +inf]"
        assert str(ClosedOpen(None, None)) == "[-inf ; +inf)"

    def test_interval_set(self) -> None:
        assert str(IntervalSet()) == "[;]"
        assert str(IntervalSet([Open(0, 1)])) == "(0 ; 1)"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3)])) == "(0 ; 1) | [2 ; 3]"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3), ClosedOpen(4, 5)])) == "(0 ; 1) | [2 ; 3] | [4 ; 5)"
        assert str(IntervalSet([Open(None, 1), Closed(2, 3), ClosedOpen(4, 5)])) == "(-inf ; 1) | [2 ; 3] | [4 ; 5)"
        assert str(IntervalSet([Open(0, 1), Closed(2, 3), ClosedOpen(4, None)])) == "(0 ; 1) | [2 ; 3] | [4 ; +inf)"
        assert str(IntervalSet([Closed(0, 1), Open(2, 3), OpenClosed(4, None)])) == "[0 ; 1] | (2 ; 3) | (4 ; +inf]"
