from abc import ABC
from itertools import product
from typing import List, Iterable, Tuple

from .types import PieceColor, File, Rank, Position, PieceKind, Piece


PiecePositionSource = Iterable[Tuple[Piece, Position]]


class BoardSetup(ABC):
    """
    Abstract class that represents a way to position pieces on a board.

    Iterating over instance of this class yields tuples `(piece, position)`.
    """

    def __iter__(self):
        return self.items()

    def items(self) -> PiecePositionSource:
        pass


class StandardBoardSetup(BoardSetup):
    """Standard piece setup according to FIDE."""

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

    def items(self) -> PiecePositionSource:
        yield from self._pawns()
        yield from self._heavy_pieces()

    def _pawns(self) -> PiecePositionSource:
        for color in PieceColor:
            for position in self._starting_pawn_positions(color):
                yield Piece(PieceKind.PAWN, color), position

    def _heavy_pieces(self) -> PiecePositionSource:
        for color, file in product(PieceColor, File):
            rank = self._heavy_piece_rank_for_color(color)
            piece_kind = self._piece_kind_for_file(file)
            yield Piece(piece_kind, color), Position(file, rank)

    def _starting_pawn_positions(self, color: PieceColor) -> List[Position]:
        rank = self._pawn_rank_for_color(color)
        return [Position(file, rank) for file in File]

    @staticmethod
    def _pawn_rank_for_color(color: PieceColor) -> Rank:
        return Rank({PieceColor.WHITE: 2, PieceColor.BLACK: 7}[color])

    @staticmethod
    def _heavy_piece_rank_for_color(color: PieceColor) -> Rank:
        return Rank({PieceColor.WHITE: 1, PieceColor.BLACK: 8}[color])

    @classmethod
    def _piece_kind_for_file(cls, file: File) -> PieceKind:
        return cls._default_piece_locations[file]
