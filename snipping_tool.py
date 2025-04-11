from PyQt5.QtWidgets import QMainWindow, QRubberBand, QWidget, QApplication
from PyQt5.QtCore import QRect, QPoint, QSize, Qt
from PyQt5.QtGui import QPainter, QPen, QColor

class SnippingTool(QMainWindow):
    """
    Screen capture tool for selecting a portion of the screen.
    Provides a transparent overlay with visual feedback during selection.
    """
    
    def __init__(self):
        super().__init__()
        self._setup_window()
        self._setup_ui()
        
    def _setup_window(self):
        """Configure window properties and attributes"""
        self.setWindowTitle("Snipping Tool")
        screen = QApplication.primaryScreen()
        self.screen_geometry = screen.geometry()
        self.setGeometry(self.screen_geometry)
        
        # Configure window behavior
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        
    def _setup_ui(self):
        """Initialize UI components"""
        # Create central widget to handle mouse events
        self.central_widget = QWidget()
        self.central_widget.setAttribute(Qt.WA_TransparentForMouseEvents, False)
        self.setCentralWidget(self.central_widget)
        
        # Initialize selection components
        self.rubberBand = None
        self.origin = QPoint()
        
        # Set cursor and show window
        self.setCursor(Qt.CrossCursor)
        self.showFullScreen()
        self.raise_()
        self.activateWindow()

    def mousePressEvent(self, event):
        """Handle mouse press to start selection"""
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            if not self.rubberBand:
                self.rubberBand = QRubberBand(QRubberBand.Rectangle, self)
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rubberBand.show()
        event.accept()

    def mouseMoveEvent(self, event):
        """Update selection area during mouse movement"""
        if self.rubberBand:
            self.rubberBand.setGeometry(QRect(self.origin, event.pos()).normalized())
        event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to capture the selected area"""
        if event.button() == Qt.LeftButton and self.rubberBand:
            self.setCursor(Qt.ArrowCursor)
            selection_geometry = self.rubberBand.geometry()
            self.rubberBand.hide()
            self.captureScreen(selection_geometry)
            self.close()
            QApplication.processEvents()
            self.destroyed.emit()
        event.accept()

    def paintEvent(self, event):
        """Draw the overlay with selection feedback"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Ensure mouse events are captured with minimal opacity
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))
        
        # Draw border
        pen = QPen(QColor(255, 0, 0), 2, Qt.SolidLine)
        painter.setPen(pen)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        
        # Draw selection overlay
        if self.rubberBand and self.rubberBand.isVisible():
            self._draw_selection_overlay(painter)

    def _draw_selection_overlay(self, painter):
        """Draw the semi-transparent overlay around selection area"""
        selection = self.rubberBand.geometry()
        overlay = QColor(0, 0, 0, 40)
        painter.setBrush(overlay)
        
        # Draw four rectangles around selection
        painter.drawRect(0, 0, self.width(), selection.top())
        painter.drawRect(0, selection.bottom(), self.width(), self.height() - selection.bottom())
        painter.drawRect(0, selection.top(), selection.left(), selection.height())
        painter.drawRect(selection.right(), selection.top(), 
                        self.width() - selection.right(), selection.height())

    def captureScreen(self, rect):
        """Capture the selected portion of the screen"""
        screen = QApplication.primaryScreen()
        if screen:
            screenshot = screen.grabWindow(0, rect.x(), rect.y(), 
                                        rect.width(), rect.height())
            screenshot.save("chessboard_snip.png", "png")