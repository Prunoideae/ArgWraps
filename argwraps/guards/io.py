from .primitive import Str
from os import path


class File(Str.__class__):
    def test(self, raw: str) -> bool:
        return path.isfile(raw)

    def transform(self, raw: str) -> str:
        return path.abspath(raw)


class Dir(Str.__class__):
    def test(self, raw: str) -> bool:
        return path.isdir(raw)

    def transform(self, raw: str) -> str:
        return path.abspath(raw)
