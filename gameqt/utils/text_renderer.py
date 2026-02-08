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
            
        # Resolve regular font
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

        # Measure total width
        dummy_img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(dummy_img)
        
        total_w = 0
        heights = []
        
        chars_info = []
        for char in text:
            # Decide which font to use for this character
            is_emoji = ord(char) > 0xFFFF or (0x2000 <= ord(char) <= 0x32FF)
            f = pil_emoji_font if is_emoji else pil_reg_font
            
            w = draw.textlength(char, font=f)
            bbox = draw.textbbox((0, 0), char, font=f, embedded_color=is_emoji)
            
            chars_info.append((char, f, is_emoji, total_w))
            total_w += w
            heights.append(bbox[3])
            
        total_h = max(heights) if heights else actual_size

        # Create image
        img = Image.new('RGBA', (int(total_w) + 10, int(total_h) + 10), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        for char, f, is_emoji, x_pos in chars_info:
            draw.text((x_pos, 0), char, font=f, fill=color, embedded_color=is_emoji)

        # Convert to Pygame
        raw_data = img.tobytes("raw", "RGBA")
        pygame_surf = pygame.image.fromstring(raw_data, img.size, "RGBA")
        
        # Scale back
        final_w, final_h = img.size[0] // render_scale, img.size[1] // render_scale
        pygame_surf = pygame.transform.smoothscale(pygame_surf, (final_w, final_h))
        
        return pygame_surf
    except Exception as e:
        print(f"Emoji rendering failed: {e}")
        font = pygame.font.SysFont(font_family if font_family != "Arial" else None, font_size)
        return font.render(str(text), True, color)
