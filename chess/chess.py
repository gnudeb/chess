from dataclasses import dataclass
from enum import Enum, auto, IntEnum
from functools import lru_cache
from itertools import product
import re
from typing import List, NamedTuple, Optional, Dict
import unicodedata


from .exceptions import InvalidNotationError, IllegalMoveError
from .util import concatenate


class PieceColor(Enum):
    BLACK = auto()
    WHITE = auto()


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


class Rank(NamedTuple):
    value: int

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

    def __repr__(self):
        return f"Position({self.file.name}, {self.rank})"

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

    def __repr__(self):
        return f"PieceKind({self.name})"

    @classmethod
    def from_letter(cls, letter: str) -> 'PieceKind':
        if not letter:
            return PieceKind.PAWN
        return PieceKind(letter.upper())


class Piece(NamedTuple):
    kind: PieceKind
    color: PieceColor

    def __str__(self):
        return f"{self.color.name}, {self.kind.name}"

    def __repr__(self):
        return f"Piece({str(self)})"

    @lru_cache(maxsize=16)
    def to_unicode(self):
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
    destination: Position
    departure: Optional[Position] = None
    piece_kind: Optional[PieceKind] = None
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
        departure: Optional[Position] = None
        if move_dict['departure']:
            departure = Position.from_algebraic_notation(move_dict['departure'])
        destination = Position.from_algebraic_notation(move_dict['destination'])
        with_capture = bool(move_dict['capture'])

        return RegularMove(destination, departure, piece_kind, with_capture)


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
        self._pieces: Dict[Position, Piece] = {}
        self._set_up_new_game()

    def __iter__(self):
        return iter(self._pieces)

    def piece_at(self, position: Position) -> Optional[Piece]:
        return self._pieces.get(position, None)

    def place_piece(self, piece: Piece, position: Position):
        self._pieces[position] = piece

    def move_piece(self, origin: Position, destination: Position):
        self.place_piece(
            piece=self._remove_piece_at(origin),
            position=destination,
        )

    def _remove_piece_at(self, position: Position) -> Piece:
        try:
            return self._pieces.pop(position)
        except KeyError:
            raise IllegalMoveError(f"No piece present at {position}")

    def _set_up_new_game(self):
        self._place_pawns()
        self._place_heavy_pieces()

    def _place_heavy_pieces(self):
        for color, file in product(PieceColor, File):
            rank = self._heavy_piece_rank_for_color(color)
            piece_kind = self._piece_kind_for_file(file)
            self.place_piece(Piece(piece_kind, color), Position(file, rank))

    def _place_pawns(self):
        for color in PieceColor:
            for position in self._starting_pawn_positions(color):
                self.place_piece(Piece(PieceKind.PAWN, color), position)

    def _starting_pawn_positions(self, color: PieceColor) -> List[Position]:
        rank = self._pawn_rank_for_color(color)
        return [Position(file, rank) for file in File]

    @concatenate
    def to_unicode(self):
        for position in Position.every():
            piece = self.piece_at(position)
            if piece is not None:
                yield piece.to_unicode()
            else:
                yield " "
            if position.file == File.H and position.rank.value is not 1:
                yield "\n"

    @staticmethod
    def _pawn_rank_for_color(color: PieceColor) -> Rank:
        return Rank({PieceColor.WHITE: 2, PieceColor.BLACK: 7}[color])

    @staticmethod
    def _heavy_piece_rank_for_color(color: PieceColor) -> Rank:
        return Rank({PieceColor.WHITE: 1, PieceColor.BLACK: 8}[color])

    @classmethod
    def _piece_kind_for_file(cls, file: File) -> PieceKind:
        return cls._default_piece_locations[file]
