from typing import Any

from pytest import FixtureRequest, fixture

from beset import EMPTY, Closed, ClosedOpen, ConcreteInterval, IntervalSet, Open, OpenClosed

_EMPTY_INTERVALS = [EMPTY, IntervalSet()]


@fixture(params=_EMPTY_INTERVALS)
def empty(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS)
def empty_a(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS)
def empty_b(request: FixtureRequest) -> IntervalSet[Any]:
    return request.param  # type:ignore[no-any-return]


@fixture(params=_EMPTY_INTERVALS)
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
