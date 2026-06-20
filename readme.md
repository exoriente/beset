# `< beset >`

_immutable, typed intervals with the interface of Python sets_

- Intervals are typed as generics and pass type checks by all common Python type checkers:
  - `mypy --strict`
  - `ty`
  - `pyright`
  - `pyrefly`
- Intervals are immutable and hashable
- Intervals behave like sets
  - If you know Python set operations, you know how to use this library
- Intervals can be used on any datatype that supports `<`, the less-than operator, for linear ordering 
  - Typical: `int`, `float`, `datetime`
  - Even a class like `str` with no notion of distance between values, can be used for intervals (e.g. dictionary ranges)

## Examples

Intervals are sets that contain all possible values between their lower and upper bounds.
The `Closed` interval also includes the bounds themselves. 

```python
>>> from beset import Closed

>>> x = Closed(1, 3)

>>> print(x)
[1 : 3]

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
[1 : 3>

>>> 2 in y, 3 in y, 4 in y
(True, False, False)
```

The `Open` interval excludes both its bounds and the `OpenClosed` interval includes its upper bound, but not its lower one. 

You can also create the required interval dynamically using their `Interval` base class.

```python
>>> from beset import Interval

>>> Interval(9, 99, include_lower_bound=False, include_upper_bound=True)
OpenClosed(9, 99)
```

Intervals support all Python `set` operations. Some examples:

```python
>>> ClosedOpen(10, 20) & ClosedOpen(15, 25)  # intersection
ClosedOpen(15, 20)

>>> ClosedOpen(3, 9) < Open(0, 10)  # is subset
True
```

Set subtraction can lead to disjoint sets. The `beset` library represents these using the class `IntervalSet`.

```python
>>> s = Open(0, 10) - Open(3, 5)

>>> s
IntervalSet((OpenClosed(0, 3), ClosedOpen(5, 10)))

>>> print(s)
<0 : 3] | [5 : 10>
```

You can also create an `IntervalSet` explicitly, but it's often easier to use the union operator on simple intervals.
The results are equal.

```python
>>> IntervalSet((Open(10, 20), Open(30, 40))) == Open(10, 20) | Open(30, 40)
True
```

The `beset` library provides an infinity object `INF`, which is defined to be larger than every other object, except `float("inf")`.
This allows for the introduction of the _complement_ operation that return the complementary interval, containing everything not in the original interval.

```python
>>> Closed(-3, 7).complement()
IntervalSet((Open(-INF, -3), Open(7, INF)))

>>> print(~ClosedOpen(0, 100))  # the ~-operator returns the complement
[-INF, 0> | [100, INF>
```

## Typing

The `Interval` and `IntervalSet` class are generics.
In most cases the type checker of your choice automatically infers the correct type.

```python
>>> reveal_type(ClosedOpen(2.718, 6.283))  # Revealed type is beset.ClosedOpen[float]
```

Taking the complement of an interval can introduce `INF` values.

```python
>>> print(x := ~Closed(0, 10))
<-INF : 0> | <10 : INF>

>>> reveal_type(x)  # Revealed type is beset.IntervalSet[int | Infinity | NegativeInfinity]
```

Getting rid of the `Infinity` types can be accomplished using intersection.

```python
>>> domain = Closed(-100, 100)
>>> y =  domain & x
>>> print(y)
[-100 : 0> | <10 : 100]

>>> reveal_type(y)  # Revealed type is beset.IntervalSet[int]
```

### `mypy`

Using `mypy` you need to be more careful using union types when instantiating intervals.

```python
>>> c = ClosedOpen(7, INF)  # type of c according to mypy: ClosedOpen[Sortable]
>>> r = c & domain          # type of r according to mypy: ClosedOpen[Sortable]
```

In `ty` and other checkers this goes better.

```python
>>> c = ClosedOpen(7, INF)  # type of c according to ty: ClosedOpen[int | Infinity]
>>> r = c & domain          # type of r according to ty: ClosedOpen[int]
```

When determining the type of the interval `mypy` uses the "closest" parent class common to the different types.
In this case `mypy` uses `Sortable`, the protocol class used as bound for `Interval`. Other checkers, like `ty`, use a union type instead, which is more convenient for type narrowing by using intersection.

As a workaround you can force `mypy` to do the same by being more explicit.

```python
>>> c = ClosedOpen[int | Infinity](7, INF)  # type of c according to mypy: ClosedOpen[int | Infinity]
>>> r = c & domain                          # type of r according to mypy: ClosedOpen[int]
```

For more information about type narrowing see the documentation.

