from PyQt5.QtWidgets import QApplication
from chessboard_app import ChessboardApp
import sys

def main():
    """Application entry point"""
    app = QApplication(sys.argv)
    window = ChessboardApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()