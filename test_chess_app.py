import chess

from chess_app import AVATARS, choose_move, evaluate


def test_ai_returns_a_legal_move_without_mutating_the_position():
    board = chess.Board()
    original_fen = board.fen()

    move = choose_move(board, depth=1, noise=0)

    assert move in board.legal_moves
    assert board.fen() == original_fen


def test_ai_returns_no_move_for_a_finished_game():
    board = chess.Board()
    for san in ("f3", "e5", "g4", "Qh4#"):
        board.push_san(san)

    assert board.is_checkmate()
    assert choose_move(board, depth=1, noise=0) is None


def test_evaluation_is_relative_to_side_to_move():
    board = chess.Board()
    for square, piece in list(board.piece_map().items()):
        if piece.color == chess.BLACK and piece.piece_type != chess.KING:
            board.remove_piece_at(square)

    board.turn = chess.WHITE
    white_to_move = evaluate(board)
    board.turn = chess.BLACK
    black_to_move = evaluate(board)

    assert white_to_move > 0
    assert black_to_move == -white_to_move


def test_ai_profiles_have_progressively_higher_search_depths():
    depths = [details["depth"] for details in AVATARS.values()]

    assert min(depths) == 1
    assert max(depths) == 4
    assert len(set(depths)) >= 4


def test_standard_chess_castling_is_available_when_path_is_clear():
    board = chess.Board("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")

    assert chess.Move.from_uci("e1g1") in board.legal_moves
    assert chess.Move.from_uci("e1c1") in board.legal_moves


def test_en_passant_is_legal_only_after_the_two_square_pawn_move():
    board = chess.Board()
    for san in ("e4", "a6", "e5", "d5"):
        board.push_san(san)
    en_passant = chess.Move.from_uci("e5d6")

    assert en_passant in board.legal_moves
    assert board.is_en_passant(en_passant)
    board.push(en_passant)
    assert board.piece_at(chess.D6) == chess.Piece(chess.PAWN, chess.WHITE)
    assert board.piece_at(chess.D5) is None


def test_promotion_exposes_all_four_piece_choices():
    board = chess.Board("7k/P7/8/8/8/8/8/7K w - - 0 1")
    promotions = {move.promotion for move in board.legal_moves if move.from_square == chess.A7}

    assert promotions == {chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT}


def test_stalemate_and_insufficient_material_are_draws():
    stalemate = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    kings_only = chess.Board("k7/8/1K6/8/8/8/8/8 w - - 0 1")

    assert stalemate.is_stalemate()
    assert stalemate.is_game_over()
    assert kings_only.is_insufficient_material()
    assert kings_only.is_game_over()
