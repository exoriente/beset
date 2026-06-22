# `⟨ beset ⟩`

_immutable, typed intervals with the interface of Python sets_

- Intervals are typed as generics and pass type checks by all common Python type checkers:
  - `mypy --strict`
  - `ty`
  - `pyright`
  - `pyrefly`
- Intervals are immutable and hashable
- Intervals behave like sets
  - If you know Python set operations, you know how to use this library
- Intervals can be used on any data type that supports `<`, the less-than operator, for linear ordering 
  - Typical: `int`, `float`, `datetime`
  - Even a class like `str` with no notion of distance between values, can be used for intervals (e.g. dictionary ranges)

## Examples

Intervals are sets that contain all possible values between their lower and upper bounds.
The `Closed` interval also includes the bounds themselves. 

```python
>>> from beset import Closed

>>> x = Closed(1, 3)

>>> print(x)
[1 ; 3]

>>> 0 in x, 1 in x, 2 in x, 3 in x, 4 in x
(False, True, True, True, False)

>>> x.start, x.stop
(1, 3)
```

The half-open `ClosedOpen` interval includes its lower bound but not its upper one.  

```python
>>> from beset import ClosedOpen

>>> y = ClosedOpen(1, 3)

>>> print(y)
[1 ; 3)

>>> 2 in y, 3 in y, 4 in y
(True, False, False)
```

The `Open` interval excludes both its bounds and the `OpenClosed` interval includes its upper bound, but not its lower one. 

You can also create the required interval dynamically using their `Interval` base class.

```python
>>> from beset import Interval

>>> Interval(9, 99, start_closed=False, stop_closed=True)
OpenClosed(9, 99)
```

Intervals support all Python `set` operations. Some examples:

```python
>>> ClosedOpen(10, 20) & ClosedOpen(15, 25)  # intersection
ClosedOpen(15, 20)

>>> ClosedOpen(3, 9) < Open(0, 10)  # is proper subset
True
```

Set subtraction can lead to disjoint sets. The `beset` library represents these using the class `IntervalSet`.

```python
>>> s = Open(0, 10) - Open(3, 5)

>>> s
IntervalSet([OpenClosed(0, 3), ClosedOpen(5, 10)])

>>> print(s)
(0 ; 3] | [5 ; 10)
```

You can also create an `IntervalSet` explicitly, but it's often easier to use the union operator on simple intervals.
The results are equal.

```python
>>> IntervalSet([Open(10, 20), Open(30, 40)]) == Open(10, 20) | Open(30, 40)
True
```

The `beset` library supports unbounded intervals without upper or lower bound.
Create such intervals by using `None` as a bound.

```python
>>> x = Closed(10, None)
>>> print(x)
[10 ; +inf⟩
>>> 100 in x
True
```

Unbounded intervals allow for the introduction of the _complement_ operation that returns the complementary interval, containing everything not in the original interval.

```python
>>> Closed(-3, 7).complement()
IntervalSet([Open(None, -3), Open(7, None)])

>>> print(~ClosedOpen(0, 100))  # the ~-operator returns the complement
⟨-inf ; 0) | [100 ; +inf⟩
```

## Typing

The `Interval` and `IntervalSet` class are generics.
Type checkers automatically infer the correct type.

```python
>>> reveal_type(ClosedOpen(2.718, 6.283))  # Revealed type is beset.ClosedOpen[float]
```

Taking the complement of an interval can introduce `None` values.

```python
>>> print(x := ~Closed(0, 10))
⟨-inf ; 0) | (10 ; +inf⟩

>>> reveal_type(x)  # Revealed type is beset.IntervalSet[int | None]
```

Getting rid of the union with `None` can be accomplished using intersection.

```python
>>> domain = Closed(-100, 100)
>>> y = domain & x
>>> print(y)
[-100 ; 0) | (10 ; 100]

>>> reveal_type(y)  # Revealed type is beset.IntervalSet[int]
```
