"""Material textures for the nine small 3D fungi (and the cultivation log fruit, the potted fungi and the lantern).

Every placed mushroom model samples these with UVs equal to each face's size, centred: cap tops are painted with a
radial light so stacked cap layers line up into one smooth dome; cap sides are painted top (light) to bottom (rim);
stems are vertical fibres."""
from __future__ import annotations

import math

from . import palette as P
from .art_kit import CLEAR, Sprite, col, fbm, hash01, mix, pick, ramp, seed_of, shade, vnoise, vnoise_a


def _radial(rmp, seed, light=0.0, spread=0.36, noise=0.22, center=(7.5, 7.5)) -> Sprite:
    s = Sprite()
    cx, cy = center
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - cx, y - cy) / 8.0
            lit = -(x - cx) * 0.025 - (y - cy) * 0.03
            t = 0.78 - d * spread + lit + light + (fbm(x, y, seed) - 0.5) * noise
            s.set(x, y, pick(rmp, t))
    return s


def _side(rmp, seed, top=0.82, bottom=0.25, noise=0.2, streak=True) -> Sprite:
    s = Sprite()
    for y in range(16):
        for x in range(16):
            n = vnoise_a(x, y, seed, 2, 8) if streak else fbm(x, y, seed)
            t = top + (bottom - top) * (y / 15) + (n - 0.5) * noise
            s.set(x, y, pick(rmp, t))
    return s


def _stem(rmp, seed, base=0.62, noise=0.45) -> Sprite:
    s = Sprite()
    for y in range(16):
        for x in range(16):
            n = vnoise_a(x, y, seed, 2, 8)
            light = 0.08 if x < 8 else -0.06  # lit left side on every face
            t = base + (n - 0.5) * noise + light
            s.set(x, y, pick(rmp, t))
    return s


def _gills(dark, light, seed, glow=None) -> Sprite:
    s = Sprite()
    for y in range(16):
        for x in range(16):
            dx, dy = x - 7.5, y - 7.5
            ang = math.atan2(dy, dx)
            gill = math.sin(ang * 14) > 0.1
            d = math.hypot(dx, dy)
            c = light if gill else dark
            if d < 1.6:
                c = dark
            if glow is not None and gill and hash01(x, y, seed) < 0.25:
                c = glow
            s.set(x, y, c)
    return s


def _dots(s: Sprite, spots, c_lit, c_dark=None, shadow=None):
    for (x, y, r) in spots:
        for yy in range(16):
            for xx in range(16):
                d = math.hypot(xx - x, yy - y)
                if d <= r:
                    lit = (xx - x) + (yy - y) < 0
                    s.set(xx, yy, c_lit if lit or c_dark is None else c_dark)
                elif shadow is not None and d <= r + 1 and xx >= x and yy >= y:
                    s.set(xx, yy, shadow)


# ------------------------------------------------------------------------------------------------- per fungus

def glowcap() -> dict[str, Sprite]:
    cap = ramp(P.GLOWCAP_CAP)
    glow = ramp(P.GLOW)
    seed = seed_of("f_glowcap")
    top = _radial(cap[1:], seed, light=0.02)
    for (x, y) in ((5, 5), (10, 6), (7, 9), (4, 10), (11, 10), (8, 3), (13, 8), (2, 7)):
        top.set(x, y, glow[3])
        top.set(x + 1, y + 1, cap[1])
    for (x, y) in ((6, 6), (10, 6), (4, 10)):
        top.set(x, y, glow[4])
    side = _side(cap[1:], seed + 1, top=0.7, bottom=0.35)
    for x in range(16):
        side.set(x, 15, glow[4] if x % 2 else glow[3])  # the luminous rim
        side.set(x, 14, col(P.GLOWCAP_RIM[1]) if x % 3 else cap[3])
        if hash01(x, 1, seed) < 0.25:
            side.set(x, 4 + int(hash01(x, 2, seed) * 8), glow[3])
    under = _gills(cap[2], glow[3], seed, glow[4])
    stem = _stem(ramp(P.GLOWCAP_STEM), seed + 3, base=0.7)
    for y in range(16):
        stem.set(round(7 + math.sin(y * 0.6) * 0.8), y, glow[1])
    return {"cap": top, "cap_side": side, "gills": under, "stem": stem}


def bouncecap() -> dict[str, Sprite]:
    cap = ramp(P.BOUNCECAP_CAP)
    spot = ramp(P.BOUNCECAP_SPOT)
    seed = seed_of("f_bouncecap")
    top = _radial(cap[1:], seed, light=0.04, spread=0.42)
    _dots(top, [(5, 5, 1.6), (10.5, 6, 1.3), (7.5, 10.5, 1.5), (3, 10, 1.0), (12, 11, 1.0), (8, 2.5, 0.9)],
          spot[2], spot[1], cap[2])
    top.set(5, 4, col("#ffffff"))
    side = _side(cap[1:], seed + 1, top=0.75, bottom=0.3)
    _dots(side, [(2, 3, 1.3), (9, 5, 1.6), (14, 2, 1.0), (5, 9, 1.0), (12, 10, 1.2)], spot[2], spot[1], None)
    for x in range(16):
        side.set(x, 15, cap[1])
    under = Sprite()
    st = ramp(P.BOUNCECAP_SPOT + ["#fffaf3"])
    for y in range(16):
        for x in range(16):
            pore = (x + (y // 2) % 2) % 2 == 0 and y % 2 == 0
            under.set(x, y, col(P.BOUNCECAP_STEM[2]) if pore else pick(st, 0.5 + (fbm(x, y, seed) - 0.5) * 0.4))
    stem = _stem(ramp(P.BOUNCECAP_STEM), seed + 3, base=0.68)
    return {"cap": top, "cap_side": side, "gills": under, "stem": stem}


def inkcap() -> dict[str, Sprite]:
    cap = ramp(P.INKCAP_CAP)
    ink = ramp(P.INK)
    seed = seed_of("f_inkcap")
    top = _radial(cap[1:], seed, light=0.06, spread=0.3)
    for (x, y) in ((6, 6), (9, 7), (7, 9)):
        top.set(x, y, cap[1])
    side = Sprite()
    for y in range(16):
        for x in range(16):
            # long vertical fibrils: the shaggy mane hangs in strands
            n = vnoise_a(x, y, seed, 1, 8)
            t = 0.72 - (y / 15) * 0.22 + (n - 0.5) * 0.6
            side.set(x, y, pick(cap[1:], t))
    # shaggy scales: lit curls with a shadow beneath
    for row in range(4):
        for k in range(5):
            x0 = (k * 4 + (2 if row % 2 else 0) + int(hash01(row, k, seed) * 2)) % 16
            y0 = row * 3 + 1
            side.set(x0, y0, cap[4])
            side.set((x0 + 1) % 16, y0, cap[4])
            side.set((x0 + 1) % 16, y0 + 1, cap[1])
            side.set((x0 + 2) % 16, y0 + 1, cap[0])
    # the inky fringe dissolving at the rim
    for x in range(16):
        depth = 2 + int(hash01(x, 9, seed) * 3)
        for k in range(depth):
            side.set(x, 15 - k, ink[1] if k < depth - 1 else ink[3])
    under = _gills(ink[0], ink[3], seed)
    stem = _stem(ramp(P.INKCAP_STEM), seed + 3, base=0.75, noise=0.35)
    return {"cap": top, "cap_side": side, "gills": under, "stem": stem}


def morel() -> dict[str, Sprite]:
    m = ramp(P.MOREL)
    seed = seed_of("f_morel")
    cap = Sprite()
    # Honeycomb: light ridges around dark pits, cells in a staggered grid.
    for y in range(16):
        for x in range(16):
            row = y // 3
            ox = 2 if row % 2 else 0
            cx = ((x + ox) // 4) * 4 - ox + 1.5
            cy = row * 3 + 1.0
            d = max(abs(x - cx) / 1.5, abs(y - cy) / 1.0)
            if d < 1.0:
                t = 0.18 + (hash01(x, y, seed) - 0.5) * 0.15
            else:
                t = 0.7 + (hash01(x, y, seed + 1) - 0.5) * 0.25 + (0.12 if (x + y) % 5 == 0 else 0)
            cap.set(x, y, pick(m, t))
    stem = _stem(ramp(["#c9b99a", "#ddd0b5", "#ece3cf", "#f7f1e3", "#fffaf0"]), seed + 3, base=0.62)
    return {"cap": cap, "cap_side": cap, "stem": stem}


def chanterelle() -> dict[str, Sprite]:
    g = ramp(P.CHANTERELLE)
    seed = seed_of("f_chanterelle")
    top = Sprite()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            # a funnel: the centre dips into shadow, the wavy rim catches light
            t = 0.35 + min(d, 6) * 0.08 - (x - 7.5) * 0.015 - (y - 7.5) * 0.02 + (fbm(x, y, seed) - 0.5) * 0.2
            top.set(x, y, pick(g, t))
    side = Sprite()
    for y in range(16):
        for x in range(16):
            ridge = (x + (1 if y > 8 and x % 4 == 0 else 0)) % 2 == 0  # forking false gills
            t = 0.62 - (y / 15) * 0.2 + (0.12 if ridge else -0.05) + (hash01(x, y, seed) - 0.5) * 0.08
            side.set(x, y, pick(g, t))
    for x in range(16):
        side.set(x, 0, g[5] if x % 3 else g[4])
    stem = _stem(ramp(["#c9851d", "#e3a63a", "#f2c45e", "#fbdc8f", "#fff0c2"]), seed + 3, base=0.6)
    return {"cap": top, "cap_side": side, "stem": stem}


def deathcap() -> dict[str, Sprite]:
    c = ramp(P.DEATHCAP_CAP)
    w = ramp(P.DEATHCAP_WHITE)
    seed = seed_of("f_deathcap")
    top = _radial(c[1:], seed, light=0.0, spread=0.35, noise=0.12)
    # fine radial fibrils and a satin sheen
    for y in range(16):
        for x in range(16):
            ang = math.atan2(y - 7.5, x - 7.5)
            if math.sin(ang * 22) > 0.85 and math.hypot(x - 7.5, y - 7.5) > 2:
                top.set(x, y, shade(top.get(x, y), -0.06))
    for (x, y) in ((5, 5), (6, 4), (5, 6)):
        top.set(x, y, c[5])
    side = _side(c[1:], seed + 1, top=0.72, bottom=0.35)
    for x in range(16):
        side.set(x, 15, c[1])
    gills = _gills(w[1], w[3], seed)
    stem = _stem(w, seed + 3, base=0.7, noise=0.3)
    for y in range(0, 16, 3):  # faint snakeskin bands
        for x in range(16):
            if (x + y) % 4 < 2:
                stem.set(x, y, shade(stem.get(x, y), -0.05))
    return {"cap": top, "cap_side": side, "gills": gills, "stem": stem}


def frostcap() -> dict[str, Sprite]:
    f = ramp(P.FROSTCAP)
    seed = seed_of("f_frostcap")
    top = _radial(f[1:], seed, light=0.05, spread=0.5)
    # a frosted white rim and sparkles
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 5.6 and hash01(x, y, seed) < 0.7:
                top.set(x, y, f[5] if hash01(x, y, seed + 1) < 0.5 else f[4])
    for (x, y) in ((6, 6), (9, 5), (8, 9)):
        top.set(x, y, col("#ffffff"))
    side = _side(f[1:], seed + 1, top=0.8, bottom=0.3)
    for x in range(16):
        side.set(x, 0, f[5])
        if hash01(x, 3, seed) < 0.35:
            side.set(x, 14, f[5])
            side.set(x, 15, f[4])
    gills = _gills(f[2], f[4], seed)
    stem = _stem(ramp(["#9fc6dc", "#bcdcec", "#d6eef8", "#ecf8ff", "#ffffff"]), seed + 3, base=0.6)
    crystal = Sprite()
    for y in range(16):
        for x in range(16):
            crystal.set(x, y, f[5] if (x + y) % 3 else f[4])
    return {"cap": top, "cap_side": side, "gills": gills, "stem": stem, "crystal": crystal}


def emberstool() -> dict[str, Sprite]:
    e = ramp(P.EMBER)
    seed = seed_of("f_emberstool")
    stalk = Sprite()
    for y in range(16):
        for x in range(16):
            # dark char at the foot, burning red-orange toward the top
            t = 0.55 - (y / 15) * 0.45 + (vnoise_a(x, y, seed, 2, 8) - 0.5) * 0.25 + (0.05 if x < 8 else -0.05)
            stalk.set(x, y, pick(e[:5], t))
    tip = Sprite()
    for y in range(16):
        for x in range(16):
            # a glowing ember: hot yellow core, orange skin, a red crust at the bottom
            t = 0.78 - (y / 15) * 0.55 + (hash01(x, y, seed) - 0.5) * 0.25
            tip.set(x, y, pick(e[2:], t))
    for (x, y) in ((4, 1), (10, 2), (7, 4), (12, 5), (2, 6)):
        tip.set(x, y, col("#fff3c4"))
    return {"stalk": stalk, "tip": tip}


def puffball() -> dict[str, Sprite]:
    p = ramp(P.PUFFBALL)
    seed = seed_of("f_puffball")
    top = _radial(p[1:], seed, light=0.08, spread=0.3, noise=0.12)
    side = _side(p[1:], seed + 1, top=0.85, bottom=0.45, streak=False, noise=0.12)
    for s in (top, side):
        for (x, y) in ((3, 4), (9, 2), (12, 9), (6, 11), (2, 13), (14, 4)):
            s.set(x, y, p[2])
            s.set(x - 1, y - 1, p[5])
    bottom = Sprite()
    for y in range(16):
        for x in range(16):
            bottom.set(x, y, mix(p[1], col(P.DIRT[2]), 0.35 + hash01(x, y, seed) * 0.2))
    return {"cap": top, "cap_side": side, "bottom": bottom}


MATERIALS = {
    "glowcap": glowcap, "bouncecap": bouncecap, "inkcap": inkcap, "morel": morel, "chanterelle": chanterelle,
    "deathcap": deathcap, "frostcap": frostcap, "emberstool": emberstool, "puffball": puffball,
}


def all_materials() -> dict[str, dict[str, Sprite]]:
    return {name: fn() for name, fn in MATERIALS.items()}
