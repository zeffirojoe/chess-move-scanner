import os
from PyQt5.QtWidgets import QMainWindow, QLabel, QTextEdit, QPushButton, QVBoxLayout, QWidget, QApplication
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
        self._setup_window()
        self._setup_ai()
        self._setup_ui()

    def _setup_window(self):
        """Configure main window properties"""
        self.setWindowTitle("Chess Position Analyzer")
        self.setGeometry(100, 100, 800, 800)

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
        self.position_label = QLabel("Current Position (FEN):", self)
        self.position_text = QTextEdit(self)
        self.position_text.setReadOnly(True)
        self.position_text.setMaximumHeight(50)

        self.analysis_label = QLabel("Best Moves:", self)
        self.analysis_text = QTextEdit(self)
        self.analysis_text.setReadOnly(True)

        self.capture_button = QPushButton("Capture Chessboard", self)
        self.capture_button.clicked.connect(self.capture_and_analyze)

        # Set up layout
        layout = QVBoxLayout()
        layout.addWidget(self.capture_button)
        layout.addWidget(self.position_label)
        layout.addWidget(self.position_text)
        layout.addWidget(self.analysis_label)
        layout.addWidget(self.analysis_text)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

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
                return fen_position
            else:
                self.position_text.setText("No response from the model.")
                return None

        except Exception as e:
            self.position_text.setText(f"Error getting FEN position: {e}")
            return None