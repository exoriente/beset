from beset.infinity import INF
from beset.intersection import intersection
from beset.interval import Multiinterval, Open, Monointerval


def test_multiinterval_intersect_type_peeling() -> None:
    """
    type checkers should be satisfied result is Monointerval[int] and not Monointerval[int | Infinity()]
    """
    result: Multiinterval[int] = intersection(Open(1, 2), Open(0, INF))
    assert result == Open(1, 2)


def test_monointerval_intersect_type_peeling() -> None:
    """
    type checkers should be satisfied result is Monointerval[int] and not Monointerval[int | Infinity()]
    """
    result: Monointerval[int] = intersection(Open(1, 2), Open(0, INF))
    assert result == Open(1, 2)
    assert isinstance(result, Monointerval)
