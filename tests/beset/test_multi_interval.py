from beset.multi_interval import MultiInterval


def test_multi_interval_create() -> None:
    MultiInterval(bounds=[], odd=False)


def test_multi_interval_contains() -> None:
    assert 1 not in MultiInterval[int](bounds=[], odd=False)
