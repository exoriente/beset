from itertools import permutations

from beset.infinity import INF, InfinityTypes
from beset.interval import (
    Closed,
    Open,
    ClosedOpen,
    OpenClosed,
    Monointerval,
    EMPTY_INTERVAL,
    Multiinterval,
    new_monointerval,
)
from pytest import mark, raises


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_immutable(
    interval_type: type[Monointerval[int]],
) -> None:
    with raises(AttributeError):
        interval_type(0, 0).intervals = ()  # type:ignore[ty:invalid-assignment,unused-ignore,misc]

    with raises(AttributeError):
        interval_type(0, 0).start = 0  # type:ignore[ty:invalid-assignment,unused-ignore,misc]

    with raises(AttributeError):
        interval_type(0, 0).stop = 0  # type:ignore[ty:invalid-assignment,unused-ignore,misc]


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_instance_of_multiinterval(
    interval_type: type[Monointerval[int]],
) -> None:
    """
    type checkers should be satisfied a
    """
    result: Multiinterval[int] = interval_type(0, 1)
    assert result


def test_monointerval_covariant() -> None:
    """
    type checkers should be satisfied result Monointerval[bool] is a valid Multiinterval[int]
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
def test_monointerval_empty(a: int | str, b: int | str) -> None:
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


@mark.parametrize("a,b", [(0, 0), (1, 1), ("a", "a"), ("b", "b")])
def test_monointerval_eq_empty(a: int | str, b: int | str) -> None:
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


@mark.parametrize("a,b", [(0, 1), (1, 2), ("a", "b"), ("b", "c")])
def test_monointerval_eq_not_empty(a: int | str, b: int | str) -> None:
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


def test_monointerval_eq_different_type() -> None:
    assert Open(1, 2) != Open("1", "2")


def test_monointervals_iterable_union_as_method() -> None:
    assert tuple(Open(1, 2)._iterable_union(Closed(3, 4))) == (Open(1, 2), Closed(3, 4))


def test_monointervals_iterable_union() -> None:
    # empty
    assert tuple(Monointerval._iterable_union()) == ()
    assert tuple(Monointerval._iterable_union(EMPTY_INTERVAL)) == ()
    assert tuple(Monointerval._iterable_union(*((EMPTY_INTERVAL,) * 10))) == ()

    # disjoint
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 1), Closed(2, 3), Open(4, 5)) * factor):
            assert tuple(Monointerval._iterable_union(*intervals)) == (
                Open(0, 1),
                Closed(2, 3),
                Open(4, 5),
            )

    # overlapping
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Closed(1, 4), Open(3, 5)) * factor):
            assert tuple(Monointerval._iterable_union(*intervals)) == (Open(0, 5),)

    # touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Closed(2, 3)) * factor):
            assert tuple(Monointerval._iterable_union(*intervals)) == (Open(0, 4),)

    # not touching
    for factor in range(1, 3):
        for intervals in permutations((Open(0, 2), Open(2, 4), Open(2, 3)) * factor):
            assert tuple(Monointerval._iterable_union(*intervals)) == (Open(0, 2), Open(2, 4))


@mark.parametrize("interval_type_c", [Open, Closed, ClosedOpen, OpenClosed])
@mark.parametrize("interval_type_b", [Open, Closed, ClosedOpen, OpenClosed])
@mark.parametrize("interval_type_a", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_union(
    interval_type_a: type[Monointerval[int]],
    interval_type_b: type[Monointerval[int]],
    interval_type_c: type[Monointerval[int]],
) -> None:
    # empty
    a = interval_type_a(1, 0)
    b = interval_type_b(1, 0)
    c = interval_type_c(1, 0)
    assert a.union(b, c) == EMPTY_INTERVAL

    # overlapping
    a = interval_type_a(0, 2)
    b = interval_type_b(1, 4)
    c = interval_type_c(3, 5)
    assert a.union(b, c) == Multiinterval(
        (new_monointerval(0, 5, a.includes_lower_bound(), c.includes_upper_bound()),)
    )

    # disjoint
    a = interval_type_a(0, 1)
    b = interval_type_b(2, 3)
    c = interval_type_c(4, 5)
    assert a.union(b, c) == Multiinterval((a, b, c))


@mark.parametrize("interval_type_b", [Open, Closed, ClosedOpen, OpenClosed])
@mark.parametrize("interval_type_a", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_binary_intersection(
    interval_type_a: type[Monointerval[int]],
    interval_type_b: type[Monointerval[int]],
) -> None:
    # empty
    v = interval_type_a(0, -1)
    w = interval_type_b(0, -1)
    assert v._binary_intersection(w) == EMPTY_INTERVAL

    # zero-length
    v = interval_type_a(0, 0)
    w = interval_type_b(0, 0)
    assert v._binary_intersection(w) == EMPTY_INTERVAL if v.empty() or w.empty() else EMPTY_INTERVAL

    # disjoint
    v = interval_type_a(0, 1)
    w = interval_type_b(2, 3)
    assert v._binary_intersection(w) == EMPTY_INTERVAL

    # disjoint reversed
    v = interval_type_a(2, 3)
    w = interval_type_b(0, 1)
    assert v._binary_intersection(w) == EMPTY_INTERVAL

    # overlapping
    v = interval_type_a(0, 2)
    w = interval_type_b(1, 3)
    assert v._binary_intersection(w) == new_monointerval(
        1, 2, w.includes_lower_bound(), v.includes_upper_bound()
    )

    # overlapping reversed
    v = interval_type_a(1, 3)
    w = interval_type_b(0, 2)
    assert v._binary_intersection(w) == new_monointerval(
        1, 2, v.includes_lower_bound(), w.includes_upper_bound()
    )

    # touching
    v = interval_type_a(0, 1)
    w = interval_type_b(1, 2)
    assert (
        v._binary_intersection(w) == Closed(1, 1)
        if v.includes_upper_bound() and w.includes_lower_bound()
        else EMPTY_INTERVAL
    )

    # touching reversed
    v = interval_type_a(1, 2)
    w = interval_type_b(0, 1)
    assert (
        v._binary_intersection(w) == Closed(1, 1)
        if v.includes_lower_bound() and w.includes_upper_bound()
        else EMPTY_INTERVAL
    )

    # touching lower bound internally
    v = interval_type_a(0, 1)
    w = interval_type_b(0, 2)
    assert v._binary_intersection(w) == new_monointerval(
        0, 1, v.includes_lower_bound() and w.includes_lower_bound(), v.includes_upper_bound()
    )

    # touching lower bound internally reversed
    v = interval_type_a(0, 2)
    w = interval_type_b(0, 1)
    assert v._binary_intersection(w) == new_monointerval(
        0, 1, v.includes_lower_bound() and w.includes_lower_bound(), w.includes_upper_bound()
    )

    # touching upper bound internally
    v = interval_type_a(0, 2)
    w = interval_type_b(1, 2)
    assert v._binary_intersection(w) == new_monointerval(
        1, 2, w.includes_lower_bound(), v.includes_upper_bound() and w.includes_upper_bound()
    )

    # touching upper bound internally reversed
    v = interval_type_a(1, 2)
    w = interval_type_b(0, 2)
    assert v._binary_intersection(w) == new_monointerval(
        1, 2, v.includes_lower_bound(), v.includes_upper_bound() and w.includes_upper_bound()
    )


def test_monointerval_intersection_interval_type() -> None:
    """
    type checkers should be satisfied result is Monointerval and not Multiinterval
    """
    result: Monointerval[int] = Open(0, 2).intersection(Open(1, 3))
    assert result == Open(1, 2)


def test_monointerval_bounded() -> None:
    """
    type checkers should be satisfied that result is interval of type int without InfinityTypes
    """
    # mypy disapproves
    result_1: Monointerval[int] = (Open(-INF, 1) & Open(0, INF)).bounded()  # type:ignore[assignment]
    assert result_1 == Open(0, 1)

    # all approve
    result_2: Monointerval[int] = (
        Open[int | InfinityTypes](-INF, 1) & Open[int | InfinityTypes](0, INF)
    ).bounded()
    assert result_2 == Open(0, 1)


def test_monointerval_bounded_error() -> None:
    """
    type checkers should be satisfied that result is interval of type int without InfinityTypes
    """
    with raises(TypeError):
        Open(-INF, 0).bounded()
    with raises(TypeError):
        Open(0, INF).bounded()


# @mark.parametrize("interval_type_c", [Open, Closed, ClosedOpen, OpenClosed])
# @mark.parametrize("interval_type_b", [Open, Closed, ClosedOpen, OpenClosed])
# @mark.parametrize("interval_type_a", [Open, Closed, ClosedOpen, OpenClosed])
# def test_monointerval_intersection(
#     interval_type_a: type[Monointerval[int]],
#     interval_type_b: type[Monointerval[int]],
#     interval_type_c: type[Monointerval[int]],
# ) -> None:
#     assert False  # todo: implement
