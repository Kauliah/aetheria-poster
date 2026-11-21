#!/usr/bin/env python3
"""Draw AETHERIA — a travel poster for a place that isn't there.

A floating-isles poster: dusk sky, a low gold sun, three floating islands
with a waterfall pouring off the main island into a sea of clouds below,
a small lighthouse, a drifting balloon, and the place name set large in
serif type. 1024x1024 PNG, well under 1 MiB.
"""
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def vgrad(stops, height):
    """Vertical gradient. stops: list of (y_frac, (r, g, b))."""
    ys = np.array([s[0] * (height - 1) for s in stops], dtype=float)
    cols = np.array([s[1] for s in stops], dtype=float)
    y = np.arange(height, dtype=float)
    r = np.interp(y, ys, cols[:, 0])
    g = np.interp(y, ys, cols[:, 1])
    b = np.interp(y, ys, cols[:, 2])
    arr = np.stack([r, g, b], axis=1).astype(np.uint8)
    return np.repeat(arr[:, None, :], W, axis=1)


def sky():
    stops = [
        (0.00, (16, 22, 60)),
        (0.26, (36, 64, 112)),
        (0.45, (58, 104, 128)),
        (0.58, (122, 132, 118)),
        (0.66, (238, 170, 100)),
    ]
    return Image.fromarray(vgrad(stops, H), "RGB")


def ellipse_layer(draw_fn, blur=0):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    draw_fn(d)
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    return layer


def cloud(img, cx, cy, rx, ry, color, blur=6):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=color + (255,))
    d.ellipse([cx - rx * 0.6, cy - ry * 1.5, cx + rx * 0.5, cy + ry * 0.4],
              fill=color + (255,))
    d.ellipse([cx - rx * 0.3, cy - ry * 0.9, cx + rx * 0.8, cy + ry * 0.6],
              fill=color + (255,))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    img.alpha_composite(layer)


def island(draw, top_y, x0, x1, tip_y, tip_x, rock, rock_light, grass):
    """A floating island: flat grassy top, cliff tapering to a point."""
    mid = (x0 + x1) // 2
    cliff = [(x0, top_y), (x1, top_y),
             (tip_x + (x1 - tip_x) // 3, tip_y - 40),
             (tip_x, tip_y),
             (tip_x - (tip_x - x0) // 3, tip_y - 40)]
    draw.polygon(cliff, fill=rock)
    # strata lines on the cliff
    for i, f in enumerate((0.25, 0.5, 0.72)):
        y = top_y + (tip_y - top_y) * f
        w = (x1 - x0) * (1 - f) * 0.42
        draw.line([(mid - w, y), (mid + w, y)], fill=rock_light, width=4)
    # grassy cap
    draw.ellipse([x0 - 8, top_y - 16, x1 + 8, top_y + 14], fill=grass)
    draw.rectangle([x0, top_y - 6, x1, top_y + 4], fill=grass)


def pine(draw, x, y, s, color):
    draw.polygon([(x, y - s), (x - s * 0.45, y), (x + s * 0.45, y)], fill=color)
    draw.polygon([(x, y - s * 1.7), (x - s * 0.32, y - s * 0.5),
                  (x + s * 0.32, y - s * 0.5)], fill=color)
    draw.rectangle([x - 2, y, x + 2, y + s * 0.25], fill=(60, 42, 34))


def tracked_text(draw, cx, y, text, font, fill, tracking=0, shadow=None):
    widths = [draw.textlength(ch, font=font) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = cx - total / 2
    if shadow:
        sx, sy, scol = shadow
        xx = cx - total / 2
        for ch, w in zip(text, widths):
            draw.text((xx + sx, y + sy), ch, font=font, fill=scol)
            xx += w + tracking
    for ch, w in zip(text, widths):
        draw.text((x, y), ch, font=font, fill=fill)
        x += w + tracking
    return total


def main():
    img = sky().convert("RGBA")

    # --- sun glow and sun, low on the horizon ---
    glow = ellipse_layer(
        lambda d: d.ellipse([560, 350, 830, 620], fill=(255, 196, 110, 170)),
        blur=55)
    img.alpha_composite(glow)
    d = ImageDraw.Draw(img)
    d.ellipse([648, 448, 752, 552], fill=(255, 216, 132, 255))
    d.ellipse([660, 460, 740, 540], fill=(255, 232, 170, 255))

    # --- wispy high clouds ---
    for (cx, cy, rx, ry, col) in [
            (180, 300, 180, 16, (250, 220, 190)),
            (830, 250, 200, 14, (240, 205, 185)),
            (480, 180, 150, 12, (220, 195, 210))]:
        cloud(img, cx, cy, rx, ry, col, blur=10)

    # --- distant right island (hazy) ---
    d = ImageDraw.Draw(img)
    island(d, 300, 800, 930, 420, 868, (122, 104, 128), (150, 132, 146),
           (128, 140, 116))

    # --- left island with pines ---
    island(d, 420, 110, 300, 560, 205, (88, 66, 86), (128, 100, 112),
           (80, 122, 80))
    pine(d, 170, 414, 26, (52, 84, 56))
    pine(d, 215, 414, 20, (58, 90, 60))
    pine(d, 255, 414, 24, (52, 84, 56))

    # --- main island, centre ---
    island(d, 360, 380, 660, 580, 520, (96, 72, 92), (138, 106, 118),
           (88, 132, 84))
    pine(d, 430, 354, 26, (54, 88, 58))
    pine(d, 470, 354, 20, (60, 94, 62))

    # --- lighthouse on the main island ---
    lx = 606
    d.rectangle([lx - 7, 306, lx + 7, 360], fill=(250, 244, 230))
    d.rectangle([lx - 9, 300, lx + 9, 308], fill=(196, 70, 60))
    d.polygon([(lx - 10, 300), (lx + 10, 300), (lx, 288)], fill=(196, 70, 60))
    d.ellipse([lx - 4, 312, lx + 4, 320], fill=(255, 214, 120))
    lamp = ellipse_layer(
        lambda dd: dd.ellipse([lx - 26, 296, lx + 26, 332],
                              fill=(255, 210, 110, 150)), blur=8)
    img.alpha_composite(lamp)
    d = ImageDraw.Draw(img)

    # --- waterfall off the main island's edge ---
    wf = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wf)
    for i, (x, wdt) in enumerate([(556, 10), (572, 7), (586, 12), (600, 6)]):
        wd.line([(x, 372), (x + 6, 660)], fill=(226, 238, 246, 235),
                width=wdt)
        wd.line([(x, 372), (x + 6, 660)], fill=(255, 255, 255, 200),
                width=max(2, wdt // 3))
    wf = wf.filter(ImageFilter.GaussianBlur(1.2))
    img.alpha_composite(wf)
    d = ImageDraw.Draw(img)
    d.ellipse([540, 648, 640, 676], fill=(240, 246, 250, 220))

    # --- sea of clouds, bottom third ---
    sea = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea)
    sd.rectangle([0, 660, W, H], fill=(246, 228, 202, 255))
    sea = sea.filter(ImageFilter.GaussianBlur(2))
    img.alpha_composite(sea)
    for (cx, cy, rx, ry, col) in [
            (150, 760, 260, 90, (250, 236, 212)),
            (420, 820, 300, 110, (244, 206, 184)),
            (700, 780, 280, 100, (250, 224, 196)),
            (920, 840, 260, 110, (240, 200, 178)),
            (300, 950, 320, 110, (238, 196, 176)),
            (640, 960, 320, 110, (246, 210, 182)),
            (60, 900, 220, 90, (228, 190, 190)),
            (880, 700, 200, 70, (252, 214, 158))]:
        cloud(img, cx, cy, rx, ry, col, blur=8)

    # --- drifting balloon (clear sky, top right) ---
    d = ImageDraw.Draw(img)
    bx, by = 150, 335
    d.ellipse([bx - 34, by - 42, bx + 34, by + 30], fill=(214, 92, 74))
    d.ellipse([bx - 12, by - 42, bx + 12, by + 30], fill=(250, 232, 200))
    d.polygon([(bx - 30, by + 28), (bx + 30, by + 28), (bx + 8, by + 52),
               (bx - 8, by + 52)], fill=(120, 84, 60))
    d.rectangle([bx - 9, by + 52, bx + 9, by + 66], fill=(90, 60, 40))

    # --- birds ---
    for (x, y, s) in [(760, 260, 12), (150, 130, 12),
                      (700, 150, 9), (330, 120, 10)]:
        d.arc([x - s, y - s // 2, x, y + s // 2], 200, 340,
              fill=(40, 34, 60), width=3)
        d.arc([x, y - s // 2, x + s, y + s // 2], 200, 340,
              fill=(40, 34, 60), width=3)

    # --- type ---
    d = ImageDraw.Draw(img)
    name_font = ImageFont.truetype(SERIF, 118)
    tag_font = ImageFont.truetype(SANS, 30)
    foot_font = ImageFont.truetype(SANS_B, 24)
    tracked_text(d, W // 2, 62, "AETHERIA", name_font,
                 (252, 244, 224), tracking=16,
                 shadow=(4, 5, (20, 16, 48)))
    d.line([(W // 2 - 150, 208), (W // 2 + 150, 208)],
           fill=(232, 190, 120), width=3)
    d.polygon([(W // 2 - 7, 201), (W // 2 + 7, 201), (W // 2, 215),
               (W // 2 - 7, 201)], fill=(232, 190, 120))
    tracked_text(d, W // 2, 226, "THE ISLES ABOVE THE CLOUDS", tag_font,
                 (240, 210, 150), tracking=8,
                 shadow=(2, 2, (20, 16, 48)))
    tracked_text(d, W // 2, 948, "WHERE THE SEA FALLS INTO THE SKY",
                 foot_font, (255, 250, 235), tracking=5,
                 shadow=(2, 2, (60, 40, 50)))

    out = img.convert("RGB")
    out.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
