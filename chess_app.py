"""Chess Quest: learn chess or play an AI opponent."""

from __future__ import annotations

import math
import json
import random
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

try:
    import chess
except ImportError as exc:  # pragma: no cover - shown to the user at launch
    raise SystemExit("Missing dependency. Run: python -m pip install -r requirements.txt") from exc


SQUARE = 68
APP_BG = "#0f172a"
SURFACE = "#192134"
SURFACE_RAISED = "#202b40"
TEXT = "#f8fafc"
MUTED = "#a9b4c5"
GREEN = "#15803d"
GREEN_HOVER = "#166534"
GOLD = "#d97706"
BORDER = "#334155"
ERROR = "#dc2626"
HIGHLIGHT = "#e3b341"
PIECE_GLYPHS = {
    "P": "♙", "N": "♘", "B": "♗", "R": "♖", "Q": "♕", "K": "♔",
    "p": "♟", "n": "♞", "b": "♝", "r": "♜", "q": "♛", "k": "♚",
}
PIECE_VALUES = {
    chess.PAWN: 100, chess.KNIGHT: 320, chess.BISHOP: 330,
    chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0,
}
AVATARS = {
    "Rookie Robin": {"monogram": "R", "color": "#4f9d69", "depth": 1, "noise": 180, "blurb": "A friendly first opponent. Great for trying things out."},
    "Tactician Fox": {"monogram": "T", "color": "#d97706", "depth": 2, "noise": 55, "blurb": "Looks for useful captures and simple tactics."},
    "Club Knight": {"monogram": "C", "color": "#3979a8", "depth": 2, "noise": 8, "blurb": "A steadier club-level challenge with fewer random moves."},
    "Grandmaster Owl": {"monogram": "G", "color": "#7c63b8", "depth": 3, "noise": 0, "blurb": "Plans ahead and punishes loose pieces."},
    "Phoenix Pro": {"monogram": "P", "color": "#b94d45", "depth": 4, "noise": 0, "blurb": "The toughest built-in opponent; searches farther ahead."},
}

BOARD_THEMES = {
    "Classic": ("#eadfc9", "#5b8060", "#e3b341"),
    "Slate": ("#d8dee9", "#596579", "#a3be8c"),
    "Forest": ("#e5e9d3", "#66835d", "#e9c46a"),
}

LESSONS = [
    ("1 · The board", "The chessboard has 64 squares in an 8 × 8 grid. Put a light square at each player's right-hand corner. Files are named a–h; ranks are numbered 1–8. Each side starts with 16 pieces.", "Try it: find the square e4. Its file is e and its rank is 4."),
    ("2 · How pieces move", "Pawns move forward one square (or two from their starting square) and capture diagonally. Knights jump in an L shape. Bishops slide diagonally; rooks slide along ranks and files. Queens combine rook and bishop moves. Kings move one square in any direction.", "A sliding piece cannot jump over another piece. Knights can."),
    ("3 · Check and checkmate", "A king is in check when an enemy piece attacks it. You must answer the check by moving the king, capturing the attacker, or blocking its line. Checkmate means there is no legal answer: the game is over.", "You may never make a move that leaves your own king in check."),
    ("4 · Special moves", "Castling moves the king two squares toward a rook and brings the rook beside it. It is allowed only when neither piece has moved, the path is clear, and the king does not cross check. En passant is a special pawn capture available immediately after an enemy pawn advances two squares beside yours.", "A pawn that reaches the last rank promotes, usually to a queen."),
    ("5 · Opening principles", "In the opening, fight for the centre, develop knights and bishops, and castle to protect your king. Try not to move the same piece repeatedly or bring your queen out too early.", "A useful first move is 1. e4: it controls central squares and opens lines for the bishop and queen."),
    ("6 · Tactics and planning", "Look for checks, captures, and threats. A fork attacks two targets at once; a pin makes moving a piece unsafe; a skewer attacks a valuable piece that must move, exposing another behind it. Before every move, ask: what is my opponent threatening?", "Slow down and check whether a piece will be left undefended."),
    ("7 · Draws and game etiquette", "A game can be drawn by stalemate (the player to move has no legal move but is not in check), agreement, threefold repetition, the fifty-move rule, or insufficient material. Resign only when you are ready, and be gracious whether you win or lose.", "A stalemated player is not in check, so the result is a draw."),
]

QUIZZES = [
    ("Which square is on the e-file and fourth rank?", ("e4", "d4", "e5"), 0, "Files use letters and ranks use numbers, so e4 is the answer."),
    ("Which piece can jump over other pieces?", ("Bishop", "Knight", "Rook"), 1, "The knight jumps in an L shape; the other pieces cannot jump."),
    ("What must you do when your king is in check?", ("Ignore it if you want", "Make a legal move that ends the check", "Move any pawn"), 1, "You must answer check and may not leave your king attacked."),
    ("When is en passant available?", ("Any time a pawn is beside yours", "Immediately after an adjacent pawn advances two squares", "Only when promoting"), 1, "En passant must be played immediately after that two-square pawn move."),
    ("What is a sound opening principle?", ("Develop pieces and contest the centre", "Move the queen repeatedly", "Keep every piece on its starting square"), 0, "Developing pieces and controlling central squares helps you build a position."),
    ("What does a fork do?", ("Attacks two or more targets at once", "Moves a king two squares", "Creates a draw"), 0, "A fork is a double attack, often made by a knight or pawn."),
    ("What is stalemate?", ("The king is checkmated", "No legal move is available, but the king is not in check", "A player resigns"), 1, "Stalemate is a draw because the player to move has no legal move but is not checked."),
]

PROGRESS_FILE = Path.home() / ".chess_quest_progress.json"


def load_progress() -> set[int]:
    try:
        data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            return set()
        completed = data.get("completed_lessons", [])
        if not isinstance(completed, list):
            return set()
        return {index for index in completed if isinstance(index, int) and not isinstance(index, bool) and 0 <= index < len(LESSONS)}
    except (OSError, ValueError, TypeError):
        return set()


def save_progress(completed: set[int]) -> None:
    try:
        PROGRESS_FILE.write_text(json.dumps({"completed_lessons": sorted(completed)}, indent=2), encoding="utf-8")
    except OSError:
        # Lessons remain usable if this device does not allow local persistence.
        pass


def evaluate(board: chess.Board) -> int:
    """Static score from the side-to-move's perspective."""
    if board.is_checkmate():
        return -100_000
    if board.is_game_over():
        return 0
    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        # Mild preference for active minor pieces and central pawns.
        if piece.piece_type in (chess.KNIGHT, chess.BISHOP):
            value += 8
        if piece.piece_type == chess.PAWN:
            value += max(0, 3 - abs(3.5 - chess.square_file(square))) * 3
        score += value if piece.color == board.turn else -value
    return score


def choose_move(board: chess.Board, depth: int, noise: int) -> chess.Move | None:
    """Small negamax search with alpha-beta pruning."""
    if board.is_game_over():
        return None

    def search(d: int, alpha: int, beta: int, ply: int) -> int:
        if board.is_checkmate():
            return -100_000 + ply
        if board.is_game_over() or d == 0:
            return evaluate(board)
        best = -math.inf
        moves = list(board.legal_moves)
        moves.sort(key=lambda move: (board.is_capture(move), move.promotion is not None), reverse=True)
        for move in moves:
            board.push(move)
            score = -search(d - 1, -beta, -alpha, ply + 1)
            board.pop()
            best = max(best, score)
            alpha = max(alpha, score)
            if alpha >= beta:
                break
        return int(best)

    options = []
    alpha = -math.inf
    beta = math.inf
    for move in list(board.legal_moves):
        board.push(move)
        root_alpha = -math.inf if noise else alpha
        searched_value = -search(max(0, depth - 1), -beta, -root_alpha, 1)
        board.pop()
        alpha = max(alpha, searched_value)
        value = searched_value
        if noise:
            value += random.randint(-noise, noise)
        options.append((value, move))
    return max(options, key=lambda item: item[0])[1] if options else None


class ChessQuest:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Chess Quest · Learn & Play")
        self.root.configure(bg=APP_BG)
        self.root.geometry("1040x760")
        self.root.minsize(900, 680)
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("TCombobox", fieldbackground=SURFACE_RAISED, background=SURFACE_RAISED, foreground=TEXT, arrowcolor=TEXT, bordercolor=BORDER, padding=6)
        style.map("TCombobox", fieldbackground=[("readonly", SURFACE_RAISED)], foreground=[("readonly", TEXT)])
        self.board = chess.Board()
        self.selected: chess.Square | None = None
        self.last_move: chess.Move | None = None
        self.cursor_square = chess.E2
        self.square_size = SQUARE
        self.board_origin_x = 0
        self.board_origin_y = 0
        self.player_color = chess.WHITE
        self.avatar = "Rookie Robin"
        self.lesson_index = 0
        self.completed_lessons = load_progress()
        self.board_theme = "Classic"
        self.resigned = False
        self.thinking = False
        self.in_game = False
        self.game_id = 0
        self.show_home()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def heading(self, parent, title, subtitle=""):
        tk.Label(parent, text=title, font=("Segoe UI", 26, "bold"), fg=TEXT, bg=APP_BG).pack(pady=(26, 4))
        if subtitle:
            tk.Label(parent, text=subtitle, font=("Segoe UI", 12), fg=MUTED, bg=APP_BG).pack(pady=(0, 22))

    def button(self, parent, label, command, variant="primary", **kwargs):
        colors = {
            "primary": (GREEN, GREEN_HOVER, TEXT),
            "secondary": (SURFACE_RAISED, BORDER, TEXT),
            "accent": (GOLD, "#b45309", APP_BG),
            "danger": (ERROR, "#b91c1c", TEXT),
        }
        background, hover, foreground = colors[variant]
        widget = tk.Button(parent, text=label, command=command, font=("Segoe UI", 11, "bold"), bg=background, fg=foreground, activebackground=hover, activeforeground=foreground, relief="flat", padx=16, pady=9, cursor="hand2", borderwidth=0, **kwargs)
        widget.bind("<Enter>", lambda _event: widget.configure(bg=hover))
        widget.bind("<Leave>", lambda _event: widget.configure(bg=background))
        return widget

    def avatar_badge(self, parent, name, size=46):
        details = AVATARS[name]
        badge = tk.Canvas(parent, width=size, height=size, bg=parent.cget("bg"), highlightthickness=0, takefocus=False)
        badge.create_oval(3, 3, size - 3, size - 3, fill=details["color"], outline="")
        badge.create_text(size / 2, size / 2, text=details["monogram"], font=("Segoe UI", int(size * 0.38), "bold"), fill=TEXT)
        return badge

    def show_home(self):
        self.invalidate_ai_search()
        self.clear()
        self.heading(self.root, "♟  CHESS QUEST", "Learn the game. Find your level. Make your move.")
        card = tk.Frame(self.root, bg=SURFACE, padx=30, pady=26, highlightbackground=BORDER, highlightthickness=1)
        card.pack(padx=70, pady=12, fill="x")
        tk.Label(card, text="LEARN CHESS", font=("Segoe UI", 18, "bold"), fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(card, text=f"A guided path from board basics to tactics and draws.  {len(self.completed_lessons)}/{len(LESSONS)} lessons completed.", wraplength=720, font=("Segoe UI", 11), fg=MUTED, bg=SURFACE).pack(anchor="w", pady=8)
        self.button(card, "Explore the lessons  →", self.show_lessons).pack(anchor="w", pady=(8, 0))
        card2 = tk.Frame(self.root, bg=SURFACE, padx=30, pady=26, highlightbackground=BORDER, highlightthickness=1)
        card2.pack(padx=70, pady=12, fill="x")
        tk.Label(card2, text="PLAY AN AI AVATAR", font=("Segoe UI", 18, "bold"), fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(card2, text="Choose an opponent that matches your confidence and play a full game.", wraplength=720, font=("Segoe UI", 11), fg=MUTED, bg=SURFACE).pack(anchor="w", pady=8)
        self.button(card2, "Choose an opponent  →", self.show_opponents).pack(anchor="w", pady=(8, 0))
        tk.Label(self.root, text="Private by default · Your games stay on this device", font=("Segoe UI", 9), fg=MUTED, bg=APP_BG).pack(pady=18)

    def show_lessons(self):
        self.invalidate_ai_search()
        self.clear()
        title, body, tip = LESSONS[self.lesson_index]
        self.heading(self.root, "THE LEARNING PATH", f"Lesson {self.lesson_index + 1} of {len(LESSONS)}")
        panel = tk.Frame(self.root, bg=SURFACE, padx=32, pady=24, highlightbackground=BORDER, highlightthickness=1)
        panel.pack(fill="both", expand=True, padx=48, pady=10)
        tk.Label(panel, text=title, font=("Segoe UI", 21, "bold"), fg=TEXT, bg=SURFACE).pack(anchor="w")
        tk.Label(panel, text=body, font=("Segoe UI", 12), fg=MUTED, bg=SURFACE, wraplength=690, justify="left", anchor="nw").pack(fill="x", pady=(16, 10))
        tk.Label(panel, text=tip, font=("Segoe UI", 11, "italic"), fg="#9bd1a7", bg=SURFACE, wraplength=690, justify="left").pack(anchor="w", pady=10)
        question, answers, correct, explanation = QUIZZES[self.lesson_index]
        tk.Label(panel, text=question, font=("Segoe UI", 12, "bold"), fg=TEXT, bg=SURFACE, wraplength=690, justify="left").pack(anchor="w", pady=(8, 5))
        self.quiz_choice = tk.IntVar(value=-1)
        for answer_index, answer in enumerate(answers):
            tk.Radiobutton(panel, text=answer, variable=self.quiz_choice, value=answer_index, font=("Segoe UI", 10), fg=TEXT, bg=SURFACE, selectcolor=SURFACE_RAISED, activebackground=SURFACE, activeforeground=TEXT).pack(anchor="w", padx=8)
        self.quiz_feedback = tk.StringVar(value="Lesson quiz completed ✓" if self.lesson_index in self.completed_lessons else "")
        tk.Label(panel, textvariable=self.quiz_feedback, font=("Segoe UI", 10, "bold"), fg="#9bd1a7", bg=SURFACE, wraplength=690, justify="left").pack(anchor="w", pady=5)
        self.button(panel, "Check answer", lambda: self.check_quiz(correct, explanation)).pack(anchor="w", pady=4)
        nav = tk.Frame(self.root, bg=APP_BG)
        nav.pack(pady=18)
        self.button(nav, "← Back", self.show_home).pack(side="left", padx=7)
        if self.lesson_index:
            self.button(nav, "Previous", self.previous_lesson).pack(side="left", padx=7)
        next_label = "Finish lessons ✓" if self.lesson_index == len(LESSONS) - 1 else "Next lesson →"
        self.button(nav, next_label, self.next_lesson).pack(side="left", padx=7)

    def next_lesson(self):
        if self.lesson_index < len(LESSONS) - 1:
            self.lesson_index += 1
            self.show_lessons()
        else:
            self.show_home()

    def previous_lesson(self):
        self.lesson_index = max(0, self.lesson_index - 1)
        self.show_lessons()

    def check_quiz(self, correct: int, explanation: str):
        if self.quiz_choice.get() < 0:
            self.quiz_feedback.set("Choose an answer first.")
            return
        if self.quiz_choice.get() == correct:
            self.completed_lessons.add(self.lesson_index)
            save_progress(self.completed_lessons)
            self.quiz_feedback.set(f"Correct! {explanation}")
        else:
            self.quiz_feedback.set(f"Not quite. Try again. {explanation}")

    def show_opponents(self):
        self.invalidate_ai_search()
        self.clear()
        self.heading(self.root, "PICK YOUR OPPONENT", "Every avatar has a different playing style and challenge level.")
        self.avatar_var = tk.StringVar(value=self.avatar)
        for name, details in AVATARS.items():
            frame = tk.Frame(self.root, bg=SURFACE, padx=18, pady=11, highlightbackground=BORDER, highlightthickness=1)
            frame.pack(fill="x", padx=65, pady=5)
            self.avatar_badge(frame, name, 40).pack(side="left", padx=(0, 12))
            text_frame = tk.Frame(frame, bg=SURFACE)
            text_frame.pack(side="left", fill="x", expand=True)
            tk.Radiobutton(text_frame, text=name, variable=self.avatar_var, value=name, font=("Segoe UI", 13, "bold"), fg=TEXT, bg=SURFACE, selectcolor=SURFACE_RAISED, activebackground=SURFACE, activeforeground=TEXT, anchor="w").pack(anchor="w")
            tk.Label(text_frame, text=details["blurb"], font=("Segoe UI", 10), fg=MUTED, bg=SURFACE).pack(anchor="w", padx=22, pady=(1, 0))
        color_frame = tk.Frame(self.root, bg=APP_BG)
        color_frame.pack(pady=12)
        tk.Label(color_frame, text="Play as:", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=APP_BG).pack(side="left", padx=7)
        self.color_var = tk.StringVar(value="White")
        ttk.Combobox(color_frame, textvariable=self.color_var, values=("White", "Black", "Random"), state="readonly", width=12).pack(side="left", padx=7)
        tk.Label(color_frame, text="Board:", font=("Segoe UI", 11, "bold"), fg=TEXT, bg=APP_BG).pack(side="left", padx=(16, 5))
        self.theme_var = tk.StringVar(value=self.board_theme)
        ttk.Combobox(color_frame, textvariable=self.theme_var, values=tuple(BOARD_THEMES), state="readonly", width=10).pack(side="left", padx=5)
        nav = tk.Frame(self.root, bg=APP_BG)
        nav.pack(pady=14)
        self.button(nav, "← Back", self.show_home).pack(side="left", padx=8)
        self.button(nav, "Start game ♟", self.start_game).pack(side="left", padx=8)

    def start_game(self):
        # Invalidate any AI result still being calculated for the previous game.
        self.game_id += 1
        self.thinking = False
        self.avatar = self.avatar_var.get()
        self.board_theme = self.theme_var.get()
        choice = self.color_var.get()
        self.player_color = random.choice([chess.WHITE, chess.BLACK]) if choice == "Random" else choice == "White"
        self.cursor_square = chess.E2 if self.player_color else chess.E7
        self.begin_game()

    def begin_game(self):
        self.in_game = True
        self.board = chess.Board()
        self.selected = None
        self.last_move = None
        self.last_feedback = ""
        self.resigned = False
        self.show_game()
        if not self.player_color:
            self.schedule_ai_turn(300)

    def rematch(self):
        self.invalidate_ai_search()
        self.begin_game()

    def invalidate_ai_search(self):
        """Ignore an AI result if the user leaves the game while it is searching."""
        self.cancel_ai_search()
        self.in_game = False

    def cancel_ai_search(self):
        self.game_id += 1
        self.thinking = False

    def schedule_ai_turn(self, delay: int):
        game_id = self.game_id
        self.root.after(delay, lambda: self.ai_turn() if self.in_game and game_id == self.game_id else None)

    def show_game(self):
        self.clear()
        outer = tk.Frame(self.root, bg=APP_BG)
        outer.pack(fill="both", expand=True, padx=22, pady=16)
        left = tk.Frame(outer, bg=APP_BG)
        left.pack(side="left", padx=(0, 22))
        details = AVATARS[self.avatar]
        identity = tk.Frame(left, bg=APP_BG)
        identity.pack(anchor="w")
        self.avatar_badge(identity, self.avatar, 42).pack(side="left", padx=(0, 10))
        tk.Label(identity, text=self.avatar, font=("Segoe UI", 16, "bold"), fg=TEXT, bg=APP_BG).pack(side="left")
        self.status_var = tk.StringVar()
        tk.Label(left, textvariable=self.status_var, font=("Segoe UI", 11, "bold"), fg="#a9d9b2", bg=APP_BG, wraplength=230, justify="left").pack(anchor="w", pady=(8, 18))
        tk.Label(left, text="MOVE HISTORY", font=("Segoe UI", 9, "bold"), fg=MUTED, bg=APP_BG).pack(anchor="w")
        self.history = tk.Text(left, width=28, height=18, bg=SURFACE, fg=TEXT, relief="flat", font=("Consolas", 10), state="disabled", padx=10, pady=8, highlightthickness=1, highlightbackground=BORDER, insertbackground=TEXT)
        self.history.pack(pady=6)
        actions = tk.Frame(left, bg=APP_BG)
        actions.pack(anchor="w", pady=6, fill="x")
        self.button(actions, "Undo turn", self.undo_turn, variant="secondary").pack(side="left", padx=(0, 6))
        self.button(actions, "Resign", self.resign, variant="danger").pack(side="left")
        self.button(left, "Rematch", self.rematch).pack(anchor="w", pady=3)
        btns = tk.Frame(left, bg=APP_BG)
        btns.pack(anchor="w", pady=3)
        self.button(btns, "New opponent", self.show_opponents, variant="secondary").pack(side="left", padx=(0, 6))
        self.button(btns, "Home", self.show_home, variant="secondary").pack(side="left")
        self.canvas = tk.Canvas(outer, width=SQUARE * 8, height=SQUARE * 8, highlightthickness=0, takefocus=True)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.bind("<Button-1>", self.on_board_click)
        self.canvas.bind("<KeyPress>", self.on_board_key)
        self.canvas.bind("<Configure>", self.on_board_resize)
        self.draw_board()
        self.canvas.focus_set()
        self.update_status()
        self.update_history()

    def draw_board(self):
        self.canvas.delete("all")
        width = max(1, self.canvas.winfo_width())
        height = max(1, self.canvas.winfo_height())
        self.square_size = max(44, min(SQUARE, min(width, height) // 8))
        board_pixels = self.square_size * 8
        self.board_origin_x = max(0, (width - board_pixels) // 2)
        self.board_origin_y = max(0, (height - board_pixels) // 2)
        light_color, dark_color, highlight_color = BOARD_THEMES[self.board_theme]
        legal_targets = {move.to_square for move in self.board.legal_moves if self.selected is not None and move.from_square == self.selected}
        for row in range(8):
            for col in range(8):
                file_ = col if self.player_color else 7 - col
                rank = 7 - row if self.player_color else row
                square = chess.square(file_, rank)
                size = self.square_size
                x, y = self.board_origin_x + col * size, self.board_origin_y + row * size
                color = light_color if (file_ + rank) % 2 else dark_color
                if self.last_move and square in (self.last_move.from_square, self.last_move.to_square):
                    color = highlight_color
                if self.selected == square:
                    color = HIGHLIGHT
                self.canvas.create_rectangle(x, y, x + size, y + size, fill=color, outline=color)
                if col == 0:
                    label_color = "#4b594a" if color == light_color else "#f4eddd"
                    self.canvas.create_text(x + 5, y + 4, text=str(rank + 1), anchor="nw", fill=label_color, font=("Segoe UI", 8, "bold"))
                if row == 7:
                    label_color = "#4b594a" if color == light_color else "#f4eddd"
                    self.canvas.create_text(x + size - 5, y + size - 4, text=chess.FILE_NAMES[file_], anchor="se", fill=label_color, font=("Segoe UI", 8, "bold"))
                if self.cursor_square == square:
                    self.canvas.create_rectangle(x + 2, y + 2, x + size - 2, y + size - 2, outline="#2563eb", width=3)
                piece = self.board.piece_at(square)
                if piece:
                    # A contrasting offset glyph keeps both sides visible on both
                    # square colors, including on systems with monochrome fonts.
                    center_x, center_y = x + size / 2, y + size / 2
                    foreground = "#fffaf0" if piece.color == chess.WHITE else "#17212b"
                    shadow = "#5a3d28" if piece.color == chess.WHITE else "#f6e6ca"
                    glyph = PIECE_GLYPHS[piece.symbol()]
                    font_size = max(30, int(size * 0.63))
                    self.canvas.create_text(center_x + 1, center_y + 2, text=glyph, font=("Segoe UI Symbol", font_size), fill=shadow, tags="piece")
                    self.canvas.create_text(center_x, center_y, text=glyph, font=("Segoe UI Symbol", font_size), fill=foreground, tags="piece")
                if square in legal_targets:
                    if self.board.piece_at(square):
                        self.canvas.create_oval(x + 5, y + 5, x + size - 5, y + size - 5, outline="#2b2b2b", width=3)
                    else:
                        self.canvas.create_oval(x + size / 2 - 7, y + size / 2 - 7, x + size / 2 + 7, y + size / 2 + 7, fill="#315a45", outline="")

    def on_board_resize(self, _event):
        self.draw_board()

    def on_board_click(self, event):
        if self.thinking or self.resigned or self.board.is_game_over() or self.board.turn != self.player_color:
            return
        col = (event.x - self.board_origin_x) // self.square_size
        row = (event.y - self.board_origin_y) // self.square_size
        if not (0 <= col < 8 and 0 <= row < 8):
            return
        file_ = col if self.player_color else 7 - col
        rank = 7 - row if self.player_color else row
        square = chess.square(file_, rank)
        self.cursor_square = square
        if self.selected is not None:
            candidates = [move for move in self.board.legal_moves if move.from_square == self.selected and move.to_square == square]
            if candidates:
                move = self.pick_promotion(candidates)
                if move:
                    self.make_move(move)
                return
        piece = self.board.piece_at(square)
        self.selected = square if piece and piece.color == self.player_color else None
        self.draw_board()

    def on_board_key(self, event):
        if self.thinking or self.board.is_game_over() or self.resigned or self.board.turn != self.player_color:
            return "break"
        col = chess.square_file(self.cursor_square)
        row = chess.square_rank(self.cursor_square)
        if event.keysym in ("Left", "Right", "Up", "Down"):
            view_col = col if self.player_color else 7 - col
            view_row = 7 - row if self.player_color else row
            view_col += -1 if event.keysym == "Left" else 1 if event.keysym == "Right" else 0
            view_row += -1 if event.keysym == "Up" else 1 if event.keysym == "Down" else 0
            if 0 <= view_col < 8 and 0 <= view_row < 8:
                file_ = view_col if self.player_color else 7 - view_col
                rank = 7 - view_row if self.player_color else view_row
                self.cursor_square = chess.square(file_, rank)
                self.draw_board()
        elif event.keysym in ("Return", "space"):
            square = self.cursor_square
            if self.selected is not None:
                candidates = [move for move in self.board.legal_moves if move.from_square == self.selected and move.to_square == square]
                if candidates:
                    move = self.pick_promotion(candidates)
                    if move:
                        self.make_move(move)
                    return "break"
            piece = self.board.piece_at(square)
            self.selected = square if piece and piece.color == self.player_color else None
            self.draw_board()
        elif event.keysym == "Escape":
            self.selected = None
            self.draw_board()
        return "break"

    def pick_promotion(self, candidates: list[chess.Move]) -> chess.Move | None:
        promotions = [move for move in candidates if move.promotion]
        if not promotions:
            return candidates[0]
        choices = {move.promotion: move for move in promotions}
        dialog = tk.Toplevel(self.root)
        dialog.title("Promote pawn")
        dialog.configure(bg=SURFACE)
        dialog.transient(self.root)
        dialog.grab_set()
        tk.Label(dialog, text="Choose a piece", font=("Segoe UI", 14, "bold"), fg=TEXT, bg=SURFACE).pack(padx=20, pady=(16, 8))
        result: list[chess.Move | None] = [None]
        row = tk.Frame(dialog, bg=SURFACE)
        row.pack(padx=12, pady=(0, 16))
        for piece_type, label in ((chess.QUEEN, "Queen"), (chess.ROOK, "Rook"), (chess.BISHOP, "Bishop"), (chess.KNIGHT, "Knight")):
            if piece_type not in choices:
                continue
            self.button(row, f"{PIECE_GLYPHS[chess.Piece(piece_type, self.player_color).symbol()]} {label}", lambda p=piece_type: (result.__setitem__(0, choices[p]), dialog.destroy())).pack(side="left", padx=4)
        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.wait_window()
        return result[0]

    def make_move(self, move):
        actor = "You" if self.board.turn == self.player_color else self.avatar
        captured = self.board.piece_at(move.to_square)
        if self.board.is_en_passant(move):
            captured = chess.Piece(chess.PAWN, not self.board.turn)
        self.board.push(move)
        self.last_move = move
        self.last_feedback = f"{actor} captured a {chess.piece_name(captured.piece_type)}." if captured else ""
        self.selected = None
        self.draw_board()
        self.update_status()
        self.update_history()
        if not self.board.is_game_over() and self.board.turn != self.player_color:
            self.schedule_ai_turn(200)

    def undo_turn(self):
        if self.thinking:
            self.cancel_ai_search()
        if not self.board.move_stack:
            return
        # If the AI just moved, roll back the AI and the preceding player move.
        plies = 2 if self.board.turn == self.player_color else 1
        for _ in range(min(plies, len(self.board.move_stack))):
            self.board.pop()
        self.resigned = False
        self.selected = None
        self.last_move = self.board.peek() if self.board.move_stack else None
        self.last_feedback = ""
        self.draw_board()
        self.update_history()
        self.update_status()
        if self.board.turn != self.player_color and not self.board.is_game_over():
            self.schedule_ai_turn(200)

    def resign(self):
        if self.board.is_game_over() or self.resigned:
            return
        if messagebox.askyesno("Resign game?", "Are you sure you want to resign this game?"):
            self.cancel_ai_search()
            self.resigned = True
            self.update_status()

    def ai_turn(self):
        if not self.in_game or self.resigned or self.board.is_game_over() or self.board.turn == self.player_color or self.thinking:
            return
        self.thinking = True
        self.update_status("Thinking…")
        fen = self.board.fen()
        settings = AVATARS[self.avatar]
        game_id = self.game_id
        def worker():
            try:
                temporary = chess.Board(fen)
                move = choose_move(temporary, settings["depth"], settings["noise"])
                error = None
            except Exception as exc:  # Keep the UI responsive if the engine fails.
                move = None
                error = str(exc)
            try:
                self.root.after(0, lambda: self.finish_ai(game_id, move, error))
            except tk.TclError:
                # The app may have closed while the background search was running.
                pass
        threading.Thread(target=worker, daemon=True).start()

    def finish_ai(self, game_id, move, error=None):
        if game_id != self.game_id or not self.in_game:
            return
        self.thinking = False
        if error:
            self.update_status("The AI had trouble choosing a move. Please try again.")
            messagebox.showerror("AI error", f"The opponent could not choose a move:\n{error}")
            return
        if move and move in self.board.legal_moves:
            self.make_move(move)
        elif not self.board.is_game_over() and self.board.turn != self.player_color:
            self.update_status("The AI could not find a legal move. Start a new game to continue.")

    def update_status(self, override=None):
        if override:
            text = override
        elif self.resigned:
            text = f"You resigned — {self.avatar} wins."
        elif self.board.is_checkmate():
            winner = "You win!" if self.board.turn != self.player_color else f"{self.avatar} wins."
            text = f"Checkmate — {winner}"
        elif self.board.is_stalemate():
            text = "Stalemate — the game is a draw."
        elif self.board.is_game_over():
            text = f"Draw — {self.board.result()}."
        else:
            who = "Your move" if self.board.turn == self.player_color else f"{self.avatar} to move"
            feedback = f" · {self.last_feedback}" if self.last_feedback else ""
            text = f"{who}{' · Check!' if self.board.is_check() else ''}{feedback}"
        self.status_var.set(text)

    def update_history(self):
        sans = list(self.board.move_stack)
        temp = chess.Board()
        rows = []
        for index in range(0, len(sans), 2):
            white = temp.san(sans[index])
            temp.push(sans[index])
            black = ""
            if index + 1 < len(sans):
                black = temp.san(sans[index + 1])
                temp.push(sans[index + 1])
            rows.append(f"{index // 2 + 1:>2}. {white:<8} {black}")
        self.history.configure(state="normal")
        self.history.delete("1.0", "end")
        self.history.insert("1.0", "\n".join(rows[-28:]))
        self.history.see("end")
        self.history.configure(state="disabled")


def main():
    root = tk.Tk()
    ChessQuest(root)
    root.mainloop()


if __name__ == "__main__":
    main()
