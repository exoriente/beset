from typing import Any

from pytest import FixtureRequest, fixture

from beset import EMPTY, Closed, ClosedOpen, ConcreteInterval, Interval, IntervalSet, Open, OpenClosed

_EMPTY_INTERVALS = [EMPTY, Open(1, 0), IntervalSet()]
_EMPTY_INTERVALS_IDS = ["default", "interval", "interval_set"]


@fixture(params=_EMPTY_INTERVALS, ids=_EMPTY_INTERVALS_IDS)
def empty(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS, ids=_EMPTY_INTERVALS_IDS)
def empty_a(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS, ids=_EMPTY_INTERVALS_IDS)
def empty_b(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS, ids=_EMPTY_INTERVALS_IDS)
def empty_c(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


_INTERVAL_CLASSES = [Open, Closed, ClosedOpen, OpenClosed]


@fixture(params=_INTERVAL_CLASSES)
def interval_class(request: FixtureRequest) -> type[ConcreteInterval[Any]]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_INTERVAL_CLASSES)
def interval_class_a(request: FixtureRequest) -> type[ConcreteInterval[Any]]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_INTERVAL_CLASSES)
def interval_class_b(request: FixtureRequest) -> type[ConcreteInterval[Any]]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_INTERVAL_CLASSES)
def interval_class_c(request: FixtureRequest) -> type[ConcreteInterval[Any]]:
    return request.param  # type:ignore[no-any-return]


_RELATIVE_BOUNDS_VALUES = {
    0: "below",
    1: "below",
    2: "lower_bound",
    3: "interior",
    4: "interior",
    5: "upper_bound",
    6: "above",
    7: "above",
}

_RELATIVE_SPANS = {
    f"{label_x}-{label_y}": (value_x, value_y)
    for value_x, label_x in _RELATIVE_BOUNDS_VALUES.items()
    for value_y, label_y in _RELATIVE_BOUNDS_VALUES.items()
    if value_x < value_y
}


@fixture(params=_RELATIVE_SPANS.values(), ids=list(_RELATIVE_SPANS.keys()))
def relative_combination(
    interval_class_a: type[ConcreteInterval[int]],
    interval_class_b: type[ConcreteInterval[int]],
    request: FixtureRequest,
) -> tuple[Interval[int], Interval[int]]:
    x, y = request.param
    return interval_class_a(2, 5), interval_class_b(x, y)
