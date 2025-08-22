import time
import threading
import sys
import os
from validator import MoveValidator

# Shared clock state
white_time = 0
black_time = 0
active_color = None
game_running = True
lock = threading.Lock()

# How many lines above the prompt the clock line is.
# Layout per turn:
#   (many lines)  <- board
#   clock line
#   Moves so far: ...
#   <prompt line> "<Color>'s turn: "
CLOCK_LINES_ABOVE_PROMPT = 2

def _format_secs(s):
    m = int(s // 60)
    sec = int(s % 60)
    return f"{m}:{sec:02d}"

def _update_clock_line():
    """Redraw only the clock line above the prompt, without touching user input."""
    # Save cursor (at prompt), jump to clock line, print, restore cursor
    sys.stdout.write("\033[s")                         # save cursor
    sys.stdout.write(f"\033[{CLOCK_LINES_ABOVE_PROMPT}A")  # up to clock line
    sys.stdout.write("\r")                             # start of line
    sys.stdout.write(
        f"⏱ White: {_format_secs(white_time)} | Black: {_format_secs(black_time)}"
    )
    sys.stdout.write("\033[K")                         # clear to end of line
    sys.stdout.write("\033[u")                         # restore cursor (back to prompt)
    sys.stdout.flush()

def clock_thread():
    """Runs in the background, updates clocks every second and redraws the clock line."""
    global white_time, black_time, active_color, game_running

    while game_running:
        time.sleep(1)
        with lock:
            if active_color == "white":
                white_time -= 1
                if white_time <= 0:
                    print("\n⏰ White’s time is up! Black wins.")
                    game_running = False
                    return
            elif active_color == "black":
                black_time -= 1
                if black_time <= 0:
                    print("\n⏰ Black’s time is up! White wins.")
                    game_running = False
                    return

            # Refresh only the clock line (keeps prompt on its own line)
            _update_clock_line()

def render_board(board):
    """
    Print a bigger, more readable chess board.
    Horizontal and vertical spacing fixed so columns align perfectly.
    """
    square_width = 4  # width per square
    left_padding = 3  # aligns the bottom letters with squares

    print()
    for rank in range(8, 0, -1):
        # First line of the rank
        row = f"{rank}  "
        for file in range(8):
            square_index = (rank - 1) * 8 + file
            piece = board.piece_at(square_index)
            if piece:
                symbol = piece.symbol().upper() if piece.color else piece.symbol().lower()
            else:
                symbol = "."
            row += f"{symbol:^{square_width}}"  # center piece in fixed-width
        print(row)

        # Second line (blank) for vertical spacing
        print(" " * left_padding + " " * square_width * 8)

    # File letters at bottom, aligned
    bottom = " " * left_padding
    for file in range(8):
        bottom += f"{chr(ord('a') + file):^{square_width}}"
    print(bottom + "\n")


def play_chess():
    global white_time, black_time, active_color, game_running

    print("Welcome to Command-Line Chess!")
    print("Modes: [1] Play New/Continue Game  [2] Replay PGN\n")
    mode = input("Choose mode (1 or 2): ").strip()

    # ---------------- Replay Mode ----------------
    if mode == "2":
        filename = input("Enter PGN filename to replay: ").strip()
        game = MoveValidator()
        try:
            for board in game.replay_pgn(filename):
                os.system("cls" if os.name == "nt" else "clear")
                print(board)
                input("Press Enter for next move...")
            print("✅ Replay finished.")
        except Exception as e:
            print(f"❌ Failed to replay PGN: {e}")
        return

    # ---------------- Play Mode ----------------
    print("Enter moves in SAN (e.g., e4, Nf3, O-O) or UCI (e2e4, g1f3).")
    print("Type 'undo' to undo, 'quit' to exit.\n")

    load = input("Do you want to load a saved PGN game? (y/n): ").strip().lower()
    game = MoveValidator()
    if load == "y":
        filename = input("Enter PGN filename to load: ").strip()
        try:
            game.import_pgn(filename)
            print(f"✅ Loaded game from {filename}")
        except Exception as e:
            print(f"❌ Failed to load PGN: {e}")

    # ---------------- Time Control ----------------
    try:
        minutes = int(input("Set time control (minutes per player): ").strip())
    except ValueError:
        minutes = 5
    white_time = minutes * 60
    black_time = minutes * 60

    # Start clock thread
    t = threading.Thread(target=clock_thread, daemon=True)
    t.start()

    # ---------------- Main Game Loop ----------------
    while game_running:
        # Clear and print board + static info (clock will be updated by thread)
        os.system("cls" if os.name == "nt" else "clear")
        render_board(game.board)
        print(f"\n⏱ White: {_format_secs(white_time)} | Black: {_format_secs(black_time)}")

        # --- Move history in SAN (nice PGN-style) ---
        move_history = game.get_move_history() or "(none)"
        print(f"Moves so far: {move_history}")

        with lock:
            active_color = "white" if game.board.turn else "black"

        # Prompt on a NEW line; save cursor so the clock thread can redraw above it
        prompt = f"{active_color.capitalize()}'s turn: "
        sys.stdout.write(prompt)
        sys.stdout.flush()
        sys.stdout.write("\033[s")  # save cursor position at the end of the prompt
        sys.stdout.flush()

        try:
            move = input().strip()
        except KeyboardInterrupt:
            print("\nGame interrupted. Exiting quietly...")
            with lock:
                game_running = False
            break

        # If flag fell while we were typing, exit to save prompt
        if not game_running:
            break

        if move.lower() == "quit":
            with lock:
                game_running = False
            print("Goodbye!")
            break

        if move.lower() == "undo":
            game.undo_move()
            continue

        if game.make_move(move):
            # After a legal move, show updated SAN history immediately next loop
            if game.board.is_checkmate():
                # Show final position and announce
                os.system("cls" if os.name == "nt" else "clear")
                print(game.board)
                print("♟ Checkmate! Game over.")
                break
            elif game.board.is_stalemate():
                os.system("cls" if os.name == "nt" else "clear")
                print(game.board)
                print("Stalemate! Game over.")
                break
            elif game.board.is_insufficient_material():
                os.system("cls" if os.name == "nt" else "clear")
                print(game.board)
                print("Draw (insufficient material).")
                break
        else:
            print("❌ Invalid move. Try again.")
            time.sleep(1)

    # Stop clock thread
    game_running = False

    # -------- After game ends → offer to save PGN (always) --------
    try:
        save = input("Do you want to save the game as PGN? (y/n): ").strip().lower()
    except EOFError:
        save = "n"
    if save == "y":
        filename = input("Enter filename to save: ").strip() or "game.pgn"
        game.export_pgn(filename)
        print(f"✅ Game saved to {filename}")

if __name__ == "__main__":
    play_chess()
