import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QEventLoop
from snipping_tool import SnippingTool

def capture_chessboard():
    """Create and run the snipping tool to capture a portion of the screen"""
    app = QApplication.instance() or QApplication([])
    
    snippingTool = SnippingTool()
    
    # Wait for snipping tool to complete
    loop = QEventLoop()
    snippingTool.destroyed.connect(loop.quit)
    loop.exec_()

    image_path = "chessboard_snip.png"
    if not os.path.exists(image_path):
        raise ValueError("No image found. Please take a screenshot and try again.")
    return image_path