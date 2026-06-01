from abc import ABC


class _Singleton(ABC):
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance


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


Infinities = Infinity | NegativeInfinity
INF = Infinity()
