import pygame
from ..core import Qt, QSize
from ..widgets import QWidget

class QSplitter(QWidget):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._items, self._orientation, self._sizes = [], orientation, None
    def addWidget(self, w): self._items.append(w); w._set_parent(self); w.show()
    def setSizes(self, sizes): self._sizes = sizes
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        visible_items = [i for i in self._items if i.isVisible()]
        if visible_items:
            n = len(visible_items)
            proportions = [self._sizes[self._items.index(i)] for i in visible_items] if self._sizes and len(self._sizes) == len(self._items) else [1]*n
            total = sum(proportions); curr = 0
            for i, item in enumerate(visible_items):
                p = proportions[i] / total
                if self._orientation == Qt.Orientation.Horizontal:
                    w = int(self._rect.width * p)
                    item._rect = pygame.Rect(curr, 0, w, self._rect.height); curr += w
                else:
                    h = int(self._rect.height * p)
                    item._rect = pygame.Rect(0, curr, self._rect.width, h); curr += h
        super()._draw_recursive(offset)
