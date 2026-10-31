"""Block-model geometry for the 3D fungi, built from boxes whose face UVs equal the face size (one texel per
pixel), centred on the material texture. Also: the potted versions and the fruit clusters of the cultivation log."""
from __future__ import annotations

from .paths import MOD_ID

FACES = ("north", "south", "east", "west", "up", "down")


def _clamp(v: float) -> float:
    return round(max(0.0, min(16.0, v)), 3)


def element(fr, to, faces: dict, rotation: dict | None = None) -> dict:
    """faces: face -> (texture var, vtop or None). Side faces sample rows vtop.. (default: bottom-aligned)."""
    w, h, d = to[0] - fr[0], to[1] - fr[1], to[2] - fr[2]
    out = {}
    for face, (tex, vtop) in faces.items():
        if face in ("up", "down"):
            uw, uh = w, d
            u0, v0 = 8 - uw / 2, 8 - uh / 2
        else:
            uw = w if face in ("north", "south") else d
            uh = h
            u0 = 8 - uw / 2
            v0 = vtop if vtop is not None else 16 - uh
        out[face] = {"uv": [_clamp(u0), _clamp(v0), _clamp(u0 + uw), _clamp(v0 + uh)], "texture": f"#{tex}"}
    el = {"from": [round(c, 3) for c in fr], "to": [round(c, 3) for c in to], "faces": out}
    if rotation:
        el["rotation"] = rotation
    return el


def cap(fr, to, vtop=0, top="cap", side="cap_side", under="gills") -> dict:
    faces = {f: (side, vtop) for f in ("north", "south", "east", "west")}
    if top:
        faces["up"] = (top, None)
    if under:
        faces["down"] = (under, None)
    return element(fr, to, faces)


def stem(fr, to, tex="stem", vtop=None, top=False, bottom=False) -> dict:
    faces = {f: (tex, vtop) for f in ("north", "south", "east", "west")}
    if top:
        faces["up"] = (tex, None)
    if bottom:
        faces["down"] = (tex, None)
    return element(fr, to, faces)


def block(fr, to, tex, vtop=None) -> dict:
    return element(fr, to, {f: (tex, vtop) for f in FACES})


FULL_BRIGHT = {"block_light": 15, "sky_light": 15, "ambient_occlusion": False}


def glow(el: dict) -> dict:
    """Marks a glowing element full-bright on NeoForge (Fabric and vanilla ignore the key)."""
    el["neoforge_data"] = dict(FULL_BRIGHT)
    return el


# --------------------------------------------------------------------------------------------- the nine fungi

def fungus_elements(name: str) -> list[dict]:
    if name == "glowcap":
        return [
            stem((6.5, 0, 6.5), (9.5, 1, 9.5), bottom=False),
            stem((7, 1, 7), (9, 6, 9)),
            glow(cap((4, 6, 4), (12, 7, 12), vtop=13)),
            glow(cap((5, 7, 5), (11, 8, 11), vtop=11)),
            glow(cap((6, 8, 6), (10, 9, 10), vtop=9)),
            stem((3, 0, 10), (4, 3, 11)),
            glow(cap((2, 3, 9), (5, 4, 12), vtop=13)),
        ]
    if name == "bouncecap":
        return [
            stem((6, 0, 6), (10, 4, 10)),
            cap((3, 4, 3), (13, 6, 13), vtop=12),
            cap((4, 6, 4), (12, 8, 12), vtop=8),
            cap((5, 8, 5), (11, 9, 11), vtop=5, under=None),
            cap((6, 9, 6), (10, 10, 10), vtop=3, under=None),
        ]
    if name == "inkcap":
        # A shaggy mane: a tall, narrow bell over a short stem, tapering to a rounded tip; the cap is over
        # three quarters of the height and its lower edge dissolves into ink. A closed young one beside it.
        return [
            stem((7, 0, 7), (9, 3, 9)),
            cap((5.5, 3, 5.5), (10.5, 9, 10.5), vtop=10),
            cap((6, 9, 6), (10, 11, 10), vtop=7, under=None),
            cap((6.5, 11, 6.5), (9.5, 12.5, 9.5), vtop=5, under=None),
            cap((7.25, 12.5, 7.25), (8.75, 13, 8.75), vtop=4, under=None),
            stem((3, 0, 3), (4, 1, 4)),
            cap((2.5, 1, 2.5), (4.5, 5, 4.5), vtop=12),
            cap((3, 5, 3), (4, 6, 4), vtop=8, under=None),
        ]
    if name == "morel":
        return [
            stem((6, 0, 6), (10, 3, 10)),
            cap((5, 3, 5), (11, 6, 11), vtop=0, under="cap"),
            cap((6, 6, 6), (10, 9, 10), vtop=4, under=None),
            cap((7, 9, 7), (9, 11, 9), vtop=8, under=None),
            stem((11, 0, 4), (13, 1, 6)),
            cap((10.5, 1, 3.5), (13.5, 4, 6.5), vtop=2, under="cap"),
            cap((11, 4, 4), (13, 6, 6), vtop=6, under=None),
        ]
    if name == "chanterelle":
        return [
            stem((7, 0, 7), (9, 3, 9)),
            cap((6, 3, 6), (10, 5, 10), vtop=10, top=None, under="cap_side"),
            cap((5, 5, 5), (11, 7, 11), vtop=0, under="cap_side"),
            stem((3, 0, 10), (5, 2, 12)),
            cap((2, 2, 9), (6, 4, 13), vtop=0, under="cap_side"),
            stem((11, 0, 4), (12, 1, 5)),
            cap((10, 1, 3), (13, 2, 6), vtop=0, under="cap_side"),
        ]
    if name == "deathcap":
        return [
            stem((6, 0, 6), (10, 2, 10), top=True),
            stem((7, 2, 7), (9, 7, 9)),
            stem((6, 5, 6), (10, 6, 10), top=True, bottom=True),
            cap((4, 7, 4), (12, 9, 12), vtop=12),
            cap((5, 9, 5), (11, 10, 11), vtop=8, under=None),
        ]
    if name == "frostcap":
        return [
            stem((7, 0, 7), (9, 4, 9)),
            cap((5, 4, 5), (11, 6, 11), vtop=12),
            cap((6, 6, 6), (10, 8, 10), vtop=6, under=None),
            block((7.5, 8, 7.5), (8.5, 9, 8.5), "crystal"),
            block((5, 3, 5), (6, 4, 6), "crystal"),
            block((10, 3, 10), (11, 4, 11), "crystal"),
            stem((2, 0, 10), (3, 2, 11)),
            cap((1, 2, 9), (4, 3, 12), vtop=12),
        ]
    if name == "emberstool":
        return [
            # Slender charred stalks, each topped by a glowing ember head.
            stem((7.5, 0, 7.5), (8.5, 6, 8.5), tex="stalk"),
            glow(block((7, 6, 7), (9, 8, 9), "tip", vtop=2)),
            glow(block((7.5, 8, 7.5), (8.5, 9, 8.5), "tip", vtop=0)),
            stem((5, 0, 9), (6, 4, 10), tex="stalk"),
            glow(block((4.5, 4, 8.5), (6.5, 6, 10.5), "tip", vtop=3)),
            stem((10, 0, 5), (11, 5, 6), tex="stalk"),
            glow(block((9.5, 5, 4.5), (11.5, 7, 6.5), "tip", vtop=2)),
            stem((10, 0, 10), (11, 2, 11), tex="stalk"),
            glow(block((9.5, 2, 9.5), (11.5, 3.5, 11.5), "tip", vtop=6)),
        ]
    if name == "puffball":
        # Rounded balls built from stacked layers.
        return [
            cap((6, 0, 6), (10, 1, 10), vtop=15, top=None, under="bottom"),
            cap((5, 1, 5), (11, 2, 11), vtop=13, top=None, under="bottom"),
            cap((4, 2, 4), (12, 5, 12), vtop=8, under="bottom"),
            cap((5, 5, 5), (11, 6, 11), vtop=4, under=None),
            cap((6, 6, 6), (10, 7, 10), vtop=2, under=None),
            cap((2.5, 0, 10.5), (4.5, 0.5, 12.5), vtop=15, top=None, under="bottom"),
            cap((2, 0.5, 10), (5, 2.5, 13), vtop=8, under="bottom"),
            cap((2.5, 2.5, 10.5), (4.5, 3, 12.5), vtop=3, under=None),
        ]
    raise KeyError(name)


FUNGUS_TEXTURES = {
    "glowcap": ["cap", "cap_side", "gills", "stem"],
    "bouncecap": ["cap", "cap_side", "gills", "stem"],
    "inkcap": ["cap", "cap_side", "gills", "stem"],
    "morel": ["cap", "cap_side", "stem"],
    "chanterelle": ["cap", "cap_side", "stem"],
    "deathcap": ["cap", "cap_side", "gills", "stem"],
    "frostcap": ["cap", "cap_side", "gills", "stem", "crystal"],
    "emberstool": ["stalk", "tip"],
    "puffball": ["cap", "cap_side", "bottom"],
}


def fungus_textures(name: str) -> dict:
    tex = {k: f"{MOD_ID}:block/fungus/{name}_{k}" for k in FUNGUS_TEXTURES[name]}
    tex["particle"] = tex.get("cap") or tex.get("tip")
    return tex


def fungus_model(name: str) -> dict:
    return {"ambientocclusion": False, "render_type": "minecraft:cutout", "textures": fungus_textures(name),
            "elements": fungus_elements(name)}


def transform(elements: list[dict], scale: float, dy: float, center=(8.0, 0.0, 8.0), dx: float = 0.0,
              dz: float = 0.0) -> list[dict]:
    out = []
    cx, cy, cz = center
    for el in elements:
        e = dict(el)
        fr, to = el["from"], el["to"]
        e["from"] = [round(cx + (fr[0] - cx) * scale + dx, 3), round(cy + (fr[1] - cy) * scale + dy, 3),
                     round(cz + (fr[2] - cz) * scale + dz, 3)]
        e["to"] = [round(cx + (to[0] - cx) * scale + dx, 3), round(cy + (to[1] - cy) * scale + dy, 3),
                   round(cz + (to[2] - cz) * scale + dz, 3)]
        out.append(e)
    return out


def pot_elements() -> list[dict]:
    """The flower pot, built like vanilla's (walls and soil), textured with the vanilla pot and dirt by name."""
    def face(uv, tex="flowerpot"):
        return {"uv": uv, "texture": f"#{tex}"}
    return [
        {"from": [5, 0, 5], "to": [6, 6, 11], "faces": {
            "down": face([5, 5, 6, 11]), "up": face([5, 5, 6, 11]), "north": face([10, 10, 11, 16]),
            "south": face([5, 10, 6, 16]), "west": face([5, 10, 11, 16]), "east": face([5, 10, 11, 16])}},
        {"from": [10, 0, 5], "to": [11, 6, 11], "faces": {
            "down": face([10, 5, 11, 11]), "up": face([10, 5, 11, 11]), "north": face([5, 10, 6, 16]),
            "south": face([10, 10, 11, 16]), "west": face([5, 10, 11, 16]), "east": face([5, 10, 11, 16])}},
        {"from": [6, 0, 5], "to": [10, 6, 6], "faces": {
            "down": face([6, 10, 10, 11]), "up": face([6, 5, 10, 6]), "north": face([6, 10, 10, 16]),
            "south": face([6, 10, 10, 16])}},
        {"from": [6, 0, 10], "to": [10, 6, 11], "faces": {
            "down": face([6, 5, 10, 6]), "up": face([6, 10, 10, 11]), "north": face([6, 10, 10, 16]),
            "south": face([6, 10, 10, 16])}},
        {"from": [6, 0, 6], "to": [10, 4, 10], "faces": {
            "down": face([6, 12, 10, 16]), "up": face([6, 6, 10, 10], "dirt")}},
    ]


def potted_model(name: str) -> dict:
    tex = fungus_textures(name)
    tex.update({"flowerpot": "minecraft:block/flower_pot", "dirt": "minecraft:block/dirt",
                "particle": "minecraft:block/flower_pot"})
    elements = fungus_elements(name)
    # Keep only the main mushroom (the first group, inside the pot's footprint) and scale it into the pot.
    main = [e for e in elements if 4 <= (e["from"][0] + e["to"][0]) / 2 <= 12 and 4 <= (e["from"][2] + e["to"][2]) / 2 <= 12]
    return {"ambientocclusion": False, "render_type": "minecraft:cutout", "textures": tex,
            "elements": pot_elements() + transform(main, 0.72, 4.0)}


# --------------------------------------------------------------------------------------------- cultivation log

def cultivation_fruit(name: str, stage: int) -> list[dict]:
    """Fruit on top of a log lying along X (log top at y=12). Stage 1 pins, 2 young, 3 ripe."""
    els = fungus_elements(name)
    main = [e for e in els if 4 <= (e["from"][0] + e["to"][0]) / 2 <= 12 and 4 <= (e["from"][2] + e["to"][2]) / 2 <= 12]
    spots = {1: [(4.5, 7.0, 0.32), (11.0, 9.0, 0.28)],
             2: [(3.5, 7.5, 0.48), (8.5, 6.5, 0.4), (12.5, 9.0, 0.44)],
             3: [(3.0, 8.0, 0.66), (8.0, 6.5, 0.56), (12.5, 8.5, 0.62), (6.0, 10.0, 0.4)]}[stage]
    out = []
    for (x, z, s) in spots:
        out += transform(main, s, 11.7, dx=x - 8, dz=z - 8)
    return out
