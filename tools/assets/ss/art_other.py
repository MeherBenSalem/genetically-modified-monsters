"""The other fungal blocks: Glowcap Gills, Shelf Fungus, Mycelial Veils, Giant Puffball, Truffle Soil, Mycelial Soil,
the Glowcap Lantern and the Cultivation Log (textures, models, blockstates, names)."""
from __future__ import annotations

import math

from . import art_fungi, palette as P
from .art_kit import CLEAR, Sprite, col, fbm, hash01, mix, pick, ramp, seed_of, shade, vnoise, vnoise_a
from .art_models import cultivation_fruit, element, fungus_textures, glow
from .data_content import CULTIVATION, OTHER_BLOCKS
from .out import Out
from .paths import MOD_ID

ITEM_PARENTS: dict[str, str] = {}


def m(name: str) -> str:
    return f"{MOD_ID}:block/{name}"


def generate(out: Out) -> None:
    gills(out)
    shelf(out)
    veil(out)
    puffball(out)
    soils(out)
    lantern(out)
    cultivation_log(out)
    for bid, label in OTHER_BLOCKS:
        out.tr(f"block.{MOD_ID}.{bid}", label)


def cross_model(texture: str) -> dict:
    return {"parent": "minecraft:block/cross", "render_type": "minecraft:cutout", "textures": {"cross": m(texture)}}


def cross_elements(full_bright: bool = False) -> list[dict]:
    """The two diagonal planes of vanilla's cross model, optionally full-bright on NeoForge."""
    els = [
        {"from": [0.8, 0, 8], "to": [15.2, 16, 8], "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45, "rescale": True},
         "shade": False, "faces": {"north": {"uv": [0, 0, 16, 16], "texture": "#cross"},
                                   "south": {"uv": [0, 0, 16, 16], "texture": "#cross"}}},
        {"from": [8, 0, 0.8], "to": [8, 16, 15.2], "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45, "rescale": True},
         "shade": False, "faces": {"west": {"uv": [0, 0, 16, 16], "texture": "#cross"},
                                   "east": {"uv": [0, 0, 16, 16], "texture": "#cross"}}},
    ]
    if full_bright:
        for el in els:
            glow(el)
    return els


def glowing_cross_model(texture: str) -> dict:
    return {"ambientocclusion": False, "render_type": "minecraft:cutout",
            "textures": {"cross": m(texture), "particle": m(texture)}, "elements": cross_elements(True)}


# ---------------------------------------------------------------------------------------------------- gills

def gills_texture(tip: bool) -> Sprite:
    glow = ramp(P.GLOW)
    cap = ramp(P.GLOWCAP_CAP)
    seed = seed_of("gills", tip)
    s = Sprite()
    strands = [1, 3, 4, 6, 8, 9, 11, 13, 14]
    for i, x0 in enumerate(strands):
        length = 16 if not tip else 5 + int(hash01(i, 1, seed) * 9)
        phase = hash01(i, 2, seed) * 6.28
        for y in range(length):
            x = x0 + round(math.sin(y * 0.45 + phase) * 0.6)
            t = 0.3 + (y / 16) * 0.4 + (hash01(x, y, seed) - 0.5) * 0.2
            s.set(x, y, pick(glow[2:5], t))
        if tip:
            end_x = x0 + round(math.sin((length - 1) * 0.45 + phase) * 0.6)
            s.set(end_x, length, glow[4])
    # the gill folds join at the top, where they hang from the cap
    for x in range(16):
        if s.get(x, 0)[3] == 0 and hash01(x, 0, seed) < 0.7:
            s.set(x, 0, cap[3])
        if s.get(x, 1)[3] == 0 and hash01(x, 1, seed) < 0.3:
            s.set(x, 1, glow[2])
    return s


def gills(out: Out) -> None:
    out.texture("block/glowcap_gills", gills_texture(False).image())
    out.texture("block/glowcap_gills_tip", gills_texture(True).image())
    out.block_model("glowcap_gills", glowing_cross_model("glowcap_gills"))
    out.block_model("glowcap_gills_tip", glowing_cross_model("glowcap_gills_tip"))
    out.blockstate("glowcap_gills", {"variants": {"bottom=false": {"model": m("glowcap_gills")},
                                                  "bottom=true": {"model": m("glowcap_gills_tip")}}})


# ---------------------------------------------------------------------------------------------------- shelf fungus

SHELF = [(3, 5, 7, 3, 11), (8, 10, 6, 1, 9), (12, 14, 5, 5, 8)]  # y0, y1, reach, side, width (ShelfFungusBlock)


def shelf_textures() -> dict[str, Sprite]:
    sh = ramp(P.SHELF)
    grey = ramp(P.SHELF_GREY)
    seed = seed_of("shelf")
    top = Sprite()
    bands = [sh[1], sh[2], grey[1], sh[3], sh[2], grey[2], sh[4], sh[3], sh[5]]
    for y in range(16):
        for x in range(16):
            d = math.hypot((x - 7.5) * 0.75, y + 1.5) + (vnoise(x, y, seed, 4) - 0.5) * 1.1
            idx = min(len(bands) - 1, int(d / 1.15))
            c = bands[idx]
            if hash01(x, y, seed) < 0.12:
                c = shade(c, 0.06)
            top.set(x, y, c)
    bottom = Sprite()
    for y in range(16):
        for x in range(16):
            pore = (x + (y // 2)) % 3 == 0 and y % 2 == 0
            bottom.set(x, y, sh[4] if pore else pick(sh[4:], 0.4 + (hash01(x, y, seed) - 0.5) * 0.4))
    side = Sprite()
    for y in range(16):
        for x in range(16):
            band = [sh[5], sh[3], sh[2], grey[1], sh[1]][(y // 1) % 5] if y < 5 else sh[4]
            side.set(x, y, band if hash01(x, y, seed) > 0.1 else shade(band, -0.05))
    return {"top": top, "bottom": bottom, "side": side}


def shelf_model(count: int) -> dict:
    els = []
    for i in range(count):
        y0, y1, reach, a, width = SHELF[i]
        b = a + width
        tex = {"up": {"uv": [a, 0, b, reach], "texture": "#top"},
               "down": {"uv": [a, 0, b, reach], "texture": "#bottom"},
               "south": {"uv": [a, 0, b, y1 - y0], "texture": "#side"},
               "east": {"uv": [0, 0, reach, y1 - y0], "texture": "#side"},
               "west": {"uv": [0, 0, reach, y1 - y0], "texture": "#side"}}
        els.append({"from": [a, y0, 0], "to": [b, y1, reach], "faces": tex})
        # a thinner, rounder lip at the outer edge
        tex2 = {"up": {"uv": [a + 1, reach, b - 1, reach + 1], "texture": "#top"},
                "down": {"uv": [a + 1, 0, b - 1, 1], "texture": "#bottom"},
                "south": {"uv": [a + 1, 0, b - 1, 1], "texture": "#side"},
                "east": {"uv": [0, 0, 1, 1], "texture": "#side"},
                "west": {"uv": [0, 0, 1, 1], "texture": "#side"}}
        els.append({"from": [a + 1, y0, reach], "to": [b - 1, y0 + 1, reach + 1], "faces": tex2})
    return {"ambientocclusion": False, "textures": {"top": m("shelf_fungus_top"), "bottom": m("shelf_fungus_bottom"),
                                                    "side": m("shelf_fungus_side"), "particle": m("shelf_fungus_top")},
            "elements": els}


def shelf(out: Out) -> None:
    for key, sprite in shelf_textures().items():
        out.texture(f"block/shelf_fungus_{key}", sprite.image())
    for n in (1, 2, 3):
        out.block_model(f"shelf_fungus_{n}", shelf_model(n))
    variants = {}
    for facing, y in (("south", 0), ("west", 90), ("north", 180), ("east", 270)):
        for n in (1, 2, 3):
            v = {"model": m(f"shelf_fungus_{n}")}
            if y:
                v["y"] = y
            variants[f"facing={facing},shelves={n}"] = v
    out.blockstate("shelf_fungus", {"variants": variants})


# ---------------------------------------------------------------------------------------------------- veils

def veil_texture(head: bool, bulb: bool) -> Sprite:
    my = ramp(P.MYCELIUM)
    glow = ramp(P.GLOW)
    seed = seed_of("veil", head)
    s = Sprite()
    strands = [1, 4, 6, 9, 11, 14]
    for i, x0 in enumerate(strands):
        length = 16 if not head else 7 + int(hash01(i, 4, seed) * 8)
        drift = 1 if hash01(i, 5, seed) < 0.5 else -1
        bend = 5 + int(hash01(i, 6, seed) * 8)
        x = x0
        for y in range(length):
            if y == bend:
                x += drift  # each thread kinks once, so they hang loose rather than ruled
            tone = my[3] if hash01(x, y, seed) < 0.75 else my[4]
            if y > length - 3 and head:
                tone = my[2]
            s.set(x, y, tone)
        if head and hash01(i, 8, seed) < 0.6:
            s.set(x + drift, length, my[1])
    # a few fine cross-links, like cobweb
    for k in range(4 if not head else 2):
        y = 2 + int(hash01(k, 6, seed) * 10)
        x0 = strands[k % 5] + 1
        span = strands[k % 5 + 1] - strands[k % 5] - 1
        for dx in range(span):
            if s.get(x0 + dx, y)[3] == 0:
                s.set(x0 + dx, y + (1 if dx == span // 2 else 0), my[1])
    if bulb:
        cx, cy = 7, 9 if not head else 6
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - cx, y - cy)
                if d <= 1.9:
                    s.set(x, y, glow[4] if d < 0.8 else (glow[3] if x - cx + y - cy < 0 else glow[2]))
        s.set(cx, cy - 2, my[3])
        s.set(cx, cy - 3, my[3])
    return s


def bulb_texture() -> Sprite:
    glow = ramp(P.GLOW)
    s = Sprite()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            lit = (x - 7.5) + (y - 7.5) < 0
            s.set(x, y, glow[4] if d < 1.2 or (lit and d < 2.0) else glow[3])
    return s


def veil(out: Out) -> None:
    """Threads are a plain cross; a bulb is a small full-bright cube hanging among them."""
    out.texture("block/mycelial_veil_bulb", bulb_texture().image())
    for head in (True, False):
        name = "mycelial_veil" if head else "mycelial_veil_plant"
        out.texture(f"block/{name}", veil_texture(head, False).image())
        out.block_model(name, cross_model(name))
        y0 = 5 if head else 7
        bulb_el = glow(element((6.5, y0, 6.5), (9.5, y0 + 3, 9.5),
                               {f: ("bulb", None) for f in ("north", "south", "east", "west", "up", "down")}))
        out.block_model(f"{name}_bulb", {"ambientocclusion": False, "render_type": "minecraft:cutout",
                                         "textures": {"cross": m(name), "bulb": m("mycelial_veil_bulb"),
                                                      "particle": m(name)},
                                         "elements": cross_elements() + [bulb_el]})
    out.blockstate("mycelial_veil", {"variants": {"bulb=false": {"model": m("mycelial_veil")},
                                                  "bulb=true": {"model": m("mycelial_veil_bulb")}}})
    out.blockstate("mycelial_veil_plant", {"variants": {"bulb=false": {"model": m("mycelial_veil_plant")},
                                                        "bulb=true": {"model": m("mycelial_veil_plant_bulb")}}})


# ---------------------------------------------------------------------------------------------------- puffball

def puffball(out: Out) -> None:
    p = ramp(P.PUFFBALL)
    seed = seed_of("giant_puffball")
    top = Sprite()
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 6.5, y - 6.5) / 9.0
            t = 0.88 - d * 0.42 + (fbm(x, y, seed) - 0.5) * 0.18
            top.set(x, y, pick(p[1:], t))
    side = Sprite()
    for y in range(16):
        for x in range(16):
            edge = abs(x - 7.5) / 7.5
            t = 0.85 - edge * 0.25 - (y / 15) ** 2 * 0.45 + (fbm(x, y, seed + 1) - 0.5) * 0.18
            side.set(x, y, pick(p, t))
    # fine cracks in the skin and a few warts
    for s, sd in ((top, 3), (side, 4)):
        for k in range(4):
            x, y = int(hash01(k, sd, seed) * 14) + 1, int(hash01(sd, k, seed) * 12) + 1
            for i in range(3 + k % 2):
                s.set(x + i, y + (i // 2), p[2])
        for k in range(6):
            x, y = int(hash01(k, sd + 9, seed) * 16), int(hash01(sd + 9, k, seed) * 16)
            s.set(x, y, p[5])
            s.set(x + 1, y + 1, p[2])
    for x in range(16):
        side.set(x, 15, mix(p[1], col(P.DIRT[1]), 0.5))
        if hash01(x, 14, seed) < 0.5:
            side.set(x, 14, mix(p[2], col(P.DIRT[2]), 0.4))
    bottom = Sprite()
    for y in range(16):
        for x in range(16):
            bottom.set(x, y, mix(p[1], col(P.DIRT[1]), 0.35 + hash01(x, y, seed) * 0.3))
    out.texture("block/giant_puffball_top", top.image())
    out.texture("block/giant_puffball_side", side.image())
    out.texture("block/giant_puffball_bottom", bottom.image())
    out.block_model("giant_puffball", {"parent": "minecraft:block/cube_bottom_top", "textures": {
        "top": m("giant_puffball_top"), "side": m("giant_puffball_side"), "bottom": m("giant_puffball_bottom")}})
    out.blockstate("giant_puffball", {"variants": {"": [{"model": m("giant_puffball")}, {"model": m("giant_puffball"), "y": 90},
                                                        {"model": m("giant_puffball"), "y": 180},
                                                        {"model": m("giant_puffball"), "y": 270}]}})


# ---------------------------------------------------------------------------------------------------- soils

def _dirt(seed, rmp) -> Sprite:
    s = Sprite()
    for y in range(16):
        for x in range(16):
            t = 0.5 + (fbm(x, y, seed, cells=(4.0, 2.0, 1.0)) - 0.5) * 0.9
            s.set(x, y, pick(rmp, t))
    return s


def _threads(s: Sprite, seed: int, count: int, rmp, ymax: int = 16, ystart: int = 0, length: int = 7,
             wrap: bool = True) -> None:
    """Fine mycelial threads: 1px diagonal-ish walks that never double back into blobs."""
    for k in range(count):
        x = int(hash01(k, 1, seed) * 16)
        y = ystart + int(hash01(k, 2, seed) * max(1, ymax - ystart))
        dx = 1 if hash01(k, 4, seed) < 0.5 else -1
        for step in range(length - 2 + int(hash01(k, 3, seed) * 5)):
            if y >= ymax or (not wrap and not (0 <= x < 16)):
                break
            s.set(x % 16, y % 16, rmp[3] if step % 4 else rmp[2])
            r = hash01(k, step, seed + 5)
            if r < 0.55:
                x += dx
            elif r < 0.85:
                y += 1
            else:
                x += dx
                y += 1


def soils(out: Out) -> None:
    dirt = ramp(["#3b281b", "#4d3524", "#61442e", "#77573c", "#8c6a4c"])
    truffle = ramp(P.TRUFFLE)
    seed = seed_of("truffle_soil")
    ts = _dirt(seed, dirt)
    # truffle nodules: dark lumps with a marbled glint
    for (cx, cy, r) in ((4, 4, 2.2), (11.5, 9, 2.6), (5, 12.5, 1.7), (13, 2, 1.4)):
        for y in range(16):
            for x in range(16):
                d = math.hypot(x - cx, y - cy) + (hash01(x, y, seed) - 0.5) * 0.8
                if d <= r:
                    lit = (x - cx) + (y - cy) < -0.5
                    ts.set(x, y, truffle[3] if lit else truffle[1])
                    if hash01(x, y, seed + 2) < 0.18:
                        ts.set(x, y, col(P.TRUFFLE_MARBLE[0]))
                elif d <= r + 0.8 and (x - cx) + (y - cy) > 0:
                    ts.set(x, y, dirt[0])
    for k in range(4):  # root hairs
        x, y = int(hash01(k, 8, seed) * 16), int(hash01(8, k, seed) * 16)
        for i in range(3):
            ts.set(x + i, y + i % 2, col("#a3876b"))
    out.texture("block/truffle_soil", ts.image())
    out.block_model("truffle_soil", {"parent": "minecraft:block/cube_all", "textures": {"all": m("truffle_soil")}})
    out.blockstate("truffle_soil", {"variants": {"": [{"model": m("truffle_soil")}, {"model": m("truffle_soil"), "y": 90},
                                                      {"model": m("truffle_soil"), "y": 180},
                                                      {"model": m("truffle_soil"), "y": 270}]}})

    loam = ramp(P.LOAM)
    my = ramp(P.MYCELIUM)
    seed = seed_of("mycelial_soil")
    bottom = _dirt(seed, loam)
    _threads(bottom, seed + 1, 3, my)
    top = _dirt(seed + 2, loam)
    _threads(top, seed + 3, 10, my, length=6)
    for k in range(6):  # little white knots where threads meet, and a few spores
        x, y = int(hash01(k, 9, seed) * 16), int(hash01(9, k, seed) * 16)
        top.set(x, y, my[4] if k % 2 else col(P.SPORE[2]))
    side = _dirt(seed + 4, loam)
    for x in range(16):
        depth = 1 + (1 if hash01(x, 0, seed) < 0.55 else 0)
        for y in range(depth):
            side.set(x, y, my[3] if y == 0 else my[2])
        if hash01(x, 2, seed) < 0.22:  # threads creeping down the side
            for y in range(depth, depth + 2 + int(hash01(x, 3, seed) * 4)):
                side.set(x + (1 if y > depth + 2 else 0), y, my[2])
    _threads(side, seed + 5, 3, my, ymax=14, ystart=6, length=4)
    out.texture("block/mycelial_soil", bottom.image())
    out.texture("block/mycelial_soil_top", top.image())
    out.texture("block/mycelial_soil_side", side.image())
    out.block_model("mycelial_soil", {"parent": "minecraft:block/cube_bottom_top", "textures": {
        "top": m("mycelial_soil_top"), "side": m("mycelial_soil_side"), "bottom": m("mycelial_soil")}})
    out.blockstate("mycelial_soil", {"variants": {"": [{"model": m("mycelial_soil")}, {"model": m("mycelial_soil"), "y": 90},
                                                       {"model": m("mycelial_soil"), "y": 180},
                                                       {"model": m("mycelial_soil"), "y": 270}]}})


# ---------------------------------------------------------------------------------------------------- lantern

def lantern_textures() -> dict[str, Sprite]:
    stem = ramp(P.GLOWCAP_STEM)
    glow = ramp(P.GLOW)
    seed = seed_of("lantern")
    side = Sprite()
    for y in range(16):
        for x in range(16):
            # frame bars at the edges, glowing gill core between them
            if x in (0, 1, 14, 15) or y in (0, 15):
                c = stem[3] if x in (0, 1) else stem[1] if x in (14, 15) else stem[2]
            else:
                gill = x % 2 == 0
                c = glow[4] if gill else glow[3]
                if hash01(x, y, seed) < 0.12:
                    c = glow[4]
            side.set(x, y, c)
    plate = Sprite()
    for y in range(16):
        for x in range(16):
            plate.set(x, y, pick(stem, 0.55 + (hash01(x, y, seed + 1) - 0.5) * 0.3 - (x + y - 15) * 0.012))
    return {"lantern_side": side, "lantern_plate": plate}


def lantern_elements(dy: float) -> list[dict]:
    def sh(fr, to):
        return [fr[0], fr[1] + dy, fr[2]], [to[0], to[1] + dy, to[2]]

    def box(fr, to, tex, vtop=None, top=None, bottom=None):
        f, t = sh(fr, to)
        faces = {k: (tex, vtop) for k in ("north", "south", "east", "west")}
        faces["up"] = (top or tex, None)
        faces["down"] = (bottom or tex, None)
        return element(f, t, faces)

    return [
        box((5, 0, 5), (11, 1, 11), "plate"),
        glow(element(*sh((5.5, 1, 5.5), (10.5, 6, 10.5)), {k: ("side", 5) for k in ("north", "south", "east", "west")})),
        glow(box((4, 6, 4), (12, 8, 12), "cap_side", vtop=12, top="cap", bottom="gills")),
        box((6, 8, 6), (10, 9, 10), "cap_side", vtop=10, top="cap"),
        box((7, 9, 7), (9, 10, 9), "plate"),
    ]


def lantern(out: Out) -> None:
    for key, sprite in lantern_textures().items():
        out.texture(f"block/glowcap_{key}", sprite.image())
    tex = fungus_textures("glowcap")
    textures = {"cap": tex["cap"], "cap_side": tex["cap_side"], "gills": tex["gills"],
                "side": m("glowcap_lantern_side"), "plate": m("glowcap_lantern_plate"), "particle": m("glowcap_lantern_side"),
                "chain": "minecraft:block/chain"}
    out.block_model("glowcap_lantern", {"parent": "minecraft:block/block", "ambientocclusion": False,
                                        "textures": textures, "elements": lantern_elements(0)})
    chain = [
        {"from": [6.5, 11, 8], "to": [9.5, 16, 8], "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45},
         "shade": False, "faces": {"north": {"uv": [0, 0, 3, 5], "texture": "#chain"},
                                   "south": {"uv": [0, 0, 3, 5], "texture": "#chain"}}},
        {"from": [8, 11, 6.5], "to": [8, 16, 9.5], "rotation": {"origin": [8, 8, 8], "axis": "y", "angle": 45},
         "shade": False, "faces": {"west": {"uv": [3, 0, 6, 5], "texture": "#chain"},
                                   "east": {"uv": [3, 0, 6, 5], "texture": "#chain"}}},
    ]
    out.block_model("glowcap_lantern_hanging", {"parent": "minecraft:block/block", "ambientocclusion": False,
                                                "render_type": "minecraft:cutout", "textures": textures,
                                                "elements": lantern_elements(1) + chain})
    out.blockstate("glowcap_lantern", {"variants": {"hanging=false": {"model": m("glowcap_lantern")},
                                                    "hanging=true": {"model": m("glowcap_lantern_hanging")}}})


# ---------------------------------------------------------------------------------------------------- cultivation log

def log_textures() -> dict[str, Sprite]:
    bark = ramp(P.BARK)
    seed = seed_of("cultivation_log")
    side = Sprite()
    for y in range(16):
        for x in range(16):
            n = vnoise_a(x, y, seed, 8, 2)
            t = 0.5 + (n - 0.5) * 0.8 + (hash01(x, y, seed) - 0.5) * 0.15
            side.set(x, y, pick(bark, t))
    for row in (3, 7, 11):  # bark furrows running along the log
        for x in range(16):
            if hash01(x, row, seed) < 0.75:
                side.set(x, row + (1 if hash01(row, x, seed) < 0.2 else 0), bark[0])
    # wax-sealed inoculation plugs, the mark of a real shiitake log
    wax = ramp(["#7a5a2a", "#a98244", "#cfa968"])
    for (px, py) in ((3, 5), (11, 1), (7, 13), (13, 9)):
        side.set(px, py, wax[2])
        side.set(px + 1, py, wax[1])
        side.set(px, py + 1, wax[0])
    # one lichen patch
    for k in range(1):
        x, y = int(hash01(k, 3, seed) * 14), int(hash01(3, k, seed) * 14)
        for (dx, dy) in ((0, 0), (1, 0), (0, 1), (1, 1), (2, 1)):
            if hash01(x + dx, y + dy, seed) < 0.8:
                side.set(x + dx, y + dy, col("#6f7f4a") if (dx + dy) % 2 else col("#8a9a5c"))
    end = Sprite()
    wood = ramp(["#8a6a48", "#a6845d", "#c2a074", "#d8b98d", "#e9d0a6"])
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            if d > 5.6:
                end.set(x, y, pick(bark, 0.4 + (hash01(x, y, seed) - 0.5) * 0.4))
            else:
                ring = (math.sin(d * 2.4) + 1) / 2
                end.set(x, y, pick(wood, 0.35 + ring * 0.45 + (hash01(x, y, seed + 1) - 0.5) * 0.1))
    end.set(7, 7, wood[0])
    my = ramp(P.MYCELIUM)
    colon = Sprite()
    _threads(colon, seed + 7, 2, my, length=5)
    for k in range(2):  # small white patches where the mycelium breaks through the bark
        x, y = int(hash01(k, 11, seed) * 15), 2 + int(hash01(11, k, seed) * 11)
        colon.set(x, y, my[4])
        colon.set(x + 1, y, my[3])
    return {"cultivation_log": side, "cultivation_log_end": end, "cultivation_log_mycelium": colon}


def cultivation_log(out: Out) -> None:
    for key, sprite in log_textures().items():
        out.texture(f"block/{key}", sprite.image())
    long_faces = {f: {"uv": [0, 2, 16, 14], "texture": "#bark"} for f in ("north", "south", "up", "down")}
    long_faces["down"]["cullface"] = "down"
    ends = {f: {"uv": [2, 2, 14, 14], "texture": "#end"} for f in ("east", "west")}
    out.block_model("cultivation_log", {"parent": "minecraft:block/block", "textures": {
        "bark": m("cultivation_log"), "end": m("cultivation_log_end"), "particle": m("cultivation_log")},
        "elements": [{"from": [0, 0, 2], "to": [16, 12, 14], "faces": {**long_faces, **ends}}]})
    over = {f: {"uv": [0, 2, 16, 14], "texture": "#mycelium"} for f in ("north", "south", "up")}
    out.block_model("cultivation_log_colonized", {"render_type": "minecraft:cutout", "ambientocclusion": False,
                                                  "textures": {"mycelium": m("cultivation_log_mycelium"),
                                                               "particle": m("cultivation_log")},
                                                  "elements": [{"from": [-0.01, 0, 1.99], "to": [16.01, 12.01, 14.01],
                                                                "faces": over}]})
    parts = [{"when": {"axis": "x"}, "apply": {"model": m("cultivation_log")}},
             {"when": {"axis": "z"}, "apply": {"model": m("cultivation_log"), "y": 90}},
             {"when": {"axis": "x", "fungus": "|".join(CULTIVATION)}, "apply": {"model": m("cultivation_log_colonized")}},
             {"when": {"axis": "z", "fungus": "|".join(CULTIVATION)},
              "apply": {"model": m("cultivation_log_colonized"), "y": 90}}]
    for fungus in CULTIVATION:
        tex = fungus_textures(fungus)
        for stage in (1, 2, 3):
            name = f"cultivation_log_{fungus}_{stage}"
            out.block_model(name, {"ambientocclusion": False, "render_type": "minecraft:cutout", "textures": tex,
                                   "elements": cultivation_fruit(fungus, stage)})
            parts.append({"when": {"axis": "x", "fungus": fungus, "stage": str(stage)}, "apply": {"model": m(name)}})
            parts.append({"when": {"axis": "z", "fungus": fungus, "stage": str(stage)}, "apply": {"model": m(name), "y": 90}})
    out.blockstate("cultivation_log", {"multipart": parts})
    ITEM_PARENTS["cultivation_log"] = m("cultivation_log")
