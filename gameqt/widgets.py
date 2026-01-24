import pygame
from .core import QObject, Signal, QMouseEvent, Qt
from .application import QApplication

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet = pygame.Rect(0, 0, 100, 100), False, None, ""
        self._parent, self._children = parent, []
        if parent and hasattr(parent, '_children'): parent._children.append(self)
        self.clicked = Signal()
    def setWindowTitle(self, title):
        from .widgets import QMainWindow
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): self._rect.width, self._rect.height = w, h
    def setMinimumSize(self, w, h): pass
    def setCursor(self, cursor): pass
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def setStyleSheet(self, ss): self._stylesheet = ss
    def show(self):
        self._visible = True
        for child in self._children:
            from .menus import QMenu
            if hasattr(child, 'show') and not isinstance(child, QMenu): child.show()
    def hide(self):
        self._visible = False
        for child in self._children:
            if hasattr(child, 'hide'): child.hide()
    def setVisible(self, v): (self.show() if v else self.hide())
    def isVisible(self): return self._visible
    def close(self): self.hide()
    def setLayout(self, layout): self._layout = layout; layout._parent = self
    def _set_parent(self, parent):
        if self._parent and self in self._parent._children: self._parent._children.remove(self)
        if not parent and QApplication._instance and self not in QApplication._instance._windows: 
            QApplication._instance._windows.append(self)
        elif parent and QApplication._instance and self in QApplication._instance._windows:
            QApplication._instance._windows.remove(self)
        self._parent = parent
        if parent and hasattr(parent, '_children'): parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Special handling for QMainWindow with menu bar
        if hasattr(self, '_menu_bar') and self._menu_bar:
            # Check if event is a mouse event in menu bar area
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu_bar_rect = pygame.Rect(my_pos.x, my_pos.y, 
                                            self._menu_bar._rect.width, 
                                            self._menu_bar._rect.height)
                mouse_pos = pygame.mouse.get_pos()
                
                # If clicking in menu bar area OR menu bar has active menu, let it handle the event
                if menu_bar_rect.collidepoint(mouse_pos) or (hasattr(self._menu_bar, '_active_menu') and self._menu_bar._active_menu):
                    self._menu_bar._handle_event(event, my_pos)
                    return  # Menu bar handled it, don't propagate
        
        # Normal event propagation to children
        for child in reversed(self._children): 
            child._handle_event(event, my_pos)
        
        # Handle events for this widget
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                q_event = QMouseEvent(local_pos, 
                                     getattr(event, 'button', Qt.MouseButton.NoButton), 
                                     pygame.key.get_mods())
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'mousePressEvent'): self.mousePressEvent(q_event)
                    self.clicked.emit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, 'mouseReleaseEvent'): self.mouseReleaseEvent(q_event)
                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, 'mouseMoveEvent'): self.mouseMoveEvent(q_event)
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        if self._layout and hasattr(self._layout, 'arrange'): self._layout.arrange(self._rect)
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        for child in self._children: child._draw_recursive(my_pos)
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen and self.__class__.__name__ != 'QMainWindow':
            color = (220, 220, 225)
            class_name = self.__class__.__name__
            if "Thumbnail" in class_name: color = (190, 190, 200)
            elif "Inspector" in class_name: color = (200, 200, 210)
            elif "Canvas" in class_name: color = (255, 255, 255)
            elif "Splitter" in class_name: color = (230, 230, 230)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.rect(screen, (120, 120, 130), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
            if self._rect.width > 50 and self._rect.height > 20:
                font = pygame.font.SysFont(None, 18)
                txt = font.render(class_name, True, (80, 80, 90))
                screen.blit(txt, (pos.x + 4, pos.y + 4))
    def statusBar(self):
        class MockStatusBar:
            def addWidget(self, w): 
                if QApplication._instance and QApplication._instance._windows:
                    w._set_parent(QApplication._instance._windows[0]); w.show()
        return MockStatusBar()
    def setAcceptDrops(self, b): 
        self._accept_drops = b
    def addAction(self, action): 
        if not hasattr(self, '_actions'):
            self._actions = []
        self._actions.append(action)
    def setContextMenuPolicy(self, policy): 
        self._context_menu_policy = policy

class QMainWindow(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._screen = None; self._central_widget = None; self._menu_bar = None
        if QApplication._instance: QApplication._instance._windows.append(self)
    def setMenuBar(self, menu_bar):
        self._menu_bar = menu_bar
        menu_bar._set_parent(self); menu_bar.show()
    def setCentralWidget(self, widget):
        self._central_widget = widget
        widget._set_parent(self); widget.show()
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        menu_h = 35 if self._menu_bar and self._menu_bar.isVisible() else 0
        if self._menu_bar: self._menu_bar._rect = pygame.Rect(0, 0, self._rect.width, menu_h)
        if self._central_widget: self._central_widget._rect = pygame.Rect(0, menu_h, self._rect.width, self._rect.height - menu_h)
        
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        # Draw central widget and other children first
        if self._central_widget: self._central_widget._draw_recursive(my_pos)
        for child in self._children:
            if child not in (self._central_widget, self._menu_bar): child._draw_recursive(my_pos)
        
        # Draw menu bar LAST so dropdowns appear on top
        if self._menu_bar: self._menu_bar._draw_recursive(my_pos)
    def show(self):
        super().show()
        if not self._screen: self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
    def _draw(self, pos): (self._screen.fill((230, 230, 235)) if self._screen else None)

class QDialog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        if not parent and QApplication._instance: QApplication._instance._windows.append(self)
    def exec(self): self.show(); return 1

class QLabel(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def text(self): return self._text
    def _draw(self, pos):
        font = pygame.font.SysFont(None, 22)
        txt = font.render(self._text, True, (20, 20, 20))
        if QApplication._instance and QApplication._instance._windows and QApplication._instance._windows[0]._screen:
            QApplication._instance._windows[0]._screen.blit(txt, (pos.x + 2, pos.y + 2))

class QPushButton(QWidget):
    def __init__(self, text="", parent=None): super().__init__(parent); self._text = text
    def setText(self, text): self._text = text
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen:
            color = (100, 150, 240)
            if pygame.Rect(pos.x, pos.y, self._rect.width, self._rect.height).collidepoint(pygame.mouse.get_pos()): color = (120, 170, 255)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height), border_radius=4)
            pygame.draw.rect(screen, (50, 80, 180), (pos.x, pos.y, self._rect.width, self._rect.height), 1, border_radius=4)
            font = pygame.font.SysFont(None, 18)
            txt = font.render(self._text, True, (255, 255, 255))
            screen.blit(txt, (pos.x + (self._rect.width - txt.get_width())//2, pos.y + (self._rect.height - txt.get_height())//2))

class QSlider(QWidget):
    valueChanged = Signal(int)
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        super().__init__(parent); self._val, self._min, self._max = 50, 0, 100
    def setRange(self, mi, ma): self._min, self._max = mi, ma
    def setMinimum(self, v): self._min = v
    def setMaximum(self, v): self._max = v
    def setValue(self, v): self._val = v; self.valueChanged.emit(v)
    def value(self): return self._val
    def _draw(self, pos):
        if not QApplication._instance or not QApplication._instance._windows: return
        screen = QApplication._instance._windows[0]._screen
        if screen:
            cy = pos.y + self._rect.height // 2
            pygame.draw.line(screen, (150, 150, 150), (pos.x+10, cy), (pos.x+self._rect.width-10, cy), 2)
            r = (self._val - self._min) / (self._max - self._min) if self._max > self._min else 0.5
            pygame.draw.rect(screen, (100, 150, 240), (pos.x + 10 + int((self._rect.width-20)*r)-5, cy-10, 10, 20))
    def mousePressEvent(self, ev):
        if self._rect.width > 20: 
            r = max(0, min(1, (ev.pos().x() - 10) / (self._rect.width - 20)))
            self.setValue(int(self._min + r * (self._max - self._min)))

class QTabWidget(QWidget):
    def addTab(self, w, l): 
        if not hasattr(self, '_tabs'):
            self._tabs = []
        self._tabs.append({'widget': w, 'label': l})
        w._set_parent(self)
class QTextEdit(QWidget):
    def setHtml(self, h): 
        self._html = h
class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def setWidget(self, w): 
        self._scroll_widget = w
        w._set_parent(self)
    def setWidgetResizable(self, b): 
        self._widget_resizable = b
