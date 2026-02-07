class QColor:
    NAMED_COLORS = {
        'white': (255, 255, 255),
        'black': (0, 0, 0),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'yellow': (255, 255, 0),
        'cyan': (0, 255, 255),
        'magenta': (255, 0, 255),
        'gray': (128, 128, 128),
        'darkgray': (64, 64, 64),
        'lightgray': (192, 192, 192),
        'transparent': (0, 0, 0, 0)
    }
    def __init__(self, *args):
        if len(args) == 1:
            if isinstance(args[0], str):
                h = args[0].lstrip('#')
                if len(h) == 6: self.r, self.g, self.b = tuple(int(h[i:i+2], 16) for i in (0, 2, 4)); self.a = 255
                elif len(h) == 8: self.r, self.g, self.b, self.a = tuple(int(h[i:i+2], 16) for i in (0, 2, 4, 6))
                else: self.r = self.g = self.b = self.a = 255
            elif isinstance(args[0], QColor): self.r, self.g, self.b, self.a = args[0].r, args[0].g, args[0].b, args[0].a
            else: self.r = self.g = self.b = self.a = 255
        elif len(args) >= 3: self.r, self.g, self.b = args[:3]; self.a = args[3] if len(args) > 3 else 255
        else: self.r = self.g = self.b = 0; self.a = 255
    def to_pygame(self): return (self.r, self.g, self.b, self.a)
    def red(self): return self.r
    def green(self): return self.g
    def blue(self): return self.b
    def alpha(self): return self.a
