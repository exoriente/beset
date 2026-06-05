from beset.infinity import INF
from beset.intersection import intersection
from beset.interval import IntervalSet, Open, Interval


def test_IntervalSet_intersect_type_peeling() -> None:
    """
    type checkers should be satisfied result is Interval[int] and not Interval[int | Infinity()]
    """
    result: IntervalSet[int] = intersection(Open(1, 2), Open(0, INF))
    assert result == Open(1, 2)


def test_Interval_intersect_type_peeling() -> None:
    """
    type checkers should be satisfied result is Interval[int] and not Interval[int | Infinity()]
    """
    result: Interval[int] = intersection(Open(1, 2), Open(0, INF))
    assert result == Open(1, 2)
    assert isinstance(result, Interval)
