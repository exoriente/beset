from abc import ABC
from typing import Self


class _Singleton(ABC):
    __instance: Self | None = None

    def __new__(cls) -> Self:
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
        return cls.__instance


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
        return Infinity()

    def __eq__(self, other: object) -> bool:
        match other:
            case NegativeInfinity():
                return True
            case float() if other == float("-inf"):
                return True
            case _:
                return False

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
