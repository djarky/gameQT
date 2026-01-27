import pygame
from ..core import PyGameModalDialog

class QFontDialog(PyGameModalDialog):
    def __init__(self, initial=None, title="Select Font"):
        super().__init__(title, 400, 350)
        self.fonts = pygame.font.get_fonts()[:20] # Limit for demo
        self.selected_font = self.fonts[0]
        self.size = 12
    @staticmethod
    def getFont(initial=None, parent=None, title="Select Font"):
        dlg = QFontDialog(initial, title)
        res = dlg.exec_()
        from ..gui import QFont
        return QFont(dlg.selected_font, dlg.size), res
    def draw(self, screen):
        super().draw(screen)
        font = pygame.font.SysFont(None, 18)
        for i, f in enumerate(self.fonts):
            y = self.rect.y + 50 + i*15
            color = (0, 120, 215) if f == self.selected_font else (0,0,0)
            txt = font.render(f, True, color)
            screen.blit(txt, (self.rect.x + 20, y))
        # Size replacement
        y_size = self.rect.bottom - 80
        txt = font.render(f"Size: {self.size}", True, (0,0,0))
        screen.blit(txt, (self.rect.x + 20, y_size))
        # Simple buttons
        btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
        pygame.draw.rect(screen, (0, 120, 215), btn_ok, border_radius=3)
        txt = font.render("OK", True, (255,255,255))
        screen.blit(txt, (btn_ok.centerx - txt.get_width()//2, btn_ok.centery - txt.get_height()//2))
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            # Select font
            for i, f in enumerate(self.fonts):
                if pygame.Rect(self.rect.x + 20, self.rect.y + 50 + i*15, 200, 15).collidepoint(x, y):
                    self.selected_font = f
            # Check OK button
            btn_ok = pygame.Rect(self.rect.centerx - 40, self.rect.bottom - 40, 80, 25)
            if btn_ok.collidepoint(x, y):
                self.result = True
                self.running = False
