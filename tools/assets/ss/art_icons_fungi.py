"""Inventory icons of the nine small fungi: side views, lit from the top-left, with a hue-shifted outline."""
from __future__ import annotations

import math

from . import palette as P
from .art_kit import Sprite, col, hash01, mix, outlined, pick, ramp, seed_of, shade

LIGHT = (-0.55, -0.75, 0.38)


def _norm(v):
    n = math.sqrt(sum(c * c for c in v))
    return tuple(c / n for c in v)


L = _norm(LIGHT)


def dome(s: Sprite, cx: float, base_y: float, rx: float, ry: float, rmp, gloss: bool = True,
         squash_bottom: float = 0.0) -> list[tuple[int, int]]:
    """A cap seen from the side: the top half of an ellipse, lit as a sphere. Returns the filled pixels."""
    pts = []
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - base_y) / ry
            if dy > squash_bottom or dx * dx + dy * dy > 1.0:
                continue
            dz = math.sqrt(max(0.0, 1 - dx * dx - min(dy, 0) ** 2))
            lum = -(dx * L[0] + min(dy, 0) * L[1]) + dz * L[2]
            t = 0.25 + lum * 0.62
            s.set(x, y, pick(rmp, t))
            pts.append((x, y))
    if gloss:
        hx = round(cx - rx * 0.45)
        hy = round(base_y - ry * 0.7)
        if (hx, hy) in pts:
            s.set(hx, hy, shade(rmp[-1], 0.08))
            if (hx + 1, hy) in pts:
                s.set(hx + 1, hy, rmp[-1])
    return pts


def stalk(s: Sprite, x0: int, x1: int, y0: int, y1: int, rmp) -> None:
    for y in range(y0, y1 + 1):
        for x in range(x0, x1 + 1):
            if x == x0:
                c = rmp[-2]
            elif x == x1:
                c = rmp[1]
            else:
                c = rmp[-3] if (y + x) % 5 else rmp[-2]
            s.set(x, y, c)


def rim(s: Sprite, x0: int, x1: int, y: int, c) -> None:
    for x in range(x0, x1 + 1):
        if s.opaque(x, y - 1) or s.opaque(x, y):
            s.set(x, y, c)


def glowcap() -> Sprite:
    s = Sprite()
    cap = ramp(P.GLOWCAP_CAP)
    glow = ramp(P.GLOW)
    stalk(s, 7, 8, 8, 13, ramp(P.GLOWCAP_STEM))
    s.set(6, 13, col(P.GLOWCAP_STEM[2]))
    s.set(9, 13, col(P.GLOWCAP_STEM[1]))
    s.set(7, 10, glow[1])
    dome(s, 7.5, 7.0, 6.6, 4.4, cap[1:])
    # glowing gills under the parasol
    for x in range(2, 14):
        s.set(x, 7, glow[2] if x % 2 else glow[3])
    for x in range(4, 12):
        if x not in (7, 8):
            s.set(x, 8, glow[1])
    for (x, y) in ((4, 5), (10, 4), (7, 4), (12, 6), (3, 6)):
        if s.opaque(x, y):
            s.set(x, y, glow[3])
    return outlined(s)


def bouncecap() -> Sprite:
    s = Sprite()
    cap = ramp(P.BOUNCECAP_CAP)
    spot = ramp(P.BOUNCECAP_SPOT)
    stalk(s, 5, 10, 9, 14, ramp(P.BOUNCECAP_STEM))
    for x in range(5, 11):
        s.set(x, 9, col(P.BOUNCECAP_STEM[0]))
    dome(s, 7.5, 9.2, 6.6, 7.2, cap[1:])
    for (x, y, big) in ((5, 4, True), (9, 3, False), (11, 6, True), (7, 7, False), (3, 7, False)):
        if s.opaque(x, y):
            s.set(x, y, spot[2])
            if big:
                s.set(x + 1, y, spot[1])
                s.set(x, y + 1, spot[1])
                s.set(x + 1, y + 1, spot[0])
    for x in range(2, 14):
        if s.opaque(x, 8):
            s.set(x, 8, cap[1])
    return outlined(s)


INKCAP_ART = """
................
.......WW.......
......WWwv......
.....WWwWvv.....
.....WvwwWvu....
....WWwWwvwu....
....WwvwwWvu....
....WWwwvwvuu...
...WWvwWwwvwu...
...WwwwwvWvuu...
...kKKKKKKKKkk..
...kjkKkkjkKk...
....j..kK...j...
.......Ss.......
.......Ss.......
......SSss......
"""


def inkcap() -> Sprite:
    from .art_kit import from_ascii
    cap = ramp(P.INKCAP_CAP)
    ink = ramp(P.INK)
    st = ramp(P.INKCAP_STEM)
    s = from_ascii(INKCAP_ART, {"W": cap[4], "w": cap[3], "v": cap[2], "u": cap[1], "k": ink[1], "K": ink[2],
                                "j": ink[3], "S": st[3], "s": st[1]})
    return outlined(s)


def morel() -> Sprite:
    s = Sprite()
    m = ramp(P.MOREL)
    stalk(s, 6, 9, 10, 14, ramp(["#b8a689", "#d6c8ab", "#ebe0c8", "#f7f0e0", "#fffaf0"]))
    for y in range(1, 11):
        half = 1.0 + (y - 1) * 0.36
        for x in range(16):
            if abs(x + 0.5 - 7.9) <= half:
                s.set(x, y, m[3])
    seed = seed_of("morel_icon")
    for y in range(1, 11):
        for x in range(16):
            if not s.opaque(x, y):
                continue
            pit = ((x + (y // 2) % 2) % 3 == 1) and y % 2 == 0
            lit = x < 8
            s.set(x, y, m[0] if pit else (m[4] if lit and (x + y) % 3 else m[3] if lit else m[2]))
    s.set(7, 1, m[5])
    return outlined(s)


CHANTERELLE_ART = """
................
................
..ff............
.fffe.......ee..
.feeeddddeeeffd.
..edcccccddeeed.
..dcdcdcdcdcdcc.
...bdcdcdcdcbb..
....bdcdcdcb....
.....bdcdcb.....
......edcb......
......edcb......
......eddb......
.....eeddbb.....
......aaaa......
................
"""


def chanterelle() -> Sprite:
    from .art_kit import from_ascii
    g = ramp(P.CHANTERELLE)
    s = from_ascii(CHANTERELLE_ART, {"a": g[1], "b": g[1], "c": g[2], "d": g[3], "e": g[4], "f": g[5]})
    s.set(6, 14, mix(g[1], col(P.DIRT[2]), 0.5))
    s.set(7, 14, mix(g[1], col(P.DIRT[2]), 0.5))
    s.set(8, 14, mix(g[0], col(P.DIRT[1]), 0.5))
    s.set(9, 14, mix(g[0], col(P.DIRT[1]), 0.5))
    return outlined(s)


def deathcap() -> Sprite:
    s = Sprite()
    c = ramp(P.DEATHCAP_CAP)
    w = ramp(P.DEATHCAP_WHITE)
    stalk(s, 7, 8, 8, 12, w)
    for x in range(5, 11):  # skirt
        s.set(x, 10, w[2] if x < 8 else w[1])
    for y in (12, 13, 14):  # the volva, a white cup at the foot
        for x in range(5, 11):
            if y == 14 and x in (5, 10):
                continue
            s.set(x, y, w[3] if x < 7 else (w[2] if x < 9 else w[1]))
    dome(s, 7.5, 7.0, 6.4, 4.2, c[1:])
    for x in range(2, 14):
        if s.opaque(x, 6):
            s.set(x, 7, w[2] if x % 2 else w[1])
    return outlined(s)


def frostcap() -> Sprite:
    s = Sprite()
    f = ramp(P.FROSTCAP)
    stalk(s, 7, 8, 8, 14, ramp(["#7fb0cc", "#a7cfe3", "#cbe7f5", "#e9f7ff", "#ffffff"]))
    dome(s, 7.5, 7.2, 5.6, 4.6, f[1:])
    for x in range(2, 14):  # frosted rim
        if s.opaque(x, 6):
            s.set(x, 6, f[5] if x % 2 else f[4])
    for x in (3, 6, 9, 12):  # icicles
        s.set(x, 7, f[4])
        if x in (3, 9):
            s.set(x, 8, f[3])
    s.set(6, 3, col("#ffffff"))
    s.set(9, 2, col("#ffffff"))
    return outlined(s)


def emberstool() -> Sprite:
    s = Sprite()
    e = ramp(P.EMBER)
    for (x, top) in ((5, 7), (8, 3), (11, 8)):
        for y in range(top + 2, 15):
            s.set(x, y, e[1] if y > 11 else e[2])
            s.set(x + 1, y, e[0] if y > 11 else e[1])
        # ember head
        s.set(x, top, e[4])
        s.set(x + 1, top, e[3])
        s.set(x, top + 1, e[3])
        s.set(x + 1, top + 1, e[2])
        s.set(x, top - 1, e[5])
    s.set(9, 0, e[4])
    s.set(4, 4, e[3])
    return outlined(s)


def puffball() -> Sprite:
    s = Sprite()
    p = ramp(P.PUFFBALL)
    for y in range(16):
        for x in range(16):
            dx, dy = (x + 0.5 - 7.5) / 5.2, (y + 0.5 - 9.0) / 4.8
            if dx * dx + dy * dy <= 1.0:
                dz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
                lum = -(dx * L[0] + dy * L[1]) + dz * L[2]
                s.set(x, y, pick(p[1:], 0.2 + lum * 0.7))
    for (x, y) in ((5, 7), (8, 6), (10, 9), (6, 10), (9, 12)):
        s.set(x, y, p[2])
    s.set(5, 6, p[5])
    s.set(6, 6, p[5])
    for x in range(6, 10):
        s.set(x, 14, mix(p[1], col(P.DIRT[2]), 0.4))
    return outlined(s)


ICONS = {"glowcap": glowcap, "bouncecap": bouncecap, "inkcap": inkcap, "morel": morel, "chanterelle": chanterelle,
         "deathcap": deathcap, "frostcap": frostcap, "emberstool": emberstool, "puffball": puffball}
