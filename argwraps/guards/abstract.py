from typing import Generic, TypeVar

T = TypeVar('T')


class AbstractGuard(Generic[T]):
    def __init__(self) -> None:
        pass

    def test(self, raw: str) -> bool:
        pass

    def transform(self, raw: str) -> T:
        pass
