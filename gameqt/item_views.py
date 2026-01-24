import pygame
from .core import Signal, Qt
from .widgets import QWidget
from .application import QApplication

class QAbstractItemView(QWidget):
    class SelectionMode: SingleSelection = 1; MultiSelection = 2; ExtendedSelection = 3; ContourSelection = 4
    class DragDropMode: NoDragDrop = 0; InternalMove = 4
    def setDragDropMode(self, m): pass
    def setSelectionMode(self, m): pass

class QHeaderView:
    class ResizeMode: Stretch = 1; ResizeToContents = 2; Fixed = 3; Interactive = 0
    def setSectionResizeMode(self, c, m): pass

class QStyledItemDelegate: pass
class QStyleOptionViewItem: pass

class QTreeWidget(QAbstractItemView):
    itemChanged, itemSelectionChanged, customContextMenuRequested = Signal(object, int), Signal(), Signal(object)
    def __init__(self, parent=None):
        super().__init__(parent); self._items, self._header = [], QHeaderView(); self._root = QTreeWidgetItem(self); self.tree = self
    def clear(self): self._items = []
    def invisibleRootItem(self): return self._root
    def header(self): return self._header
    def setHeaderLabels(self, l): pass
    def setItemDelegateForColumn(self, c, d): pass
    def setContextMenuPolicy(self, p): pass
    def setDragEnabled(self, b): pass
    def setAcceptDrops(self, b): pass
    def topLevelItem(self, i): return self._items[i] if i < len(self._items) else None
    def _draw(self, pos):
        super()._draw(pos)
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, 25))
            txt = pygame.font.SysFont(None, 14).render("Element | Type | Vis | Opacity", True, (50, 50, 50))
            screen.blit(txt, (pos.x + 5, pos.y + 5))

class QTreeWidgetItem:
    def __init__(self, parent=None):
        self._parent, self._children, self._data, self._text = parent, [], {}, {}
        if parent and hasattr(parent, 'addChild'): parent.addChild(self)
    def data(self, c, r): return self._data.get((c, r))
    def setData(self, c, r, v): self._data[(c, r)] = v
    def text(self, c): return self._text.get(c, "")
    def setText(self, c, t): self._text[c] = t
    def addChild(self, i): self._children.append(i); i._parent = self
    def childCount(self): return len(self._children)
    def child(self, i): return self._children[i]
    def parent(self): return self._parent if isinstance(self._parent, QTreeWidgetItem) else None

class QListWidget(QAbstractItemView):
    class ViewMode: IconMode = 1; ListMode = 0
    def __init__(self, parent=None):
        super().__init__(parent); self.itemClicked, self._items = Signal(), []
        self._model = type('MockModel', (), {'rowsMoved': Signal()})()
    def setIconSize(self, s): pass
    def setViewMode(self, m): pass
    def setSelectionMode(self, m): pass
    def setDragEnabled(self, b): pass
    def setDropIndicatorShown(self, b): pass
    def setDragDropMode(self, m): pass
    def model(self): return self._model
    def addItem(self, i): self._items.append(i); i._list = self
    def count(self): return len(self._items)
    def clear(self): self._items = []

class QListWidgetItem:
    def __init__(self, *args):
        self._data = {}
        if len(args) > 1: self.text = args[1]
        elif len(args) > 0: self.text = args[0]
    def setData(self, r, v): self._data[r] = v
    def data(self, r): return self._data.get(r)
