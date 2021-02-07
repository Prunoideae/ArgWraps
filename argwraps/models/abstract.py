from argwraps.guards.abstract import AbstractGuard
from types import FunctionType
from ..util import _
from typing import Any, Dict
from dataclasses import dataclass
import inspect


class IllegalArgError(Exception):

    def __init__(self, name: str, annotation: object) -> None:
        self.__name__ = name
        self.__annotation__ = annotation

    def __str__(self) -> str:
        return f"Arg {self.__name__} cannot be of class {self.__annotation__.__class__}, which is not instance of AbstractGuard!"


class UnknownParameterError(Exception):

    def __init__(self, name: str, matcher) -> None:
        self.__name__ = name
        self.__matcher__ = matcher

    def __str__(self) -> str:
        return f"Parameter {self.__name__} is not present in matcher {self.__matcher__}"

    def __repr__(self) -> str:
        return self.__str__()


@dataclass(init=False)
class AbstractMatcher():

    def __init__(self, **kwargs) -> None:
        self.__dict__ |= kwargs

    @classmethod
    def inspect(cls, args: dict):
        if hasattr(cls, '__annotations__'):
            guards: Dict[str, AbstractGuard] = {k: v for k, v in cls.__annotations__.items() if isinstance(v, AbstractGuard)}
        else:
            guards = {}
        transformed = {}
        for k, v in args.items():
            if k in guards:
                if not guards[k].test(v):
                    return None
                transformed[k] = guards[k].transform(v)

        return cls(**transformed)

    def wraps(self, fn: FunctionType) -> Dict[str, Any]:
        argspec = inspect.getfullargspec(fn)
        parameter_list = argspec.args + argspec.kwonlyargs
        return {x: self.__dict__[x] for x in parameter_list}

    def call(self, fn: FunctionType) -> Any:
        return fn(**self.wraps(fn))
