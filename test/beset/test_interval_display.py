from pytest import mark

from beset.interval import Open, Closed, ClosedOpen, OpenClosed, IntervalSet, ConcreteInterval


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_Interval_repr(
    interval_type: type[ConcreteInterval[int]],
) -> None:
    assert repr(interval_type(0, 1)) == f"{interval_type.__name__}(0, 1)"


def test_Interval_str() -> None:
    assert str(Open(0, 1)) == "<0 : 1>"
    assert str(Closed(0, 1)) == "[0 : 1]"
    assert str(ClosedOpen(0, 1)) == "[0 : 1>"
    assert str(OpenClosed(0, 1)) == "<0 : 1]"

    assert str(Open(0, -1)) == "<:>"
    assert str(Closed(0, -1)) == "[:]"
    assert str(ClosedOpen(0, -1)) == "[:>"
    assert str(OpenClosed(0, -1)) == "<:]"


def test_IntervalSet_repr() -> None:
    assert repr(IntervalSet(())) == "IntervalSet(())"
    assert repr(IntervalSet((Open(0, 1),))) == "IntervalSet((OpenInterval(0, 1),))"
    assert repr(IntervalSet((Open(0, 1), Closed(2, 3)))) == "IntervalSet((OpenInterval(0, 1), ClosedInterval(2, 3)))"


def test_IntervalSet_str() -> None:
    assert str(IntervalSet(())) == "<:>"
    assert str(IntervalSet((Open(0, 1),))) == "<0 : 1>"
    assert str(IntervalSet((Open(0, 1), Closed(2, 3)))) == "<0 : 1> U [2 : 3]"
    assert str(IntervalSet((Open(0, 1), Closed(2, 3), Open(4, 5)))) == "<0 : 1> U [2 : 3] U <4 : 5>"
