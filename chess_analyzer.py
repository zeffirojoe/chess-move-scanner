import os
import subprocess

class ChessAnalyzer:
    """
    Handles chess position analysis using Stockfish engine.
    Provides move suggestions and position evaluation.
    """
    
    def __init__(self, stockfish_path):
        self.stockfish_path = stockfish_path
        if not os.path.exists(stockfish_path):
            raise FileNotFoundError(f"Stockfish not found at {stockfish_path}")

    def analyze_position(self, fen_position):
        """
        Analyze a chess position using Stockfish.
        Returns evaluation score and suggested moves.
        """
        try:
            with self._create_stockfish_process() as stockfish:
                self._configure_stockfish(stockfish, fen_position)
                return self._get_analysis(stockfish)
        except Exception as e:
            return f"Error analyzing position: {str(e)}"

    def _create_stockfish_process(self):
        """Create and return a Stockfish subprocess"""
        return subprocess.Popen(
            self.stockfish_path,
            universal_newlines=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def _configure_stockfish(self, stockfish, fen_position):
        """Send initial configuration commands to Stockfish"""
        commands = [
            "uci",
            "isready",
            "setoption name UCI_AnalyseMode value true",
            "setoption name MultiPV value 1",
            f"position fen {fen_position}",
            "go movetime 3000"
        ]
        for cmd in commands:
            stockfish.stdin.write(cmd + "\n")
            stockfish.stdin.flush()

    def _get_analysis(self, stockfish):
        """Read and parse Stockfish analysis output"""
        info_lines = []
        while True:
            line = stockfish.stdout.readline().strip()
            if not line:
                continue
            if line.startswith("bestmove"):
                best_move = line.split()[1]
                break
            if "score cp" in line and "pv" in line:
                info_lines.append(line)

        return self._parse_analysis(info_lines[-1] if info_lines else None)

    def _parse_analysis(self, info):
        """Parse Stockfish analysis line into readable format"""
        if not info:
            return "Could not analyze position"

        try:
            # Extract score
            score = 0
            if "score cp" in info:
                score_parts = info.split("score cp")[1].strip().split()
                score = int(score_parts[0]) / 100.0

            # Extract moves
            moves = []
            if "pv" in info:
                pv_index = info.find(" pv ") + 4
                moves = info[pv_index:].strip().split()[:2]

            # Format moves
            white_move = self._format_move(moves[0]) if moves else "no move found"
            black_move = self._format_move(moves[1]) if len(moves) > 1 else None

            # Build result string
            result = f"Evaluation: {score:+.2f}\n"
            result += f"Best move for White: {white_move}"
            if black_move:
                result += f"\nPredicted response for Black: {black_move}"
            return result

        except Exception as e:
            return f"Error parsing analysis: {str(e)}"

    @staticmethod
    def _format_move(move):
        """Convert UCI move format to human-readable format"""
        if not move or len(move) < 4:
            return "invalid move"

        try:
            from_file = move[0]
            from_rank = move[1]
            to_file = move[2]
            to_rank = move[3]
            promotion = move[4] if len(move) > 4 else ''

            if not all(c in 'abcdefgh' for c in [from_file, to_file]) or \
               not all(c in '12345678' for c in [from_rank, to_rank]):
                return "invalid move"

            readable = f"{from_file}{from_rank} to {to_file}{to_rank}"
            if promotion:
                piece_names = {'q': 'Queen', 'r': 'Rook', 'b': 'Bishop', 'n': 'Knight'}
                readable += f" (promote to {piece_names.get(promotion.lower(), promotion)})"
            return readable
        except Exception as e:
            return f"invalid move ({str(e)})"