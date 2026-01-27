import pygame
from ..core import PyGameModalDialog

class QMessageBox:
    class StandardButton: Ok = 1; Yes = 2; No = 3; Cancel = 4
    class Icon: Warning = 1; Information = 2; Critical = 3; Question = 4
    @staticmethod
    def warning(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def information(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def critical(parent, title, text, buttons=StandardButton.Ok, defaultButton=StandardButton.Ok):
        return MessageBox(title, text, buttons).exec_()
    @staticmethod
    def question(parent, title, text, buttons=StandardButton.Yes|StandardButton.No, defaultButton=StandardButton.No):
        return MessageBox(title, text, buttons).exec_()

class MessageBox(PyGameModalDialog):
    def __init__(self, title, text, buttons):
        super().__init__(title, 350, 200)
        self.text = text
        self.buttons = buttons
        self.btn_rects = []
        
    def draw(self, screen):
        super().draw(screen)
        
        font = pygame.font.SysFont("Arial", 14)
        
        # Text wrapping
        words = self.text.split(' ')
        lines = []
        curr_line = ""
        for w in words:
            test_line = curr_line + " " + w if curr_line else w
            if font.size(test_line)[0] < self.rect.width - 40:
                curr_line = test_line
            else:
                lines.append(curr_line)
                curr_line = w
        lines.append(curr_line)
        
        y = self.rect.y + 50
        for line in lines:
            txt = font.render(line, True, (0, 0, 0))
            screen.blit(txt, (self.rect.x + 20, y))
            y += 20
            
        # Buttons
        self.btn_rects = []
        btn_y = self.rect.bottom - 40
        btn_w = 80
        
        flags = QMessageBox.StandardButton
        btns_to_show = []
        if self.buttons & flags.Ok: btns_to_show.append((flags.Ok, "OK"))
        if self.buttons & flags.Yes: btns_to_show.append((flags.Yes, "Yes"))
        if self.buttons & flags.No: btns_to_show.append((flags.No, "No"))
        if self.buttons & flags.Cancel: btns_to_show.append((flags.Cancel, "Cancel"))
        
        total_w = len(btns_to_show) * (btn_w + 10)
        start_x = self.rect.centerx - total_w // 2
        
        mouse_pos = pygame.mouse.get_pos()
        
        for i, (val, label) in enumerate(btns_to_show):
            r = pygame.Rect(start_x + i*(btn_w+10), btn_y, btn_w, 25)
            self.btn_rects.append((val, r))
            
            color = (0, 100, 200) if r.collidepoint(mouse_pos) else (0, 120, 215)
            pygame.draw.rect(screen, color, r, border_radius=3)
            
            txt = font.render(label, True, (255, 255, 255))
            screen.blit(txt, (r.centerx - txt.get_width()//2, r.centery - txt.get_height()//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            for val, r in self.btn_rects:
                if r.collidepoint(x, y):
                    self.result = val
                    self.running = False
