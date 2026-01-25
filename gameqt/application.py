import pygame
from .core import QMouseEvent, Qt, QPointF
from .gui import QImage

class QApplication:
    _instance = None
    def __init__(self, args): 
        pygame.init()
        QApplication._instance = self
        self._windows = []
        self._shortcuts = []
    def setApplicationName(self, name):
        self._app_name = name
        if self._windows:
            pygame.display.set_caption(name)
    @staticmethod
    def instance(): return QApplication._instance
    @staticmethod
    def clipboard():
        class MockClipboard:
            def mimeData(self):
                class MockMime:
                    def hasImage(self): return False
                    def hasText(self): return False
                    def text(self): return ""
                return MockMime()
            def setMimeData(self, data): 
                self._mime_data = data
                print(f"[Clipboard] Data set: {data}")
            def image(self): return QImage()
        return MockClipboard()
    def quit(self):
        self._running = False
    def exec(self):
        clock = pygame.time.Clock(); self._running = True
        while self._running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT: self._running = False
                elif event.type == pygame.KEYDOWN:
                    # Check shortcuts
                    for shortcut in self._shortcuts:
                        if hasattr(shortcut._sequence, 'matches') and shortcut._sequence.matches(event.key, event.mod):
                            shortcut.activated.emit()
                            # Should we break here? Usually yes if shortcut is triggered
                            break
                elif event.type == pygame.VIDEORESIZE:
                    for win in self._windows:
                        # QMainWindow is imported here to avoid circular dependency
                        from .widgets import QMainWindow
                        if isinstance(win, QMainWindow): 
                            win.resize(event.w, event.h)
                            win._screen = pygame.display.get_surface()
                for win in self._windows:
                    if win.isVisible(): win._handle_event(event, pygame.Vector2(0,0))
                
                # Check for hover/motion globally if needed, or let windows handle it


            if not self._windows: break
            has_visible = False
            for win in self._windows:
                if win.isVisible():
                    has_visible = True
                    win._draw_recursive(pygame.Vector2(0,0))
            if not has_visible and clock.get_time() > 5000: break
            pygame.display.flip(); clock.tick(60)
        pygame.quit(); return 0
