# `⟨ beset ⟩`

_typed intervals with the interface of Python sets_


[![PyPI](https://img.shields.io/pypi/v/beset?color=blue)](https://pypi.org/project/beset/)
[![Python versions](https://img.shields.io/pypi/pyversions/beset)](https://pypi.org/project/beset/)
[![License](https://img.shields.io/pypi/l/beset)](https://github.com/exoriente/beset/blob/main/license)
[![Build](https://img.shields.io/github/actions/workflow/status/exoriente/beset/ci.yaml?branch=main)](https://github.com/exoriente/beset/actions)


The `beset` Python library provides generic interval classes for use in typed Python.
It is tested to work well with `mypy`, `ty`, `pyright` and `pyrefly`.

The interface of `beset` interval mirrors that of Python `set`.
If you know Python `set` operations, you know how to use this library.


## Contents

- [Installation](#installation)
- [Development status](#development-status)
- [Quick demo](#quick-demo)
- [Why use `beset`?](#why-use-beset)
- [Some additional examples](#some-additional-examples)
- [Typing](#typing)
- [Other libraries](#other-libraries)


## Installation

`beset` is available on [PyPI](https://pypi.org/project/beset/) and can be installed using `pip`.

```shell
$ pip install beset
```

Popular package managers can install it out of the box.
For instance, you can run `poetry add beset` or `uv add beset` if you use these tools.


## Development status

The `beset` library is currently still in an early stage of development.
Its design and API are likely to change in upcoming versions until version 1.0 is reached.

If maturity and stability are requirements, check out some [other libraries](#other-libraries) that might meet your needs.
Conversely, if you have requirements or needs you'd like to see the `beset` library satisfy or have feedback on the current design or API, any input or contribution is highly appreciated. 


## Quick demo

Let's assume `beset` is imported as follows:

```python
>>> import beset as b
```

We can use one of the interval classes, such as `ClosedOpen`, to create intervals and perform standard set operations on them:

```python
>>> working_hours = b.ClosedOpen(9, 17)
>>> lunch_break = b.ClosedOpen(12, 13)

>>> available = working_hours - lunch_break  # set subtraction operator

>>> print(available)
[9 ; 12) | [13 ; 17)

>>> meeting = b.ClosedOpen(11, 12)
>>> meeting <= available  # is a subset operator
True
```


## Why use `beset`?


### When writing typed Python code

Use `beset` when you need statically typed intervals. Its generic classes preserve bound types through interval and set operations and are understood by type checkers.


### Adherence to the Python `set` interface

Adherence to the existing interface of Python `set` means you can jump in and start using this library with little prior knowledge.

Note: Since `beset` intervals are immutable it would be more accurate to say they follow the interface of `frozenset`, which itself matches most of the `set` interface.


### Strict function signatures and variable definitions

`beset` classes allow you to strictly specify in function signatures and variable type hints what kinds of intervals your code expects and to use type checkers to enforce
those expectations. For example, the `Open[int]` type hint limits objects to open continuous non-empty intervals defined on integer bounds,
while `ClosedOpenSet[datetime | None]` allows bounded and unbounded multiintervals defined on date-times.

That means your code needs fewer run-time checks and error handling to deal with intervals of the wrong type or containing the wrong type of data.


### Intervals work on many data types

`beset` intervals can be defined on any type of data that can be ordered using its less-than (`<`) operator.
This not only includes `int`, `float`, `datetime` and similar types, but also types like `str` that have an ordering without a concept of distance between values.
Intervals can be defined on your own classes as well, as long as you provide an implementation for the less-than operator.

Note: `beset` is not the only interval library providing this. See [below](#other-libraries) for some others.


### Intervals are immutable and hashable

`beset` interval objects are immutable and hashable, as long as the objects used as bounds can be hashed.


## Some additional examples

Intervals can have open or closed bounds:

```python
>>> print(b.Open(6, 7))
(6 ; 7)

>>> print(b.OpenClosed(6, 7))
(6 ; 7]

>>> print(b.ClosedOpen(6, 7))
[6 ; 7)

>>> print(b.Closed(6, 7))
[6 ; 7]
```

Intervals contain all possible values between their lower and upper bounds:

```python
>>> 6 in b.ClosedOpen(7, 9)
False

>>> 7 in b.ClosedOpen(7, 9)
True

>>> 8 in b.ClosedOpen(7, 9)
True

>>> 9 in b.ClosedOpen(7, 9)
False

>>> 10 in b.ClosedOpen(7, 9)
False
```

`beset` intervals have methods and operators mirroring those of Python `set` (or `frozenset` more specifically, since `beset` intervals are immutable).
Some examples:

```python
>>> b.ClosedOpen(10, 20) & b.ClosedOpen(15, 25)  # intersection
ClosedOpen(15, 20)

>>> b.ClosedOpen(3, 9) < b.Open(0, 10)  # is proper subset
True
```

Set subtraction can lead to disjoint sets. The `beset` library represents these using the class `IntervalSet`.

```python
>>> s = b.Open(0, 10) - b.Open(3, 5)

>>> s
IntervalSet([OpenClosed(0, 3), ClosedOpen(5, 10)])

>>> print(s)
(0 ; 3] | [5 ; 10)
```

You can also create an `IntervalSet` explicitly, but it's often easier to use the union operator on simple intervals.
The results are the same.

```python
>>> b.IntervalSet([b.Open(10, 20), b.Open(30, 40)]) == b.Open(10, 20) | b.Open(30, 40)
True
```

The `beset` library supports unbounded intervals without upper or lower bound.
Create such intervals by using `None` as a bound.

```python
>>> x = b.Closed(10, None)
>>> print(x)
[10 ; +inf⟩

>>> 100 in x
True
```

Unbounded intervals allow for the introduction of the _complement_ operation that returns the complementary interval, containing everything not in the original interval.

```python
>>> b.Closed(-3, 7).complement()
OpenSet([RightOpen(-3), LeftOpen(7)])

>>> print(~b.ClosedOpen(0, 100))  # the ~-operator returns the complement
⟨-inf ; 0) | [100 ; +inf⟩
```

## Typing

The `beset` classes are generic.
Type checkers automatically infer the correct type.

```python
>>> reveal_type(b.ClosedOpen(2.718, 6.283))  # Revealed type is beset.ClosedOpen[float]
```

You can use the `beset` classes to specify precisely what kind of interval your code expects.
In the following inventory of classes we assume intervals with `int` bounds, but any suitable type will work. 

```python
# IntervalSet matches any type of interval; atomic (single) intervals as well as unions of intervals or the empty interval
# Including None will mean unbounded intervals, with plus or minus infinity as bounds, are also permitted
a: b.IntervalSet[int | None]

# Using a stricter IntervalSet, by dropping None, will allow only bounded intervals, multiintervals and the empty interval, but no unbounded ones
b: b.IntervalSet[int]

# The Interval class matches any type of interval (Closed, Open, ClosedOpen, OpenClosed) and will allow unbounded ones as well, but not empty ones
c: b.Interval[int | None]

# The Interval class matches any type of interval (Closed, Open, ClosedOpen, OpenClosed) but will not allow unbounded intervals or empty ones
d: b.Interval[int]

# This matches all atomic intervals as well as the empty one (the empty interval class takes no type argument because it has no bounds)
e: b.Interval[int] | b.Empty

# Some applications strictly use ClosedOpen intervals
f: b.ClosedOpen[int]

# Union sets of closed-open intervals can also be specified
g: b.ClosedOpenSet[int]

# Such classes exist also for closed, open and open-closed intervals
```

When performing operations on intervals their type or their type argument may change.
For example, taking the complement of any `Interval[int]` will give you an `IntervalSet[int | None]`.

```python
>>> x = ~b.Closed(0, 10)
>>> print(x)
⟨-inf ; 0) | (10 ; +inf⟩

>>> reveal_type(x)  # Revealed type is beset.IntervalSet[int | None]
```

Getting rid of the union with `None` can be accomplished using the intersection operation.
Continuing the example:

```python
>>> y = x & b.Closed(-100, 100)
>>> print(y)
[-100 ; 0) | (10 ; 100]

>>> reveal_type(y)  # Revealed type is beset.IntervalSet[int]
```


## Other libraries

There are already excellent Python libraries available that provide interval data structures and operations.
They may suit your use case better, depending on your needs.

- [`portion`](https://github.com/AlexandreDecan/portion)
  - A very mature interval library (and one of the main inspirations for `beset`)
- [`intervaltree`](https://github.com/chaimleib/intervaltree)
  - Focused on speed and performance for large interval sets
