from beset.infinity import Infinity, NegativeInfinity, Infinities


def test_infinity_eq() -> None:
    assert Infinity() == Infinity()
    assert Infinity() == float("inf")
    assert NegativeInfinity() == NegativeInfinity()
    assert NegativeInfinity() == float("-inf")
    assert not Infinity() == 0
    assert not Infinity() == "a"
    assert not Infinity() == object()
    assert not NegativeInfinity() == 0
    assert not NegativeInfinity() == "a"
    assert not NegativeInfinity() == object()


def test_infinity_neg() -> None:
    assert -Infinity() == NegativeInfinity()
    assert -NegativeInfinity() == Infinity()
    assert not -Infinity() == Infinity()
    assert not -NegativeInfinity() == NegativeInfinity()


def test_infinity_lt() -> None:
    assert not Infinity() < 0
    assert not Infinity() < "a"
    assert not Infinity() < object()
    assert not Infinity() < Infinity()
    assert not Infinity() < float("inf")
    assert not Infinity() < NegativeInfinity()
    assert not Infinity() < float("-inf")

    assert NegativeInfinity() < 0
    assert NegativeInfinity() < "a"
    assert NegativeInfinity() < object()
    assert NegativeInfinity() < Infinity()
    assert NegativeInfinity() < float("inf")
    assert not NegativeInfinity() < NegativeInfinity()
    assert not NegativeInfinity() < float("-inf")


def test_infinity_gt() -> None:
    assert Infinity() > 0
    assert Infinity() > "a"
    assert Infinity() > object()
    assert not Infinity() > Infinity()
    assert not Infinity() > float("inf")
    assert Infinity() > NegativeInfinity()
    assert Infinity() > float("-inf")

    assert not NegativeInfinity() > 0
    assert not NegativeInfinity() > "a"
    assert not NegativeInfinity() > object()
    assert not NegativeInfinity() > Infinity()
    assert not NegativeInfinity() > float("inf")
    assert not NegativeInfinity() > NegativeInfinity()
    assert not NegativeInfinity() > float("-inf")


def test_infinity_sortable() -> None:
    numbers: list[int | Infinities] = [4, Infinity(), 2, 3, NegativeInfinity(), 1]
    assert sorted(numbers) == [NegativeInfinity(), 1, 2, 3, 4, Infinity()]

    letters: list[str | Infinities] = ["d", Infinity(), "b", "c", NegativeInfinity(), "a"]
    assert sorted(letters) == [NegativeInfinity(), "a", "b", "c", "d", Infinity()]
