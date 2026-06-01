from pytest import mark

from beset.interval import Open, Closed, ClosedOpen, OpenClosed, Multiinterval


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_monointerval_repr(
    interval_type: type[Open | Closed | ClosedOpen | OpenClosed],
) -> None:
    assert repr(interval_type(0, 1)) == f"{interval_type.__name__}(0, 1)"


def test_monointerval_str() -> None:
    assert str(Open(0, 1)) == "<0 : 1>"
    assert str(Closed(0, 1)) == "[0 : 1]"
    assert str(ClosedOpen(0, 1)) == "[0 : 1>"
    assert str(OpenClosed(0, 1)) == "<0 : 1]"

    assert str(Open(0, -1)) == "<:>"
    assert str(Closed(0, -1)) == "[:]"
    assert str(ClosedOpen(0, -1)) == "[:>"
    assert str(OpenClosed(0, -1)) == "<:]"


def test_multiinterval_repr() -> None:
    assert repr(Multiinterval(())) == "Multiinterval(())"
    assert repr(Multiinterval((Open(0, 1),))) == "Multiinterval((OpenInterval(0, 1),))"
    assert (
        repr(Multiinterval((Open(0, 1), Closed(2, 3))))
        == "Multiinterval((OpenInterval(0, 1), ClosedInterval(2, 3)))"
    )


def test_multiinterval_str() -> None:
    assert str(Multiinterval(())) == "<:>"
    assert str(Multiinterval((Open(0, 1),))) == "<0 : 1>"
    assert str(Multiinterval((Open(0, 1), Closed(2, 3)))) == "<0 : 1> U [2 : 3]"
    assert (
        str(Multiinterval((Open(0, 1), Closed(2, 3), Open(4, 5)))) == "<0 : 1> U [2 : 3] U <4 : 5>"
    )
