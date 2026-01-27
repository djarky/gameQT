import pygame
from .qwidget import QWidget
from .qlabel import QLabel

class QStatusBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._rect.height = 25
        self._message_label = QLabel("", self)
        self._message_label._rect = pygame.Rect(5, 5, 200, 15)
        
    def showMessage(self, text, timeout=0):
        self._message_label.setText(text)
        # Timeout not implemented in this simple version
        
    def addWidget(self, widget):
        widget._set_parent(self)
        widget.show()
        # Simple layout: append to the right
        x = sum(c._rect.width + 5 for c in self._children if c != self._message_label)
        widget._rect.x = x + 210 # Offset by message label
        
    def _draw(self, pos):
        from ..application import QApplication
        screen = QApplication._instance._windows[0]._screen
        if not screen: return
        
        pygame.draw.rect(screen, (240, 240, 245), (pos.x, pos.y, self._rect.width, self._rect.height))
        pygame.draw.line(screen, (180, 180, 190), (pos.x, pos.y), (pos.x + self._rect.width, pos.y))
