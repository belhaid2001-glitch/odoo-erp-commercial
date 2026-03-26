"""
Generate module icons for all custom Odoo modules.
Creates simple, professional PNG icons with colored backgrounds and Font Awesome-style symbols.
"""
import struct
import zlib
import os
import math

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ADDONS_DIR = os.path.join(BASE_DIR, "custom_addons")

# Module definitions: (folder, bg_color_hex, symbol_char_description)
MODULES = {
    "custom_sale": {"color": (52, 152, 219), "bg": (235, 245, 253), "label": "VENTE", "symbol": "cart"},
    "custom_purchase": {"color": (46, 204, 113), "bg": (234, 250, 241), "label": "ACHAT", "symbol": "truck"},
    "custom_stock": {"color": (243, 156, 18), "bg": (254, 247, 235), "label": "STOCK", "symbol": "box"},
    "custom_accounting": {"color": (155, 89, 182), "bg": (245, 238, 250), "label": "COMPTA", "symbol": "calc"},
    "custom_hr": {"color": (231, 76, 60), "bg": (253, 237, 235), "label": "RH", "symbol": "people"},
    "custom_crm": {"color": (26, 188, 156), "bg": (233, 250, 246), "label": "CRM", "symbol": "target"},
    "custom_calendar": {"color": (52, 73, 94), "bg": (236, 238, 241), "label": "AGENDA", "symbol": "cal"},
    "custom_discuss": {"color": (41, 128, 185), "bg": (235, 243, 250), "label": "DISCUSS", "symbol": "chat"},
    "custom_documents": {"color": (22, 160, 133), "bg": (233, 247, 244), "label": "DOCS", "symbol": "file"},
    "custom_contacts": {"color": (192, 57, 43), "bg": (251, 237, 235), "label": "CONTACT", "symbol": "user"},
    "custom_dashboard": {"color": (44, 62, 80), "bg": (236, 238, 241), "label": "TABLEAU", "symbol": "dash"},
}

def create_png(width, height, pixels):
    """Create a PNG file from raw pixel data (list of (r,g,b) tuples)."""
    def make_chunk(chunk_type, data):
        chunk = chunk_type + data
        return struct.pack('>I', len(data)) + chunk + struct.pack('>I', zlib.crc32(chunk) & 0xffffffff)

    header = b'\x89PNG\r\n\x1a\n'
    ihdr = make_chunk(b'IHDR', struct.pack('>IIBBBBB', width, height, 8, 2, 0, 0, 0))

    raw_data = b''
    for y in range(height):
        raw_data += b'\x00'  # filter byte
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw_data += struct.pack('BBB', r, g, b)

    idat = make_chunk(b'IDAT', zlib.compress(raw_data, 9))
    iend = make_chunk(b'IEND', b'')
    return header + ihdr + idat + iend


def draw_rounded_rect(pixels, w, h, x1, y1, x2, y2, radius, color):
    """Draw a filled rounded rectangle."""
    for y in range(y1, y2):
        for x in range(x1, x2):
            inside = False
            # Check corners
            if x < x1 + radius and y < y1 + radius:
                if (x - (x1 + radius))**2 + (y - (y1 + radius))**2 <= radius**2:
                    inside = True
            elif x >= x2 - radius and y < y1 + radius:
                if (x - (x2 - radius - 1))**2 + (y - (y1 + radius))**2 <= radius**2:
                    inside = True
            elif x < x1 + radius and y >= y2 - radius:
                if (x - (x1 + radius))**2 + (y - (y2 - radius - 1))**2 <= radius**2:
                    inside = True
            elif x >= x2 - radius and y >= y2 - radius:
                if (x - (x2 - radius - 1))**2 + (y - (y2 - radius - 1))**2 <= radius**2:
                    inside = True
            else:
                inside = True

            if inside and 0 <= x < w and 0 <= y < h:
                pixels[y * w + x] = color


def draw_circle(pixels, w, h, cx, cy, r, color):
    """Draw a filled circle."""
    for y in range(max(0, cy - r), min(h, cy + r + 1)):
        for x in range(max(0, cx - r), min(w, cx + r + 1)):
            if (x - cx)**2 + (y - cy)**2 <= r**2:
                pixels[y * w + x] = color


def draw_rect(pixels, w, h, x1, y1, x2, y2, color):
    """Draw a filled rectangle."""
    for y in range(max(0, y1), min(h, y2)):
        for x in range(max(0, x1), min(w, x2)):
            pixels[y * w + x] = color


def draw_line(pixels, w, h, x1, y1, x2, y2, thickness, color):
    """Draw a thick line."""
    dx = x2 - x1
    dy = y2 - y1
    length = max(abs(dx), abs(dy), 1)
    for i in range(length + 1):
        x = int(x1 + dx * i / length)
        y = int(y1 + dy * i / length)
        for ty in range(-thickness//2, thickness//2 + 1):
            for tx in range(-thickness//2, thickness//2 + 1):
                px, py = x + tx, y + ty
                if 0 <= px < w and 0 <= py < h:
                    pixels[py * w + px] = color


def draw_triangle(pixels, w, h, x1, y1, x2, y2, x3, y3, color):
    """Draw a filled triangle."""
    min_y = max(0, min(y1, y2, y3))
    max_y = min(h - 1, max(y1, y2, y3))
    for y in range(min_y, max_y + 1):
        intersections = []
        edges = [(x1,y1,x2,y2), (x2,y2,x3,y3), (x3,y3,x1,y1)]
        for ex1, ey1, ex2, ey2 in edges:
            if ey1 == ey2:
                continue
            if min(ey1, ey2) <= y <= max(ey1, ey2):
                x = ex1 + (y - ey1) * (ex2 - ex1) / (ey2 - ey1)
                intersections.append(int(x))
        intersections.sort()
        for i in range(0, len(intersections) - 1, 2):
            for x in range(max(0, intersections[i]), min(w, intersections[i+1] + 1)):
                pixels[y * w + x] = color


def draw_symbol(pixels, w, h, symbol, color, white):
    """Draw a simple symbol in the center of the icon."""
    cx, cy = w // 2, h // 2 - 5

    if symbol == "cart":
        # Shopping cart
        draw_line(pixels, w, h, cx-20, cy-15, cx-10, cy-15, 3, color)
        draw_line(pixels, w, h, cx-10, cy-15, cx-5, cy+10, 3, color)
        draw_line(pixels, w, h, cx-5, cy+10, cx+20, cy+10, 3, color)
        draw_line(pixels, w, h, cx+20, cy+10, cx+25, cy-15, 3, color)
        draw_line(pixels, w, h, cx-10, cy-15, cx+25, cy-15, 3, color)
        draw_circle(pixels, w, h, cx-2, cy+18, 4, color)
        draw_circle(pixels, w, h, cx+16, cy+18, 4, color)

    elif symbol == "truck":
        # Delivery truck
        draw_rounded_rect(pixels, w, h, cx-25, cy-10, cx+5, cy+12, 3, color)
        draw_rounded_rect(pixels, w, h, cx+5, cy-3, cx+25, cy+12, 3, color)
        draw_rect(pixels, w, h, cx+15, cy-10, cx+25, cy-3, color)
        draw_circle(pixels, w, h, cx-15, cy+15, 5, color)
        draw_circle(pixels, w, h, cx+18, cy+15, 5, color)
        draw_circle(pixels, w, h, cx-15, cy+15, 3, white)
        draw_circle(pixels, w, h, cx+18, cy+15, 3, white)

    elif symbol == "box":
        # Box / package
        draw_rect(pixels, w, h, cx-18, cy-5, cx+18, cy+20, color)
        draw_rect(pixels, w, h, cx-22, cy-12, cx+22, cy-5, color)
        draw_line(pixels, w, h, cx, cy-12, cx, cy+20, 3, white)
        draw_rect(pixels, w, h, cx-5, cy-15, cx+5, cy-5, color)
        # Top flaps
        draw_triangle(pixels, w, h, cx-22, cy-12, cx, cy-20, cx, cy-12, color)
        draw_triangle(pixels, w, h, cx, cy-12, cx, cy-20, cx+22, cy-12, color)

    elif symbol == "calc":
        # Calculator
        draw_rounded_rect(pixels, w, h, cx-15, cy-20, cx+15, cy+22, 4, color)
        draw_rect(pixels, w, h, cx-10, cy-15, cx+10, cy-5, white)
        # Buttons
        for row in range(3):
            for col in range(3):
                bx = cx - 9 + col * 7
                by = cy + row * 7
                draw_rect(pixels, w, h, bx, by, bx+5, by+5, white)

    elif symbol == "people":
        # People / HR
        draw_circle(pixels, w, h, cx-12, cy-12, 8, color)
        draw_circle(pixels, w, h, cx-12, cy+8, 12, color)
        draw_circle(pixels, w, h, cx+12, cy-12, 8, color)
        draw_circle(pixels, w, h, cx+12, cy+8, 12, color)
        # Cut bottom
        draw_rect(pixels, w, h, cx-30, cy+15, cx+30, cy+30, white)

    elif symbol == "target":
        # Target / CRM
        draw_circle(pixels, w, h, cx, cy, 22, color)
        draw_circle(pixels, w, h, cx, cy, 18, white)
        draw_circle(pixels, w, h, cx, cy, 14, color)
        draw_circle(pixels, w, h, cx, cy, 10, white)
        draw_circle(pixels, w, h, cx, cy, 6, color)

    elif symbol == "cal":
        # Calendar
        draw_rounded_rect(pixels, w, h, cx-18, cy-15, cx+18, cy+20, 4, color)
        draw_rect(pixels, w, h, cx-18, cy-15, cx+18, cy-7, color)
        draw_rect(pixels, w, h, cx-18, cy-7, cx+18, cy+20, white)
        # Border
        draw_rect(pixels, w, h, cx-18, cy-7, cx-17, cy+20, color)
        draw_rect(pixels, w, h, cx+17, cy-7, cx+18, cy+20, color)
        draw_rect(pixels, w, h, cx-18, cy+19, cx+18, cy+20, color)
        # Day cells
        for row in range(3):
            for col in range(4):
                bx = cx - 14 + col * 8
                by = cy - 3 + row * 8
                draw_rect(pixels, w, h, bx, by, bx+5, by+5, color)
        # Top hooks
        draw_rect(pixels, w, h, cx-10, cy-20, cx-6, cy-12, color)
        draw_rect(pixels, w, h, cx+6, cy-20, cx+10, cy-12, color)

    elif symbol == "chat":
        # Chat bubble
        draw_rounded_rect(pixels, w, h, cx-22, cy-18, cx+22, cy+8, 8, color)
        draw_triangle(pixels, w, h, cx-8, cy+8, cx-15, cy+22, cx+2, cy+8, color)
        # Lines inside
        draw_line(pixels, w, h, cx-14, cy-10, cx+14, cy-10, 2, white)
        draw_line(pixels, w, h, cx-14, cy-3, cx+10, cy-3, 2, white)
        draw_line(pixels, w, h, cx-14, cy+3, cx+6, cy+3, 2, white)

    elif symbol == "file":
        # Document file
        draw_rounded_rect(pixels, w, h, cx-15, cy-20, cx+18, cy+22, 3, color)
        # Folded corner
        draw_triangle(pixels, w, h, cx+5, cy-20, cx+18, cy-7, cx+5, cy-7, white)
        draw_line(pixels, w, h, cx+5, cy-20, cx+18, cy-7, 2, color)
        draw_line(pixels, w, h, cx+5, cy-20, cx+5, cy-7, 2, color)
        # Lines
        draw_line(pixels, w, h, cx-8, cy-5, cx+10, cy-5, 2, white)
        draw_line(pixels, w, h, cx-8, cy+2, cx+10, cy+2, 2, white)
        draw_line(pixels, w, h, cx-8, cy+9, cx+5, cy+9, 2, white)
        draw_line(pixels, w, h, cx-8, cy+16, cx+10, cy+16, 2, white)

    elif symbol == "user":
        # User / contact
        draw_circle(pixels, w, h, cx, cy-10, 10, color)
        draw_circle(pixels, w, h, cx, cy+15, 18, color)
        draw_rect(pixels, w, h, cx-25, cy+20, cx+25, cy+35, white)

    elif symbol == "dash":
        # Dashboard / chart
        # Bar chart
        draw_rect(pixels, w, h, cx-20, cy+5, cx-12, cy+18, color)
        draw_rect(pixels, w, h, cx-8, cy-8, cx, cy+18, color)
        draw_rect(pixels, w, h, cx+4, cy-2, cx+12, cy+18, color)
        draw_rect(pixels, w, h, cx+16, cy-15, cx+24, cy+18, color)
        # Trend line
        draw_line(pixels, w, h, cx-18, cy+2, cx-4, cy-10, 2, white)
        draw_line(pixels, w, h, cx-4, cy-10, cx+8, cy-5, 2, white)
        draw_line(pixels, w, h, cx+8, cy-5, cx+20, cy-18, 2, white)


def draw_text_simple(pixels, w, h, text, cx, cy, color, scale=1):
    """Draw very simple block-letter text centered at (cx, cy)."""
    # Simple 5x7 font for uppercase + digits
    FONT = {
        'A': ["01110","10001","10001","11111","10001","10001","10001"],
        'B': ["11110","10001","10001","11110","10001","10001","11110"],
        'C': ["01110","10001","10000","10000","10000","10001","01110"],
        'D': ["11100","10010","10001","10001","10001","10010","11100"],
        'E': ["11111","10000","10000","11110","10000","10000","11111"],
        'F': ["11111","10000","10000","11110","10000","10000","10000"],
        'G': ["01110","10001","10000","10111","10001","10001","01110"],
        'H': ["10001","10001","10001","11111","10001","10001","10001"],
        'I': ["01110","00100","00100","00100","00100","00100","01110"],
        'K': ["10001","10010","10100","11000","10100","10010","10001"],
        'L': ["10000","10000","10000","10000","10000","10000","11111"],
        'M': ["10001","11011","10101","10101","10001","10001","10001"],
        'N': ["10001","11001","10101","10101","10011","10001","10001"],
        'O': ["01110","10001","10001","10001","10001","10001","01110"],
        'P': ["11110","10001","10001","11110","10000","10000","10000"],
        'R': ["11110","10001","10001","11110","10100","10010","10001"],
        'S': ["01111","10000","10000","01110","00001","00001","11110"],
        'T': ["11111","00100","00100","00100","00100","00100","00100"],
        'U': ["10001","10001","10001","10001","10001","10001","01110"],
        'V': ["10001","10001","10001","10001","01010","01010","00100"],
        'W': ["10001","10001","10001","10101","10101","11011","10001"],
        'X': ["10001","10001","01010","00100","01010","10001","10001"],
        ' ': ["00000","00000","00000","00000","00000","00000","00000"],
    }

    char_w = 5 * scale + scale  # width per char including gap
    total_w = len(text) * char_w - scale
    start_x = cx - total_w // 2

    for ci, ch in enumerate(text.upper()):
        glyph = FONT.get(ch, FONT.get(' '))
        if glyph is None:
            continue
        ox = start_x + ci * char_w
        for gy, row in enumerate(glyph):
            for gx, bit in enumerate(row):
                if bit == '1':
                    for sy in range(scale):
                        for sx in range(scale):
                            px = ox + gx * scale + sx
                            py = cy + gy * scale + sy
                            if 0 <= px < w and 0 <= py < h:
                                pixels[py * w + px] = color


def generate_icon(module_name, config, size=128):
    """Generate a single module icon."""
    w, h = size, size
    color = config["color"]
    bg = config["bg"]
    label = config["label"]
    symbol = config["symbol"]
    white = (255, 255, 255)

    pixels = [bg] * (w * h)

    # Background rounded rect
    draw_rounded_rect(pixels, w, h, 4, 4, w-4, h-4, 16, white)

    # Top colored bar
    draw_rounded_rect(pixels, w, h, 4, 4, w-4, 32, 16, color)
    draw_rect(pixels, w, h, 4, 20, w-4, 32, color)

    # Draw the symbol
    draw_symbol(pixels, w, h, symbol, color, white)

    # Draw label text at bottom
    draw_text_simple(pixels, w, h, label, w // 2, h - 22, color, scale=1)

    # Border
    for x in range(w):
        for t in range(2):
            if 0 <= 4+t < h: pixels[(4+t) * w + x] = color if x >= 4 and x < w-4 else pixels[(4+t) * w + x]
            if 0 <= h-5-t < h: pixels[(h-5-t) * w + x] = color if x >= 4 and x < w-4 else pixels[(h-5-t) * w + x]
    for y in range(h):
        for t in range(2):
            if 0 <= 4+t < w: pixels[y * w + 4+t] = color if y >= 4 and y < h-4 else pixels[y * w + 4+t]
            if 0 <= w-5-t < w: pixels[y * w + w-5-t] = color if y >= 4 and y < h-4 else pixels[y * w + w-5-t]

    return create_png(w, h, pixels)


def main():
    print("Generating module icons...")
    for module_name, config in MODULES.items():
        # Create directory
        icon_dir = os.path.join(ADDONS_DIR, module_name, "static", "description")
        os.makedirs(icon_dir, exist_ok=True)

        # Generate icon
        png_data = generate_icon(module_name, config)
        icon_path = os.path.join(icon_dir, "icon.png")
        with open(icon_path, 'wb') as f:
            f.write(png_data)
        print(f"  ✓ {module_name}/static/description/icon.png ({len(png_data)} bytes)")

    print(f"\nDone! Generated {len(MODULES)} icons.")


if __name__ == "__main__":
    main()
