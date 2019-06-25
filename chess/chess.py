from dataclasses import dataclass, field
from typing import Dict

from .moves import Move, RegularMove
from .types import PieceColor, File, Position, Piece
from .board_setups import BoardSetup, StandardBoardSetup
from .exceptions import IllegalMoveError
from .util import concatenate


class Board:

    def __init__(self, setup: BoardSetup = None):
        self._pieces: Dict[Position, Piece] = {}
        self._set_up_with(setup or StandardBoardSetup())

    def __iter__(self):
        return iter(self._pieces.values())

    def piece_at(self, position: Position) -> Piece:
        if self.has_piece_at(position):
            return self._pieces[position]
        else:
            raise KeyError(f"No piece present at {position}")

    def place_piece(self, piece: Piece, position: Position):
        self._pieces[position] = piece

    def has_piece_at(self, position: Position) -> bool:
        return position in self._pieces.keys()

    def move_piece(self, origin: Position, destination: Position):
        self.place_piece(
            piece=self._remove_piece_at(origin),
            position=destination,
        )

    def position_of(self, piece: Piece) -> Position:
        """Return a position corresponding to a given piece.

        This method expects only those `Piece` objects that have been fetched
        from this instance of `Board`. This means that calls like
        `board.position_of(Piece(PieceKind.KING, PieceColor.WHITE))`
        will always throw `KeyError`.
        """
        for position, piece_on_board in self._pieces.items():
            if piece_on_board is piece:
                return position
        raise KeyError

    def _set_up_with(self, setup: BoardSetup):
        for piece, position in setup:
            self.place_piece(piece, position)

    def _remove_piece_at(self, position: Position) -> Piece:
        try:
            return self._pieces.pop(position)
        except KeyError:
            raise IllegalMoveError(f"No piece present at {position}")

    @concatenate
    def to_unicode(self):
        for position in Position.every():
            if self.has_piece_at(position):
                yield self.piece_at(position).to_unicode()
            else:
                yield " "
            if position.file == File.H and position.rank.value is not 1:
                yield "\n"


@dataclass
class Game:
    board: Board = field(default_factory=Board)
    current_player: PieceColor = PieceColor.WHITE

    def attempt_move(self, move: Move):
        if isinstance(move, RegularMove):
            self._attempt_regular_move(move)

    def _attempt_regular_move(self, move: RegularMove):
        self._ensure_piece_is_present_at(move.origin)
        self._ensure_player_can_move(self.board.piece_at(move.origin))

        self.board.move_piece(
            origin=move.origin,
            destination=move.destination,
        )

    def _ensure_piece_is_present_at(self, position: Position):
        if not self.board.has_piece_at(position):
            raise IllegalMoveError(
                f"Tried to move piece from {position}, "
                f"but square is empty"
            )

    def _ensure_player_can_move(self, piece: Piece):
        if piece.color != self.current_player:
            raise IllegalMoveError(
                f"Tried to move {piece.color} piece, "
                f"but it is {self.current_player}'s turn"
            )
