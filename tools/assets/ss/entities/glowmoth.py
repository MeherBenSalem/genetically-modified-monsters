"""Glowmoth: a soft, fuzzy moth with dark slate wings that carry luminous teal eye-spots and veins, feathery
antennae and a glowing abdomen tip. It flutters toward light and glowcaps. The wings are thin planes, so they flap
from the thorax and are drawn on both sides."""
from __future__ import annotations

import math

from ..palette import GLOW
from .anim import Anim
from .kit import MOTH_FUZZ, MOTH_WING, eye, fuzz, quant
from .paint import Px, as_rgba, paint
from .rig import Rig

NAME = "glowmoth"
CLASS = "Glowmoth"


def rig() -> Rig:
    r = Rig(NAME, (64, 32))
    body = r.root.child("body", (0, -5, 0))
    body.box("thorax", (-1, -1.5, -1.5), (2, 2, 3), mat="fuzz")
    head = body.child("head", (0, -0.5, -1.5))
    head.box("head", (-1, -1, -2), (2, 2, 2), mat="head")
    head.child("left_antenna", (0.5, -1, -1.5), rot=(-35, 0, 20)).box("left_antenna", (0, -4, -0.5), (0, 4, 1), mat="antenna")
    head.child("right_antenna", (-0.5, -1, -1.5), rot=(-35, 0, -20)).box("right_antenna", (0, -4, -0.5), (0, 4, 1),
                                                                        mat="antenna")
    body.child("abdomen", (0, -0.5, 1.5), rot=(-10, 0, 0)).box("abdomen", (-1, -1, 0), (2, 2, 4), mat="abdomen")
    lw = body.child("left_wing", (1, -1.5, -0.5))
    lw.box("left_fore", (0, 0, -2.5), (7, 0, 5), mat="fore")
    lw.box("left_hind", (0, 0.01, 1.5), (5, 0, 4), mat="hind")
    rw = body.child("right_wing", (-1, -1.5, -0.5))
    rw.box("right_fore", (-7, 0, -2.5), (7, 0, 5), mat="fore", mirror=True)
    rw.box("right_hind", (-5, 0.01, 1.5), (5, 0, 4), mat="hind", mirror=True)
    return r


def anims() -> list[Anim]:
    fly = Anim("fly", 0.3, loop=True)
    fly.rot("left_wing", (0, 0, 0, -55), (0.15, 0, 0, 35), (0.3, 0, 0, -55))
    fly.rot("right_wing", (0, 0, 0, 55), (0.15, 0, 0, -35), (0.3, 0, 0, 55))
    fly.pos("body", (0, 0, -0.4, 0), (0.15, 0, 0.5, 0), (0.3, 0, -0.4, 0))
    fly.rot("abdomen", (0, 4, 0, 0), (0.15, -8, 0, 0), (0.3, 4, 0, 0))

    hover = Anim("hover", 1.2, loop=True)
    hover.rot("left_wing", (0, 0, 0, -20), (0.3, 0, 0, 10), (0.6, 0, 0, -20), (0.9, 0, 0, 10), (1.2, 0, 0, -20))
    hover.rot("right_wing", (0, 0, 0, 20), (0.3, 0, 0, -10), (0.6, 0, 0, 20), (0.9, 0, 0, -10), (1.2, 0, 0, 20))
    hover.pos("body", (0, 0, 0, 0), (0.6, 0, 0.8, 0), (1.2, 0, 0, 0))
    hover.rot("left_antenna", (0, 0, 0, 0), (0.5, 8, 0, 6), (0.65, -4, 0, 0), (1.2, 0, 0, 0))
    hover.rot("right_antenna", (0, 0, 0, 0), (0.7, 8, 0, -6), (0.85, -4, 0, 0), (1.2, 0, 0, 0))
    hover.rot("abdomen", (0, 0, 0, 0), (0.6, -6, 0, 0), (1.2, 0, 0, 0))
    return [fly, hover]


# ---- textures ---------------------------------------------------------------------------------------------------

FUZZ = fuzz(MOTH_FUZZ, seed=81)


def _wing(px: Px, hind: bool):
    """Dark slate with radiating veins, a pale scalloped edge and a glowing eye-spot."""
    if px.face not in ("top", "bottom"):
        return quant(MOTH_WING, 0.3)
    w, h = px.w, px.h
    # Wing outline: rounded corners at the outer edge (u = 1 is the wing tip for the left wing).
    u, v = px.u, px.v
    if (u > 0.82 and (v < 0.18 or v > 0.82)) or (hind and u > 0.7 and v > 0.7):
        return None
    vein = abs(math.sin((math.atan2(v - 0.5, u + 0.05)) * 5)) < 0.18
    spot = ((u - 0.62) ** 2 / 0.03 + (v - 0.45) ** 2 / 0.06) < 1.0 if not hind else ((u - 0.5) ** 2 / 0.04 + (v - 0.5) ** 2 / 0.07) < 1.0
    if spot:
        core = ((u - (0.62 if not hind else 0.5)) ** 2 / 0.012 + (v - (0.45 if not hind else 0.5)) ** 2 / 0.025) < 1.0
        return quant(GLOW, 0.55 if core else 0.25)
    if u > 0.84:
        return quant(MOTH_FUZZ, 0.55)
    if vein:
        return quant(MOTH_WING, 0.85)
    return quant(MOTH_WING, 0.45 - u * 0.25 + (0.1 if px.face == "top" else -0.1))


def textures(r: Rig) -> dict:
    def painter(px: Px):
        mat = px.cube.mat
        if mat == "fore":
            return _wing(px, False)
        if mat == "hind":
            return _wing(px, True)
        if mat == "antenna":
            if px.face in ("left", "right"):
                return quant(GLOW, 0.6) if px.y == 0 else quant(MOTH_FUZZ, 0.75)
            return None
        if mat == "head" and px.face == "front":
            if px.y == 0:
                return as_rgba("#0c1016") if px.x in (0, 1) else None
            c = eye(px, 0, 0, 1, False) or None
            return c or quant(MOTH_FUZZ, 0.6)
        if mat == "head" and px.face in ("left", "right") and px.y == 0:
            return as_rgba("#0c1016")
        if mat == "abdomen":
            if px.face == "back" or (px.face != "front" and px.v > 0.75 and px.face in ("left", "right")):
                return quant(GLOW, 0.6)
            ring = (px.x if px.face in ("left", "right") else px.y) % 2 == 0
            return quant(MOTH_FUZZ, 0.45 + (0.15 if ring else 0) + px.light * 0.1)
        return FUZZ(px)

    def glow(px: Px):
        mat = px.cube.mat
        if mat in ("fore", "hind"):
            c = _wing(px, mat == "hind")
            return c if c is not None and c[:3] in [as_rgba(x)[:3] for x in GLOW] else None
        if mat == "abdomen" and (px.face == "back" or (px.face in ("left", "right") and px.v > 0.75)):
            return quant(GLOW, 0.6)
        if mat == "antenna" and px.face in ("left", "right") and px.y == 0:
            return quant(GLOW, 0.6)
        return None

    base, emissive = paint(r, painter, glow)
    return {"glowmoth": base, "glowmoth_glow": emissive}


def data(out) -> None:
    out.tr("entity.spore_and_stem.glowmoth", "Glowmoth")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [{"rolls": 1, "entries": [{"type": "minecraft:item", "name": "spore_and_stem:lumen_spores",
                                            "functions": [{"function": "minecraft:enchanted_count_increase",
                                                           "enchantment": "minecraft:looting",
                                                           "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]}],
        "random_sequence": "spore_and_stem:entities/glowmoth",
    })
