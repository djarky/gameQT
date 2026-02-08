import pygame

class QFont:
    _cache = {}
    
    def __init__(self, family="Arial", size=12): self._family, self._size = family, size
    def setPointSize(self, size): self._size = size
    def pointSize(self): return self._size
    def family(self): return self._family
    
    def get_sys_font(self):
        from .qfontdatabase import QFontDatabase
        key = (self._family, self._size)
        if key not in QFont._cache:
            custom_path = QFontDatabase.getFontPath(self._family)
            if custom_path:
                try:
                    QFont._cache[key] = pygame.font.Font(custom_path, self._size)
                except Exception as e:
                    print(f"Failed to load custom font {self._family}: {e}")
                    QFont._cache[key] = pygame.font.SysFont(None, self._size)
            else:
                QFont._cache[key] = pygame.font.SysFont(self._family if self._family != "Arial" else None, self._size)
        return QFont._cache[key]
