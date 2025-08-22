import chess
import chess.pgn
import io

class MoveValidator:
    def __init__(self, fen: str = None):
        self.board = chess.Board(fen) if fen else chess.Board()

    def is_legal(self, move_str: str) -> bool:
        """Check if a move is legal (SAN or UCI)."""
        try:
            move = self.board.parse_san(move_str)  # Try SAN
        except ValueError:
            try:
                move = chess.Move.from_uci(move_str)  # Try UCI
            except ValueError:
                return False
        return move in self.board.legal_moves

    def make_move(self, move_str: str) -> bool:
        """Play a move if legal. Returns True if move was made."""
        try:
            move = self.board.parse_san(move_str)
        except ValueError:
            try:
                move = chess.Move.from_uci(move_str)
            except ValueError:
                return False

        if move in self.board.legal_moves:
            self.board.push(move)
            return True
        return False

    def undo_move(self):
        if self.board.move_stack:
            self.board.pop()

    def get_board(self) -> str:
        return str(self.board)

    def is_game_over(self) -> bool:
        return self.board.is_game_over()

    def result(self) -> str:
        return self.board.result()

    def get_move_history(self) -> str:
        """Return PGN-style move history as a string."""
        history = []
        board_copy = chess.Board()
        for move in self.board.move_stack:
            move_san = board_copy.san(move)
            if board_copy.turn == chess.WHITE:
                history.append(f"{len(history)//2 + 1}. {move_san}")
            else:
                history[-1] += f" {move_san}"
            board_copy.push(move)
        return " ".join(history)

    def is_check(self) -> bool:
        return self.board.is_check()

    def is_checkmate(self) -> bool:
        return self.board.is_checkmate()

    def game_end_reason(self) -> str:
        """Return a human-readable explanation if the game ended."""
        if not self.board.is_game_over():
            return ""
        if self.board.is_checkmate():
            return "Checkmate!"
        if self.board.is_stalemate():
            return "Draw by stalemate."
        if self.board.is_insufficient_material():
            return "Draw due to insufficient material."
        if self.board.is_seventyfive_moves():
            return "Draw by seventy-five move rule."
        if self.board.is_fivefold_repetition():
            return "Draw by fivefold repetition."
        return "Game drawn."

    def export_pgn(self, filename="game.pgn", white="White", black="Black"):
        """Save the current game as a PGN file."""
        game = chess.pgn.Game.from_board(self.board)
        game.headers["White"] = white
        game.headers["Black"] = black
        game.headers["Result"] = self.result()

        with open(filename, "w") as f:
            print(game, file=f)

        return filename

    import chess.pgn

    def import_pgn(self, filename: str):
        """Load a PGN file into the current board."""
        with open(filename) as f:
            game = chess.pgn.read_game(f)
            if game is None:
                raise ValueError("No valid PGN found in file.")

            # Rebuild the board from the PGN game
            board = chess.Board()
            for move in game.mainline_moves():
                board.push(move)

            self.board = board
        return True
    
    def replay_pgn(self, filename: str):
        """Yield board positions step by step from a PGN file."""
        with open(filename) as f:
            game = chess.pgn.read_game(f)
            if game is None:
                raise ValueError("No valid PGN found in file.")

            board = chess.Board()
            yield board.copy()  # starting position

            for move in game.mainline_moves():
                board.push(move)
                yield board.copy()