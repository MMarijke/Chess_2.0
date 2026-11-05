# Chess_2.0 · Chess Quest

Chess Quest is a desktop app for learning standard chess and playing against AI opponents. This repository also preserves the original Kings-and-Knights command-line exercise as a separate legacy mode.

## Run Chess Quest

Requirements: Python 3.10+ with Tkinter enabled.

```powershell
python -m pip install -r requirements.txt
python chess_app.py
```

The app includes guided lessons and quizzes, five AI difficulty levels, legal standard chess, move history, promotion choices, undo/resign/rematch controls, and several board themes. Lesson progress is stored locally in `~/.chess_quest_progress.json` where supported.

## Run the original Kings-and-Knights exercise

```powershell
python chess_puzzle.py
```

The CLI asks for a board-configuration filename. Its rules are intentionally limited to kings and knights on configurable 3–26 square boards; they are separate from the full-chess rules used by Chess Quest.

## Development

Install development dependencies and run the complete suite:

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

The original CLI tests remain in `test_chess_puzzle.py`. Chess Quest-specific AI tests are in `test_chess_app.py`.
