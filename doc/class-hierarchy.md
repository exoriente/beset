# Class hierarchy

The following diagram offers an overview of the different classes and their inheritance relationships.

![Class hierarchy diagram](class-hierarchy.png)

All arrows point from subclasses to their superclasses.

Dotted arrows have a special meaning.
Those arrows indicate that the subclasses inherit from the superclasses, but always introduce `None` into their type argument.
As a concrete example: `LeftOpen[T]` does not inherit from `Open[T]` or `OpenClosed[T]`,
but instead inherits from `Open[T | None]` and `OpenClosed[T | None`.
The result is that `LefOpen[int]` may be used where `Open[int | None]` or `OpenClosed[T | None]` is required, but not where `Open[int]` or `OpenClosed[T]`is specified.


## Overview of classes

### IntervalSet

Any `IntervalSet` is a disjoint union of zero or more atomic intervals.
It supports iteration and slicing over its atomic intervals and supports all set-operations, like union, intersection and many others.
`IntervalSet` places no constraints on the mix of interval types it consists of and its atomic intervals are always simplified and sorted.
What's more, the type of the created object is automatically normalized as explained below.


### Creating interval objects

When using `IntervalSet` to instantiate a new interval set object, the actual object created might not be of the type `IntervalSet`.
Instead, an object of a subclass of `IntervalSet` could be created.

- When creating an `IntervalSet` of zero atomic intervals an instance of type `Empty` will be created
- When creating an `IntervalSet` of one atomic interval an instance of a subtype of `Interval` will be created
- When creating an `IntervalSet` of multiple atomic intervals of the same type an `OpenSet`, `ClosedSet`, `OpenClosedSet` or `CloseOpenSet` will be created, depending on the type of the atomic intervals
- Only when creating an `IntervalSet` of multiple atomic intervals of mixed type a `IntervalSet` will be created. There are exception to this rule. Mixed atomic interval can sometimes combine to subclasses of `IntervalSet` after all. Some examples:
    - `IntervalSet([RightOpen(3), ClosedOpen(5, 8), LeftClosed(10)])` will result in a `ClosedOpenSet` instance  
    - `IntervalSet([RightOpen(3), LeftClosed(10)])` will result in a `ClosedOpenSet` instance as well
    - `IntervalSet([RightOpen(3), Closed(10, 20)])` is not compatible with any subtype and will result in an `IntervalSet`

All `beset` interval classes show this behavior consistently.
For instance, `Open(3, None)` will give `LeftOpen(3)` instead of an instance of the `Open` interval class.
This automatic type normalization behaves in such a way to uphold these guarantees:

- Each interval or interval set can and will be represented by exactly one type
- When using an interval class to create an interval object the resulting object will always have a type that is a subclass of the class used to create it


### OpenSet, ClosedSet, OpenClosedSet, ClosedOpenSet

These classes are restricted versions of `IntervalSet` and behave in the same way, except that they only allow atomic intervals of their associated type or their subtypes. For example, a `ClosedOpenSet` may contain `ClosedOpen` intervals, `RightOpen`, `LeftClosed` and `Unbounded` intervals.

Some details to realize:

- `ClosedOpenSet[int]` can only contain `ClosedOpen[int]` intervals, since `None` bounds are not allowed. Mixing in `RightOpen[int]`, `LeftClosed[int]` and `Unbounded` is only allowed in a `ClosedOpenSet[int | None]`. 
- Any interval set constructed with `Unbounded` as one of its intervals will result in an `Unbounded` interval. So interval sets can never "contain" an `Unbounded` interval, but can be constructed with one, if their type argument allows `None` bounds.


### Empty

This class represents any `IntervalSet` with zero atomic intervals or any empty `Interval`. No value is contained in this interval.
It is not a generic and has no type because it has no bounds.
It inherits from all `IntervalSet` types, regardless of their type argument.
It is not considered atomic, since its interval count is zero and does no implement the `start` or `stop` properties.


### Interval

This is the abstract base class for all atomic intervals.
It can be used to instantiate an atomic interval of one of its subtypes.
For example `Interval(5, 9, left_closed=True, right_closed=False)` will result in `ClosedOpen(5, 9)`.

All objects of the `Interval` type feature the read-only `start` and `stop` properties, which expose their bounds.


### Open, Closed, OpenClosed, ClosedOpen

These concrete atomic intervals 