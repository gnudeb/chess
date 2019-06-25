from typing import Collection, List
import unittest

from chess.chess import Board
from chess.types import PieceColor, File, Rank, Position, PieceKind, Piece


class TestPosition(unittest.TestCase):

    def test_algebraic_notation_constructor(self):
        self._given_position_is("e2")

        self._then_file_is("e")
        self._then_rank_is(2)

    def test_there_are_64_unique_positions(self):
        self._given_all_positions()

        self._then_number_of_unique_positions_is(64)

    def _given_position_is(self, position: str):
        self.position: Position = Position.from_algebraic_notation(position)

    def _then_file_is(self, file: str):
        self.assertEqual(self.position.file, File.from_algebraic_notation(file))

    def _then_rank_is(self, rank: int):
        self.assertEqual(self.position.rank, Rank(rank))

    def _given_all_positions(self):
        self.positions: Collection[Position] = list(Position.every())

    def _then_number_of_unique_positions_is(self, number: int):
        self.assertEqual(number, len(set(self.positions)))


class TestBoard(unittest.TestCase):

    def setUp(self):
        self.selected_pieces: List[Piece] = []

    def test_iterating_over_board_yields_pieces(self):
        self._given_board_with_pieces()

        self._then_every_board_value_is_instance_of(Piece)

    def test_moving_a_piece(self):
        self._given_board_with_pieces()

        self._when_piece_is_moved("e2", "e4")

        self._then_position_is_empty("e2")
        self._then_piece_is_present_at("e4")

    def test_new_board_has_32_pieces(self):
        self._given_board_with_pieces()

        self._then_number_of_pieces_is(32)

    def test_every_white_pawn_is_on_rank_2(self):
        self._given_board_with_pieces()

        self._when_selected_pieces_are(
            Piece(PieceKind.PAWN, PieceColor.WHITE)
        )

        self._then_all_selected_pieces_are_on_rank(2)

    def test_every_black_pawn_is_on_rank_7(self):
        self._given_board_with_pieces()

        self._when_selected_pieces_are(
            Piece(PieceKind.PAWN, PieceColor.BLACK)
        )

        self._then_all_selected_pieces_are_on_rank(7)

    def _given_board_with_pieces(self):
        self.board = Board()

    def _when_piece_is_moved(self, origin: str, destination: str):
        self.board.move_piece(
            origin=Position.from_algebraic_notation(origin),
            destination=Position.from_algebraic_notation(destination),
        )

    def _then_position_is_empty(self, position: str):
        self.assertFalse(self.board.has_piece_at(
            Position.from_algebraic_notation(position)
        ))

    def _then_piece_is_present_at(self, position: str):
        self.assertTrue(self.board.has_piece_at(
            Position.from_algebraic_notation(position)
        ))

    def _then_number_of_pieces_is(self, number: int):
        self.assertEqual(number, len(list(self.board)))

    def _then_every_board_value_is_instance_of(self, cls):
        for object_ in self.board:
            self.assertIsInstance(object_, cls)

    def _when_selected_pieces_are(self, matched_piece: Piece):
        for piece in self.board:
            if piece == matched_piece:
                self.selected_pieces.append(piece)

    def _then_all_selected_pieces_are_on_rank(self, rank: int):
        for piece in self.selected_pieces:
            self.assertEqual(rank, self.board.position_of(piece).rank.value)


if __name__ == '__main__':
    unittest.main()
