from beset.interval import (
    Closed,
    Open,
    ClosedOpen,
    OpenClosed,
    Multiinterval,
    union,
    Monointerval,
    EMPTY_INTERVAL,
)
from pytest import mark, raises


def test_multiinterval_immutable() -> None:
    with raises(AttributeError):
        Multiinterval(()).intervals = ()


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_immutable(
    interval_type: type[Open | Closed | ClosedOpen | OpenClosed],
) -> None:
    with raises(AttributeError):
        interval_type(0, 0).start = 0

    with raises(AttributeError):
        interval_type(0, 0).stop = 0


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


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_multiinterval_eq(interval_type: type[Open | Closed | ClosedOpen | OpenClosed]) -> None:
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
    interval_type: type[Open | Closed | ClosedOpen | OpenClosed],
) -> None:
    assert Multiinterval(()) == interval_type(1, 0)
    assert interval_type(1, 0) == Multiinterval(())
    assert Multiinterval((interval_type(0, 1),)) == interval_type(0, 1)


@mark.parametrize("interval_type_a", [Open, Closed, ClosedOpen, OpenClosed])
@mark.parametrize("interval_type_b", [Open, Closed, ClosedOpen, OpenClosed])
def test_union(
    interval_type_a: type[Open | Closed | ClosedOpen | OpenClosed],
    interval_type_b: type[Open | Closed | ClosedOpen | OpenClosed],
) -> None:
    v = interval_type_a(0, 0)
    w = interval_type_b(0, 0)
    assert union(v, w) == (EMPTY_INTERVAL if v.empty() and w.empty() else Closed(0, 0),)

    v = interval_type_a(0, 0)
    w = interval_type_b(1, 1)
    if v.empty():
        if w.empty():
            assert union(v, w) == (EMPTY_INTERVAL,)
        else:
            assert union(v, w) == (w,)
    elif w.empty():
        assert union(v, w) == (v,)
    else:
        assert union(v, w) == (v, w)

    v = interval_type_a(1, 1)
    w = interval_type_b(0, 0)
    if v.empty():
        if w.empty():
            assert union(v, w) == (EMPTY_INTERVAL,)
        else:
            assert union(v, w) == (w,)
    elif w.empty():
        assert union(v, w) == (v,)
    else:
        assert union(v, w) == (w, v)

    v = interval_type_a(0, 0)
    w = interval_type_b(1, 2)
    assert union(v, w) == (w,) if v.empty() else (v, w)

    v = interval_type_a(1, 2)
    w = interval_type_b(0, 0)
    assert union(v, w) == (v,) if w.empty() else (v, w)

    v = interval_type_a(1, 2)
    w = interval_type_b(3, 4)
    assert union(v, w) == (v, w)

    v = interval_type_a(3, 4)
    w = interval_type_b(1, 2)
    assert union(v, w) == (w, v)

    v = interval_type_a(1, 2)
    w = interval_type_b(2, 3)
    assert (
        union(v, w)
        == (Monointerval.create(1, 3, v.includes_lower_bound(), w.includes_upper_bound()),)
        if v.includes_upper_bound() or w.includes_lower_bound()
        else (v, w)
    )

    v = interval_type_a(2, 3)
    w = interval_type_b(1, 2)
    assert (
        union(v, w)
        == (Monointerval.create(1, 3, w.includes_lower_bound(), v.includes_upper_bound()),)
        if w.includes_upper_bound() or v.includes_lower_bound()
        else (w, v)
    )

    v = interval_type_a(1, 3)
    w = interval_type_b(2, 4)
    assert union(v, w) == (
        Monointerval.create(1, 4, v.includes_lower_bound(), w.includes_upper_bound()),
    )

    v = interval_type_a(2, 4)
    w = interval_type_b(1, 3)
    assert union(v, w) == (
        Monointerval.create(1, 4, w.includes_lower_bound(), v.includes_upper_bound()),
    )

    v = interval_type_a(1, 4)
    w = interval_type_b(2, 3)
    assert union(v, w) == (v,)

    v = interval_type_a(2, 3)
    w = interval_type_b(1, 4)
    assert union(v, w) == (w,)

    ...
    # todo: internal touching