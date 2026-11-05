# Chess_2.0 audit and Chess Quest integration plan

## Scope and recommendation

The GitHub repository is a small command-line **Kings and Knights** chess exercise on configurable 3–26 square boards. Chess Quest is a Tkinter app for standard 8×8 chess, lessons, and AI opponents. They overlap in chess concepts, but they are not interchangeable implementations of the same rules.

**Recommendation: integrate on a branch and retain the existing exercise as a legacy/mini-chess mode initially.** Use `python-chess` as the sole rules authority for standard games. Do not overwrite the GitHub project in place or adapt its custom board engine into the standard game engine. Once the new app is stable in the repository, decide whether the old mode remains a supported feature or is kept only in Git history.

The audit is based on the public `main` branch as currently exposed by GitHub. It has three commits, ending with the test-suite commit on 2026-05-04. The repository root contains only `README.md`, `chess_puzzle.py`, and `test_chess_puzzle.py`.

## What the repo gets right

- **A clear domain model for its intended variant.** Coordinate conversion, `Piece`, `Knight`, `King`, board queries, move checks, and end-state checks are named separately in [`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L4-L56) and [`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L71-L255).
- **Some useful state discipline.** `move_to` returns a new tuple and piece list rather than directly editing the list supplied by the caller ([knight](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L119-L140), [king](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L184-L202)). The contained `Piece` objects are still mutable and shared, so this is only a partial immutable-state design.
- **Input validation at the file boundary.** `read_board` limits board size, piece kinds and coordinates, duplicate squares, and king counts ([`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L258-L360)).
- **Tests cover several important basics.** The suite has 50 test functions for coordinates, occupancy, king/knight movement patterns, check/checkmate/stalemate, invalid board files, and Unicode rendering ([`test_chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/test_chess_puzzle.py)). It uses `pytest` fixtures such as `tmp_path` for file tests.
- **The history shows incremental work.** The commit sequence separates the initial scaffold, game implementation, and tests ([commit history](https://github.com/MMarijke/Chess_2.0/commits/main/)).

## Problems and limitations

### Critical for standard chess

- **The model allows capturing the opposing king.** `Knight.can_reach` and `King.can_reach` reject a same-side piece but permit an opposing king as a destination ([knight](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L75-L99), [king](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L146-L167)). `is_check` then returns `False` when it cannot find that side’s king ([`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L204-L222)); a king capture can therefore become an invalid position and may be reported as stalemate. Standard chess ends at checkmate and never captures a king.
- **It is intentionally not full chess.** Only kings and knights are parsed or implemented; there are no pawns, bishops, rooks, queens, castling, en passant, or promotion ([`read_board`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L258-L354)). That is reasonable for the exercise, but it cannot power Chess Quest’s standard game mode.
- **The computer opponent is random.** `find_black_move` shuffles pieces and every square, then returns the first legal move ([`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L386-L406)). It provides neither a meaningful skill level nor tactical planning.

### Correctness, maintainability, and delivery risks

- **The implementation is one large module.** Rules, parsing, persistence, rendering, prompts, and the game loop all live in `chess_puzzle.py`; this will become harder to extend once lessons, GUI, storage, and AI are added ([`main`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L439-L552)).
- **Some public helpers rely on undocumented board invariants.** `is_check` treats a missing king as safe, while `move_to` assumes the supplied piece belongs to the board and the move is valid. `read_board` protects its own input path, but callers can construct invalid boards directly.
- **End-state checks scan every square for every piece.** `is_checkmate` and `is_stalemate` enumerate all coordinates and call `can_move_to` ([`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L224-L255)). For this small variant it is understandable; it is not a good base for a general chess engine.
- **The CLI hides useful parse errors.** It catches an `IOError` but prints only a generic invalid-file prompt instead of the exception detail ([`chess_puzzle.py`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L439-L450)). Broad exception catches in the parser and `main` also risk disguising programming errors ([`read_board`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L258-L361), [`main`](https://github.com/MMarijke/Chess_2.0/blob/main/chess_puzzle.py#L439-L552)).
- **A couple of tests overstate what they verify.** `test_is_checkmate_complex_scenario` only asserts that the result is a `bool`, so it passes regardless of correctness ([test](https://github.com/MMarijke/Chess_2.0/blob/main/test_chess_puzzle.py#L375-L388)). `test_is_checkmate_false_can_block` is named as a block case, but its fixture uses a knight check, which cannot be blocked; the test only establishes that the position is not checkmate ([test](https://github.com/MMarijke/Chess_2.0/blob/main/test_chess_puzzle.py#L366-L373)).
- **Important flows lack direct tests.** There are no dedicated tests for `can_move_to` protecting a king, `find_black_move`, `save_board` round-tripping, or the interactive `main` loop. The suite also imports the whole module with `from chess_puzzle import *`, which makes dependencies less explicit ([test imports](https://github.com/MMarijke/Chess_2.0/blob/main/test_chess_puzzle.py#L1-L2)).
- **The repository is hard to set up.** The README is only `# Chess_2.0` ([README](https://github.com/MMarijke/Chess_2.0/blob/main/README.md)); there is no dependency manifest, test/run guide, `.gitignore`, or CI workflow in the root listing. The existing tests require `pytest`, but that development dependency is not declared.
- **No license is declared.** If this will be shared or accept outside contributions, add the intended license explicitly. This does not prevent the repository owner from integrating their own work.

## Recommended migration plan

### 1. Protect the existing project

- Create a migration branch from `main` and tag or otherwise record the current commit before changes.
- Keep the current `chess_puzzle.py` and its tests intact for the first integration pass. Do not delete or rewrite them as part of the app import.
- Confirm whether Kings and Knights should remain a playable mini-chess/puzzle mode. If not, keep the implementation available as legacy code/history until the new app is accepted.

### 2. Bring Chess Quest into the repository as the new product shell

- Add the current app, requirements, and a real README with setup and run instructions. Initially keep a simple root entry point (`python chess_app.py`) so there is no premature packaging churn.
- Use `python-chess` for standard board state, legal moves, SAN, check/checkmate, promotion, and draw rules. Keep the built-in AI behind a small interface so a stronger engine can be added later without changing the UI.
- Separate responsibilities as the code grows: `ui`/Tkinter screens, standard game/AI adapter, lesson content and quizzes, and local progress storage. Avoid duplicating the old rules in the new engine.
- If mini-chess is retained, expose it as a separate mode and label its rules clearly; do not silently mix its 3–26 board and K/N-only assumptions with standard chess.

### 3. Establish a reliable project baseline

- Preserve and run the existing 50 tests before refactoring; then improve the weak checkmate tests and add explicit tests for king safety, king-capture rejection, save/load, and random-move legality.
- Add standard-chess tests for every special move, promotion choice, checkmate/stalemate/draw conditions, undo, and AI move legality. Keep GUI tests focused on screen/state transitions rather than duplicating `python-chess` rules tests.
- Add `pytest` as a development dependency, document the test command, add a `.gitignore`, and set up CI to install dependencies and run the suite on each push/PR.
- Make error messages actionable and narrow exception handling around expected user/file errors.

### 4. Decide how to retire the old mode

- After the full-chess app and its tests are stable, choose one: keep the K/N exercise as an optional mini-chess mode, move it into an explicitly named `legacy`/`mini_chess` package while retaining compatibility imports, or remove it in a later dedicated change.
- Update the README and entry points to make the supported product and modes unambiguous. Preserve the original Git history regardless of whether the source file remains in the final tree.

## Overwrite vs. integrate

| Choice | Benefit | Cost | Assessment |
|---|---|---|---|
| Integrate on a branch (recommended) | Preserves tested K/N work and history while making Chess Quest the main app | Keeps a small legacy surface until the mode decision is made | Lowest-risk path |
| Overwrite the three current files immediately | Cleaner root sooner | Loses accessible source/tests from the working tree, creates an avoidable migration risk, and discards the mini-chess option | Only choose if you explicitly want the old exercise abandoned |

This audit is a source and repository-structure review; the remote repository was not cloned, and its test suite was not executed in this pass.
