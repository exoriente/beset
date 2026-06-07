from itertools import permutations
from typing import Any

from pytest import mark, raises

from beset import (
    EMPTY,
    INF,
    Closed,
    ClosedOpen,
    ConcreteInterval,
    InfinityTypes,
    Interval,
    IntervalSet,
    Open,
    OpenClosed,
)


def test_interval_immutable(
    interval_class: type[ConcreteInterval[int]],
) -> None:
    with raises(AttributeError):
        interval_class(0, 0).intervals = ()  # type:ignore[ty:invalid-assignment,unused-ignore,misc]

    with raises(AttributeError):
        interval_class(0, 0).start = 0  # type:ignore[ty:invalid-assignment,unused-ignore,misc]

    with raises(AttributeError):
        interval_class(0, 0).stop = 0  # type:ignore[ty:invalid-assignment,unused-ignore,misc]


def test_interval_instance_of_interval_set(
    interval_class: type[ConcreteInterval[int]],
) -> None:
    """
    type checkers should be satisfied an interval is an interval set
    """
    result: IntervalSet[int] = interval_class(0, 1)
    assert result


def test_interval_covariant() -> None:
    """
    type checkers should be satisfied result Interval[bool] is a valid IntervalSet[int]
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


@mark.parametrize("a,b", [(0, 1), (1, 2), ("a", "b"), ("b", "c")])
def test_interval_empty(a: int | str, b: int | str) -> None:
    assert Closed(b, a).empty()
    assert not Closed(b, b).empty()
    assert not Closed(a, b).empty()

    assert Open(b, a).empty()
    assert Open(b, b).empty()
    assert not Open(a, b).empty()

    assert ClosedOpen(b, a).empty()
    assert ClosedOpen(b, b).empty()
    assert not ClosedOpen(a, b).empty()

    assert OpenClosed(b, a).empty()
    assert OpenClosed(b, b).empty()
    assert not OpenClosed(a, b).empty()


def test_interval_empty_infinity(interval_class: type[ConcreteInterval[Any]]) -> None:
    assert interval_class(-INF, -INF).empty()
    assert interval_class(INF, INF).empty()


@mark.parametrize("a,b", [(0, 0), (1, 1), ("a", "a"), ("b", "b")])
def test_interval_eq_empty(a: int | str, b: int | str) -> None:
    assert Open(a, b) == Open(a, b)
    assert not Open(a, b) == Closed(a, b)
    assert Open(a, b) == ClosedOpen(a, b)
    assert Open(a, b) == OpenClosed(a, b)

    assert not Closed(a, b) == Open(a, b)
    assert Closed(a, b) == Closed(a, b)
    assert not Closed(a, b) == ClosedOpen(a, b)
    assert not Closed(a, b) == OpenClosed(a, b)

    assert ClosedOpen(a, b) == Open(a, b)
    assert not ClosedOpen(a, b) == Closed(a, b)
    assert ClosedOpen(a, b) == ClosedOpen(a, b)
    assert ClosedOpen(a, b) == OpenClosed(a, b)

    assert OpenClosed(a, b) == Open(a, b)
    assert not OpenClosed(a, b) == Closed(a, b)
    assert OpenClosed(a, b) == ClosedOpen(a, b)
    assert OpenClosed(a, b) == OpenClosed(a, b)


def test_interval_eq_empty_different_types(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
) -> None:
    assert interval_class_a(1, 0) == interval_class_b(2, 0)


@mark.parametrize("a,b", [(0, 1), (1, 2), ("a", "b"), ("b", "c")])
def test_interval_eq_not_empty(a: int | str, b: int | str) -> None:
    assert Open(a, b) == Open(a, b)
    assert not Open(a, b) == Closed(a, b)
    assert not Open(a, b) == ClosedOpen(a, b)
    assert not Open(a, b) == OpenClosed(a, b)

    assert not Closed(a, b) == Open(a, b)
    assert Closed(a, b) == Closed(a, b)
    assert not Closed(a, b) == ClosedOpen(a, b)
    assert not Closed(a, b) == OpenClosed(a, b)

    assert not ClosedOpen(a, b) == Open(a, b)
    assert not ClosedOpen(a, b) == Closed(a, b)
    assert ClosedOpen(a, b) == ClosedOpen(a, b)
    assert not ClosedOpen(a, b) == OpenClosed(a, b)

    assert not OpenClosed(a, b) == Open(a, b)
    assert not OpenClosed(a, b) == Closed(a, b)
    assert not OpenClosed(a, b) == ClosedOpen(a, b)
    assert OpenClosed(a, b) == OpenClosed(a, b)


def test_interval_hash_unbounded_different_types(
    interval_class_a: type[ConcreteInterval[Any]],
    interval_class_b: type[ConcreteInterval[Any]],
) -> None:
    assert interval_class_a(-INF, INF) == interval_class_b(-INF, INF)


def test_interval_eq_different_type() -> None:
    assert Open(1, 2) != Open("1", "2")


@mark.parametrize("a,b", [(0, 0), (1, 1), ("a", "a"), ("b", "b")])
def test_interval_hash_empty(a: int | str, b: int | str) -> None:
    assert hash(Open(a, b)) == hash(Open(a, b))
    assert not hash(Open(a, b)) == hash(Closed(a, b))
    assert hash(Open(a, b)) == hash(ClosedOpen(a, b))
    assert hash(Open(a, b)) == hash(OpenClosed(a, b))

    assert not hash(Closed(a, b)) == hash(Open(a, b))
    assert hash(Closed(a, b)) == hash(Closed(a, b))
    assert not hash(Closed(a, b)) == hash(ClosedOpen(a, b))
    assert not hash(Closed(a, b)) == hash(OpenClosed(a, b))

    assert hash(ClosedOpen(a, b)) == hash(Open(a, b))
    assert not hash(ClosedOpen(a, b)) == hash(Closed(a, b))
    assert hash(ClosedOpen(a, b)) == hash(ClosedOpen(a, b))
    assert hash(ClosedOpen(a, b)) == hash(OpenClosed(a, b))

    assert hash(OpenClosed(a, b)) == hash(Open(a, b))
    assert not hash(OpenClosed(a, b)) == hash(Closed(a, b))
    assert hash(OpenClosed(a, b)) == hash(ClosedOpen(a, b))
    assert hash(OpenClosed(a, b)) == hash(OpenClosed(a, b))


def test_interval_hash_empty_different_types(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
) -> None:
    assert hash(interval_class_a(1, 0)) == hash(interval_class_b(2, 0))


@mark.parametrize("a,b", [(0, 1), (1, 2), ("a", "b"), ("b", "c")])
def test_interval_hash_not_empty(a: int | str, b: int | str) -> None:
    assert hash(Open(a, b)) == hash(Open(a, b))
    assert not hash(Open(a, b)) == hash(Closed(a, b))
    assert not hash(Open(a, b)) == hash(ClosedOpen(a, b))
    assert not hash(Open(a, b)) == hash(OpenClosed(a, b))

    assert not hash(Closed(a, b)) == hash(Open(a, b))
    assert hash(Closed(a, b)) == hash(Closed(a, b))
    assert not hash(Closed(a, b)) == hash(ClosedOpen(a, b))
    assert not hash(Closed(a, b)) == hash(OpenClosed(a, b))

    assert not hash(ClosedOpen(a, b)) == hash(Open(a, b))
    assert not hash(ClosedOpen(a, b)) == hash(Closed(a, b))
    assert hash(ClosedOpen(a, b)) == hash(ClosedOpen(a, b))
    assert not hash(ClosedOpen(a, b)) == hash(OpenClosed(a, b))

    assert not hash(OpenClosed(a, b)) == hash(Open(a, b))
    assert not hash(OpenClosed(a, b)) == hash(Closed(a, b))
    assert not hash(OpenClosed(a, b)) == hash(ClosedOpen(a, b))
    assert hash(OpenClosed(a, b)) == hash(OpenClosed(a, b))


def test_interval_eq_unbounded_different_types(
    interval_class_a: type[ConcreteInterval[Any]],
    interval_class_b: type[ConcreteInterval[Any]],
) -> None:
    assert hash(interval_class_a(-INF, INF)) == hash(interval_class_b(-INF, INF))


def test_interval_hash_different_type() -> None:
    assert hash(Open(1, 2)) != hash(Open("1", "2"))


def test_contains(interval_class: type[ConcreteInterval[int]]) -> None:
    interval = interval_class(1, 3)
    assert 0 not in interval
    assert (1 in interval) == interval.includes_lower_bound()
    assert 2 in interval
    assert (3 in interval) == interval.includes_upper_bound()
    assert 4 not in interval
    assert "a" not in interval


def test_contains_empty(empty: IntervalSet[int]) -> None:
    assert 0 not in empty


def test_contains_different_type() -> None:
    assert "a" not in (Open(0, 1) | Open(2, 3))


def test_intervals_iterable_union_as_method() -> None:
    assert tuple(Open(1, 2)._iterable_union(Closed(3, 4))) == (Open(1, 2), Closed(3, 4))


def test_intervals_iterable_union(empty: IntervalSet[int]) -> None:
    # empty
    assert tuple(Interval._iterable_union()) == ()
    assert tuple(Interval._iterable_union(EMPTY)) == ()
    assert tuple(Interval._iterable_union(*((EMPTY,) * 10))) == ()

    # disjoint
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 1), Closed(2, 3), Open(4, 5)) * factor):
            assert tuple(Interval._iterable_union(*intervals)) == (
                Open(0, 1),
                Closed(2, 3),
                Open(4, 5),
            )

    # overlapping
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Closed(1, 4), Open(3, 5)) * factor):
            assert tuple(Interval._iterable_union(*intervals)) == (Open(0, 5),)

    # touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Closed(2, 3)) * factor):
            assert tuple(Interval._iterable_union(*intervals)) == (Open(0, 4),)

    # not touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Open(2, 3)) * factor):
            assert tuple(Interval._iterable_union(*intervals)) == (Open(0, 2), Open(2, 4))


def test_interval_union(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
    interval_class_c: type[ConcreteInterval[int]],
    empty: IntervalSet[int],
) -> None:
    # empty
    a = interval_class_a(1, 0)
    b = interval_class_b(1, 0)
    c = interval_class_c(1, 0)
    assert a.union(b, c) == empty

    # overlapping
    a = interval_class_a(0, 2)
    b = interval_class_b(1, 4)
    c = interval_class_c(3, 5)
    assert a.union(b, c) == IntervalSet((Interval(0, 5, a.includes_lower_bound(), c.includes_upper_bound()),))

    # disjoint
    a = interval_class_a(0, 1)
    b = interval_class_b(2, 3)
    c = interval_class_c(4, 5)
    assert a.union(b, c) == IntervalSet((a, b, c))


def test_interval_binary_intersection(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
    empty: IntervalSet[int],
) -> None:
    # empty
    v = interval_class_a(0, -1)
    w = interval_class_b(0, -1)
    assert v._binary_intersection(w) == empty

    # zero-length
    v = interval_class_a(0, 0)
    w = interval_class_b(0, 0)
    assert v._binary_intersection(w) == Interval(
        0,
        0,
        v.includes_lower_bound() and w.includes_lower_bound(),
        v.includes_upper_bound() and w.includes_upper_bound(),
    )

    # disjoint
    v = interval_class_a(0, 1)
    w = interval_class_b(2, 3)
    assert v._binary_intersection(w) == empty

    # disjoint reversed
    v = interval_class_a(2, 3)
    w = interval_class_b(0, 1)
    assert v._binary_intersection(w) == empty

    # overlapping
    v = interval_class_a(0, 2)
    w = interval_class_b(1, 3)
    assert v._binary_intersection(w) == Interval(1, 2, w.includes_lower_bound(), v.includes_upper_bound())

    # overlapping reversed
    v = interval_class_a(1, 3)
    w = interval_class_b(0, 2)
    assert v._binary_intersection(w) == Interval(1, 2, v.includes_lower_bound(), w.includes_upper_bound())

    # touching
    v = interval_class_a(0, 1)
    w = interval_class_b(1, 2)
    assert v._binary_intersection(w) == (
        Closed(1, 1) if v.includes_upper_bound() and w.includes_lower_bound() else empty
    )

    # touching reversed
    v = interval_class_a(1, 2)
    w = interval_class_b(0, 1)
    assert v._binary_intersection(w) == (
        Closed(1, 1) if v.includes_lower_bound() and w.includes_upper_bound() else empty
    )

    # touching lower bound internally
    v = interval_class_a(0, 1)
    w = interval_class_b(0, 2)
    assert v._binary_intersection(w) == Interval(
        0, 1, v.includes_lower_bound() and w.includes_lower_bound(), v.includes_upper_bound()
    )

    # touching lower bound internally reversed
    v = interval_class_a(0, 2)
    w = interval_class_b(0, 1)
    assert v._binary_intersection(w) == Interval(
        0, 1, v.includes_lower_bound() and w.includes_lower_bound(), w.includes_upper_bound()
    )

    # touching upper bound internally
    v = interval_class_a(0, 2)
    w = interval_class_b(1, 2)
    assert v._binary_intersection(w) == Interval(
        1, 2, w.includes_lower_bound(), v.includes_upper_bound() and w.includes_upper_bound()
    )

    # touching upper bound internally reversed
    v = interval_class_a(1, 2)
    w = interval_class_b(0, 2)
    assert v._binary_intersection(w) == Interval(
        1, 2, v.includes_lower_bound(), v.includes_upper_bound() and w.includes_upper_bound()
    )


def test_interval_intersection(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
    interval_class_c: type[ConcreteInterval[int]],
    empty: IntervalSet[int],
) -> None:
    a = interval_class_a(0, 3)
    b = interval_class_b(1, 4)
    c = interval_class_c(2, 6)
    assert a & b & c == Interval(2, 3, c.includes_lower_bound(), a.includes_upper_bound())

    a = interval_class_a(0, 4)
    b = interval_class_b(1, 4)
    c = interval_class_c(2, 3)
    assert a & b & c == c

    a = interval_class_a(0, 3)
    b = interval_class_b(1, 3)
    c = interval_class_c(2, 3)
    assert a & b & c == Interval(
        2,
        3,
        c.includes_lower_bound(),
        a.includes_upper_bound() and b.includes_upper_bound() and c.includes_upper_bound(),
    )

    a = interval_class_a(0, 1)
    b = interval_class_b(2, 3)
    c = interval_class_c(4, 5)
    assert a & b & c == empty

    a = interval_class_a(0, 3)
    b = interval_class_b(2, 2)
    c = interval_class_c(1, 4)
    assert a & b & c == b


def test_interval_intersection_interval_type() -> None:
    """
    type checkers should be satisfied result is Interval and not IntervalSet
    """
    result: Interval[int] = Open(0, 2).intersection(Open(1, 3))
    assert result == Open(1, 2)


def test_interval_bounded() -> None:
    """
    type checkers should be satisfied that result is interval of type int without InfinityTypes
    """
    # mypy disapproves
    result_1: Interval[int] = (Open(-INF, 1) & Open(0, INF)).bounded()  # type:ignore[assignment]
    assert result_1 == Open(0, 1)

    # all approve
    result_2: Interval[int] = (Open[int | InfinityTypes](-INF, 1) & Open[int | InfinityTypes](0, INF)).bounded()
    assert result_2 == Open(0, 1)


def test_interval_bounded_error() -> None:
    with raises(TypeError):
        Open(-INF, 0).bounded()
    with raises(TypeError):
        Open(0, INF).bounded()


@mark.parametrize(
    ["interval_class_a", "interval_class_b"],
    [(Open, Open), (Closed, Closed), (ClosedOpen, ClosedOpen), (OpenClosed, OpenClosed)],
)
def test_interval_intersection_type_narrowing(
    interval_class_a: type[ConcreteInterval[int]], interval_class_b: type[ConcreteInterval[int | InfinityTypes]]
) -> None:
    """
    type checkers should be satisfied that x will be an interval of type int without InfinityTypes
    (the reverse is not supported though; intervals without InfinityTypes must always come first)
    """
    x: Interval[int] = interval_class_a(0, 2) & interval_class_b(1, INF)
    assert x == interval_class_a(1, 2)


def test_interval_complement(empty: IntervalSet[int]) -> None:
    assert ~empty == Closed(-INF, INF)
    assert ~Open(-INF, 0) == Closed(0, INF)
    assert ~Closed(-INF, 0) == Open(0, INF)
    assert ~Open(0, INF) == Closed(-INF, 0)
    assert ~Closed(0, INF) == Open(-INF, 0)
    assert ~ClosedOpen(-INF, 0) == ClosedOpen(0, INF)
    assert ~OpenClosed(-INF, 0) == OpenClosed(0, INF)
    assert ~ClosedOpen(0, INF) == ClosedOpen(-INF, 0)
    assert ~OpenClosed(0, INF) == OpenClosed(-INF, 0)


def test_interval_difference(
    empty_a: IntervalSet[int],
    empty_b: IntervalSet[int],
    empty_c: IntervalSet[int],
) -> None:
    assert empty_a - empty_b == empty_c
    assert Closed(0, 10) - empty_a == Closed(0, 10)
    assert Closed(0, 10) - Open(2, 3) == Closed(0, 2) | Closed(3, 10)
    assert Closed(0, 10) - Open(0, 10) == Closed(0, 0) | Closed(10, 10)
    assert Closed(0, 10).difference(Open(2, 3), Closed(5, 6)) == Closed(0, 2) | ClosedOpen(3, 5) | OpenClosed(6, 10)
    assert Closed(0, 10).difference(Open(-INF, 2), Open(8, INF)) == Closed(2, 8)
    assert Closed(0, 10).difference(Closed(4, 4), Closed(6, 6)) == ClosedOpen(0, 4) | Open(4, 6) | OpenClosed(6, 10)


def test_interval_isdisjoint_empty(empty_a: IntervalSet[Any], empty_b: IntervalSet[Any]) -> None:
    assert empty_a.isdisjoint(empty_b)


def test_interval_isdisjoint_empty_non_empty(empty: IntervalSet[Any]) -> None:
    assert empty.isdisjoint(Open(0, 1))
    assert Open(0, 1).isdisjoint(empty)


def test_interval_le_empty(empty_a: IntervalSet[Any], empty_b: IntervalSet[Any]) -> None:
    assert empty_a <= empty_b


def test_interval_le_empty_full(empty: IntervalSet[Any], interval_class: type[ConcreteInterval[int]]) -> None:
    assert empty <= interval_class(0, 1)


def test_interval_le(relative_combination: tuple[Interval[int], Interval[int]]) -> None:
    a, b = relative_combination

    left_covered = b.start < a.start or b.includes_lower_bound() >= a.includes_lower_bound() and not a.start < b.start
    right_covered = a.stop < b.stop or b.includes_upper_bound() >= a.includes_upper_bound() and not b.stop < a.stop

    assert (a <= b) == (left_covered and right_covered)
