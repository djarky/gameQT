import pygame
from PIL import Image, ImageDraw, ImageFont
import os
import re

# Common emoji font paths
EMOJI_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/noto-emoji/NotoColorEmoji.ttf",
    "/usr/share/fonts/truetype/emoji/NotoColorEmoji.ttf",
]

# Common regular font paths for fallback
REGULAR_FONTS = [
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]

_emoji_font_path = None
for path in EMOJI_FONTS:
    if os.path.exists(path):
        _emoji_font_path = path
        break

_regular_font_path = None
for path in REGULAR_FONTS:
    if os.path.exists(path):
        _regular_font_path = path
        break

def has_emoji(text):
    """Simple check if text contains potential emoji or non-BMP characters."""
    if any(ord(c) > 0xFFFF for c in text): return True
    if re.search(r'[\u2000-\u32ff\u2700-\u27bf]', text): return True
    return False

def render_text(text, font_family, font_size, color):
    """
    Renders text to a pygame surface. 
    Uses Pillow for hybrid rendering if emojis are detected.
    """
    from ..gui.qfontdatabase import QFontDatabase
    
    if not has_emoji(text) or not _emoji_font_path:
        # Check if font_family is a custom font
        custom_path = QFontDatabase.getFontPath(font_family)
        if custom_path:
            try:
                font = pygame.font.Font(custom_path, font_size)
            except:
                font = pygame.font.SysFont(None, font_size)
        else:
            font = pygame.font.SysFont(font_family if font_family != "Arial" else None, font_size)
        return font.render(str(text), True, color)

    try:
        # Hybrid rendering with Pillow
        render_scale = 2
        actual_size = font_size * render_scale
        
        try:
            pil_emoji_font = ImageFont.truetype(_emoji_font_path, actual_size)
        except:
            pil_emoji_font = ImageFont.load_default()
            
        pil_reg_font = None
        custom_path = QFontDatabase.getFontPath(font_family)
        if custom_path:
            try:
                pil_reg_font = ImageFont.truetype(custom_path, actual_size)
            except: pass
            
        if not pil_reg_font:
            try:
                pil_reg_font = ImageFont.truetype(_regular_font_path, actual_size) if _regular_font_path else ImageFont.load_default()
            except:
                pil_reg_font = ImageFont.load_default()

        # Measure characters and offsets
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)

        chars_info = []
        total_w = 0
        max_h = 0
        min_top = 0

        for char in text:
            codepoint = ord(char)
            # Try to determine if emoji font has a better glyph than regular font
            has_emoji_glyph = False
            if _emoji_font_path:
                try:
                    mask = pil_emoji_font.getmask(char)
                    if mask.getbbox():
                        has_emoji_glyph = True
                except: pass

            # Decision: use emoji font if it has a glyph AND it's either in emoji range or reg font doesn't have it
            is_emoji_range = (codepoint > 0xFFFF) or (0x2300 <= codepoint <= 0x32FF) or (0x203C <= codepoint <= 0x21AA)
            use_emoji = has_emoji_glyph and (is_emoji_range or codepoint > 127)
            
            f = pil_emoji_font if use_emoji else pil_reg_font
            if not f: f = pil_emoji_font if pil_emoji_font else pil_reg_font
            
            w = draw.textlength(char, font=f)
            bbox = draw.textbbox((0, 0), char, font=f, embedded_color=use_emoji)
            h = bbox[3] - bbox[1]
            
            chars_info.append({
                'char': char, 'font': f, 'is_emoji': use_emoji, 'x': total_w,
                'offset_y': bbox[1], 'w': w, 'h': h
            })
            total_w += w
            max_h = max(max_h, h)
            min_top = min(min_top, bbox[1])
            
            # print(f"[DEBUG-CHAR] '{char}' (U+{codepoint:04X}) -> {'Emoji' if use_emoji else 'Reg'} Font")

        # Canvas size: apply some padding
        padding = 5
        img_w = int(total_w) + padding * 2
        img_h = int(max_h - min_top) + padding * 2
        
        img = Image.new('RGBA', (max(1, img_w), max(1, img_h)), (0, 0, 0, 0))
        draw_pil = ImageDraw.Draw(img)
        
        for ch in chars_info:
            draw_pil.text((ch['x'] + padding, -min_top + padding), ch['char'], font=ch['font'], fill=color, embedded_color=ch['is_emoji'])

        # Convert to Pygame
        pygame_surf = pygame.image.fromstring(img.tobytes("raw", "RGBA"), img.size, "RGBA")
        return pygame_surf
    except Exception as e:
        print(f"Emoji rendering failed: {e}")
        font = pygame.font.SysFont(font_family if font_family != "Arial" else None, font_size)
        return font.render(str(text), True, color)
