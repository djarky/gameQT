import pygame

class QFont:
    _cache = {}
    
    def __init__(self, family="Arial", size=12): self._family, self._size = family, size
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size
    
    def get_sys_font(self):
        key = (self._family, self._size)
        if key not in QFont._cache:
            QFont._cache[key] = pygame.font.SysFont(self._family if self._family != "Arial" else None, self._size)
        return QFont._cache[key]
