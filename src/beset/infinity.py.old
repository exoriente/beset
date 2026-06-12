from abc import ABC
from typing import TypeVar, cast

S = TypeVar("S", bound="_Singleton")


class _Singleton(ABC):
    __instance: "_Singleton | None" = None

    def __new__(cls: type[S]) -> S:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)  # pyright:ignore[reportArgumentType]
        return cast(S, cls.__instance)


class Infinity(_Singleton):
    def __neg__(self) -> "NegativeInfinity":
        return NegativeInfinity()

    def __eq__(self, other: object) -> bool:
        match other:
            case Infinity():
                return True
            case float() if other == float("inf"):
                return True
            case _:
                return False

    def __hash__(self) -> int:
        return hash(float("inf"))

    def __lt__(self, other: object) -> bool:
        return False

    def __gt__(self, other: object) -> bool:
        match other:
            case Infinity():
                return False
            case float() if other == float("inf"):
                return False
            case _:
                return True

    def __repr__(self) -> str:
        return "INF"

    def __str__(self) -> str:
        return "∞"


class NegativeInfinity(_Singleton):
    def __neg__(self) -> "Infinity":
        return INF

    def __eq__(self, other: object) -> bool:
        match other:
            case NegativeInfinity():
                return True
            case float() if other == float("-inf"):
                return True
            case _:
                return False

    def __hash__(self) -> int:
        return hash(float("-inf"))

    def __lt__(self, other: object) -> bool:
        match other:
            case NegativeInfinity():
                return False
            case float() if other == float("-inf"):
                return False
            case _:
                return True

    def __gt__(self, other: object) -> bool:
        return False

    def __repr__(self) -> str:
        return "-INF"

    def __str__(self) -> str:
        return "-∞"


InfinityTypes = Infinity | NegativeInfinity
INF = Infinity()
