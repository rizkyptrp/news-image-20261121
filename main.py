#!/usr/bin/env python3
"""THE WORLD TODAY -- front page for Saturday 21 November 2026.

Draws a newspaper front page in code (own PNG writer, own 5x7 bitmap
font, own drawing primitives) and writes it to entry.png. Standard
library only, no network, deterministic output.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

PAPER = (248, 244, 233)
INK = (17, 17, 17)
NAVY = (27, 42, 74)
NAVY_LT = (43, 63, 105)
RED = (178, 34, 34)
RED_LT = (214, 90, 80)
GREEN = (34, 120, 70)
BLUE = (38, 84, 160)
SKY = (205, 225, 240)
GOLD = (212, 160, 40)
GREY = (120, 120, 116)
GREY_LT = (228, 226, 218)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# ---------------------------------------------------------------- canvas

PIX = bytearray(W * H * 3)


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        PIX[i], PIX[i + 1], PIX[i + 2] = c


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            PIX[i], PIX[i + 1], PIX[i + 2] = c


def hline(x, y, w, c, t=1):
    fill_rect(x, y, w, t, c)


def vline(x, y, h, c, t=1):
    fill_rect(x, y, t, h, c)


def rect_outline(x, y, w, h, c, t=2):
    hline(x, y, w, c, t)
    hline(x, y + h - t, w, c, t)
    vline(x, y, h, c, t)
    vline(x + w - t, y, h, c, t)


def line(x0, y0, x1, y1, c, t=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    while True:
        for a in range(t):
            for b in range(t):
                px(x0 + a, y0 + b, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def circle(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                px(xx, yy, c)


def triangle(x0, y0, x1, y1, x2, y2, c):
    # Fill a triangle by scanlines.
    ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
    (ay, ax), (by, bx), (cy, cx) = ys
    def interp(y, y_a, x_a, y_b, x_b):
        if y_b == y_a:
            return x_a
        return x_a + (x_b - x_a) * (y - y_a) / (y_b - y_a)
    for y in range(ay, cy + 1):
        if y < by:
            xa = interp(y, ay, ax, by, bx)
        else:
            xa = interp(y, by, bx, cy, cx)
        xb = interp(y, ay, ax, cy, cx)
        lo, hi = sorted([int(round(xa)), int(round(xb))])
        for x in range(lo, hi + 1):
            px(x, y, c)


# ---------------------------------------------------------------- font
# Hand-made 5x7 bitmap font. Each glyph: 7 rows of 5 bits ("#" on, "." off).

def _g(*rows):
    return rows


FONT = {
    "A": _g("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": _g("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": _g("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": _g("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": _g("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": _g("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": _g("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": _g("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": _g("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": _g("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": _g("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": _g("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": _g("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": _g("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": _g("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": _g("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": _g("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": _g("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": _g("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": _g("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": _g("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": _g("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": _g("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": _g("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": _g("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": _g("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": _g("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": _g("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": _g("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": _g("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": _g("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": _g("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": _g("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": _g("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": _g("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": _g("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": _g(".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": _g(".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": _g(".....", ".....", ".....", ".....", ".##..", ".#...", "#...."),
    "%": _g("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "$": _g("..#..", ".####", "#.#.#", ".###.", "..#.#", "####.", "..#.."),
    "-": _g(".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    ":": _g(".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": _g(".....", ".##..", ".##..", ".....", ".##..", ".#...", "#...."),
    "(": _g("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": _g(".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": _g("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "&": _g(".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "!": _g("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": _g(".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "+": _g(".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
}

CHAR_W = 6  # 5 pixels + 1 spacing, times scale


def text_width(text, scale):
    return len(text) * CHAR_W * scale - scale


def draw_text(x, y, text, scale, c):
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] in ("1", "#"):
                    fill_rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += CHAR_W * scale
    return cx


def draw_text_centered(cx, y, text, scale, c):
    draw_text(cx - text_width(text, scale) // 2, y, text, scale, c)


def wrap_text(text, max_w, scale):
    """Greedy word wrap; returns list of lines fitting max_w pixels."""
    cw = CHAR_W * scale
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if len(trial) * cw - scale <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_para(x, y, text, max_w, scale, c, line_h=None):
    if line_h is None:
        line_h = 7 * scale + 4
    for i, ln in enumerate(wrap_text(text, max_w, scale)):
        draw_text(x, y + i * line_h, ln, scale, c)
    return y + len(wrap_text(text, max_w, scale)) * line_h


# ---------------------------------------------------------------- pictures

def draw_chart(x, y, w, h):
    fill_rect(x, y, w, h, (232, 238, 244))
    rect_outline(x, y, w, h, NAVY, 2)
    # grid
    for gy in range(1, 4):
        hline(x + 8, y + gy * h // 4, w - 16, (200, 208, 218), 1)
    # falling bars
    bars = [0.82, 0.74, 0.78, 0.62, 0.55, 0.60, 0.44, 0.38, 0.30, 0.22]
    bw = (w - 24) // len(bars)
    for i, f in enumerate(bars):
        bx = x + 12 + i * bw
        bh = int(f * (h - 60))
        fill_rect(bx + 2, y + h - 30 - bh, bw - 4, bh, RED_LT if i % 2 else RED)
    # trend line over the bars
    pts = []
    for i, f in enumerate(bars):
        pts.append((x + 12 + i * bw + bw // 2, y + h - 30 - int(f * (h - 60)) - 6))
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], NAVY, 3)
    for p in pts:
        circle(p[0], p[1], 4, NAVY)
    draw_text(x + 12, y + h - 24, "NASDAQ -5.28%", 2, RED)


def draw_skyline(x, y, w, h):
    fill_rect(x, y, w, h, SKY)
    rect_outline(x, y, w, h, NAVY, 2)
    circle(x + w - 52, y + 30, 18, GOLD)
    # buildings, back row then front row
    heights = [0.55, 0.75, 0.45, 0.9, 0.6, 0.8, 0.5]
    bw = w // len(heights)
    for i, f in enumerate(heights):
        bx = x + i * bw + 2
        bh = int(f * h * 0.75)
        fill_rect(bx, y + h - bh, bw - 4, bh, NAVY_LT)
        for wy in range(y + h - bh + 8, y + h - 6, 14):
            for wx in range(bx + 5, bx + bw - 9, 12):
                fill_rect(wx, wy, 4, 5, GOLD)
    fill_rect(x, y + h - 10, w, 10, GREEN)
    draw_text(x + 10, y + 8, "$3.79BN", 3, NAVY)


def draw_prison(x, y, w, h):
    fill_rect(x, y, w, h, (226, 226, 220))
    rect_outline(x, y, w, h, NAVY, 2)
    # main block
    fill_rect(x + w // 6, y + 18, w * 2 // 3, h - 48, GREY)
    rect_outline(x + w // 6, y + 18, w * 2 // 3, h - 48, INK, 2)
    # roof
    triangle(x + w // 6 - 8, y + 18, x + w // 2, y + 2, x + w * 5 // 6 + 8, y + 18, INK)
    # barred windows
    for i in range(4):
        wx = x + w // 6 + 14 + i * (w * 2 // 3 - 28) // 4
        wy = y + 30
        fill_rect(wx, wy, 18, 26, (40, 40, 40))
        for b in range(3):
            vline(wx + 4 + b * 5, wy, 26, (200, 200, 190), 2)
    # door with bars
    dx = x + w // 2 - 14
    fill_rect(dx, y + h - 62, 28, 32, (40, 40, 40))
    for b in range(4):
        vline(dx + 3 + b * 7, y + h - 62, 32, (200, 200, 190), 2)
    # water at the bottom
    fill_rect(x, y + h - 16, w, 16, BLUE)
    hline(x, y + h - 12, w, WHITE, 1)
    draw_text(x + 10, y + h - 44, "2032", 3, INK)


def draw_gavel(x, y, w, h):
    fill_rect(x, y, w, h, (238, 232, 220))
    rect_outline(x, y, w, h, NAVY, 2)
    # sound block
    fill_rect(x + w // 2 - 52, y + h - 34, 104, 16, (120, 72, 32))
    # handle
    line(x + 34, y + h - 44, x + w - 40, y + 34, (120, 72, 32), 7)
    # head
    fill_rect(x + w - 92, y + 14, 72, 30, (90, 54, 24))
    rect_outline(x + w - 92, y + 14, 72, 30, INK, 2)
    fill_rect(x + w - 100, y + 10, 8, 38, (90, 54, 24))
    fill_rect(x + w - 16, y + 10, 8, 38, (90, 54, 24))
    draw_text(x + 10, y + 10, "$7.25BN", 3, NAVY)


def draw_court(x, y, w, h):
    fill_rect(x, y, w, h, (232, 230, 222))
    rect_outline(x, y, w, h, NAVY, 2)
    # pediment
    triangle(x + 14, y + 34, x + w // 2, y + 8, x + w - 14, y + 34, NAVY)
    circle(x + w // 2, y + 24, 5, GOLD)
    # columns
    for i in range(4):
        cx0 = x + 24 + i * (w - 48) // 4
        fill_rect(cx0, y + 38, 16, h - 66, WHITE)
        rect_outline(cx0, y + 38, 16, h - 66, INK, 1)
    # steps
    fill_rect(x + 10, y + h - 28, w - 20, 8, GREY)
    fill_rect(x + 4, y + h - 18, w - 8, 8, GREY_LT)


def draw_flags(x, y, w, h):
    fill_rect(x, y, w, h, (238, 238, 234))
    rect_outline(x, y, w, h, NAVY, 2)
    # US flag, left half
    ux, uy, uw, uh = x + 10, y + 14, w // 2 - 16, h - 28
    for s in range(7):
        fill_rect(ux, uy + s * (uh // 7), uw, uh // 14 + 1, RED if s % 2 == 0 else WHITE)
    fill_rect(ux, uy, uw * 2 // 5, uh * 4 // 7, BLUE)
    for r in range(3):
        for c in range(4):
            circle(ux + 8 + c * 12, uy + 8 + r * 10, 2, WHITE)
    # Mexico flag, right half
    mx = x + w // 2 + 6
    mw = w // 2 - 16
    fill_rect(mx, uy, mw // 3, uh, GREEN)
    fill_rect(mx + mw // 3, uy, mw // 3, uh, WHITE)
    fill_rect(mx + 2 * mw // 3, uy, mw // 3, uh, RED)
    circle(mx + mw // 2, uy + uh // 2, 9, (160, 110, 40))
    # poles
    vline(x + 10, y + 6, h - 12, INK, 2)
    vline(x + w - 12, y + 6, h - 12, INK, 2)


# ---------------------------------------------------------------- layout

def story_cell(x, y, w, pic_h, kicker, headline, stand, pic_fn,
               head_scale=3, head_lines=3):
    draw_text(x, y, kicker, 2, RED)
    draw_para(x, y + 20, headline, w, head_scale, INK, line_h=7 * head_scale + 5)
    n_head = len(wrap_text(headline, w, head_scale))
    sy = y + 20 + n_head * (7 * head_scale + 5) + 6
    draw_para(x, sy, stand, w, 2, INK, line_h=17)
    return sy


def main():
    fill_rect(0, 0, W, H, PAPER)
    rect_outline(20, 20, W - 40, H - 40, INK, 3)

    # ---- masthead
    fill_rect(32, 32, 960, 118, NAVY)
    draw_text_centered(512, 46, "THE WORLD TODAY", 6, WHITE)
    hline(52, 96, 920, (150, 160, 190), 1)
    draw_text_centered(512, 106, "SATURDAY 21 NOVEMBER 2026", 3, WHITE)

    # ---- lead story
    draw_text(32, 176, "TOP STORY", 2, RED)
    draw_text(32, 200, "AI SELL-OFF DEEPENS", 5, INK)
    draw_para(32, 248, "ANTHROPIC SHARES FALL MORE THAN 9% THE DAY "
             "AFTER ITS RECORD IPO. THE NASDAQ FELL 5.28% ON FRIDAY "
             "AND NVIDIA DROPPED ABOUT 14%.", 600, 2, INK, line_h=19)
    draw_text(32, 404, "SOURCE: NDTV", 2, GREY)
    draw_chart(664, 176, 328, 240)

    hline(32, 448, 960, INK, 2)

    # ---- row 2: stories 2, 3, 4
    cols = [(32, 304), (360, 304), (688, 304)]
    pics = [draw_skyline, draw_prison, draw_gavel]
    heads = ["GTA VI BANKS $3.79 BILLION ON DAY ONE",
             "MAMDANI TO CLOSE RIKERS ISLAND BY 2032",
             "JUDGE APPROVES BAYER $7.25BN ROUNDUP DEAL"]
    stands = ["RECORD FIRST-DAY RETAIL SALES FOR THE GAME.",
              "MAYOR-ELECT ANNOUNCES PLAN TO SHUT THE JAIL.",
              "US JUDGE SIGNS OFF ON THE CANCER SETTLEMENT."]
    kicks = ["GAMING", "NEW YORK", "COURTS"]
    for (cx, cw), pic, hd, st, kk in zip(cols, pics, heads, stands, kicks):
        pic(cx, 464, cw, 112)
        story_cell(cx, 588, cw, 112, kk, hd, st, pic)
    vline(344, 464, 248, GREY_LT, 2)
    vline(672, 464, 248, GREY_LT, 2)

    hline(32, 730, 960, INK, 2)

    # ---- row 3: stories 5, 6
    cols2 = [(32, 464), (528, 464)]
    pics2 = [draw_court, draw_flags]
    heads2 = ["19 YEARS FOR US ASSASSINATION PLOT",
              "TRUMP CLOSE TO MEXICO TRADE DEAL"]
    stands2 = ["INDIAN MAN JAILED OVER PLOT TO KILL A SIKH "
               "SEPARATIST LEADER.",
               "PRESIDENT SAYS MORE WORK TO DO WITH CANADA."]
    kicks2 = ["JUSTICE", "TRADE"]
    for (cx, cw), pic, hd, st, kk in zip(cols2, pics2, heads2, stands2, kicks2):
        pic(cx, 742, cw, 108)
        story_cell(cx, 858, cw, 108, kk, hd, st, pic)
    vline(512, 742, 228, GREY_LT, 2)

    # ---- footer
    draw_text_centered(512, 980, "SOURCES: NDTV - BBC - DEUTSCHE WELLE", 2, GREY)

    write_png()


# ---------------------------------------------------------------- PNG writer

def chunk(tag, data):
    out = struct.pack(">I", len(data)) + tag + data
    out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
    return out


def write_png():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    raw = bytearray()
    for yy in range(H):
        raw.append(0)  # filter: none
        raw += PIX[yy * W * 3:(yy + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(png)
    print("wrote", path, len(png), "bytes")


if __name__ == "__main__":
    main()
