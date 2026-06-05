from pytest import mark

from beset import Closed, ClosedOpen, ConcreteInterval, IntervalSet, Open, OpenClosed


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_interval_repr_int(
    interval_type: type[ConcreteInterval[int]],
) -> None:
    assert repr(interval_type(0, 1)) == f"{interval_type.__name__}(0, 1)"


@mark.parametrize("interval_type", [Open, Closed, ClosedOpen, OpenClosed])
def test_interval_repr_str(
    interval_type: type[ConcreteInterval[str]],
) -> None:
    assert repr(interval_type("aaa", "bbb")) == f"{interval_type.__name__}('aaa', 'bbb')"


def test_interval_str() -> None:
    assert str(Open(0, 1)) == "<0 : 1>"
    assert str(Closed(0, 1)) == "[0 : 1]"
    assert str(ClosedOpen(0, 1)) == "[0 : 1>"
    assert str(OpenClosed(0, 1)) == "<0 : 1]"

    assert str(Open("aaa", "bbb")) == "<'aaa' : 'bbb'>"
    assert str(Closed("aaa", "bbb")) == "['aaa' : 'bbb']"
    assert str(ClosedOpen("aaa", "bbb")) == "['aaa' : 'bbb'>"
    assert str(OpenClosed("aaa", "bbb")) == "<'aaa' : 'bbb']"

    assert str(Open(0, -1)) == "<:>"
    assert str(Closed(0, -1)) == "[:]"
    assert str(ClosedOpen(0, -1)) == "[:>"
    assert str(OpenClosed(0, -1)) == "<:]"


def test_interval_set_repr() -> None:
    assert repr(IntervalSet(())) == "IntervalSet(())"
    assert repr(IntervalSet((Open(0, 1),))) == "IntervalSet((OpenInterval(0, 1),))"
    assert repr(IntervalSet((Open(0, 1), Closed(2, 3)))) == "IntervalSet((OpenInterval(0, 1), ClosedInterval(2, 3)))"


def test_interval_set_str() -> None:
    assert str(IntervalSet(())) == "<:>"
    assert str(IntervalSet((Open(0, 1),))) == "<0 : 1>"
    assert str(IntervalSet((Open(0, 1), Closed(2, 3)))) == "<0 : 1> | [2 : 3]"
    assert str(IntervalSet((Open(0, 1), Closed(2, 3), Open(4, 5)))) == "<0 : 1> | [2 : 3] | <4 : 5>"
