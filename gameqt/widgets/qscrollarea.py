import pygame
from .qwidget import QWidget

class QScrollArea(QWidget):
    class Shape: NoFrame = 0
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scroll_widget = None
        self._scroll_y = 0
        
    def setWidget(self, w): 
        self._scroll_widget = w
        w._set_parent(self)
        
    def setWidgetResizable(self, b): 
        self._widget_resizable = b
        
    def setFrameShape(self, shape): pass
    
    def _draw_recursive(self, offset=pygame.Vector2(0,0)):
        if not self.isVisible(): return
        my_pos = offset + pygame.Vector2(self._rect.topleft)
        self._draw(my_pos)
        
        if self._scroll_widget:
            # Resize child to match width
            if self._scroll_widget._rect.width != self._rect.width:
                self._scroll_widget._rect.width = self._rect.width
                if hasattr(self._scroll_widget, '_calculate_natural_size'):
                    self._scroll_widget._calculate_natural_size()
            
            # Height is managed by child itself or natural size
            from ..application import QApplication
            screen = QApplication._instance._windows[0]._screen
            old_clip = screen.get_clip()
            screen.set_clip(pygame.Rect(my_pos.x, my_pos.y, self._rect.width, self._rect.height))
            
            self._scroll_widget._draw_recursive(my_pos + pygame.Vector2(0, -self._scroll_y))
            
            screen.set_clip(old_clip)
            
            # Scrollbar
            if self._scroll_widget._rect.height > self._rect.height:
                bar_h = max(20, self._rect.height * (self._rect.height / self._scroll_widget._rect.height))
                bar_y = my_pos.y + (self._scroll_y / self._scroll_widget._rect.height) * self._rect.height
                pygame.draw.rect(screen, (180, 180, 180), (my_pos.x + self._rect.width - 8, bar_y, 6, bar_h), border_radius=3)

    def wheelEvent(self, ev):
        if self._scroll_widget:
            delta = ev.angleDelta().y()
            max_scroll = max(0, self._scroll_widget._rect.height - self._rect.height)
            move = (delta / 120.0) * 40 
            self._scroll_y = max(0, min(max_scroll, self._scroll_y - move))
            ev.accept()

    def mousePressEvent(self, ev):
        if ev.button() == 4: # Scroll Up
            self._scroll_y = max(0, self._scroll_y - 20)
            ev.accept()
        elif ev.button() == 5: # Scroll Down
            if self._scroll_widget:
                max_scroll = max(0, self._scroll_widget._rect.height - self._rect.height)
                self._scroll_y = min(max_scroll, self._scroll_y + 20)
                ev.accept()
        else:
            # Propagate click to child?
            # Simple hit test
            if self._scroll_widget:
                # We need to offset event pos 
                # ev.pos() is local to ScrollArea.
                # Child expects local to Child.
                # Child is at (0, -scroll_y).
                # So child_local = ev.pos() - (0, -scroll_y) = ev.pos() + (0, scroll_y)
                
                local_pos = ev.pos() + pygame.Vector2(0, self._scroll_y)
                # Create mapped event
                # This is getting complex for MVP.
                pass
