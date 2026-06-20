from typing import Any, TypeVar

from pytest import FixtureRequest, fixture

from beset import Closed, ClosedOpen, Open, OpenClosed, Sortable

T = TypeVar("T", covariant=True, bound=Sortable | None)


INTERVAL_CLASSES = [Open, Closed, ClosedOpen, OpenClosed]
IntervalType = Open[T] | Closed[T] | ClosedOpen[T] | OpenClosed[T]


@fixture(params=INTERVAL_CLASSES)
def interval_class(request: FixtureRequest) -> IntervalType[Any]:
    return request.param  # type:ignore[no-any-return]
