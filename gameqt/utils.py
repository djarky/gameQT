import os
from .core import QObject, Signal
from .gui import QPixmap, QImage
from .widgets import QWidget

class QUndoStack(QObject):
    def __init__(self, parent=None): super().__init__(parent)
    def push(self, cmd): cmd.redo()
    def undo(self): pass
    def redo(self): pass
    def beginMacro(self, text): pass
    def endMacro(self): pass

class QUndoCommand:
    def __init__(self, text=""): pass
    def redo(self): pass
    def undo(self): pass

class QSettings(QObject):
    def __init__(self, organization="GameQt", application="Editor"):
        super().__init__()
        self._path = os.path.expanduser(f"~/.{organization}_{application}.json")
        self._cache = {}
        if os.path.exists(self._path):
            try:
                import json
                with open(self._path, 'r') as f: self._cache = json.load(f)
            except: pass
    def value(self, key, default=None, type=None):
        val = self._cache.get(key, default)
        return val
    def setValue(self, key, val):
        self._cache[key] = val
        try:
            import json
            with open(self._path, 'w') as f: json.dump(self._cache, f)
        except: pass

class QFileDialog:
    @staticmethod
    def getOpenFileName(*args): return ("", "")
    @staticmethod
    def getSaveFileName(*args): return ("", "")

class QMessageBox:
    StandardButton = type('StandardButton', (), {'Yes':1, 'No':0})
    @staticmethod
    def information(*args): pass
    @staticmethod
    def warning(*args): pass
    @staticmethod
    def critical(*args): pass
    @staticmethod
    def question(*args): return 0

class QBuffer:
    def open(self, m): pass
    def data(self): return type('MockData', (), {'data': lambda: b""})()

class QIODevice:
    class OpenModeFlag: ReadWrite = 1

class QMimeData:
    def hasImage(self): return False

class QModelIndex: pass
class QPrinter: pass

class QDrag:
    def __init__(self, *args): pass
    def exec(self, *args): pass

class QUndoView(QWidget):
    # This inherits from QWidget, imported locally
    pass

from .widgets import QWidget
class QUndoView(QWidget):
    def __init__(self, stack=None, parent=None): 
        super().__init__(parent)
        self._stack = stack
