import os
import chess
import chess.svg
from PyQt5.QtWidgets import QMainWindow, QLabel, QTextEdit, QPushButton, QVBoxLayout, QWidget, QApplication
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt
from utils import capture_chessboard
from chess_analyzer import ChessAnalyzer
import google.generativeai as genai

class ChessboardApp(QMainWindow):
    """
    Main application window for chess position analysis.
    Combines screen capture, position recognition, and move analysis.
    """
    
    def __init__(self):
        super().__init__()
        self.board = chess.Board()  # Initialize the chess board
        self.board_flipped = False  # Track board orientation
        self._setup_window()
        self._setup_ai()
        self._setup_ui()

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Chess Position Analyzer")
        self.setGeometry(100, 100, 600, 700)  # Adjusted dimensions to reduce width and better fit the chessboard

    def _setup_ai(self):
        """Initialize AI components"""
        # Configure Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if api_key:
            genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Initialize Stockfish analyzer
        stockfish_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "stockfish.exe")
        self.analyzer = ChessAnalyzer(stockfish_path)

    def _setup_ui(self):
        """Initialize UI components"""
        # Create widgets
        self.orientation_label = QLabel("White's side at bottom", self)
        self.orientation_label.setAlignment(Qt.AlignCenter)

        self.position_label = QLabel("Current Position (FEN):", self)
        self.position_text = QTextEdit(self)
        self.position_text.setReadOnly(True)
        self.position_text.setMaximumHeight(50)

        self.analysis_label = QLabel("Best Moves:", self)
        self.analysis_text = QTextEdit(self)
        self.analysis_text.setReadOnly(True)

        self.capture_button = QPushButton("Capture Chessboard", self)
        self.capture_button.clicked.connect(self.capture_and_analyze)

        self.flip_button = QPushButton("Flip Board", self)
        self.flip_button.clicked.connect(self.flip_board)

        self.svg_widget = QSvgWidget()

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.capture_button)
        layout.addWidget(self.flip_button)
        layout.addWidget(self.orientation_label)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_text)
        layout.addWidget(self.analysis_label)
        layout.addWidget(self.analysis_text)
        layout.addWidget(self.svg_widget)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.update_board()

    def capture_and_analyze(self):
        """Capture screen region and analyze chess position"""
        try:
            # Ensure clean state
            if os.path.exists("chessboard_snip.png"):
                os.remove("chessboard_snip.png")

            # Capture image
            image_path = self._capture_image()
            if not image_path:
                return

            # Get FEN position
            fen_position = self._get_fen_position(image_path)
            if not fen_position:
                return

            # Analyze position
            analysis = self.analyzer.analyze_position(fen_position)
            self.analysis_text.setText(analysis)

            # Extract the best move in UCI format
            lines = analysis.split("\n")
            for line in lines:
                if "Best move for" in line:
                    move_parts = line.split(":")[-1].strip().split(" to ")
                    if len(move_parts) == 2:
                        best_move = move_parts[0] + move_parts[1]  # Convert to UCI format
                        self.highlight_moves(best_move)
                        break

        except Exception as e:
            self.position_text.setText(f"An error occurred: {e}")
            self.analysis_text.setText("Analysis not available.")

    def _capture_image(self):
        """Capture and validate chess position image"""
        image_path = capture_chessboard()
        QApplication.processEvents()
        
        if not os.path.exists(image_path):
            self.position_text.setText("No image found. Please take a screenshot and try again.")
            return None
        return image_path

    def _get_fen_position(self, image_path):
        """Get FEN position from image using Gemini Vision"""
        try:
            with open(image_path, 'rb') as img_file:
                image_data = img_file.read()

            response = self.model.generate_content([
                "Analyze this chess board image and return ONLY the FEN "
                "(Forsyth–Edwards Notation) string representing the current position. "
                "Do not include any other text or explanation.",
                {"mime_type": "image/png", "data": image_data}
            ])

            if response.text:
                fen_position = response.text.strip()
                self.position_text.setText(fen_position)
                self.board.set_fen(fen_position)
                self.update_board()
                return fen_position
            else:
                self.position_text.setText("No response from the model.")
                return None

        except Exception as e:
            self.position_text.setText(f"Error getting FEN position: {e}")
            return None

    def update_board(self):
        """Update the SVG chessboard display"""
        board_svg = chess.svg.board(self.board, flipped=self.board_flipped)
        self.svg_widget.load(bytearray(board_svg, encoding='utf-8'))

    def flip_board(self):
        """Flip the board view between white and black perspective"""
        self.board_flipped = not self.board_flipped
        self.orientation_label.setText("Black's side at bottom" if self.board_flipped else "White's side at bottom")
        self.update_board()

    def highlight_moves(self, move):
        """Highlight the recommended move on the board without altering the game state."""
        if move:
            try:
                chess_move = chess.Move.from_uci(move)
                if chess_move in self.board.legal_moves:
                    board_svg = chess.svg.board(self.board, lastmove=chess_move, flipped=self.board_flipped)
                    self.svg_widget.load(bytearray(board_svg, encoding='utf-8'))
            except ValueError:
                pass
        else:
            self.update_board()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    viewer = ChessboardApp()
    viewer.show()
    sys.exit(app.exec_())