# from __future__ import annotations
#
#
# class FruitMeta(type):
#     def __call__(cls, *args, **kwargs):
#         if cls is Fruit:
#             fruit_type = kwargs.pop("fruit_type", None)
#
#             if fruit_type is None:
#                 fruit_type, *args = args
#
#             try:
#                 cls = Fruit._registry[fruit_type.lower()]
#             except KeyError:
#                 raise ValueError(f"Unknown fruit type: {fruit_type!r}")
#
#         return super(FruitMeta, cls).__call__(*args, **kwargs)
#
#
# class Fruit(metaclass=FruitMeta):
#     _registry: dict[str, type["Fruit"]] = {}
#
#     def __init_subclass__(cls, *, kind: str | None = None, **kwargs):
#         super().__init_subclass__(**kwargs)
#         if kind is not None:
#             Fruit._registry[kind.lower()] = cls
#
#     def __init__(self, fruit_type: str, color: str):
#         # Never actually called.
#         # Exists only to document/type the Fruit constructor.
#         raise NotImplementedError
#
#
# class Apple(Fruit, kind="apple"):
#     def __init__(self, color: str):
#         self.color = color
#
#
# class Pear(Fruit, kind="pear"):
#     def __init__(self, color: str):
#         self.color = color
#
#
# class Banana(Fruit, kind="banana"):
#     def __init__(self, color: str):
#         self.color = color
#
# a = Fruit(color="red", fruit_type="apple")
# p = Fruit("pear", "green")
# b = Fruit("banana", "yellow")
#
# print(type(a).__name__, a.color)  # Apple red
# print(type(p).__name__, p.color)  # Pear green
# print(type(b).__name__, b.color)  # Banana yellow
#
# a2 = Apple(color="dark red")
# print(type(a2).__name__, a2.color)  # Apple dark red
