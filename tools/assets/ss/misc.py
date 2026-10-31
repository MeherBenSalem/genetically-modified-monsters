"""The mod logo, mob effect icons, particle sprites and the armor layer textures."""
from __future__ import annotations

import math

from PIL import Image

from . import palette as P
from .art_icons_fungi import L as LIGHT
from .art_kit import Sprite, col, from_ascii, hash01, mix, outlined, pick, ramp, seed_of, shade
from .out import Out
from .paths import MAIN_RESOURCES, MOD_ID

G = ramp(P.GLOW)


def generate(out: Out) -> None:
    logo = logo_image()
    path = MAIN_RESOURCES / "logo.png"
    logo.save(path, optimize=True)
    for name, sprite in effect_icons().items():
        out.texture(f"mob_effect/{name}", sprite.image())
    particles(out)
    for name, image in armor_layers().items():
        out.png(out.asset_path(f"textures/models/armor/{name}.png"), image)


# ---------------------------------------------------------------------------------------------------- logo

def _dome(img: Sprite, cx, base, rx, ry, rmp, spec=True):
    for y in range(img.h):
        for x in range(img.w):
            dx, dy = (x + 0.5 - cx) / rx, (y + 0.5 - base) / ry
            if dy > 0 or dx * dx + dy * dy > 1:
                continue
            dz = math.sqrt(max(0.0, 1 - dx * dx - dy * dy))
            lum = -(dx * LIGHT[0] + dy * LIGHT[1]) + dz * LIGHT[2]
            img.set(x, y, pick(rmp, 0.18 + lum * 0.7))
    if spec:
        hx, hy = round(cx - rx * 0.42), round(base - ry * 0.72)
        img.set(hx, hy, rmp[-1])
        img.set(hx + 1, hy, rmp[-1])
        img.set(hx, hy + 1, shade(rmp[-1], -0.08))


def _stem(img: Sprite, cx, top, bottom, w, rmp):
    for y in range(top, bottom):
        for x in range(round(cx - w / 2), round(cx + w / 2)):
            rel = (x + 0.5 - (cx - w / 2)) / w
            img.set(x, y, pick(rmp, 0.85 - rel * 0.7))


def logo_image() -> Image.Image:
    n = 64
    s = Sprite(n, n)
    seed = seed_of("logo")
    # night backdrop, a soft teal glow behind the hero cap
    for y in range(n):
        for x in range(n):
            t = y / n
            base = mix(col("#0e1a22"), col("#1a2e36"), t)
            g = max(0.0, 1 - math.hypot(x - 32, y - 26) / 30)
            c = mix(base, col("#1f5f5d"), g * 0.55)
            if hash01(x, y, seed) < 0.012 and y < 30:
                c = mix(c, col("#cfeee6"), 0.7)
            s.set(x, y, c)
    # ground: loam threaded with mycelium
    loam = ramp(P.LOAM)
    my = ramp(P.MYCELIUM)
    for y in range(50, n):
        for x in range(n):
            h = 50 + round(math.sin(x * 0.18) * 1.2)
            if y >= h:
                s.set(x, y, loam[2] if hash01(x, y, seed) < 0.6 else loam[1])
                if y == h or (y == h + 1 and hash01(x, 1, seed) < 0.4):
                    s.set(x, y, my[3] if hash01(x, y, seed + 1) < 0.6 else my[2])
    # side fungi: a bouncecap (left) and an inkcap (right)
    _stem(s, 13, 43, 52, 4, ramp(P.BOUNCECAP_STEM))
    _dome(s, 13, 44, 8, 8, ramp(P.BOUNCECAP_CAP)[1:])
    for (x, y) in ((10, 39), (15, 38), (12, 42), (17, 41), (8, 42)):
        s.set(x, y, col(P.BOUNCECAP_SPOT[2]))
        s.set(x + 1, y, col(P.BOUNCECAP_SPOT[1]))
    ink = ramp(P.INK)
    cap = ramp(P.INKCAP_CAP)
    _stem(s, 52, 44, 52, 2, ramp(P.INKCAP_STEM))
    for y in range(30, 45):
        half = min(4.5, 1.5 + (y - 30) * 0.45)
        for x in range(64):
            if abs(x + 0.5 - 52) <= half:
                s.set(x, y, pick(cap[1:], 0.75 - (x - 52) * 0.08))
    for (x, y) in ((51, 34), (53, 37), (50, 39), (54, 41)):
        s.set(x, y, cap[1])
    for x in range(47, 58):
        s.set(x, 44, ink[1])
        s.set(x, 45, ink[2] if x % 2 else ink[0])
    s.set(49, 46, ink[3])
    s.set(55, 47, ink[3])
    # the hero: a great glowcap
    _stem(s, 32, 27, 52, 4, ramp(P.GLOWCAP_STEM))
    for y in range(27, 52):
        s.set(32 + round(math.sin(y * 0.5) * 0.7), y, G[1])
    _dome(s, 32, 27, 22, 14, ramp(P.GLOWCAP_CAP)[1:])
    for x in range(11, 54):  # glowing gills under the cap
        if abs(x + 0.5 - 32) < 21.0:
            s.set(x, 27, G[3] if x % 2 else G[2])
            if abs(x + 0.5 - 32) < 17.0 and abs(x + 0.5 - 32) > 2.0:
                s.set(x, 28, G[2] if x % 2 else G[1])
    for (x, y, r) in ((24, 18, 1), (38, 15, 1), (30, 21, 0), (44, 21, 0), (18, 24, 0), (33, 11, 0)):
        s.set(x, y, G[4])
        if r:
            s.set(x + 1, y, G[3])
            s.set(x, y + 1, G[3])
    # drifting glow spores
    for k in range(14):
        x, y = int(hash01(k, 1, seed) * 60) + 2, 30 + int(hash01(k, 2, seed) * 18)
        if s.get(x, y)[:3] != col(P.GLOWCAP_CAP[3])[:3]:
            s.set(x, y, G[3] if k % 3 else G[4])
    # a rounded frame
    for y in range(n):
        for x in range(n):
            cx = min(x, n - 1 - x)
            cy = min(y, n - 1 - y)
            if cx + cy < 3 or (cx < 3 and cy < 3 and math.hypot(3 - cx, 3 - cy) > 3.2):
                s.px[y][x] = (0, 0, 0, 0)
            elif cx == 0 or cy == 0 or (cx < 3 and cy < 3 and math.hypot(3 - cx, 3 - cy) > 2.2):
                s.set(x, y, col("#3fc7c0"))
    return s.image().resize((128, 128), Image.NEAREST)


# ---------------------------------------------------------------------------------------------------- effects

MYCOSIS_ICON = """
..................
..................
......cc..........
.....cddc....b....
....cdeedc..bcb...
....cdddddc..b....
.....bbcbb........
......aga.....c...
..b...aga....cdc..
.bcb..aga.....c...
..b..aagaa........
....acgggca...b...
...accccccca.bcb..
..acddcddddca.b...
..aabbbbbbbaa.....
..................
..................
..................
"""

SPORE_WARD_ICON = """
..................
..................
....aaaaaaaaaa....
...abbbbbbbbbba...
...abccccccccba...
...abcceeeeccba...
...abcegggggcba...
...abcegffgecba...
...abcegffgecba...
...abccegggecba...
....abcceeccba....
....abccccccba....
.....abccccba.....
......abccba......
.......abba.......
........aa........
..................
..................
"""

ROOTED_ICON = """
..................
..................
.....dd....dd.....
.....cd....cd.....
.....cd....cd.....
...bbcdb..bcdbb...
..bc.bcd..dcb.cb..
.bc...bcddcb...cb.
.b....bbccbb....b.
.....bcbbbbcb.....
....bc..bb..cb....
...bc..bccb..cb...
..aaaaaaaaaaaaaa..
..abbabbbabbbaba..
..................
..................
..................
..................
"""


def effect_icons() -> dict[str, Sprite]:
    myc = ramp(P.MYCOSIS)
    root = ramp(P.ROOT)
    return {
        "mycosis": outlined(from_ascii(MYCOSIS_ICON, {"a": myc[1], "b": myc[2], "c": myc[3], "d": myc[4],
                                                      "e": col("#f4ffe8"), "g": col(P.SPORE[2])})),
        "spore_ward": outlined(from_ascii(SPORE_WARD_ICON, {"a": col("#8c7a5a"), "b": col("#b9a47a"),
                                                            "c": col(P.SPORE[2]), "e": col(P.SPORE[3]),
                                                            "g": G[2], "f": G[4]})),
        "rooted": outlined(from_ascii(ROOTED_ICON, {"a": col(P.DIRT[1]), "b": root[1], "c": root[2], "d": root[3]})),
    }


# ---------------------------------------------------------------------------------------------------- particles

def _mote(size: int, core, edge, halo=None) -> Sprite:
    s = Sprite(8, 8)
    c = 3.5
    for y in range(8):
        for x in range(8):
            d = math.hypot(x - c, y - c)
            if d <= size * 0.5:
                s.px[y][x] = core if d <= size * 0.25 else edge
            elif halo is not None and d <= size * 0.5 + 1.2:
                s.px[y][x] = halo
    return s


def particles(out: Out) -> None:
    sp = ramp(P.SPORE)
    frames = {
        "spore": [_mote(4, sp[3], sp[2]), _mote(3, sp[3], sp[2]), _mote(3, sp[2], sp[1]), _mote(2, sp[2], sp[2])],
        "glow_spore": [_mote(4, G[4], G[3], G[2][:3] + (110,)), _mote(3, G[4], G[3], G[2][:3] + (90,)),
                       _mote(3, G[3], G[2], G[1][:3] + (70,)), _mote(2, G[3], G[2])],
    }
    ink = ramp(P.INK)
    drip = Sprite(8, 8)
    for (x, y, c) in ((3, 2, ink[2]), (4, 2, ink[2]), (3, 3, ink[1]), (4, 3, ink[2]), (3, 4, ink[1]), (4, 4, ink[1]),
                      (3, 1, ink[3]), (4, 5, ink[0]), (3, 5, ink[0])):
        drip.set(x, y, c)
    drip.set(3, 2, ink[4])
    frames["ink_drip"] = [drip]
    for name, sprites in frames.items():
        names = []
        for i, sprite in enumerate(sprites):
            tex = f"{name}_{i}"
            out.texture(f"particle/{tex}", sprite.image())
            names.append(f"{MOD_ID}:{tex}")
        out.asset_json(f"particles/{name}.json", {"textures": names})


# ---------------------------------------------------------------------------------------------------- armor

def _region(img: Image.Image, x0, y0, w, h, fn):
    for y in range(h):
        for x in range(w):
            c = fn(x, y, w, h)
            if c is not None:
                img.putpixel((x0 + x, y0 + y), c)


def _box(img, u, v, w, h, d, painter):
    """Paints every face of a model box (vanilla box UV layout) with painter(face, x, y, fw, fh)."""
    faces = {"top": (u + d, v, w, d), "bottom": (u + d + w, v, w, d), "right": (u, v + d, d, h),
             "front": (u + d, v + d, w, h), "left": (u + d + w, v + d, d, h), "back": (u + d + w + d, v + d, w, h)}
    for face, (x0, y0, fw, fh) in faces.items():
        _region(img, x0, y0, fw, fh, lambda x, y, ww, hh, f=face: painter(f, x, y, ww, hh))


def armor_layers() -> dict[str, Image.Image]:
    ml = ramp(P.MYCOLEATHER)
    my = ramp(P.MYCELIUM)
    seed = seed_of("armor")

    def leather(x, y, k=0):
        n = hash01(x + k * 31, y, seed)
        t = 0.55 + (n - 0.5) * 0.35 + (0.1 if (x * 3 + y) % 9 == 0 else 0)
        return pick(ml, t)

    layer1 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))

    def hood(face, x, y, w, h):
        if face == "front":
            # frame the face: brow and cheeks only
            if y <= 1 or x == 0 or x == w - 1:
                return my[2] if y == 1 and 0 < x < w - 1 else leather(x, y, 1)
            return None
        if face == "bottom":
            return None
        c = leather(x, y, 2)
        if face in ("right", "left", "back") and y == h - 1:
            return my[2]
        return c

    _box(layer1, 0, 0, 8, 8, 8, hood)

    def cap_shell(face, x, y, w, h):
        # the hood's outer shell is a little cap: a dome on top and a brim at the brow
        if face == "top":
            d = math.hypot(x - 3.5, y - 3.5)
            if (x, y) in ((2, 2), (5, 3), (3, 5)):
                return my[3]
            return pick(ml, 0.85 - d * 0.08)
        if face == "bottom":
            return None
        if y <= 1:
            return ml[4] if y == 0 else ml[3]
        if y == 2 and face != "front":
            return ml[1]
        return None

    _box(layer1, 32, 0, 8, 8, 8, cap_shell)

    def tunic(face, x, y, w, h):
        if face in ("top", "bottom"):
            return leather(x, y, 3)
        c = leather(x, y, 4)
        if face == "front" and x in (3, 4) and y % 3 == 1:
            return my[3]  # mycelium lacing
        if face == "front" and (x == 3 or x == 4):
            return ml[1]
        if y == h - 1:
            return ml[1]
        return c

    _box(layer1, 16, 16, 8, 12, 4, tunic)
    shelf = ramp(P.SHELF)

    def arm(face, x, y, w, h):
        if face == "bottom":
            return None
        if y < 4 and face != "top":
            return [shelf[4], shelf[3], shelf[2], shelf[1]][y]  # shelf-fungus shoulder plates
        if face == "top":
            return shelf[4]
        if y >= 10:
            return my[2] if y == 10 else leather(x, y, 5)
        return leather(x, y, 6)

    _box(layer1, 40, 16, 4, 12, 4, arm)

    def boots(face, x, y, w, h):
        if face == "top":
            return None
        if face == "bottom":
            return ml[0]
        if y < 7:
            return None
        if y == 7:
            return my[2]
        return ml[1] if y == h - 1 else leather(x, y, 7)

    _box(layer1, 0, 16, 4, 12, 4, boots)

    layer2 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))

    def waist(face, x, y, w, h):
        if face in ("top", "bottom"):
            return None
        if y < 7:
            return None
        if y == 7:
            return ml[1]
        return leather(x, y, 8)

    _box(layer2, 16, 16, 8, 12, 4, waist)

    def legs(face, x, y, w, h):
        if face in ("top",):
            return leather(x, y, 9)
        if face == "bottom":
            return None
        if y >= 10:
            return None
        if y == 5 and face in ("front", "back"):
            return my[2]
        return leather(x, y, 10)

    _box(layer2, 0, 16, 4, 12, 4, legs)

    # The Crown of the Bloom: a golden band with glowing caps rising from it.
    bloom1 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    gold = ramp(["#7a4a12", "#b07419", "#e0a22c", "#f7d061", "#fff1a8"])
    capr = ramp(P.GLOWCAP_CAP)

    def band(face, x, y, w, h):
        if face in ("top", "bottom"):
            return None
        if y == 2:
            return gold[3]
        if y == 3:
            return gold[2] if (x % 3) else G[3]
        if y == 4:
            return gold[1]
        return None

    _box(bloom1, 0, 0, 8, 8, 8, band)

    def caps(face, x, y, w, h):
        if face in ("top", "bottom"):
            return None
        # three little glowcaps along each side of the outer shell
        cx = [1.5, 3.5, 5.5]
        for c in cx:
            if y == 0 and abs(x - c) <= 0.6:
                return G[3]
            if y == 1 and abs(x - c) <= 1.1:
                return capr[3] if x < c else capr[2]
        return None

    _box(bloom1, 32, 0, 8, 8, 8, caps)
    bloom2 = Image.new("RGBA", (64, 32), (0, 0, 0, 0))
    return {"mycoleather_layer_1": layer1, "mycoleather_layer_2": layer2, "bloom_layer_1": bloom1,
            "bloom_layer_2": bloom2}
