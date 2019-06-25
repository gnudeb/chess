import re
from dataclasses import dataclass
from typing import Optional

from chess.exceptions import InvalidNotationError
from chess.types import Position, PieceKind


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
    origin: Optional[Position] = None
    piece_kind: Optional[PieceKind] = None
    with_capture: bool = False

    _regex = re.compile(
        """
        (?P<piece_kind>[KQNBR])?
        (?P<origin>[a-h][1-8])?
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
        origin: Optional[Position] = None
        if move_dict['origin']:
            origin = Position.from_algebraic_notation(move_dict['origin'])
        destination = Position.from_algebraic_notation(
            move_dict['destination']
        )
        with_capture = bool(move_dict['capture'])

        return RegularMove(destination, origin, piece_kind, with_capture)


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
