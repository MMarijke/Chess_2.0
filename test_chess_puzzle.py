import pytest
from chess_puzzle import *

# Test location2index function
def test_location2index_basic():
    assert location2index("e2") == (5, 2)
    assert location2index("a1") == (1, 1)
    assert location2index("z26") == (26, 26)
    assert location2index("b10") == (2, 10)
    assert location2index("c3") == (3, 3)

def test_location2index_edge_cases():
    with pytest.raises(ValueError):
        location2index("1a")  # Invalid format
    with pytest.raises(ValueError):
        location2index("aa")  # Invalid row
    with pytest.raises(ValueError):
        location2index("z27")  # Row out of range
    with pytest.raises(ValueError):
        location2index("@1")  # Invalid column
    with pytest.raises(ValueError):
        location2index("")  # Empty string

# Test index2location function
def test_index2location_basic():
    assert index2location(5, 2) == "e2"
    assert index2location(1, 1) == "a1"
    assert index2location(26, 26) == "z26"
    assert index2location(2, 10) == "b10"
    assert index2location(3, 3) == "c3"

def test_index2location_edge_cases():
    with pytest.raises(ValueError):
        index2location(0, 1)  # x out of range
    with pytest.raises(ValueError):
        index2location(1, 0)  # y out of range
    with pytest.raises(ValueError):
        index2location(27, 1)  # x out of range
    with pytest.raises(ValueError):
        index2location(1, 27)  # y out of range
    with pytest.raises(ValueError):
        index2location(-1, 5)  # negative coordinates

# Test is_piece_at function
def test_is_piece_at_basic():
    wn1 = Knight(1, 2, True)
    bn1 = Knight(1, 1, False)
    B1 = (5, [wn1, bn1])
    
    assert is_piece_at(1, 2, B1) == True
    assert is_piece_at(1, 1, B1) == True
    assert is_piece_at(2, 2, B1) == False
    assert is_piece_at(3, 3, B1) == False
    assert is_piece_at(5, 5, B1) == False

def test_is_piece_at_empty_board():
    B_empty = (5, [])
    assert is_piece_at(1, 1, B_empty) == False
    assert is_piece_at(3, 3, B_empty) == False
    assert is_piece_at(5, 5, B_empty) == False

def test_is_piece_at_multiple_pieces():
    wn1 = Knight(1, 2, True)
    wn2 = Knight(5, 2, True)
    wk1 = King(3, 5, True)
    bn1 = Knight(1, 1, False)
    bk1 = King(2, 3, False)
    B1 = (5, [wn1, bn1, wn2, wk1, bk1])
    
    assert is_piece_at(1, 2, B1) == True
    assert is_piece_at(5, 2, B1) == True
    assert is_piece_at(3, 5, B1) == True
    assert is_piece_at(4, 4, B1) == False

# Test piece_at function
def test_piece_at_basic():
    wn1 = Knight(1, 2, True)
    bn1 = Knight(1, 1, False)
    B1 = (5, [wn1, bn1])
    
    p1 = piece_at(1, 2, B1)
    assert isinstance(p1, Knight)
    assert p1.pos_x == 1 and p1.pos_y == 2 and p1.side == True
    
    p2 = piece_at(1, 1, B1)
    assert isinstance(p2, Knight)
    assert p2.pos_x == 1 and p2.pos_y == 1 and p2.side == False

def test_piece_at_king():
    wk1 = King(3, 5, True)
    bk1 = King(2, 3, False)
    B1 = (5, [wk1, bk1])
    
    p1 = piece_at(3, 5, B1)
    assert isinstance(p1, King)
    assert p1.pos_x == 3 and p1.pos_y == 5 and p1.side == True
    
    p2 = piece_at(2, 3, B1)
    assert isinstance(p2, King)
    assert p2.pos_x == 2 and p2.pos_y == 3 and p2.side == False

def test_piece_at_no_piece():
    wn1 = Knight(1, 2, True)
    B1 = (5, [wn1])
    
    with pytest.raises(ValueError):
        piece_at(2, 2, B1)
    with pytest.raises(ValueError):
        piece_at(5, 5, B1)

# Test Knight.can_reach function
def test_knight_can_reach_valid_moves():
    knight = Knight(3, 3, True)
    B = (8, [knight])
    
    # Valid knight moves (L-shape)
    assert knight.can_reach(5, 4, B) == True  # 2 right, 1 up
    assert knight.can_reach(5, 2, B) == True  # 2 right, 1 down
    assert knight.can_reach(1, 4, B) == True  # 2 left, 1 up
    assert knight.can_reach(1, 2, B) == True  # 2 left, 1 down
    assert knight.can_reach(4, 5, B) == True  # 1 right, 2 up

def test_knight_can_reach_invalid_moves():
    knight = Knight(3, 3, True)
    B = (8, [knight])
    
    # Invalid moves
    assert knight.can_reach(3, 3, B) == False  # Same position
    assert knight.can_reach(4, 4, B) == False  # Diagonal
    assert knight.can_reach(3, 5, B) == False  # Straight line
    assert knight.can_reach(6, 6, B) == False  # Too far

def test_knight_can_reach_blocked_by_same_side():
    knight = Knight(3, 3, True)
    blocking_piece = Knight(5, 4, True)  # Same side
    B = (8, [knight, blocking_piece])
    
    assert knight.can_reach(5, 4, B) == False  # Blocked by same side

def test_knight_can_reach_capture_opponent():
    knight = Knight(3, 3, True)
    opponent_piece = Knight(5, 4, False)  # Opponent
    B = (8, [knight, opponent_piece])
    
    assert knight.can_reach(5, 4, B) == True  # Can capture opponent

def test_knight_can_reach_out_of_bounds():
    knight = Knight(1, 1, True)
    B = (5, [knight])
    
    assert knight.can_reach(0, 2, B) == False  # Out of bounds
    assert knight.can_reach(-1, 3, B) == False  # Out of bounds
    assert knight.can_reach(6, 2, B) == False  # Out of bounds

def test_knight_cannot_capture_opposing_king():
    white_king = King(1, 1, True)
    knight = Knight(1, 2, True)
    black_king = King(2, 4, False)
    B = (5, [white_king, knight, black_king])

    assert knight.can_reach(2, 4, B)  # Attack geometry still sees the king.
    assert not knight.can_move_to(2, 4, B)  # Legal moves may not capture it.

def test_king_cannot_capture_opposing_king():
    white_king = King(1, 1, True)
    black_king = King(2, 1, False)
    B = (5, [white_king, black_king])

    assert not white_king.can_move_to(2, 1, B)

def test_piece_cannot_move_while_leaving_own_king_in_check():
    white_king = King(1, 1, True)
    knight = Knight(5, 5, True)
    black_king = King(5, 4, False)
    checking_knight = Knight(3, 2, False)
    B = (5, [white_king, knight, black_king, checking_knight])

    assert knight.can_reach(4, 3, B)
    assert not knight.can_move_to(4, 3, B)

# Test King.can_reach function
def test_king_can_reach_valid_moves():
    king = King(3, 3, True)
    B = (8, [king])
    
    # Valid king moves (one square in any direction)
    assert king.can_reach(4, 3, B) == True  # Right
    assert king.can_reach(2, 3, B) == True  # Left
    assert king.can_reach(3, 4, B) == True  # Up
    assert king.can_reach(3, 2, B) == True  # Down
    assert king.can_reach(4, 4, B) == True  # Diagonal

def test_king_can_reach_invalid_moves():
    king = King(3, 3, True)
    B = (8, [king])
    
    # Invalid moves
    assert king.can_reach(3, 3, B) == False  # Same position
    assert king.can_reach(5, 3, B) == False  # Too far
    assert king.can_reach(3, 5, B) == False  # Too far
    assert king.can_reach(5, 5, B) == False  # Too far diagonal

def test_king_can_reach_blocked_by_same_side():
    king = King(3, 3, True)
    blocking_piece = Knight(4, 3, True)  # Same side
    B = (8, [king, blocking_piece])
    
    assert king.can_reach(4, 3, B) == False  # Blocked by same side

def test_king_can_reach_capture_opponent():
    king = King(3, 3, True)
    opponent_piece = Knight(4, 3, False)  # Opponent
    B = (8, [king, opponent_piece])
    
    assert king.can_reach(4, 3, B) == True  # Can capture opponent

def test_king_can_reach_out_of_bounds():
    king = King(1, 1, True)
    B = (5, [king])
    
    assert king.can_reach(0, 1, B) == False  # Out of bounds
    assert king.can_reach(1, 0, B) == False  # Out of bounds
    assert king.can_reach(6, 1, B) == False  # Out of bounds

# Test is_check function
def test_is_check_true():
    wk = King(4, 5, True)
    bn = Knight(2, 4, False)  # Black knight attacking white king
    B = (5, [wk, bn])
    
    assert is_check(True, B) == True

def test_is_check_false():
    wk = King(4, 5, True)
    bn = Knight(1, 1, False)  # Black knight not attacking white king
    B = (5, [wk, bn])
    
    assert is_check(True, B) == False

def test_is_check_no_king():
    bn = Knight(1, 1, False)
    B = (5, [bn])
    
    assert is_check(True, B) == False  # No white king

def test_is_check_multiple_pieces():
    wk = King(3, 3, True)
    wn = Knight(1, 1, True)
    bk = King(5, 5, False)
    bn = Knight(1, 2, False)  # Can reach white king
    B = (5, [wk, wn, bk, bn])
    
    assert is_check(True, B) == True

def test_is_check_king_attacking():
    wk = King(3, 3, True)
    bk = King(4, 3, False)  # Black king next to white king
    B = (5, [wk, bk])
    
    assert is_check(True, B) == True
    assert is_check(False, B) == True  # Both kings in check

# Test Knight.move_to function
def test_knight_move_to_empty_square():
    knight = Knight(1, 2, True)
    other_piece = Knight(5, 5, False)
    B = (5, [knight, other_piece])
    
    new_board = knight.move_to(2, 4, B)
    size, pieces = new_board
    
    assert size == 5
    assert len(pieces) == 2
    
    # Check that knight moved
    moved_knight = None
    for piece in pieces:
        if isinstance(piece, Knight) and piece.side == True:
            moved_knight = piece
            break
    
    assert moved_knight is not None
    assert moved_knight.pos_x == 2 and moved_knight.pos_y == 4

def test_knight_move_to_capture():
    knight = Knight(1, 2, True)
    enemy_knight = Knight(2, 4, False)
    B = (5, [knight, enemy_knight])
    
    new_board = knight.move_to(2, 4, B)
    size, pieces = new_board
    
    assert size == 5
    assert len(pieces) == 1  # Enemy piece captured
    
    # Check that only white knight remains
    remaining_piece = pieces[0]
    assert isinstance(remaining_piece, Knight)
    assert remaining_piece.side == True
    assert remaining_piece.pos_x == 2 and remaining_piece.pos_y == 4

def test_knight_move_to_preserves_other_pieces():
    knight = Knight(1, 2, True)
    other_knight = Knight(5, 5, True)
    enemy_king = King(3, 3, False)
    B = (5, [knight, other_knight, enemy_king])
    
    new_board = knight.move_to(2, 4, B)
    size, pieces = new_board
    
    assert size == 5
    assert len(pieces) == 3  # All pieces preserved except moving knight is replaced
    
    # Check pieces are correct
    piece_positions = [(p.pos_x, p.pos_y, type(p), p.side) for p in pieces]
    expected_positions = [(2, 4, Knight, True), (5, 5, Knight, True), (3, 3, King, False)]
    
    for expected in expected_positions:
        found = False
        for actual in piece_positions:
            if (actual[0], actual[1], actual[2], actual[3]) == expected:
                found = True
                break
        assert found, f"Expected piece {expected} not found in {piece_positions}"

# Test King.move_to function
def test_king_move_to_empty_square():
    king = King(3, 3, True)
    other_piece = Knight(5, 5, False)
    B = (5, [king, other_piece])
    
    new_board = king.move_to(3, 4, B)
    size, pieces = new_board
    
    assert size == 5
    assert len(pieces) == 2
    
    # Check that king moved
    moved_king = None
    for piece in pieces:
        if isinstance(piece, King) and piece.side == True:
            moved_king = piece
            break
    
    assert moved_king is not None
    assert moved_king.pos_x == 3 and moved_king.pos_y == 4

def test_king_move_to_capture():
    king = King(3, 3, True)
    enemy_knight = Knight(3, 4, False)
    B = (5, [king, enemy_knight])
    
    new_board = king.move_to(3, 4, B)
    size, pieces = new_board
    
    assert size == 5
    assert len(pieces) == 1  # Enemy piece captured
    
    # Check that only white king remains
    remaining_piece = pieces[0]
    assert isinstance(remaining_piece, King)
    assert remaining_piece.side == True
    assert remaining_piece.pos_x == 3 and remaining_piece.pos_y == 4

# Test is_checkmate function
def test_is_checkmate_true():
    # White king at (1,1), checked by black knight at (2,3).
    # Black king at (3,2) controls (2,1),(2,2); black knight at (3,3) controls (1,2) and (2,1).
    # White king has no legal escape squares — genuine checkmate.
    wk = King(1, 1, True)
    bk = King(3, 2, False)
    bn1 = Knight(2, 3, False)
    bn2 = Knight(3, 3, False)
    B = (5, [wk, bk, bn1, bn2])

    assert is_checkmate(True, B) == True

def test_is_checkmate_false_not_in_check():
    wk = King(3, 3, True)
    bn = Knight(1, 1, False)
    B = (5, [wk, bn])
    
    assert is_checkmate(True, B) == False  # Not in check

def test_is_checkmate_false_can_escape():
    wk = King(3, 3, True)
    bn = Knight(1, 2, False)  # Attacking king but king can move
    B = (5, [wk, bn])
    
    assert is_checkmate(True, B) == False  # King can escape

def test_is_checkmate_false_king_can_escape():
    wk = King(3, 3, True)
    wn = Knight(1, 1, True)  # White knight can potentially help
    bn = Knight(1, 2, False)  # Black knight attacking
    B = (5, [wk, wn, bn])

    # The knight check cannot be blocked, but the king has escape squares.
    assert is_checkmate(True, B) == False

def test_is_checkmate_complex_scenario():
    # White king at a1 with black king at c3 and two black knights covering all escape squares
    wk = King(1, 1, True)
    bk = King(3, 3, False)
    bn1 = Knight(2, 3, False)
    bn2 = Knight(3, 2, False)
    B = (5, [wk, bk, bn1, bn2])

    # White king at (1,1): adjacent squares are (1,2), (2,1), (2,2)
    # bk at (3,3) controls (2,2); bn1 at (2,3) controls (1,1) and (4,2); bn2 at (3,2) controls (1,1),(2,4),(4,4),(1,3)
    # This arrangement is not mate: the white king can escape to b1.
    assert is_checkmate(True, B) is False

# Test is_stalemate function
def test_is_stalemate_true():
    # White king not in check but no legal moves
    wk = King(1, 5, True)
    bn1 = Knight(2, 2, False)
    bn2 = Knight(4, 4, False)
    bk = King(3, 4, False)
    B = (5, [wk, bn1, bn2, bk])
    
    assert is_stalemate(True, B) == True

def test_is_stalemate_false_in_check():
    wk = King(3, 3, True)
    bn = Knight(1, 2, False)  # Attacking king
    B = (5, [wk, bn])
    
    assert is_stalemate(True, B) == False  # In check, so not stalemate

def test_is_stalemate_false_has_moves():
    wk = King(3, 3, True)
    bn = Knight(1, 1, False)  # Not attacking, king has moves
    B = (5, [wk, bn])
    
    assert is_stalemate(True, B) == False  # King has legal moves

def test_is_stalemate_with_other_pieces():
    wk = King(1, 1, True)
    wn = Knight(2, 2, True)  # White knight might have moves
    bk = King(5, 5, False)
    B = (5, [wk, wn, bk])
    
    assert is_stalemate(True, B) == False  # White knight likely has moves

def test_is_stalemate_edge_case():
    # King in corner with limited mobility on a 3x3 board
    # Both kings present; white king at (1,1), black king at (3,3) — opposite corners
    wk = King(1, 1, True)
    bk = King(3, 3, False)
    B = (3, [wk, bk])

    # White king at (1,1) can move to (1,2), (2,1), (2,2) — none are controlled by bk at (3,3)
    assert is_stalemate(True, B) == False

# Test read_board function
def test_read_board_valid_file(tmp_path):
    # Create a temporary file with valid board configuration
    board_file = tmp_path / "test_board.txt"
    board_file.write_text("5\nNa2, Ne2, Ne4, Kc5\nNa1, Kb3, Nb4\n")
    
    board = read_board(str(board_file))
    size, pieces = board
    
    assert size == 5
    assert len(pieces) == 7  # 4 white + 3 black pieces
    
    # Check for correct number of kings
    white_kings = sum(1 for p in pieces if isinstance(p, King) and p.side)
    black_kings = sum(1 for p in pieces if isinstance(p, King) and not p.side)
    assert white_kings == 1
    assert black_kings == 1

def test_read_board_invalid_file():
    with pytest.raises(IOError):
        read_board("nonexistent_file.txt")

def test_read_board_invalid_format(tmp_path):
    # Test various invalid formats
    
    # Wrong number of lines
    board_file = tmp_path / "invalid1.txt"
    board_file.write_text("5\nNa2, Kc5\n")  # Missing third line
    with pytest.raises(IOError):
        read_board(str(board_file))
    
    # Invalid board size
    board_file = tmp_path / "invalid2.txt"
    board_file.write_text("2\nKa1\nKb2\n")  # Size too small
    with pytest.raises(IOError):
        read_board(str(board_file))
    
    # Invalid piece type
    board_file = tmp_path / "invalid3.txt"
    board_file.write_text("5\nQa1, Kc5\nKb3\n")  # Q is not valid piece
    with pytest.raises(IOError):
        read_board(str(board_file))

def test_read_board_duplicate_positions(tmp_path):
    board_file = tmp_path / "duplicate.txt"
    board_file.write_text("5\nKa1, Na1\nKb3\n")  # Two pieces at a1
    with pytest.raises(IOError):
        read_board(str(board_file))

def test_read_board_wrong_king_count(tmp_path):
    # No white king
    board_file = tmp_path / "no_white_king.txt"
    board_file.write_text("5\nNa1, Na2\nKb3\n")
    with pytest.raises(IOError):
        read_board(str(board_file))

    # Two white kings
    board_file = tmp_path / "two_white_kings.txt"
    board_file.write_text("5\nKa1, Kb2\nKc3\n")
    with pytest.raises(IOError):
        read_board(str(board_file))

def test_save_board_round_trip(tmp_path):
    board_file = tmp_path / "saved_board.txt"
    board = (5, [King(1, 1, True), Knight(2, 3, True), King(5, 5, False), Knight(4, 2, False)])

    save_board(str(board_file), board)
    restored = read_board(str(board_file))

    def pieces_by_value(state):
        size, pieces = state
        return size, sorted((type(piece).__name__, piece.pos_x, piece.pos_y, piece.side) for piece in pieces)

    assert pieces_by_value(restored) == pieces_by_value(board)

def test_find_black_move_returns_legal_black_move():
    board = (5, [King(1, 1, True), King(5, 5, False), Knight(3, 3, False)])

    piece, to_x, to_y = find_black_move(board)

    assert piece.side is False
    assert piece.can_move_to(to_x, to_y, board)

# Test conf2unicode function
def test_conf2unicode_basic():
    wn1 = Knight(1, 2, True)
    wk1 = King(3, 5, True)
    bn1 = Knight(1, 1, False)
    bk1 = King(2, 3, False)
    B = (5, [wn1, wk1, bn1, bk1])
    
    result = conf2unicode(B)
    lines = result.split('\n')
    
    assert len(lines) == 5  # 5x5 board
    assert len(lines[0]) == 5  # Each line has 5 characters
    
    # Check that pieces appear in correct positions
    # Note: y=1 is bottom row, so we need to check accordingly
    assert '\u2654' in result  # White king
    assert '\u2658' in result  # White knight
    assert '\u265A' in result  # Black king
    assert '\u265E' in result  # Black knight

def test_conf2unicode_empty_board():
    B = (3, [])
    result = conf2unicode(B)
    lines = result.split('\n')
    
    assert len(lines) == 3
    for line in lines:
        assert len(line) == 3
        assert all(c == '\u2001' for c in line)  # All spaces

def test_conf2unicode_single_piece():
    king = King(2, 2, True)
    B = (3, [king])
    
    result = conf2unicode(B)
    lines = result.split('\n')
    
    assert len(lines) == 3
    # King at (2,2) should be in the middle of 3x3 board
    # y=2 means second row from bottom, which is lines[1]
    # x=2 means second column, which is index 1
    assert lines[1][1] == '\u2654'

def test_conf2unicode_all_piece_types():
    wk = King(1, 1, True)
    wn = Knight(2, 1, True)
    bk = King(1, 2, False)
    bn = Knight(2, 2, False)
    B = (2, [wk, wn, bk, bn])
    
    result = conf2unicode(B)
    
    # Check all piece types are represented
    assert '\u2654' in result  # White king
    assert '\u2658' in result  # White knight
    assert '\u265A' in result  # Black king
    assert '\u265E' in result  # Black knight

def test_conf2unicode_large_board():
    king = King(10, 10, True)
    B = (15, [king])
    
    result = conf2unicode(B)
    lines = result.split('\n')
    
    assert len(lines) == 15
    for line in lines:
        assert len(line) == 15
