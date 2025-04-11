# Chess Position Analyzer

## Overview

The Chess Position Analyzer is a Python application that allows users to capture a portion of their screen containing a chessboard, analyze the position using the Stockfish chess engine, and receive move suggestions. The application also integrates with Gemini AI for advanced position recognition.

## Features

- **Screen Capture**: Use a snipping tool to capture a chessboard from your screen.
- **Position Analysis**: Analyze the captured position using the Stockfish chess engine.
- **Move Suggestions**: Get the best moves and evaluation for the current position.
- **AI Integration**: Use Gemini AI to recognize chess positions from images.

## Requirements

- Python 3.10 or later
- Windows OS
- Stockfish chess engine (included in the repository)
- Gemini API Key: Obtain an API key from [Gemini AI](https://ai.google/tools/) to enable advanced position recognition.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/zeffirojoe/chess-move-scanner.git
   ```
2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```bash
   python main.py
   ```
2. Use the "Capture Chessboard" button to snip a portion of your screen containing a chessboard.
3. View the FEN position and analysis in the application window.

## File Structure

- `main.py`: Entry point for the application.
- `chessboard_app.py`: Main application logic and UI.
- `snipping_tool.py`: Screen capture functionality.
- `chess_analyzer.py`: Stockfish integration for position analysis.
- `utils.py`: Utility functions.
- `stockfish/`: Source code and binaries for the Stockfish chess engine.

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

## Acknowledgments

- [Stockfish Chess Engine](https://stockfishchess.org/)
- [PyQt5](https://riverbankcomputing.com/software/pyqt/intro)
- [Gemini AI](https://ai.google/tools/)

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.
