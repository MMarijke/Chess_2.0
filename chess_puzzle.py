# Chess Board
import random

def location2index(loc: str) -> tuple[int, int]:
    '''converts chess location to corresponding x and y coordinates'''
    if len(loc) < 2:
        raise ValueError("Invalid location format")
    
    col = loc[0].lower()
    row_str = loc[1:]
    
    if not ('a' <= col <= 'z'):
        raise ValueError("Invalid column")
    
    try:
        row = int(row_str)
    except ValueError:
        raise ValueError("Invalid row")
    
    if not (1 <= row <= 26):
        raise ValueError("Row out of range")
    
    x = ord(col) - ord('a') + 1
    y = row
    
    return (x, y)

def index2location(x: int, y: int) -> str:
    '''converts pair of coordinates to corresponding location'''
    if not (1 <= x <= 26) or not (1 <= y <= 26):
        raise ValueError("Coordinates out of range")
    
    col = chr(ord('a') + x - 1)
    row = str(y)
    
    return col + row

class Piece:
    pos_x : int 
    pos_y : int
    side : bool #True for White and False for Black
    
    def __init__(self, pos_X : int, pos_Y : int, side_ : bool):
        '''sets initial values'''
        self.pos_x = pos_X
        self.pos_y = pos_Y
        self.side = side_

Board = tuple[int, list[Piece]]

def is_piece_at(pos_X : int, pos_Y : int, B: Board) -> bool:
    '''checks if there is piece at coordinates pos_X, pos_Y of board B'''
    size, pieces = B
    for piece in pieces:
        if piece.pos_x == pos_X and piece.pos_y == pos_Y:
            return True
    return False

def piece_at(pos_X : int, pos_Y : int, B: Board) -> Piece:
    '''
    returns the piece at coordinates pos_X, pos_Y of board B 
    assumes some piece at coordinates pos_X, pos_Y of board B is present
    '''
    size, pieces = B
    for piece in pieces:
        if piece.pos_x == pos_X and piece.pos_y == pos_Y:
            return piece
    raise ValueError("No piece at specified coordinates")

class Knight(Piece):
    def __init__(self, pos_X : int, pos_Y : int, side_ : bool):
        '''sets initial values by calling the constructor of Piece'''
        super().__init__(pos_X, pos_Y, side_)
    
    def can_reach(self, pos_X : int, pos_Y : int, B: Board) -> bool:
        '''
        checks if this knight can move to coordinates pos_X, pos_Y
        on board B according to rule [Rule1] and [Rule3]
        '''
        size, pieces = B
        
        # Check if destination is within board bounds
        if not (1 <= pos_X <= size and 1 <= pos_Y <= size):
            return False
        
        # Check knight movement pattern (L-shape)
        dx = abs(pos_X - self.pos_x)
        dy = abs(pos_Y - self.pos_y)
        
        if not ((dx == 2 and dy == 1) or (dx == 1 and dy == 2)):
            return False
        
        # Check Rule3: cannot move to square occupied by same side
        if is_piece_at(pos_X, pos_Y, B):
            target_piece = piece_at(pos_X, pos_Y, B)
            if target_piece.side == self.side:
                return False
        
        return True
    
    def can_move_to(self, pos_X : int, pos_Y : int, B: Board) -> bool:
        '''
        checks if this knight can move to coordinates pos_X, pos_Y
        on board B according to all chess rules
        '''
        # First check basic movement rules
        if not self.can_reach(pos_X, pos_Y, B):
            return False
        
        # Create new board after the move to check Rule4
        new_board = self.move_to(pos_X, pos_Y, B)
        
        # Check if this move would put own king in check (Rule4)
        if is_check(self.side, new_board):
            return False
        
        return True
    
    def move_to(self, pos_X : int, pos_Y : int, B: Board) -> Board:
        '''
        returns new board resulting from move of this knight to coordinates pos_X, pos_Y on board B 
        assumes this move is valid according to chess rules
        '''
        size, pieces = B
        new_pieces = []
        
        # Copy all pieces except the moving knight and any captured piece
        for piece in pieces:
            if piece is self:
                continue  # Skip the moving knight
            if piece.pos_x == pos_X and piece.pos_y == pos_Y:
                continue  # Skip captured piece
            new_pieces.append(piece)
        
        # Add the knight at new position
        new_knight = Knight(pos_X, pos_Y, self.side)
        new_pieces.append(new_knight)
        
        return (size, new_pieces)

class King(Piece):
    def __init__(self, pos_X : int, pos_Y : int, side_ : bool):
        '''sets initial values by calling the constructor of Piece'''
        super().__init__(pos_X, pos_Y, side_)
    
    def can_reach(self, pos_X : int, pos_Y : int, B: Board) -> bool:
        '''checks if this king can move to coordinates pos_X, pos_Y on board B according to rule [Rule2] and [Rule3]'''
        size, pieces = B
        
        # Check if destination is within board bounds
        if not (1 <= pos_X <= size and 1 <= pos_Y <= size):
            return False
        
        # Check king movement pattern (one square in any direction)
        dx = abs(pos_X - self.pos_x)
        dy = abs(pos_Y - self.pos_y)
        
        if not (dx <= 1 and dy <= 1 and (dx != 0 or dy != 0)):
            return False
        
        # Check Rule3: cannot move to square occupied by same side
        if is_piece_at(pos_X, pos_Y, B):
            target_piece = piece_at(pos_X, pos_Y, B)
            if target_piece.side == self.side:
                return False
        
        return True
    
    def can_move_to(self, pos_X : int, pos_Y : int, B: Board) -> bool:
        '''checks if this king can move to coordinates pos_X, pos_Y on board B according to all chess rules'''
        # First check basic movement rules
        if not self.can_reach(pos_X, pos_Y, B):
            return False
        
        # Create new board after the move to check Rule4
        new_board = self.move_to(pos_X, pos_Y, B)
        
        # Check if this move would put own king in check (Rule4)
        if is_check(self.side, new_board):
            return False
        
        return True
    
    def move_to(self, pos_X : int, pos_Y : int, B: Board) -> Board:
        '''
        returns new board resulting from move of this king to coordinates pos_X, pos_Y on board B
        assumes this move is valid according to chess rules
        '''
        size, pieces = B
        new_pieces = []
        
        for piece in pieces:
            if piece is self:
                continue  # Skip the moving king
            if piece.pos_x == pos_X and piece.pos_y == pos_Y:
                continue  # Skip captured piece
            new_pieces.append(piece)
        
        new_king = King(pos_X, pos_Y, self.side)
        new_pieces.append(new_king)
        
        return (size, new_pieces)

def is_check(side: bool, B: Board) -> bool:
    """Returns True if the king of the given side is currently in check on board B."""
    size, pieces = B
    
    king = None
    for piece in pieces:
        if isinstance(piece, King) and piece.side == side:
            king = piece
            break
    
    if king is None:
        return False  # No king found
    
    for piece in pieces:
        if piece.side != side:  # Opponent piece
            if piece.can_reach(king.pos_x, king.pos_y, B):
                return True
    
    return False

def is_checkmate(side: bool, B: Board) -> bool:
    """Returns True if the given side is in checkmate: in check with no legal moves."""
    if not is_check(side, B):
        return False
    
    size, pieces = B
    
    # Check if any piece of the side can make a legal move
    for piece in pieces:
        if piece.side == side:
            for x in range(1, size + 1):
                for y in range(1, size + 1):
                    if piece.can_move_to(x, y, B):
                        return False  # Found a legal move
    
    return True  # No legal moves available while in check

def is_stalemate(side: bool, B: Board) -> bool:
    """Returns True if the given side is in stalemate: not in check but with no legal moves."""
    if is_check(side, B):
        return False
    
    size, pieces = B
    
    # Check if any piece of the side can make a legal move
    for piece in pieces:
        if piece.side == side:
            for x in range(1, size + 1):
                for y in range(1, size + 1):
                    if piece.can_move_to(x, y, B):
                        return False  # Found a legal move
    
    return True  # No legal moves available while not in check

def read_board(filename: str) -> Board:
    """
    Reads a board configuration from a file.
    File format: first line is board size, second line is white pieces,
    third line is black pieces. Pieces are formatted as e.g. 'Ka2, Nb4'.
    Raises IOError if the file is missing or the format is invalid.
    """
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        if len(lines) != 3:
            raise IOError("Invalid file format: must have exactly 3 lines")
        
        try:
            size = int(lines[0].strip())
            if not (3 <= size <= 26):
                raise IOError("Invalid board size: must be between 3 and 26")
        except ValueError:
            raise IOError("Invalid board size format")
        
        pieces = []
        white_king_count = 0
        black_king_count = 0
        occupied_positions = set()
        
        white_line = lines[1].strip()
        if white_line:
            white_pieces_str = [p.strip() for p in white_line.split(',') if p.strip()]
            for piece_str in white_pieces_str:
                if len(piece_str) < 3:
                    raise IOError(f"Invalid piece format: {piece_str}")
                
                piece_type = piece_str[0].upper()
                location = piece_str[1:]
                
                if piece_type not in ['K', 'N']:
                    raise IOError(f"Invalid piece type: {piece_type}")
                
                try:
                    x, y = location2index(location)
                except ValueError as e:
                    raise IOError(f"Invalid location {location}: {e}")
                
                if not (1 <= x <= size and 1 <= y <= size):
                    raise IOError(f"Location {location} is outside board bounds")
                
                if (x, y) in occupied_positions:
                    raise IOError(f"Multiple pieces at location {location}")
                
                occupied_positions.add((x, y))
                
                if piece_type == 'K':
                    pieces.append(King(x, y, True))
                    white_king_count += 1
                else:  # piece_type == 'N'
                    pieces.append(Knight(x, y, True))
        
        black_line = lines[2].strip()
        if black_line:
            black_pieces_str = [p.strip() for p in black_line.split(',') if p.strip()]
            for piece_str in black_pieces_str:
                if len(piece_str) < 3:
                    raise IOError(f"Invalid piece format: {piece_str}")
                
                piece_type = piece_str[0].upper()
                location = piece_str[1:]
                
                if piece_type not in ['K', 'N']:
                    raise IOError(f"Invalid piece type: {piece_type}")
                
                try:
                    x, y = location2index(location)
                except ValueError as e:
                    raise IOError(f"Invalid location {location}: {e}")
                
                if not (1 <= x <= size and 1 <= y <= size):
                    raise IOError(f"Location {location} is outside board bounds")
                
                if (x, y) in occupied_positions:
                    raise IOError(f"Multiple pieces at location {location}")
                
                occupied_positions.add((x, y))
                
                if piece_type == 'K':
                    pieces.append(King(x, y, False))
                    black_king_count += 1
                else:  # piece_type == 'N'
                    pieces.append(Knight(x, y, False))
        
        # Validate exactly one king per side
        if white_king_count != 1:
            raise IOError(f"Invalid number of white kings: {white_king_count} (must be exactly 1)")
        if black_king_count != 1:
            raise IOError(f"Invalid number of black kings: {black_king_count} (must be exactly 1)")
        
        return (size, pieces)
    
    except FileNotFoundError:
        raise IOError(f"File {filename} not found")
    except Exception as e:
        if isinstance(e, IOError):
            raise
        raise IOError(f"Error reading file: {e}")

def save_board(filename: str, B: Board) -> None:
    size, pieces = B
    
    white_pieces = []
    black_pieces = []
    
    for piece in pieces:
        location = index2location(piece.pos_x, piece.pos_y)
        if isinstance(piece, King):
            piece_str = 'K' + location
        else:  # Knight
            piece_str = 'N' + location
        
        if piece.side:  # White
            white_pieces.append(piece_str)
        else:  # Black
            black_pieces.append(piece_str)
    
    with open(filename, 'w') as f:
        f.write(f"{size}\n")
        f.write(", ".join(white_pieces) + "\n")
        f.write(", ".join(black_pieces) + "\n")

def find_black_move(B: Board) -> tuple[Piece, int, int]:
    size, pieces = B
    
    # Get all black pieces
    black_pieces = [piece for piece in pieces if not piece.side]
    
    # Randomize order to make moves less predictable
    random.shuffle(black_pieces)
    
    # Try each black piece
    for piece in black_pieces:
        # Generate random coordinates to try
        coordinates = [(x, y) for x in range(1, size + 1) for y in range(1, size + 1)]
        random.shuffle(coordinates)
        
        for x, y in coordinates:
            if piece.can_move_to(x, y, B):
                return (piece, x, y)
    
    # This should not happen if there's at least one legal move
    raise ValueError("No legal moves available for black pieces")

def conf2unicode(B: Board) -> str:
    size, pieces = B
    
    # Create empty board
    board = [['\u2001' for _ in range(size)] for _ in range(size)]
    
    # Place pieces on board
    for piece in pieces:
        x, y = piece.pos_x, piece.pos_y
        # Convert to board array indices (y=1 is bottom row, so we need size-y)
        row = size - y
        col = x - 1
        
        if isinstance(piece, King):
            if piece.side:  # White
                board[row][col] = '\u2654'  # ♔
            else:  # Black
                board[row][col] = '\u265A'  # ♚
        else:  # Knight
            if piece.side:  # White
                board[row][col] = '\u2658'  # ♘
            else:  # Black
                board[row][col] = '\u265E'  # ♞
    
    # Convert to string
    result = []
    for row in board:
        result.append(''.join(row))
    
    return '\n'.join(result)

def main() -> None:
    try:
        while True:
            filename = input("File name for configuration: ").strip()
            if filename.upper() == "QUIT":
                return
            
            try:
                board = read_board(filename)
                break
            except IOError as e:
                print("This is not a valid file. File name for configuration: ", end="")
        
        print("The configuration is:")
        print(conf2unicode(board))
        
        # Main game loop
        while True:
            # White's turn
            while True:
                move = input("Next move of White: ").strip()
                if move.upper() == "QUIT":
                    save_filename = input("File name to store the configuration: ").strip()
                    save_board(save_filename, board)
                    print("The game configuration saved.")
                    return
                
                # Parse and validate move
                if len(move) < 4:
                    print("This is not a valid move. Next move of White: ", end="")
                    continue
                
                try:
                    # Parse move format: crCR (from cr to CR)
                    if len(move) == 4:
                        from_loc = move[:2]
                        to_loc = move[2:]
                    elif len(move) == 5:
                        if move[2].isdigit():
                            from_loc = move[:3]
                            to_loc = move[3:]
                        else:
                            from_loc = move[:2]
                            to_loc = move[2:]
                    elif len(move) == 6:
                        from_loc = move[:3]
                        to_loc = move[3:]
                    else:
                        print("This is not a valid move. Next move of White: ", end="")
                        continue
                    
                    from_x, from_y = location2index(from_loc)
                    to_x, to_y = location2index(to_loc)
                    
                    # Check if there's a white piece at the from location
                    if not is_piece_at(from_x, from_y, board):
                        print("This is not a valid move. Next move of White: ", end="")
                        continue
                    
                    piece = piece_at(from_x, from_y, board)
                    if not piece.side:  # Not white
                        print("This is not a valid move. Next move of White: ", end="")
                        continue
                    
                    # Check if the move is legal
                    if not piece.can_move_to(to_x, to_y, board):
                        print("This is not a valid move. Next move of White: ", end="")
                        continue
                    
                    # Make the move
                    board = piece.move_to(to_x, to_y, board)
                    break
                
                except (ValueError, IndexError):
                    print("This is not a valid move. Next move of White: ", end="")
                    continue
            
            print("The configuration after White's move is:")
            print(conf2unicode(board))
            
            # Check for checkmate or stalemate for Black
            if is_checkmate(False, board):
                print("Game over. White wins.")
                return
            elif is_stalemate(False, board):
                print("Game over. Stalemate.")
                return
            
            # Black's turn (computer)
            try:
                black_piece, to_x, to_y = find_black_move(board)
                from_loc = index2location(black_piece.pos_x, black_piece.pos_y)
                to_loc = index2location(to_x, to_y)
                
                print(f"Next move of Black is {from_loc}{to_loc}.")
                
                board = black_piece.move_to(to_x, to_y, board)
                
                print("The configuration after Black's move is:")
                print(conf2unicode(board))
                
                # Check for checkmate or stalemate for White
                if is_checkmate(True, board):
                    print("Game over. Black wins.")
                    return
                elif is_stalemate(True, board):
                    print("Game over. Stalemate.")
                    return
                
            except ValueError:
                # No legal moves for black (shouldn't happen if we checked properly)
                print("Game over. Stalemate.")
                return
    
    except KeyboardInterrupt:
        print("\nGame interrupted.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
