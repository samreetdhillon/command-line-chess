# Command-Line Chess

A fully-featured two-player **terminal-based chess game** implemented in Python. Play against another human, track move history, save/load games as PGN, and enjoy a dynamic clock—all in your terminal.

## Features

- **Two-player mode:** Play White vs Black in the terminal.
- **Move validation:** All moves are checked for legality using standard chess rules.
- **Move history:** Keep track of all moves in standard notation.
- **Dynamic clocks:** Each player has a countdown timer that updates in real-time.
- **Save & load PGN:** Save finished games or continue from a previously saved PGN file.
- **Replay mode:** Replay saved PGN games move by move.
- **Bigger, readable board:** Unicode pieces and clear spacing make the board easy to read.
- **Graceful exit:** Press `Ctrl+C` during the game to exit cleanly without traceback.

## Files

- `game.py`: Main script for handling chess games.
- `validator.py`: Contains validation logic for chess moves or PGN files.
- `first.pgn`: Example PGN file for testing or demonstration.

## Requirements

- Python 3.10 or higher

## Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/command-line-chess.git
cd command-line-chess
```

2. **Create a virtual environment (optional but recommended):**

```bash
python -m venv venv
source venv/bin/activate      # Linux / macOS
venv\Scripts\activate         # Windows
```

3. **Install Dependencies**

```bash
pip install -r requirements.txt
```

## Usage

1. Place your PGN files in the project directory.
2. Run `game.py`:

```bash
python game.py
```

## Game Flow

1. **Choose mode:**

- `1` – Play new or continue game

- `2` – Replay a saved PGN game

2. **If playing a game:**

- Optionally load a previously saved PGN.
- Set the time control (minutes per player).

- Enter moves in SAN (e.g., `e4`, `Nf3`, `O-O`) or UCI (e.g., `e2e4`, `g1f3`).

- Type `undo` to undo the last move.

- Type `quit` to exit the game (option to save PGN appears).

3. **After each move:**

- The board is displayed with Unicode pieces.

- Move history is printed below the board.

- Clocks for both players are dynamically updated.

## Example

```bash
8   r   n   b   q   k   b   n   r
7   p   p   p   p   p   p   p   p
6   .   .   .   .   .   .   .   .
5   .   .   .   .   .   .   .   .
4   .   .   .   .   .   .   .   .
3   .   .   .   .   .   .   .   .
2   P   P   P   P   P   P   P   P
1   R   N   B   Q   K   B   N   R
    a   b   c   d   e   f   g   h

⏱ White: 4:59 | Black: 5:00
Moves so far: 1. e4
White's turn:

```

## Notes

- Works on Windows, Linux, and macOS terminals.

- For best results, use a terminal that supports Unicode characters.

## License

MIT License © Samreet Singh Dhillon
