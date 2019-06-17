from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from functools import lru_cache
import re
from typing import List, NamedTuple
import unicodedata


class PieceColor(Enum):
    BLACK = auto()
    WHITE = auto()


class InvalidNotationError(Exception):
    pass


class File(IntEnum):
    A = 0
    B = 1
    C = 2
    D = 3
    E = 4
    F = 5
    G = 6
    H = 7

    def __repr__(self):
        return f"File.{self.name}"

    @classmethod
    def from_algebraic_notation(cls, file_letter: str) -> 'File':
        for file in File:
            if file_letter.lower() == file.name.lower():
                return file
        raise InvalidNotationError(f"No such file: {file_letter}")


Rank = int


class Location(NamedTuple):
    file: File
    rank: Rank

    def __repr__(self):
        return f"Location({self.file.name}, {self.rank})"

    def as_index(self) -> int:
        return (self.rank - 1) * 8 + self.file.value

    @classmethod
    def from_algebraic_notation(cls, location: str) -> 'Location':
        raw_file, raw_rank = location
        return Location(
            file=File.from_algebraic_notation(raw_file),
            rank=Rank(raw_rank),
        )


class PieceKind(Enum):
    PAWN = "P"
    KNIGHT = "N"
    QUEEN = "Q"
    KING = "K"
    ROOK = "R"
    BISHOP = "B"

    def __repr__(self):
        return f"PieceKind({self.name})"

    @classmethod
    def from_letter(cls, letter: str) -> 'PieceKind':
        if not letter:
            return PieceKind.PAWN
        return PieceKind(letter.upper())


class Piece(NamedTuple):
    kind: PieceKind
    color: PieceColor = None

    def __str__(self):
        return f"{self.color.name}, {self.kind.name}"

    def __repr__(self):
        return f"Piece({str(self)})"

    @lru_cache(maxsize=16)
    def to_unicode(self):
        if self.kind == PieceKind.EMPTY:
            return " "
        character_name = f"{self.color.name} CHESS {self.kind.name}"
        return unicodedata.lookup(character_name)


@dataclass
class Move:

    @classmethod
    def from_algebraic_notation(cls, move: str) -> 'Move':
        for move_subclass in cls.__subclasses__():
            try:
                return move_subclass.from_algebraic_notation(move)
            except InvalidNotationError:
                pass
        raise InvalidNotationError


@dataclass
class RegularMove(Move):
    piece_kind: PieceKind = None
    departure: Location = None
    destination: Location = None
    with_capture: bool = False

    _regex = re.compile(
        """
        (?P<piece_kind>[KQNBR])?
        (?P<departure>[a-h][1-8])?
        (?P<capture>[x:])?
        (?P<destination>[a-h][1-8])
        """,
        flags=re.VERBOSE
    )

    @classmethod
    def from_algebraic_notation(cls, move: str) -> 'Move':
        match = cls._regex.match(move)
        if not match:
            raise InvalidNotationError

        move_dict = match.groupdict()
        piece_kind = PieceKind.from_letter(move_dict["piece_kind"])
        if move_dict['departure']:
            departure = Location.from_algebraic_notation(move_dict['departure'])
        else:
            departure = None
        destination = Location.from_algebraic_notation(move_dict['destination'])
        with_capture = bool(move_dict['capture'])

        return RegularMove(piece_kind, departure, destination, with_capture)


@dataclass
class CastlingMove(Move):
    kingside: bool

    _castling_letters = "0", "O"

    @classmethod
    def from_algebraic_notation(cls, move: str) -> 'Move':
        for letter in cls._castling_letters:
            if move == cls._kingside_pattern(letter=letter):
                return CastlingMove(kingside=True)
            if move == cls._queenside_pattern(letter=letter):
                return CastlingMove(kingside=False)

        raise InvalidNotationError

    @classmethod
    def _kingside_pattern(cls, letter: str) -> str:
        return f"{letter}-{letter}"

    @classmethod
    def _queenside_pattern(cls, letter: str) -> str:
        return f"{letter}-{letter}-{letter}"


class Board:

    _default_piece_locations = {
        File.A: PieceKind.ROOK,
        File.B: PieceKind.KNIGHT,
        File.C: PieceKind.BISHOP,
        File.D: PieceKind.QUEEN,
        File.E: PieceKind.KING,
        File.F: PieceKind.BISHOP,
        File.G: PieceKind.KNIGHT,
        File.H: PieceKind.ROOK,
    }

    def __init__(self):
        self._pieces: List[Piece] = [None] * 64

    def __iter__(self):
        return iter(self._pieces)

    def piece_at(self, location: Location):
        return self._pieces[location.as_index()]

    def put_piece(self, piece: Piece, location: Location):
        self._pieces[location.as_index()] = piece

    def populate(self):
        for rank, color in [(2, PieceColor.WHITE), (7, PieceColor.BLACK)]:
            for file in File:
                self.put_piece(Piece(PieceKind.PAWN, color), Location(file, rank))

        for rank, color in [(1, PieceColor.WHITE), (8, PieceColor.BLACK)]:
            for file, piece_kind in self._default_piece_locations.values():
                self.put_piece(Piece(piece_kind, color), Location(file, rank))
