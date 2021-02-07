from types import FunctionType
from typing import Any, TypeVar
from .abstract import AbstractGuard

T = TypeVar('T')


def singleton(fn):
    return fn()


@singleton
class Int(AbstractGuard[int]):

    def __init__(self) -> None:
        super().__init__()

    def test(self, raw) -> bool:
        return type(raw) == int or raw.isdigit()

    def transform(self, raw: str) -> int:
        return int(raw)


class RangedInt(AbstractGuard[int]):

    def __init__(self, min: int, max: int) -> None:
        super().__init__()
        self.__min__ = min
        self.__max__ = max

    def test(self, raw: str) -> bool:
        return (type(raw) == int or raw.isdigit()) and int(raw) >= self.__min__ and int(raw) <= self.__max__

    def transform(self, raw: str) -> int:
        return int(raw)


@singleton
class Str(AbstractGuard[str]):

    def __init__(self) -> None:
        super().__init__()

    def test(self, raw) -> bool:
        return type(raw) == str

    def transform(self, raw: str) -> str:
        return raw


class Custom(AbstractGuard[None]):

    def __init__(self, test: FunctionType, transform: FunctionType) -> None:
        super().__init__()
        self.__test__ = test
        self.__transform__ = transform

    def test(self, raw: str) -> bool:
        return self.__test__(raw)

    def transform(self, raw: str) -> Any:
        return self.__transform__(raw)


@singleton
class Any(AbstractGuard[None]):

    def __init__(self) -> None:
        super().__init__()

    def test(self, raw) -> bool:
        return True

    def transform(self, raw) -> None:
        return raw


@singleton
class Bool(Any.__class__):
    def test(self, raw) -> bool:
        return isinstance(raw, bool)


class Wrap(AbstractGuard[None]):

    def __init__(self, inner: AbstractGuard[T], predicate: FunctionType, map: FunctionType) -> None:
        super().__init__()
        self.__inner__ = inner
        self.__predicate__ = predicate
        self.__map__ = map

    def test(self, raw: str) -> bool:
        return self.__inner__.test(raw) and self.__predicate__(raw)

    def transform(self, raw: str) -> T:
        return self.__map__(self.__inner__.transform(raw))


class Predicate(Wrap):

    def __init__(self, inner: AbstractGuard[T], predicate: FunctionType) -> None:
        super().__init__(inner, predicate, lambda x: x)


class Transform(Wrap):

    def __init__(self, inner: AbstractGuard[T], predicate: FunctionType, map: FunctionType) -> None:
        super().__init__(inner, lambda x: True, map)
