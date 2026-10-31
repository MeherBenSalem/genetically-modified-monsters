"""Wood-set textures for the three huge fungi: caps (outside and gills), stems, stripped stems, planks, doors and
trapdoors. Each species keeps one structure (hyphal grain, ringed stem tops) and its own colour story."""
from __future__ import annotations

import math

from . import palette as P
from .art_kit import (CLEAR, Sprite, col, fbm, hash01, lerp, mix, pick, ramp, seed_of, shade, vnoise, vnoise_a)

SPECIES = {
    "glowcap": dict(cap=ramp(P.GLOWCAP_CAP), rim=ramp(P.GLOWCAP_RIM), stem=ramp(P.GLOWCAP_STEM),
                    planks=ramp(P.GLOWCAP_PLANKS), accent=ramp(P.GLOW)),
    "bouncecap": dict(cap=ramp(P.BOUNCECAP_CAP), rim=ramp(P.BOUNCECAP_SPOT), stem=ramp(P.BOUNCECAP_STEM),
                      planks=ramp(P.BOUNCECAP_PLANKS), accent=ramp(P.BOUNCECAP_SPOT)),
    "inkcap": dict(cap=ramp(P.INKCAP_CAP), rim=ramp(P.INK), stem=ramp(P.INKCAP_STEM),
                   planks=ramp(P.INKCAP_PLANKS), accent=ramp(P.INK)),
}


# ---------------------------------------------------------------------------------------------------- planks

def planks(wood: str) -> Sprite:
    """Four boards, each one coherent tone with streaky hyphal grain, a dark seam and one end joint."""
    sp = SPECIES[wood]
    rp = sp["planks"]
    seed = seed_of("planks", wood)
    s = Sprite()
    joints = {"glowcap": [10, 3, 13, 6], "bouncecap": [5, 12, 2, 9], "inkcap": [12, 6, 1, 9]}[wood]
    base = {"glowcap": 3.0, "bouncecap": 3.0, "inkcap": 3.0}[wood]
    lift = [0.05, -0.03, 0.02, -0.05]
    for b in range(4):
        y0 = b * 4
        jx = joints[b]
        for dy in range(3):
            y = y0 + dy
            for x in range(16):
                # one even tone per board; only a faint long wave along it (no brick-like blotches)
                n = vnoise_a(x, y, seed + b * 13, 16, 4) - 0.5
                t = (base + 0.5) / 5 + lift[b] + n * 0.08
                if dy == 0:
                    t += 0.05
                s.set(x, y, pick(rp, t))
            # grain: one long soft streak per row (darker, or lighter on the lit top row)
            x = int(hash01(b, dy, seed) * 16)
            length = 5 + int(hash01(b * 3, dy, seed + 5) * 5)
            tone = rp[3] if dy == 0 else rp[1]
            for i in range(length):
                xx = (x + i) % 16
                if xx not in (jx, (jx + 1) % 16):
                    s.set(xx, y, mix(s.get(xx, y), tone, 0.45))
        for x in range(16):
            s.set(x, y0 + 3, rp[1] if hash01(x, b, seed + 4) < 0.85 else rp[0])
        for dy in range(3):
            s.set(jx, y0 + dy, rp[1])
            if dy == 0:
                s.set((jx + 1) % 16, y0, shade(s.get((jx + 1) % 16, y0), 0.05))
        # species accents in the grain
        for x in range(16):
            for dy in range(3):
                y = y0 + dy
                if x in (jx, (jx + 1) % 16):
                    continue
                h = hash01(x, y, seed + 77)
                if wood == "glowcap" and h < 0.018:
                    s.set(x, y, mix(sp["accent"][1], rp[2], 0.3))
                elif wood == "bouncecap" and h < 0.015:
                    s.set(x, y, mix(sp["accent"][1], rp[3], 0.5))
                elif wood == "inkcap" and h < 0.02:
                    s.set(x, y, col("#6c5b84"))
    return s


# ---------------------------------------------------------------------------------------------------- stems

def _vein(y: int, x0: float, amp: float, phase: float) -> int:
    return round(x0 + math.sin(y / 16 * 6.283 + phase) * amp) % 16


def stem_side(wood: str, stripped: bool = False) -> Sprite:
    sp = SPECIES[wood]
    rp = sp["stem"]
    seed = seed_of("stem", wood, stripped)
    s = Sprite()
    for y in range(16):
        for x in range(16):
            n = vnoise_a(x, y, seed, 2, 8)
            n2 = vnoise_a(x, y, seed + 9, 1, 4)
            if stripped:
                t = 0.62 + (n - 0.5) * 0.35 + (n2 - 0.5) * 0.18
            else:
                t = 0.42 + (n - 0.5) * 0.7 + (n2 - 0.5) * 0.3
            s.set(x, y, pick(rp, t, x, y, dither=0.35))
    if not stripped:
        # Fibrous ridges: dark streaks running up the stem, each a few pixels apart.
        for i, x0 in enumerate([1, 5, 9, 12]):
            phase = hash01(i, 3, seed) * 6.28
            for y in range(16):
                x = _vein(y, x0 + 0.5, 0.7, phase)
                if hash01(x, y, seed + i) < 0.85:
                    s.set(x, y, rp[0] if hash01(y, i, seed) < 0.5 else rp[1])
                    s.set((x + 1) % 16, y, shade(s.get((x + 1) % 16, y), 0.06))
    else:
        for i, x0 in enumerate([3, 8, 13]):
            for y in range(16):
                x = _vein(y, x0, 0.5, i * 2.1)
                if hash01(x, y, seed + i) < 0.6:
                    s.set(x, y, rp[2])
    if wood == "glowcap":
        # Bioluminescent veins: brighter on the stripped flesh.
        acc = sp["accent"]
        for i, (x0, ph) in enumerate([(3.5, 0.0), (11.5, 2.4)]):
            for y in range(16):
                x = _vein(y, x0, 1.2, ph)
                c = acc[1] if stripped else mix(acc[0], rp[1], 0.25)
                if hash01(y, i, seed + 50) < (0.25 if stripped else 0.15):
                    c = acc[2] if stripped else acc[1]
                s.set(x, y, c)
    elif wood == "bouncecap":
        blush = sp["cap"][4]
        for y in range(16):
            for x in range(16):
                b = vnoise(x, y, seed + 31, 8)
                if b > 0.62:
                    s.set(x, y, mix(s.get(x, y), blush, 0.18 if not stripped else 0.12))
    elif wood == "inkcap":
        ink = sp["accent"]
        if stripped:
            for y in range(16):
                for x in range(16):
                    if vnoise(x, y, seed + 5, 8) > 0.66:
                        s.set(x, y, mix(s.get(x, y), col("#6f6283"), 0.25))
        else:
            # Ink stains bleeding down the stem.
            for i, x in enumerate([2, 7, 13]):
                start = int(hash01(i, 1, seed) * 16)
                length = 4 + int(hash01(i, 2, seed) * 6)
                for k in range(length):
                    y = (start + k) % 16
                    s.set(x, y, ink[2] if k < length - 2 else ink[3])
                    if k < length - 4:
                        s.set((x + 1) % 16, y, mix(ink[3], rp[1], 0.4))
    return s


def stem_top(wood: str, stripped: bool = False) -> Sprite:
    sp = SPECIES[wood]
    rp = sp["stem"]
    side = stem_side(wood, stripped)
    seed = seed_of("top", wood, stripped)
    flesh = {"glowcap": ramp(P.GLOWCAP_STEM[1:] + ["#e8f0f2"]), "bouncecap": ramp(P.BOUNCECAP_STEM[2:] + ["#fff8f0"]),
             "inkcap": ramp(P.INKCAP_STEM[1:])}[wood]
    s = Sprite()
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            d = max(abs(dx), abs(dy)) * 0.55 + math.hypot(dx, dy) * 0.45
            if d > 6.6 and not stripped:
                s.set(x, y, side.get(x, y))
                continue
            if d > 6.1 and not stripped:
                s.set(x, y, rp[0])
                continue
            ring = (math.sin(d * 1.9 + vnoise(x, y, seed, 4) * 1.4) + 1) / 2
            t = 0.35 + ring * 0.35 + (hash01(x, y, seed) - 0.5) * 0.15 + (0.08 if d < 1.5 else 0)
            c = pick(flesh, t, x, y, dither=0.3)
            if stripped and d > 6.6:
                c = pick(flesh, 0.25, x, y)
            s.set(x, y, c)
    if wood == "glowcap":
        acc = sp["accent"]
        for y in range(16):
            for x in range(16):
                dx, dy = x - 7.5, y - 7.5
                d = max(abs(dx), abs(dy)) * 0.55 + math.hypot(dx, dy) * 0.45
                if 2.4 < d < 3.3:
                    s.set(x, y, acc[2] if hash01(x, y, seed) < 0.5 else acc[1])
                elif d < 1.0:
                    s.set(x, y, acc[3])
    elif wood == "inkcap":
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5)
                if d < 1.6:
                    s.set(x, y, col(P.INK[3]))
    elif wood == "bouncecap":
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5)
                if 3.0 < d < 3.8 and hash01(x, y, seed) < 0.7:
                    s.set(x, y, sp["cap"][4])
    return s


# ---------------------------------------------------------------------------------------------------- caps

def _wrap_dist(x, y, cx, cy):
    dx = min(abs(x - cx), 16 - abs(x - cx))
    dy = min(abs(y - cy), 16 - abs(y - cy))
    return math.hypot(dx, dy), dx, dy


def cap_outside(wood: str) -> Sprite:
    sp = SPECIES[wood]
    seed = seed_of("cap", wood)
    s = Sprite()
    if wood == "glowcap":
        rp = sp["cap"]
        glow = sp["accent"]
        for y in range(16):
            for x in range(16):
                n = fbm(x, y, seed)
                t = 0.45 + (n - 0.5) * 0.9
                s.set(x, y, pick(rp[1:5], t, x, y, dither=0.35))
        # Luminous scale-dots, each with a darker halo below-right.
        dots = [(2, 3), (9, 1), (13, 6), (5, 9), (11, 12), (1, 13), (7, 5), (15, 10)]
        for i, (cx, cy) in enumerate(dots):
            big = i % 3 == 0
            s.set((cx + 1) % 16, (cy + 1) % 16, rp[1])
            s.set(cx, cy, glow[4] if big else glow[3])
            if big:
                s.set((cx + 1) % 16, cy, glow[3])
                s.set(cx, (cy + 1) % 16, glow[3])
                s.set((cx + 2) % 16, (cy + 1) % 16, rp[1])
                s.set((cx + 1) % 16, (cy + 2) % 16, rp[1])
    elif wood == "bouncecap":
        rp = sp["cap"]
        spot = sp["rim"]
        for y in range(16):
            for x in range(16):
                n = fbm(x, y, seed)
                t = 0.5 + (n - 0.5) * 0.8
                s.set(x, y, pick(rp[2:6], t, x, y, dither=0.35))
        spots = [(3, 3, 2.1), (11, 2, 1.5), (13, 10, 2.3), (6, 11, 1.6), (0, 8, 1.2), (8, 7, 1.0)]
        for cx, cy, r in spots:
            for y in range(16):
                for x in range(16):
                    d, dx, dy = _wrap_dist(x + 0.5, y + 0.5, cx + 0.5, cy + 0.5)
                    if d <= r:
                        lit = (x - cx) + (y - cy) < 0
                        s.set(x, y, spot[2] if lit else spot[1])
                    elif d <= r + 0.9 and (((x - cx) % 16 + 16) % 16 < 8) and (((y - cy) % 16 + 16) % 16 < 8):
                        s.set(x, y, rp[2])  # shadow below-right of the spot
            s.set(cx % 16, cy % 16, spot[2])
    else:  # inkcap: a shaggy mane of upturned scales over pale fibrils
        rp = sp["cap"]
        ink = sp["rim"]
        for y in range(16):
            for x in range(16):
                n = vnoise_a(x, y, seed, 2, 8)
                s.set(x, y, pick(rp[2:5], 0.62 + (n - 0.5) * 0.7))
        for row in range(5):
            for k in range(4):
                jx = int(hash01(row, k, seed) * 3)
                jy = int(hash01(k, row, seed + 1) * 2)
                x0 = (k * 4 + (2 if row % 2 else 0) + jx) % 16
                y0 = (row * 3 + jy) % 16
                # a scale: a lit curl on top, its shadow below, darker toward the tip
                for dx in range(3):
                    s.set((x0 + dx) % 16, y0, rp[4])
                s.set((x0 + 1) % 16, (y0 + 1) % 16, rp[1])
                s.set((x0 + 2) % 16, (y0 + 1) % 16, rp[2])
                s.set((x0 + 2) % 16, (y0 + 2) % 16, rp[0] if hash01(row, k, seed + 3) < 0.6 else ink[4])
        return s
    return s


def cap_inside(wood: str) -> Sprite:
    sp = SPECIES[wood]
    seed = seed_of("inside", wood)
    s = Sprite()
    if wood == "glowcap":
        glow = sp["accent"]
        base = sp["cap"]
        for y in range(16):
            for x in range(16):
                gill = x % 2 == 0
                n = vnoise_a(x, y, seed, 2, 8)
                if gill:
                    c = glow[4] if n > 0.45 else glow[3]
                    if hash01(x, y, seed) < 0.06:
                        c = glow[4]
                else:
                    c = base[3] if n > 0.5 else base[2]
                s.set(x, y, c)
    elif wood == "bouncecap":
        st = ramp(P.BOUNCECAP_SPOT + ["#fffaf3"])
        for y in range(16):
            for x in range(16):
                s.set(x, y, pick(st, 0.45 + (fbm(x, y, seed) - 0.5) * 0.7, x, y, dither=1.0))
        for gy in range(0, 16, 3):
            for gx in range(0, 16, 3):
                x = (gx + (1 if (gy // 3) % 2 else 0)) % 16
                s.set(x, gy, col(P.BOUNCECAP_STEM[1]))
                s.set(x, (gy + 1) % 16, col(P.BOUNCECAP_STEM[2]))
    else:
        ink = sp["rim"]
        for y in range(16):
            for x in range(16):
                gill = x % 2 == 0
                n = vnoise_a(x, y, seed, 2, 8)
                if gill:
                    c = ink[4] if n > 0.55 else ink[3]
                    if hash01(x, y, seed) < 0.05:
                        c = col("#6c5f7d")
                else:
                    c = ink[1] if n > 0.4 else ink[0]
                s.set(x, y, c)
    return s


# ---------------------------------------------------------------------------------------------------- doors

def _board_fill(s: Sprite, rp, seed: int, x0: int, x1: int, y0: int, y1: int, vertical: bool = True) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if vertical:
                n = vnoise_a(x, y, seed, 2, 8)
                seam = (x - x0) % 4 == 3
            else:
                n = vnoise_a(x, y, seed, 8, 2)
                seam = (y - y0) % 4 == 3
            t = 0.52 + (n - 0.5) * 0.4
            s.set(x, y, rp[1] if seam else pick(rp, t))


def door(wood: str) -> tuple[Sprite, Sprite]:
    sp = SPECIES[wood]
    rp = sp["planks"]
    seed = seed_of("door", wood)
    s = Sprite(16, 32)
    _board_fill(s, rp, seed, 0, 15, 0, 31)
    frame_dark, frame = rp[0], shade(rp[1], -0.02)
    # outer frame
    for y in range(32):
        s.set(0, y, frame_dark)
        s.set(15, y, frame_dark)
        s.set(1, y, rp[3])
        s.set(14, y, frame)
    for x in range(16):
        s.set(x, 0, frame_dark)
        s.set(x, 31, frame_dark)
        s.set(x, 1, rp[3])
        s.set(x, 15, frame_dark)
        s.set(x, 16, rp[3])
        s.set(x, 30, frame)
    acc = sp["accent"]
    if wood == "glowcap":
        # An arched window with a cross mullion, rimmed with glowing veins.
        for y in range(3, 13):
            for x in range(4, 12):
                inside = (y >= 6) or ((x - 7.5) ** 2 / 16 + (y - 6.5) ** 2 / 12 <= 1)
                if inside:
                    s.set(x, y, CLEAR)
        for y in range(3, 13):
            s.set(7, y, rp[2]) if y > 4 else None
            s.set(8, y, rp[1]) if y > 4 else None
        for x in range(4, 12):
            s.set(x, 8, rp[2])
        for y in range(2, 14):
            for x in range(3, 13):
                if s.get(x, y)[3] and any(s.get(x + dx, y + dy)[3] == 0 for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))) \
                        and not (x in (7, 8) or y == 8):
                    s.set(x, y, acc[1])
        # lower panels with a vein inlay
        for (px0, px1) in ((3, 6), (9, 12)):
            for y in range(19, 28):
                for x in range(px0, px1 + 1):
                    edge = x in (px0, px1) or y in (19, 27)
                    s.set(x, y, rp[0] if edge and (x == px1 or y == 27) else (rp[3] if edge else rp[2]))
            for y in range(20, 27):
                s.set((px0 + px1) // 2 + (1 if y % 3 == 0 else 0), y, acc[0])
        s.set(12, 17, col("#d6e1e6"))
        s.set(12, 18, col("#8fa0ae"))
    elif wood == "bouncecap":
        # A round porthole like a cap spot, cream rimmed; two spots below.
        cx, cy = 7.5, 7.5
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - cx, y - cy)
                if d <= 3.2:
                    s.set(x, y, CLEAR)
                elif d <= 4.4:
                    s.set(x, y, sp["rim"][2] if (x - cx) + (y - cy) < 0 else sp["rim"][0])
        for (sx, sy, r) in ((5, 22, 1.8), (10, 25, 1.5)):
            for y in range(16, 31):
                for x in range(2, 14):
                    d = math.hypot(x - sx, y - sy)
                    if d <= r:
                        s.set(x, y, sp["rim"][2] if (x - sx) + (y - sy) < 0 else sp["rim"][1])
        s.set(12, 17, sp["rim"][2])
        s.set(12, 18, sp["rim"][0])
    else:
        # Gill slits: thin windows, with ink running from the top frame.
        for x in (4, 6, 9, 11):
            for y in range(4, 13):
                s.set(x, y, CLEAR)
            s.set(x, 3, acc[2])
            s.set(x, 13, rp[4])
        for x in range(2, 14):
            if hash01(x, 0, seed) < 0.55:
                for k in range(1 + int(hash01(x, 1, seed) * 2)):
                    s.set(x, 2 + k, acc[2])
        for y in range(19, 28):
            for x in range(3, 13):
                chev = (abs(x - 7.5) + y) % 4 < 1
                if chev:
                    s.set(x, y, rp[0])
        s.set(12, 17, col("#b9b4c7"))
        s.set(12, 18, col("#6f6a80"))
    top = Sprite()
    bottom = Sprite()
    for y in range(16):
        for x in range(16):
            top.px[y][x] = s.px[y][x]
            bottom.px[y][x] = s.px[y + 16][x]
    return top, bottom


def trapdoor(wood: str) -> Sprite:
    sp = SPECIES[wood]
    rp = sp["planks"]
    seed = seed_of("trapdoor", wood)
    s = Sprite()
    _board_fill(s, rp, seed, 0, 15, 0, 15, vertical=False)
    for i in range(16):
        for (x, y) in ((i, 0), (i, 15), (0, i), (15, i)):
            s.set(x, y, rp[0])
        for (x, y) in ((i, 1), (1, i)):
            if 0 < i < 15:
                s.set(x, y, rp[3])
    acc = sp["accent"]
    if wood == "glowcap":
        for (wx, wy) in ((3, 3), (9, 3), (3, 9), (9, 9)):
            for y in range(wy, wy + 4):
                for x in range(wx, wx + 4):
                    s.set(x, y, CLEAR)
            for k in range(4):
                s.set(wx + k, wy - 1, acc[1])
                s.set(wx - 1, wy + k, acc[1])
        for i in range(2, 14):
            s.set(7, i, rp[2])
            s.set(8, i, rp[1])
            s.set(i, 7, rp[2])
            s.set(i, 8, rp[1])
    elif wood == "bouncecap":
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - 7.5, y - 7.5)
                if d <= 3.6:
                    s.set(x, y, CLEAR)
                elif d <= 4.8:
                    s.set(x, y, sp["rim"][2] if (x - 7.5) + (y - 7.5) < 0 else sp["rim"][0])
        for (sx, sy) in ((3, 3), (12, 3), (3, 12), (12, 12)):
            s.set(sx, sy, sp["rim"][2])
            s.set(sx + 1, sy, sp["rim"][1])
            s.set(sx, sy + 1, sp["rim"][1])
    else:
        for x in (4, 6, 9, 11):
            for y in range(3, 13):
                s.set(x, y, CLEAR)
            s.set(x, 2, acc[2])
            s.set(x, 13, rp[4])
    return s


DOOR_ICON = """
....OOOOOOOO....
....OLLLLLLO....
....OLwwwwLO....
....OLwmmwLO....
....OLwwwwLO....
....OLLLLLLO....
....OLaaaaaO....
....OLLLLLLO....
....OLLLLLHO....
....OLLLLLHO....
....OLbbbbLO....
....OLb..bLO....
....OLbbbbLO....
....OLLLLLLO....
....OOOOOOOO....
................
"""


def door_item(wood: str) -> Sprite:
    """Inventory sprite: the whole door, framed, with its species window and handle."""
    from .art_kit import from_ascii, outlined
    sp = SPECIES[wood]
    rp = sp["planks"]
    acc = sp["accent"]
    if wood == "glowcap":
        window, handle = acc[1], acc[2]
    elif wood == "bouncecap":
        window, handle = sp["rim"][2], sp["rim"][2]
    else:
        window, handle = acc[3], col("#b9b4c7")
    pal = {"O": rp[0], "L": rp[2], "w": window, "m": rp[0], "a": rp[3], "H": handle, "b": rp[1]}
    s = from_ascii(DOOR_ICON, pal)
    seed = seed_of("door_item", wood)
    for y in range(16):
        for x in range(16):
            if s.get(x, y) == rp[2] and hash01(x, y, seed) < 0.3:
                s.set(x, y, rp[3] if x % 2 else rp[1])
    if wood == "glowcap":
        for (x, y) in ((6, 2), (9, 2), (6, 4), (9, 4)):
            s.set(x, y, acc[2])
    elif wood == "bouncecap":
        s.set(7, 3, rp[0]); s.set(8, 3, rp[0])
        s.set(6, 11, sp["rim"][1]); s.set(9, 11, sp["rim"][1])
    else:
        for x in (6, 8):
            for y in (2, 3, 4):
                s.set(x, y, rp[0])
    return s
