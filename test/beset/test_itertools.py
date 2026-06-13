from pytest import raises

from beset._itertools import batched


class TestBatched:
    def test_batched(self) -> None:
        assert list(batched([], 2)) == []
        assert list(batched([1, 2], 2)) == [(1, 2)]
        assert list(batched([1, 2, 3, 4], 2)) == [(1, 2), (3, 4)]
        assert list(batched([1, 2, 3, 4, 5], 2)) == [(1, 2), (3, 4), (5,)]
        assert list(batched([1, 2, 3, 4, 5], 1)) == [(1,), (2,), (3,), (4,), (5,)]

    def test_bad_batch_size(self) -> None:
        with raises(ValueError):
            list(batched([], 0))

    def test_strict(self) -> None:
        with raises(ValueError):
            list(batched([1, 2, 3], 2, strict=True))
