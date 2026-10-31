"""Shambler: the infected risen. A hunched figure of braided fibre under a broad cap that hides its face, with two
pale-green eyes glowing in the shadow, long dangling arms, a shelf-fungus bracket on one shoulder and a little
cluster of mushrooms sprouting from its back. It lurches: one leg drags, the arms swing late."""
from __future__ import annotations

from ..palette import MYCELIUM, MYCOSIS, SHELF, SHELF_GREY
from .anim import Anim
from .kit import SHAMBLER_CAP, SHAMBLER_SKIN, cap, clump, fibre, quant, spot_at, threads
from .paint import Px, as_rgba, paint
from .rig import Rig

NAME = "shambler"
CLASS = "Shambler"


def rig() -> Rig:
    r = Rig(NAME, (64, 64))
    for side, x in (("left", 2), ("right", -2)):
        r.root.child(f"{side}_leg", (x, -12, 0)).box(f"{side}_leg", (-1.5, 0, -1.5), (3, 12, 3), mat="skin")
    body = r.root.child("body", (0, -12, 0), rot=(10, 0, 0))
    body.box("torso", (-4, -11, -2), (8, 11, 4), mat="skin")
    body.box("shelf", (3, -10, -2.5), (4, 1, 4), mat="shelf")
    body.box("shelf_low", (3.5, -8, -1.5), (3, 1, 3), mat="shelf")
    back = body.child("back_shrooms", (0, -7, 2))
    back.box("back_stem_a", (0.5, -3, 0), (1, 3, 1), mat="cap_stem")
    back.box("back_cap_a", (-0.5, -4, -1), (3, 1, 3), mat="cap")
    back.box("back_stem_b", (-2.5, -1, 0), (1, 2, 1), mat="cap_stem")
    back.box("back_cap_b", (-3.5, -2, -1), (3, 1, 3), mat="cap")
    head = body.child("head", (0, -11, 0), rot=(-8, 0, 0))
    head.box("face", (-3, -6, -3), (6, 6, 6), mat="face")
    hat = head.child("hat", (0, -6, 0))
    hat.box("brim", (-6, -2, -6), (12, 2, 12), mat="cap")
    hat.box("dome", (-5, -4, -5), (10, 2, 10), mat="cap")
    hat.box("crown", (-3, -5, -3), (6, 1, 6), mat="cap")
    body.child("left_arm", (5, -10, 0), rot=(-8, 0, -4)).box("left_arm", (-1, -1, -1.5), (3, 14, 3), mat="skin")
    body.child("right_arm", (-5, -10, 0), rot=(-8, 0, 4)).box("right_arm", (-2, -1, -1.5), (3, 14, 3), mat="skin")
    return r


def anims() -> list[Anim]:
    idle = Anim("idle", 3.2, loop=True)
    idle.rot("body", (0, 0, 0, 0), (1.6, 2.5, 0, 0), (3.2, 0, 0, 0))
    idle.rot("head", (0, 0, 0, -3), (0.8, 2, 4, 0), (1.6, 0, 0, 3), (2.2, 0, -3, 0), (2.3, 6, 14, 2), (2.45, 0, -4, 0),
             (3.2, 0, 0, -3))
    idle.rot("hat", (0, 0, 0, 2), (1.6, -2, 0, -2), (3.2, 0, 0, 2))
    idle.rot("left_arm", (0, 0, 0, -2), (1.6, -6, 0, -4), (3.2, 0, 0, -2))
    idle.rot("right_arm", (0, -4, 0, 2), (1.6, 3, 0, 4), (3.2, -4, 0, 2))
    idle.rot("back_shrooms", (0, 0, 0, 0), (1.6, 5, 0, 3), (3.2, 0, 0, 0))

    # A lurch: the right leg strides, the left drags; the torso rolls and twists; the arms swing loose and late.
    walk = Anim("walk", 1.2, loop=True)
    walk.rot("left_leg", (0, -22, 0, 0), (0.35, 10, 0, 0), (0.6, 26, 0, 0), (0.95, -6, 0, 0), (1.2, -22, 0, 0))
    walk.rot("right_leg", (0, 26, 0, 0), (0.3, -10, 0, 0), (0.6, -30, 0, 0), (0.9, 6, 0, 0), (1.2, 26, 0, 0))
    walk.rot("body", (0, 4, -6, 5), (0.3, 7, 0, 0), (0.6, 4, 6, -5), (0.9, 7, 0, 0), (1.2, 4, -6, 5))
    walk.pos("body", (0, 0, 0, 0), (0.3, 0, -0.8, 0), (0.6, 0, 0, 0), (0.9, 0, -0.8, 0), (1.2, 0, 0, 0))
    walk.rot("left_arm", (0, 18, 0, -4), (0.35, 5, 0, -8), (0.7, -24, 0, -4), (1.0, -5, 0, -2), (1.2, 18, 0, -4))
    walk.rot("right_arm", (0, -24, 0, 4), (0.35, -5, 0, 8), (0.7, 20, 0, 4), (1.0, 5, 0, 2), (1.2, -24, 0, 4))
    walk.rot("head", (0, 0, 6, -4), (0.3, 4, 0, 0), (0.6, 0, -6, 4), (0.9, 4, 0, 0), (1.2, 0, 6, -4))
    walk.rot("hat", (0, 0, 0, 4), (0.6, 0, 0, -4), (1.2, 0, 0, 4))

    attack = Anim("attack", 0.75)
    for side, sign in (("left", 1), ("right", -1)):
        attack.rot(f"{side}_arm", (0, 0, 0, 0), (0.25, -160, 0, sign * -10), (0.32, -168, 0, sign * -12),
                   (0.42, -40, 0, sign * 6), (0.5, -20, 0, 0), (0.75, 0, 0, 0))
    attack.rot("body", (0, 0, 0, 0), (0.28, -12, 0, 0), (0.44, 18, 0, 0), (0.75, 0, 0, 0))
    attack.rot("head", (0, 0, 0, 0), (0.28, -10, 0, 0), (0.44, 12, 0, 0), (0.75, 0, 0, 0))
    attack.rot("hat", (0, 0, 0, 0), (0.3, -6, 0, 0), (0.48, 14, 0, 0), (0.62, -4, 0, 0), (0.75, 0, 0, 0))

    # Rising from the earth where the infected fell: it claws up, stands, and shakes the spores off.
    rise = Anim("rise", 1.8)
    for part in ("body", "left_leg", "right_leg"):
        rise.pos(part, (0, 0, -30, 0), (0.25, 0, -24, 0), (0.6, 0, -12, 0), (0.95, 0, -3, 0), (1.15, 0, 0.6, 0),
                 (1.3, 0, 0, 0), (1.8, 0, 0, 0))
    rise.rot("body", (0, 55, 0, 0), (0.6, 40, 0, 6), (0.95, 25, 0, -4), (1.2, 8, 0, 0), (1.45, 0, 0, 3), (1.6, 0, 0, -3),
             (1.8, 0, 0, 0))
    rise.rot("left_arm", (0, -170, 0, 0), (0.3, -150, 0, -10), (0.6, -110, 0, -20), (0.95, -60, 0, -10), (1.3, 0, 0, 0),
             (1.8, 0, 0, 0))
    rise.rot("right_arm", (0, -150, 0, 0), (0.35, -170, 0, 10), (0.7, -120, 0, 20), (1.0, -50, 0, 10), (1.35, 0, 0, 0),
             (1.8, 0, 0, 0))
    rise.rot("head", (0, -30, 0, 0), (0.95, -10, 0, 0), (1.45, 0, 14, 0), (1.6, 0, -14, 0), (1.8, 0, 0, 0))
    return [idle, walk, attack, rise]


# ---- textures ---------------------------------------------------------------------------------------------------

SKIN = threads(fibre(SHAMBLER_SKIN, seed=51, amount=0.38, base=0.45), seed=52, spacing=9.0, ramp=MYCELIUM[:3])
CAP = cap(SHAMBLER_CAP, MYCELIUM[2:], 0.35, seed=53, gill_ramp=MYCOSIS[:4])


def _skin(px: Px):
    """Braided dark fibre with a few winding white threads, and cushions of mycosis green on the shoulders."""
    if px.cube.name == "torso" and px.face in ("front", "back", "top", "left", "right") and px.v < 0.35:
        n = clump(px, 54, 2.5) + (0.35 - px.v)
        if n > 0.32:
            return quant(MYCOSIS[:4], 0.4 + (n - 0.32) * 2 + px.light * 0.1)
    return SKIN(px)


def _face(px: Px):
    """The face is lost in the cap's shadow; two eyes glow there."""
    if px.face == "front":
        if px.y in (2,) and px.x in (1, 4):
            return as_rgba("#d7f0bf")
        if px.y in (2, 3) and px.x in (1, 4):
            return as_rgba("#7fb069")
        return quant(SHAMBLER_SKIN, 0.05 + px.v * 0.25)
    return quant(SHAMBLER_SKIN, 0.18 + px.light * 0.08 + px.v * 0.15)


def _shelf(px: Px):
    if px.face == "top":
        ring = int(((px.x - px.w / 2) ** 2 + (px.y - px.h) ** 2) ** 0.5)
        return quant(SHELF if ring % 2 == 0 else SHELF_GREY, 0.45 + 0.1 * (ring % 3))
    return quant(SHELF, 0.3 + px.light * 0.1)


def textures(r: Rig) -> dict:
    def painter(px: Px):
        mat = px.cube.mat
        if mat == "cap":
            return CAP(px)
        if mat == "face":
            return _face(px)
        if mat == "shelf":
            return _shelf(px)
        if mat == "cap_stem":
            return quant(MYCELIUM, 0.55 + px.light * 0.1)
        return _skin(px)

    def glow(px: Px):
        if px.cube.mat == "face" and px.face == "front" and px.y in (2, 3) and px.x in (1, 4):
            return as_rgba("#d7f0bf") if px.y == 2 else as_rgba("#7fb069")
        return None

    base, emissive = paint(r, painter, glow)
    return {"shambler": base, "shambler_glow": emissive}


def data(out) -> None:
    out.tr("entity.spore_and_stem.shambler", "Shambler")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_thread",
                                      "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 0, "max": 2}},
                                                    {"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                                                     "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]},
            {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.5}],
             "entries": [{"type": "minecraft:item", "name": n} for n in
                         ("spore_and_stem:morel", "spore_and_stem:deathcap", "spore_and_stem:inkcap", "minecraft:brown_mushroom")]},
            {"rolls": 1, "conditions": [{"condition": "minecraft:killed_by_player"},
                                        {"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting",
                                         "unenchanted_chance": 0.05, "enchanted_chance": {"type": "minecraft:linear", "base": 0.06, "per_level_above_first": 0.01}}],
             "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_core"}]},
        ],
        "random_sequence": "spore_and_stem:entities/shambler",
    })
