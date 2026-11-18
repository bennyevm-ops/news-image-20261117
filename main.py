#!/usr/bin/env python3
"""Sixcast entry for make.fun bounty news-image-20261117.

"Sum up 17 November's world news in one image."

The program draws a newspaper front page for Tuesday 17 November 2026
entirely from scratch: a pure-standard-library PNG encoder (zlib +
struct), a tiny raster canvas with rect / circle / line / polygon
helpers, and a hand-authored 5x7 bitmap font.  No third-party packages,
no network, no clock, no randomness -- two runs produce byte-identical
output.

Output: $MAKEFUN_OUTPUT_DIR/entry.png (default /output), 1024x1024.
"""

import os
import struct
import zlib
from math import isqrt, sqrt

W = 1024
H = 1024

# ---------------------------------------------------------------------------
# Colours (flat, print-like)
# ---------------------------------------------------------------------------
PAPER = (246, 242, 230)
INK = (24, 24, 24)
WHITE = (250, 250, 246)
GREEN = (43, 102, 16)      # lead panel: Nvidia
RED = (154, 32, 32)        # markets down
CLAY = (148, 66, 40)       # Anthropic
TEAL = (10, 102, 102)      # Indonesia / rupiah
GOLD = (240, 184, 48)      # the coin
BLUE = (28, 72, 136)       # US retail

# ---------------------------------------------------------------------------
# 5x7 bitmap font.  Each glyph is 7 rows of 5 characters; '#' is ink.
# Covers A-Z, 0-9, space and the punctuation the headlines need.
# ---------------------------------------------------------------------------
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", ".#.#.", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "$": (".####", "#.#..", "#.#..", ".###.", "..#.#", "..#.#", "####."),
    "%": ("##..#", "##.#.", "...#.", "..#..", ".#...", ".#.##", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...##", "..#..", ".#...", ".#...", ".#...", "..#..", "...##"),
    ")": ("##...", "..#..", "...#.", "...#.", "...#.", "..#..", "##..."),
}


# ---------------------------------------------------------------------------
# Canvas: a flat RGB bytearray with small raster helpers.
# ---------------------------------------------------------------------------
def new_canvas(color):
    return bytearray(bytes(color) * (W * H))


def _set_span(px, x0, x1, y, color):
    """Fill pixels [x0, x1) on row y with color (clipped)."""
    if y < 0 or y >= H:
        return
    x0 = max(0, x0)
    x1 = min(W, x1)
    if x1 <= x0:
        return
    start = (y * W + x0) * 3
    px[start:start + (x1 - x0) * 3] = bytes(color) * (x1 - x0)


def fill_rect(px, x0, y0, x1, y1, color):
    """Fill the rectangle [x0, x1) x [y0, y1)."""
    for y in range(max(0, y0), min(H, y1)):
        _set_span(px, x0, x1, y, color)


def fill_circle(px, cx, cy, r, color):
    for dy in range(-r, r + 1):
        dx = isqrt(r * r - dy * dy)
        _set_span(px, cx - dx, cx + dx + 1, cy + dy, color)


def ring_circle(px, cx, cy, r, thickness, color):
    """Draw a circle outline of the given thickness (distance band)."""
    inner = r - thickness
    for y in range(cy - r, cy + r + 1):
        for x in range(cx - r, cx + r + 1):
            d2 = (x - cx) * (x - cx) + (y - cy) * (y - cy)
            if inner * inner < d2 <= r * r:
                if 0 <= x < W and 0 <= y < H:
                    i = (y * W + x) * 3
                    px[i:i + 3] = bytes(color)


def draw_line(px, x0, y0, x1, y1, color, thickness):
    """Thick line: every pixel within thickness/2 of the segment."""
    half = thickness / 2.0
    pad = int(half) + 1
    minx, maxx = min(x0, x1) - pad, max(x0, x1) + pad
    miny, maxy = min(y0, y1) - pad, max(y0, y1) + pad
    dx, dy = x1 - x0, y1 - y0
    seg_len2 = dx * dx + dy * dy
    for y in range(max(0, miny), min(H, maxy + 1)):
        for x in range(max(0, minx), min(W, maxx + 1)):
            if seg_len2 == 0:
                t = 0.0
            else:
                t = ((x - x0) * dx + (y - y0) * dy) / seg_len2
                t = max(0.0, min(1.0, t))
            qx, qy = x0 + t * dx, y0 + t * dy
            if sqrt((x - qx) ** 2 + (y - qy) ** 2) <= half + 0.4:
                i = (y * W + x) * 3
                px[i:i + 3] = bytes(color)


def fill_polygon(px, pts, color):
    """Scanline even-odd polygon fill."""
    ys = [p[1] for p in pts]
    for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
        nodes = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                nodes.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
        nodes.sort()
        for i in range(0, len(nodes) - 1, 2):
            _set_span(px, int(nodes[i]), int(nodes[i + 1]) + 1, y, color)


# ---------------------------------------------------------------------------
# Text
# ---------------------------------------------------------------------------
def text_width(s, scale, tracking=0):
    if not s:
        return 0
    advance = 6 * scale + tracking
    return (len(s) - 1) * advance + 5 * scale


def draw_text(px, x, y, s, scale, color, tracking=0):
    advance = 6 * scale + tracking
    for ch in s:
        glyph = FONT[ch]
        for row in range(7):
            line = glyph[row]
            for col in range(5):
                if line[col] == "#":
                    fill_rect(px, x + col * scale, y + row * scale,
                              x + (col + 1) * scale, y + (row + 1) * scale,
                              color)
        x += advance
    return x


def draw_text_centered(px, cx, y, s, scale, color, tracking=0):
    x = cx - text_width(s, scale, tracking) // 2
    draw_text(px, x, y, s, scale, color, tracking)


# ---------------------------------------------------------------------------
# PNG encoder (filter 0 rows, zlib level 9 -> deterministic bytes)
# ---------------------------------------------------------------------------
def _chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    out += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return out


def encode_png(px):
    raw = bytearray()
    row_bytes = W * 3
    for y in range(H):
        raw.append(0)
        raw += px[y * row_bytes:(y + 1) * row_bytes]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + _chunk(b"IHDR", ihdr)
            + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + _chunk(b"IEND", b""))


# ---------------------------------------------------------------------------
# Pictograms (bold, simple, drawn with the helpers above)
# ---------------------------------------------------------------------------
def draw_chip(px, cx, cy, body, accent, label_color):
    """Computer chip: body, pins on all four sides, labelled core."""
    half = 88
    x0, x1, y0, y1 = cx - half, cx + half, cy - half, cy + half
    pin_len, pin_th = 30, 16
    offsets = (-66, -22, 22, 66)
    for o in offsets:
        fill_rect(px, x0 - pin_len, cy + o - pin_th // 2, x0, cy + o + pin_th // 2, body)
        fill_rect(px, x1, cy + o - pin_th // 2, x1 + pin_len, cy + o + pin_th // 2, body)
        fill_rect(px, cx + o - pin_th // 2, y0 - pin_len, cx + o + pin_th // 2, y0, body)
        fill_rect(px, cx + o - pin_th // 2, y1, cx + o + pin_th // 2, y1 + pin_len, body)
    fill_rect(px, x0, y0, x1, y1, body)
    inner = 48
    fill_rect(px, cx - inner, cy - inner, cx + inner, cy + inner, accent)
    draw_text_centered(px, cx, cy - 24, "AI", 7, label_color, tracking=-2)


def draw_falling_chart(px, ox, oy, color):
    """Axes plus a zigzag line falling to a down-right arrowhead."""
    draw_line(px, ox + 24, oy + 46, ox + 24, oy + 152, color, 6)
    draw_line(px, ox + 24, oy + 152, ox + 118, oy + 152, color, 6)
    pts = [(ox + 34, oy + 62), (ox + 56, oy + 88), (ox + 72, oy + 74),
           (ox + 94, oy + 108), (ox + 112, oy + 134)]
    for i in range(len(pts) - 1):
        draw_line(px, pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, 7)
    fill_polygon(px, [(ox + 122, oy + 146), (ox + 100, oy + 136),
                      (ox + 118, oy + 122)], color)


def draw_robot(px, cx, cy, body, ink):
    """Simple robot head: antenna, ears, eyes, mouth, shoulders."""
    fill_rect(px, cx - 3, cy - 58, cx + 3, cy - 36, body)
    fill_circle(px, cx, cy - 65, 8, body)
    fill_rect(px, cx - 50, cy - 14, cx - 42, cy + 10, body)
    fill_rect(px, cx + 42, cy - 14, cx + 50, cy + 10, body)
    fill_rect(px, cx - 42, cy - 36, cx + 42, cy + 30, body)
    fill_circle(px, cx - 17, cy - 10, 7, ink)
    fill_circle(px, cx + 17, cy - 10, 7, ink)
    fill_rect(px, cx - 18, cy + 12, cx + 18, cy + 17, ink)
    fill_rect(px, cx - 20, cy + 30, cx + 20, cy + 38, body)
    fill_rect(px, cx - 34, cy + 38, cx + 34, cy + 46, body)


def draw_coin(px, cx, cy, face, ink):
    """A coin: rim, inner ring and the letters RP."""
    fill_circle(px, cx, cy, 48, ink)
    fill_circle(px, cx, cy, 43, face)
    ring_circle(px, cx, cy, 34, 3, ink)
    draw_text_centered(px, cx, cy - 17, "RP", 5, ink, tracking=-2)


def draw_cart(px, cx, cy, color, bg):
    """Shopping cart: handle, slatted basket, two wheels."""
    draw_line(px, cx - 58, cy - 42, cx - 40, cy - 26, color, 7)
    basket = [(cx - 40, cy - 26), (cx + 46, cy - 26),
              (cx + 36, cy + 24), (cx - 28, cy + 24)]
    fill_polygon(px, basket, color)
    for sx in (cx - 16, cx + 6, cx + 26):
        fill_rect(px, sx - 3, cy - 22, sx + 3, cy + 20, bg)
    fill_circle(px, cx - 24, cy + 40, 10, color)
    fill_circle(px, cx + 28, cy + 40, 10, color)


# ---------------------------------------------------------------------------
# Page layout: masthead, one lead panel, then a 2x2 grid.
# ---------------------------------------------------------------------------
def draw_masthead(px):
    draw_text_centered(px, W // 2, 28, "THE DAY IN ONE PICTURE", 4, INK, tracking=2)
    fill_rect(px, 28, 64, 996, 69, INK)
    draw_text_centered(px, W // 2, 82, "TUESDAY", 12, INK)
    draw_text_centered(px, W // 2, 178, "17 NOVEMBER 2026", 9, INK)
    fill_rect(px, 28, 254, 996, 263, INK)


def draw_lead(px):
    fill_rect(px, 28, 278, 996, 562, GREEN)
    draw_chip(px, 190, 420, WHITE, GREEN, WHITE)
    x = 344
    draw_text(px, x, 306, "NVIDIA SMASHES", 7, WHITE, tracking=-2)
    draw_text(px, x, 367, "ESTIMATES", 7, WHITE, tracking=-2)
    fill_rect(px, x, 440, 900, 443, WHITE)
    draw_text(px, x, 458, "REVENUE $115.8B +103%", 4, WHITE, tracking=-2)
    draw_text(px, x, 494, "GUIDES TO $130B", 4, WHITE, tracking=-2)


def draw_panel(px, x, y, bg, kind):
    fill_rect(px, x, y, x + 476, y + 201, bg)
    cx, cy = x + 68, y + 100
    tx = x + 136
    if kind == "stocks":
        draw_falling_chart(px, x + 6, y + 22, WHITE)
        draw_text(px, tx, y + 24, "STOCKS FALL", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 65, "A 4TH DAY", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 114, "AI FEARS GRIP", 4, WHITE, tracking=-3)
        draw_text(px, tx, y + 148, "WALL STREET", 4, WHITE, tracking=-3)
    elif kind == "anthropic":
        draw_robot(px, cx, cy, WHITE, INK)
        draw_text(px, tx, y + 24, "ANTHROPIC'S", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 65, "$1.5T IPO", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 114, "AI GIANT PRICES", 4, WHITE, tracking=-3)
        draw_text(px, tx, y + 148, "IPO THIS WEEK", 4, WHITE, tracking=-3)
    elif kind == "rupiah":
        draw_coin(px, cx, cy, GOLD, INK)
        draw_text(px, tx, y + 24, "RUPIAH AT", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 65, "RECORD LOW", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 114, "INDONESIA'S", 4, WHITE, tracking=-3)
        draw_text(px, tx, y + 148, "WEAKEST EVER", 4, WHITE, tracking=-3)
    elif kind == "retail":
        draw_cart(px, cx, cy, WHITE, bg)
        draw_text(px, tx, y + 24, "US SHOPPERS", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 65, "SLOW", 5, WHITE, tracking=-2)
        draw_text(px, tx, y + 116, "RETAIL +0.2%", 3, WHITE, tracking=-2)
        draw_text(px, tx, y + 143, "IMPORT PRICES +1.1%", 3, WHITE, tracking=-2)


def render():
    px = new_canvas(PAPER)
    # outer frame
    fill_rect(px, 6, 6, 1018, 11, INK)
    fill_rect(px, 6, 1013, 1018, 1018, INK)
    fill_rect(px, 6, 6, 11, 1018, INK)
    fill_rect(px, 1013, 6, 1018, 1018, INK)
    draw_masthead(px)
    draw_lead(px)
    draw_panel(px, 28, 578, RED, "stocks")
    draw_panel(px, 520, 578, CLAY, "anthropic")
    draw_panel(px, 28, 795, TEAL, "rupiah")
    draw_panel(px, 520, 795, BLUE, "retail")
    return encode_png(px)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(render())
    print("wrote", path)


if __name__ == "__main__":
    main()
