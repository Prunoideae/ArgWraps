from typing import List
from ..models.abstract import AbstractGuard


class Arg(AbstractGuard):
    '''
    An wrapper for AbstractGuard, to provide additional
    information when instantiating for CLIMatcher to build
    up.
    '''

    def __init__(self, t: AbstractGuard) -> None:
        self.__type__ = t
        self.__required__ = False
        self.__choices__ = None
        self.__default__ = None
        self.__help__ = None
        self.__short__ = None
        self.__long__ = None
        self.__flag__ = None
        self.__meta__ = None
        self.__argtype__ = None

    def test(self, raw: str) -> bool:
        return self.__type__.test(raw)

    def transform(self, raw: str):
        return self.__type__.transform(raw)

    def required(self, b):
        self.__required__ = b
        return self

    def short(self, name):
        self.__short__ = name
        return self

    def long(self, name: str):
        self.__long__ = name
        return self

    def default(self, value: str):
        self.__default__ = value
        return self

    def choices(self, value: List[str]):
        self.__choices__ = value
        return self

    def flag(self, value):
        self.__flag__ = value
        return self

    def help(self, help):
        self.__help__ = help
        return self

    def meta(self, meta):
        self.__meta__ = meta
        return self

    def type(self, type):
        self.__argtype__ = type
        return self
