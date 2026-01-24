import pygame
from .core import QObject, Signal, Qt
from .widgets import QWidget
from .application import QApplication

class QMenuBar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent); self._menus = []; self._active_menu = None; self._menu_rects = []
    def addMenu(self, title):
        m = QMenu(title, self); self._menus.append(m); return m
    def _draw(self, pos):
        screen = pygame.display.get_surface()
        if screen:
            pygame.draw.rect(screen, (240, 240, 240), (pos.x, pos.y, self._rect.width, self._rect.height))
            pygame.draw.line(screen, (180, 180, 180), (pos.x, pos.y + self._rect.height - 1), (pos.x + self._rect.width, pos.y + self._rect.height - 1))
            
            font = pygame.font.SysFont(None, 20)
            curr_x_local = 12
            self._menu_rects = []
            for m in self._menus:
                txt = font.render(m.text if m.text else "[?]", True, (30, 30, 35))
                tw, th = txt.get_size()
                item_rect_local = pygame.Rect(curr_x_local - 5, 0, tw + 20, self._rect.height)
                self._menu_rects.append((m, item_rect_local))
                
                if self._active_menu == m:
                     pygame.draw.rect(screen, (200, 210, 230), (pos.x + item_rect_local.x, pos.y, item_rect_local.width, item_rect_local.height))
                elif item_rect_local.move(pos.x, pos.y).collidepoint(pygame.mouse.get_pos()):
                     pygame.draw.rect(screen, (225, 230, 240), (pos.x + item_rect_local.x, pos.y, item_rect_local.width, item_rect_local.height))
                
                screen.blit(txt, (pos.x + curr_x_local, pos.y + (self._rect.height - th) // 2))
                if self._active_menu == m: m._draw_dropdown(pygame.Vector2(pos.x + item_rect_local.x, pos.y + self._rect.height))
                curr_x_local += tw + 25
    def mousePressEvent(self, ev):
        # First check if we clicked on an active dropdown menu
        if self._active_menu:
            for m, rect in self._menu_rects:
                if m == self._active_menu:
                    # Calculate dropdown position
                    dropdown_pos = pygame.Vector2(rect.x, self._rect.height)
                    # Check if click is within dropdown area
                    dropdown_rect = pygame.Rect(rect.x, self._rect.height, 200, len(m._actions) * 28)
                    click_pos = pygame.Vector2(ev.pos().x(), ev.pos().y())
                    
                    if dropdown_rect.collidepoint(click_pos.x, click_pos.y):
                        # Click is inside dropdown
                        local_pos = click_pos - dropdown_pos
                        res = m._handle_dropdown_click(local_pos)
                        if res: 
                            self._active_menu = None
                        return
                    break

        # Check if we clicked on a menu title
        for m, rect in self._menu_rects:
            if rect.collidepoint(ev.pos().x(), ev.pos().y()):
                # Toggle menu: close if already open, open if closed
                self._active_menu = (None if self._active_menu == m else m)
                return
        
        # Click was outside menus, close any active menu
        self._active_menu = None

class QMenu(QWidget):
    def __init__(self, title="", parent=None): super().__init__(parent); self.text = title; self._actions = []
    def addAction(self, text): a = QAction(text, self); self._actions.append(a); return a
    def addMenu(self, arg):
        m = QMenu(arg, self) if isinstance(arg, str) else arg
        self._actions.append(m); return m
    def clear(self): self._actions = []
    def addSeparator(self): self._actions.append("SEP")
    def exec(self, pos=None):
        # Show menu at position and wait for selection
        # In a real implementation, this would show a Pygame popup menu
        print(f"[QMenu] Showing popup menu at {pos}")
        return None
    def _draw(self, pos):
        # Draw the menu at the given position
        # This would render menu items using Pygame
        pass
    def _draw_dropdown(self, pos):
        screen = pygame.display.get_surface()
        if not screen or not self._actions: return
        w, h = 200, len(self._actions) * 28
        pygame.draw.rect(screen, (255, 255, 255), (pos.x, pos.y, w, h))
        pygame.draw.rect(screen, (160, 160, 170), (pos.x, pos.y, w, h), 1)
        font = pygame.font.SysFont(None, 18)
        mouse_pos = pygame.mouse.get_pos()
        for i, a in enumerate(self._actions):
            rect = pygame.Rect(pos.x, pos.y + i*28, w, 28)
            if a == "SEP":
                 pygame.draw.line(screen, (220, 220, 225), (pos.x+10, pos.y+i*28+14), (pos.x+w-10, pos.y+i*28+14))
            else:
                is_menu = isinstance(a, QMenu)
                label = (a.text if not is_menu else a.text + "  >")
                if rect.collidepoint(mouse_pos):
                    pygame.draw.rect(screen, (0, 120, 215), rect)
                    txt = font.render(label, True, (255, 255, 255))
                else:
                    txt = font.render(label, True, (45, 45, 50))
                screen.blit(txt, (pos.x + 12, pos.y + i*28 + (28 - txt.get_height()) // 2))
    def _handle_dropdown_click(self, local_pos):
        # Check if click is within dropdown bounds
        menu_width = 200
        menu_height = len(self._actions) * 28
        
        if 0 <= local_pos.x() <= menu_width and 0 <= local_pos.y() <= menu_height:
            idx = int(local_pos.y() // 28)
            if 0 <= idx < len(self._actions):
                a = self._actions[idx]
                if a == "SEP": 
                    return False
                if isinstance(a, QAction): 
                    # Only trigger if action is enabled and visible
                    if a.isEnabled() and a.isVisible():
                        a.triggered.emit()
                        return True
                elif isinstance(a, QMenu):
                    # Submenu clicked - for now just return False to keep menu open
                    return False
        return False

class QAction(QObject):
    triggered, toggled = Signal(), Signal(bool)
    def __init__(self, text="", parent=None): 
        super().__init__(parent)
        self.text = text
        self._shortcut = None
        self._enabled = True
        self._visible = True
        self._checkable = False
        self._checked = False
    def setShortcut(self, s): 
        self._shortcut = s
    def setEnabled(self, e): 
        self._enabled = e
    def setVisible(self, v): 
        self._visible = v
    def setCheckable(self, b): 
        self._checkable = b
    def setChecked(self, b): 
        if self._checkable:
            self._checked = b
            self.toggled.emit(b)
    def isEnabled(self): 
        return self._enabled
    def isVisible(self): 
        return self._visible
    def isCheckable(self): 
        return self._checkable
    def isChecked(self): 
        return self._checked
