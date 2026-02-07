import pygame
import os
import sys
from ..core import QObject, Signal, QMouseEvent, QWheelEvent, QPoint, QSize, Qt, PyGameModalDialog
from ..application import QApplication

class QWidget(QObject):
    def __init__(self, parent=None):
        super().__init__(parent); self._rect, self._visible, self._layout, self._stylesheet, self._screen = pygame.Rect(0, 0, 100, 100), False, None, "", None
        self._parent = None # Initialized by _set_parent
        self._children = []
        self._set_parent(parent)
        self.clicked = Signal(); self._accept_drops = False
        self._resized = False
        self._frame_shape = 0  # Qt.FrameShape.NoFrame
        self._window_flags = 0  # No flags by default
        self._cursor = None
    def setAcceptDrops(self, b): self._accept_drops = b
    def acceptDrops(self): return self._accept_drops
    def dragEnterEvent(self, event): 
        # Default implementation: accept nothing
        pass
    def dropEvent(self, event): 
        # Default implementation: do nothing
        pass
    def mousePressEvent(self, event):
        pass
    def mouseReleaseEvent(self, event):
        pass
    def mouseMoveEvent(self, event):
        pass
    def wheelEvent(self, event):
        pass
    def setWindowTitle(self, title):
        self._window_title = title
        from .qmainwindow import QMainWindow
        if isinstance(self, QMainWindow): pygame.display.set_caption(title)
    def resize(self, w, h): 
        self._rect.width, self._rect.height = w, h
        self._resized = True
        if hasattr(self, '_layout') and self._layout: self._layout.arrange(pygame.Rect(0, 0, w, h))
    def setGeometry(self, x, y, w, h):
        self._rect = pygame.Rect(x, y, w, h)
        self._resized = True
        if hasattr(self, '_layout') and self._layout: self._layout.arrange(pygame.Rect(0, 0, w, h))
    def move(self, x, y): self._rect.x, self._rect.y = x, y
    def setMinimumSize(self, w, h): self._min_size = (w, h)
    def minimumSize(self): return getattr(self, '_min_size', (0, 0))
    def setFrameShape(self, shape): 
        """Set the frame shape for this widget."""
        self._frame_shape = shape
    def frameShape(self): return getattr(self, '_frame_shape', 0)
    def setCursor(self, cursor): 
        """Set the cursor for this widget."""
        self._cursor = cursor
    def setWindowFlags(self, flags):
        """Set window flags (Dialog, FramelessWindowHint, etc.)."""
        self._window_flags = flags
        # Apply frameless hint if set
        from ..core import Qt
        if flags & Qt.WindowType.WindowTitleHint == 0:
            # Frameless - would need window chrome removal in future
            pass
    def windowFlags(self): return getattr(self, '_window_flags', 0)
    def viewport(self): return self # Fallback
    def window(self):
        curr = self
        while curr._parent: curr = curr._parent
        return curr
    def _get_screen(self):
        if not QApplication._instance: return None
        win = self.window()
        screen = getattr(win, '_screen', None)
        if not screen and QApplication._instance._windows: screen = getattr(QApplication._instance._windows[0], '_screen', None)
        return screen
    def mapToGlobal(self, p):
        # Calculate absolute position by traversing parent hierarchy
        abs_x, abs_y = 0, 0
        curr = self
        while curr:
            abs_x += curr._rect.x
            abs_y += curr._rect.y
            curr = curr._parent
        
        # Use QPointF if available, otherwise fallback to QPoint
        try: from ..core import QPointF
        except ImportError: from ..core import QPoint as QPointF
        
        pt = QPointF(p)
        return QPointF(abs_x + pt.x(), abs_y + pt.y())
    def setCentralWidget(self, widget):
        widget._set_parent(self); widget.show()
        widget._rect = pygame.Rect(0, 0, self._rect.width, self._rect.height)
    def sizeHint(self):
        """Returns the recommended size for the widget."""
        if hasattr(self, '_layout') and self._layout:
            return self._layout.sizeHint()
        return QSize(100, 30)
    def setStyleSheet(self, ss):
        self._stylesheet = ss
        # Basic parsing
        self._styles = {}
        for rule in ss.split(';'):
            if ':' in rule:
                k, v = rule.split(':', 1)
                self._styles[k.strip().lower()] = v.strip().lower()
        # Trigger layout update if padding or margins changed (conceptual)
    def show(self):
        self._visible = True
        if not self._parent and not self._screen:
            self._screen = pygame.display.set_mode((self._rect.width, self._rect.height), pygame.RESIZABLE)
        for child in self._children:
            from ..menus import QMenu
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
        if parent and hasattr(parent, '_children'):
            if self not in parent._children:
                parent._children.append(self)
    def _handle_event(self, event, offset):
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # Apply cursor if mouse is over this widget
        if event.type == pygame.MOUSEMOTION and hasattr(self, '_cursor') and self._cursor:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                try: 
                    pygame.mouse.set_cursor(self._cursor)
                except: 
                    pass
        
        # Special handling for QMainWindow with menu bar
        if hasattr(self, '_menu_bar') and self._menu_bar:
            if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
                menu_bar_rect = pygame.Rect(my_pos.x, my_pos.y, self._menu_bar._rect.width, self._menu_bar._rect.height)
                if menu_bar_rect.collidepoint(pygame.mouse.get_pos()) or (hasattr(self._menu_bar, '_active_menu') and self._menu_bar._active_menu):
                    return self._menu_bar._handle_event(event, my_pos)

        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_event(event, my_pos):
                return True
        
        # 2. Handle events for THIS widget
        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                btn = getattr(event, 'button', Qt.MouseButton.NoButton)
                if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                    if btn == 1: btn = Qt.MouseButton.LeftButton
                    elif btn == 2: btn = Qt.MouseButton.MidButton
                    elif btn == 3: btn = Qt.MouseButton.RightButton
                    # Do not filter out 4/5, let them be for now if needed, but QMouseEvent doesn't have flags for them
                
                btns = 0
                if event.type == pygame.MOUSEMOTION:
                    if event.buttons[0]: btns |= Qt.MouseButton.LeftButton
                    if event.buttons[1]: btns |= Qt.MouseButton.MidButton
                    if event.buttons[2]: btns |= Qt.MouseButton.RightButton
                else: btns = btn
                
                q_event = QMouseEvent(local_pos, btn, btns, pygame.key.get_mods())
                q_event.ignore() # Not accepted by default for bubbling
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if hasattr(self, 'mousePressEvent'): 
                        self.mousePressEvent(q_event)
                        q_event.accept()
                    self.clicked.emit()
                    q_event.accept() # Buttons should accept the event
                elif event.type == pygame.MOUSEBUTTONUP:
                    if hasattr(self, 'mouseReleaseEvent'): self.mouseReleaseEvent(q_event)
                elif event.type == pygame.MOUSEMOTION:
                    if hasattr(self, 'mouseMoveEvent'): self.mouseMoveEvent(q_event)
                
                return q_event.isAccepted()
        
        if event.type == pygame.MOUSEWHEEL:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                local_pos = pygame.Vector2(pygame.mouse.get_pos()) - my_pos
                px = getattr(event, 'precise_x', float(event.x))
                py = getattr(event, 'precise_y', float(event.y))
                w_event = QWheelEvent(local_pos, QPoint(int(px * 120), int(py * 120)), pygame.key.get_mods())
                w_event.ignore() # Default to ignored for bubbling
                if hasattr(self, 'wheelEvent'): self.wheelEvent(w_event)
                return w_event.isAccepted()
        
        # Legacy scroll
        if event.type == pygame.MOUSEBUTTONDOWN and event.button in (4, 5):
             mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
             if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                # We reuse mousePressEvent for legacy scroll handling in QScrollArea
                # But we should actually trigger wheelEvent or accepted mousePress
                return False # Let it bubble or be handled by specific logic
        
        return False
    
    def _handle_drop_event(self, event, offset):
        """Handle drag and drop events (DROPFILE, etc)"""
        if not self.isVisible(): return False
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        
        # 1. Deliver to children first (highest z-order)
        for child in reversed(self._children): 
            if child._handle_drop_event(event, my_pos):
                return True
        
        # 2. Check if THIS widget accepts drops and mouse is over it
        if self._accept_drops:
            mouse_rect = pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height)
            if mouse_rect.collidepoint(pygame.mouse.get_pos()):
                from ..application import QDragEnterEvent, QDropEvent
                if isinstance(event, QDragEnterEvent):
                    event.ignore() # Default to ignored, subclass must accept
                    if hasattr(self, 'dragEnterEvent'): self.dragEnterEvent(event)
                elif isinstance(event, QDropEvent):
                    event.ignore() # Default to ignored
                    if hasattr(self, 'dropEvent'): self.dropEvent(event)
                return event.isAccepted()
        return False

    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        if self._layout and hasattr(self._layout, 'arrange'): 
            # Layout arranges items relative to this widget's origin (0,0)
            self._layout.arrange(pygame.Rect(0, 0, self._rect.width, self._rect.height))
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        for child in self._children: child._draw_recursive(my_pos)
    def _draw(self, pos):
        screen = self._get_screen()
        if screen and self.__class__.__name__ != 'QMainWindow':
            from ..gui import QColor
            color = (220, 220, 225)
            class_name = self.__class__.__name__
            if "Thumbnail" in class_name: color = (190, 190, 200)
            elif "Inspector" in class_name: color = (200, 200, 210)
            elif "Canvas" in class_name: color = (255, 255, 255)
            elif "Splitter" in class_name: color = (230, 230, 230)
            pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.rect(screen, (120, 120, 130), (pos.x, pos.y, self._rect.width, self._rect.height), 1)
            if self._rect.width > 50 and self._rect.height > 20:
                from ..gui import QFont
                font = QFont(size=18).get_sys_font()
                txt = font.render(class_name, True, (80, 80, 90))
                screen.blit(txt, (pos.x + 4, pos.y + 4))
        
        # Render frame shape if set
        from ..core import Qt
        frame_shape = getattr(self, '_frame_shape', 0)
        if frame_shape != Qt.FrameShape.NoFrame and frame_shape != 0:
            rect = (pos.x, pos.y, self._rect.width, self._rect.height)
            if frame_shape == Qt.FrameShape.Box:
                # Simple box frame
                pygame.draw.rect(screen, (100, 100, 100), rect, 1)
            elif frame_shape == Qt.FrameShape.Panel:
                # Raised 3D panel effect
                # Light edges on top-left, dark on bottom-right
                pygame.draw.line(screen, (220, 220, 220), (rect[0], rect[1]), (rect[0] + rect[2], rect[1]))  # Top
                pygame.draw.line(screen, (220, 220, 220), (rect[0], rect[1]), (rect[0], rect[1] + rect[3]))  # Left
                pygame.draw.line(screen, (80, 80, 80), (rect[0], rect[1] + rect[3]), (rect[0] + rect[2], rect[1] + rect[3]))  # Bottom
                pygame.draw.line(screen, (80, 80, 80), (rect[0] + rect[2], rect[1]), (rect[0] + rect[2], rect[1] + rect[3]))  # Right
            elif frame_shape == Qt.FrameShape.StyledPanel:
                # OS-styled panel (similar to Panel but with border radius)
                pygame.draw.rect(screen, (200, 200, 200), rect, 2, border_radius=4)
        
        # Apply CSS-like styles if present
        if hasattr(self, '_stylesheet') and self._stylesheet:
            # Parse styles only if needed
            if not hasattr(self, '_parsed_styles') or self._last_stylesheet != self._stylesheet:
                self._parsed_styles = {}
                self._last_stylesheet = self._stylesheet
                for rule in self._stylesheet.split(';'):
                    if ':' in rule:
                        k, v = rule.split(':', 1)
                        self._parsed_styles[k.strip().lower()] = v.strip().lower()
            
            radius = 0
            if 'border-radius' in self._parsed_styles:
                try: radius = int(self._parsed_styles['border-radius'].replace('px', ''))
                except (ValueError, AttributeError): pass
                
            if 'background-color' in self._parsed_styles:
                try: 
                    color = QColor(self._parsed_styles['background-color']).to_pygame()
                    pygame.draw.rect(screen, color, (pos.x, pos.y, self._rect.width, self._rect.height), border_radius=radius)
                except (ValueError, AttributeError, KeyError): pass
            
            if 'border' in self._parsed_styles:
                # Simplistic border parsing
                border_color = (100, 100, 100)
                if 'solid' in self._parsed_styles['border']:
                    for c_name in QColor.NAMED_COLORS:
                        if c_name in self._parsed_styles['border']:
                            border_color = QColor.NAMED_COLORS[c_name]
                            break
                pygame.draw.rect(screen, border_color, (pos.x, pos.y, self._rect.width, self._rect.height), 1, border_radius=radius)
    def statusBar(self):
        # In Qt, only QMainWindow has a statusBar. 
        # For compatibility in nested widgets, we can try to find the window.
        curr = self
        while curr:
            if hasattr(curr, 'statusBar') and curr != self:
                return curr.statusBar()
            curr = curr._parent
        return None
    def setAcceptDrops(self, b): 
        self._accept_drops = b
    def addAction(self, action): 
        if not hasattr(self, '_actions'):
            self._actions = []
        self._actions.append(action)
    def setContextMenuPolicy(self, policy): 
        self._context_menu_policy = policy
