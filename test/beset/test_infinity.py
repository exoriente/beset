from beset.infinity import Infinity, NegativeInfinity


def test_infinity_eq() -> None:
    assert Infinity() == Infinity()
    assert Infinity() == float("inf")
    assert NegativeInfinity() == NegativeInfinity()
    assert NegativeInfinity() == float("-inf")

