import unicodedata
from enum import Enum, auto
from functools import lru_cache
from itertools import product
from typing import NamedTuple

from .exceptions import InvalidNotationError


class PieceColor(Enum):
    BLACK = auto()
    WHITE = auto()

    def __str__(self):
        return self.name.capitalize()


class File(Enum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7

    def __str__(self):
        return self.name.lower()

    @classmethod
    def from_algebraic_notation(cls, file_letter: str) -> 'File':
        for file in File:
            if file_letter.lower() == file.name.lower():
                return file
        raise InvalidNotationError(f"No such file: {file_letter}")


class Rank(NamedTuple):
    value: int

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_algebraic_notation(cls, rank: str) -> 'Rank':
        if not rank.isdigit():
            raise InvalidNotationError(f"Expected digit for rank, got {rank}")
        if not cls.is_valid_value(int(rank)):
            raise InvalidNotationError(
                f"{rank} must be in range 1 to 8 inclusive"
            )

        return Rank(int(rank))

    @classmethod
    def is_valid_value(cls, rank: int) -> bool:
        return 1 <= rank <= 8

    @classmethod
    def every(cls):
        return list(map(Rank, range(1, 9)))


class Position(NamedTuple):
    file: File
    rank: Rank

    def __str__(self):
        return f"{self.file}{self.rank}"

    def as_index(self) -> int:
        return (self.rank.value - 1) * 8 + self.file.value

    @classmethod
    def from_algebraic_notation(cls, location: str) -> 'Position':
        raw_file, raw_rank = location
        return Position(
            file=File.from_algebraic_notation(raw_file),
            rank=Rank.from_algebraic_notation(raw_rank),
        )

    @classmethod
    def every(cls):
        for rank, file in product(reversed(Rank.every()), File):
            yield Position(file, rank)


class PieceKind(Enum):
    PAWN = "P"
    KNIGHT = "N"
    QUEEN = "Q"
    KING = "K"
    ROOK = "R"
    BISHOP = "B"

    def __str__(self):
        return self.name.capitalize()

    @classmethod
    def from_letter(cls, letter: str) -> 'PieceKind':
        if not letter:
            return PieceKind.PAWN
        return PieceKind(letter.upper())


class Piece(NamedTuple):
    kind: PieceKind
    color: PieceColor

    def __str__(self):
        return f"{self.color} {self.kind}"

    @lru_cache(maxsize=16)
    def to_unicode(self):
        character_name = f"{self.color.name} CHESS {self.kind.name}"
        return unicodedata.lookup(character_name)
