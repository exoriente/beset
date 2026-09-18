# Frequently asked questions

Full disclosure: these questions are not asked frequently, or ever.
But I'd like them to be asked, since I want to give the answers and this seems like a good place to put those answers.


## How come floating point values are members of `int` intervals?

```python
>>> 0.5 in Closed(0, 1)
True
```

This is not so much a feature of the `beset` library as it is the result of the design of the `int` and `float` types.
`beset` will simply check membership like this:

```python
>>> 0 <= 0.5 <= 1
True
```

Effectively an `Interval[int]` is not defined for just integer member values.
It is defined over any value type that supports comparison with the `int` bounds of the interval.

If you really want integer-only intervals, you'll have to use a type that fails comparison with all other types you wish to exclude.


## How come closed intervals in `beset` can be unbounded? Infinite bounds are always open!

```python
x: Closed[int | None] = Closed(1, None)  # [1 ; +inf⟩
# perfectly fine using beset.Closed
```

It is true. The `beset` design of different types of intervals deviates from what is standard practice in mathematics.
In mathematics unbounded intervals are represented as intervals with an open bound of positive or negative infinity.
This makes sense, since _infinity is not a number_ and cannot be included in a conventional interval.

However, `beset` takes a different approach. Unbounded intervals in `beset` simply have no bound on one or both sides.
In the absence of a bound it makes no sense to consider it open or closed on the unbounded side.
In the string representation of unbounded intervals `beset` still yields to convention for clarity's sake and uses `-inf` and `+inf` when there are no bounds, albeit with a special type of bracket.
Open bounds are represented using parentheses `(0 ; 1)`,
closed bounds use square brackets `[0 ; 1]`
and when infinities are used to represent absent bounds angular brackets `⟨-inf ; +inf⟩` (Unicode's _mathematical angle brackets_) are used to show they are considered neither open nor closed.

What's more, special classes are used to represent such intervals.
The class `Unbounded` represents `⟨-inf ; +inf⟩` and has no bounds.
The class `LeftClosed` represents `[x ; +inf⟩` and has only one bound and `RightClosed`, `LeftOpen` and `RightOpen` function in a similar way.
What's more, `LeftClosed[T]` inherits from both `Closed[T | None]` and from `ClosedOpen[T | None]` and can be used where objects of those classes are expected, as long as their type arguments include `None`.


### But why?

This design choice has been made to support code bases that allow only one type of interval.
For instance, many code bases restrict themselves to `ClosedOpen` intervals (and [wisely](https://fhur.me/posts/always-use-closed-open-intervals) so).
However, even when working strictly with `ClosedOpen` intervals there can be use cases to reason about unbounded intervals or to make use of them when manipulating bounded `ClosedOpen` intervals.
To support such use cases `LeftClosed[T]`, `RightOpen[T]` and `Unbounded` inherit from `ClosedOpen[T | None]` and can be used without giving up the guarantees that working with only one kind of interval provides.
The same goes for other bounded and unbounded interval types.
Developers always have the option to restrict code to bounded intervals by avoiding `None` in an interval class's type argument.
