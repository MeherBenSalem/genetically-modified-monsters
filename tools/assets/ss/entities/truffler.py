"""Truffler: a stocky mossy boar with a pink snout, small upturned tusks, floppy ears, a curly tail and a little garden
of mushrooms growing in the moss on its back. It trots, sniffs the ground and now and then digs up a truffle."""
from __future__ import annotations

from ..palette import CHANTERELLE, MOREL, PUFFBALL
from .anim import Anim
from .kit import BOAR, BROWNCAP, MOSS, SNOUT, TUSK, cap, clump, eye, fuzz, quant, stem
from .paint import Px, as_rgba, paint
from .rig import Rig

NAME = "truffler"
CLASS = "Truffler"


def rig() -> Rig:
    r = Rig(NAME, (64, 64))
    for name, x, z in (("front_left", 3, -4), ("front_right", -3, -4), ("back_left", 3, 5), ("back_right", -3, 5)):
        r.root.child(f"{name}_leg", (x, -5, z)).box(f"{name}_leg", (-1.5, 0, -1.5), (3, 5, 3), mat="leg")
    body = r.root.child("body", (0, -5, 0))
    body.box("torso", (-5, -8, -7), (10, 8, 14), mat="hide")
    garden = body.child("garden", (0, -8, 0))
    garden.box("shroom_a_stem", (2, -2, -3), (1, 2, 1), mat="shroom_stem")
    garden.box("shroom_a_cap", (1, -3, -4), (3, 1, 3), mat="cap_brown")
    garden.box("shroom_b_stem", (-3, -3, 1), (1, 3, 1), mat="shroom_stem")
    garden.box("shroom_b_cap", (-4.5, -5, -0.5), (4, 2, 4), mat="cap_gold")
    garden.box("puff", (1, -2, 3), (2, 2, 2), mat="puff")
    head = body.child("head", (0, -5, -7))
    head.box("skull", (-4, -4, -6), (8, 7, 6), mat="hide")
    head.box("snout", (-2, 0, -8), (4, 3, 2), mat="snout")
    head.box("left_tusk", (2, -1, -7.5), (1, 2, 1), mat="tusk")
    head.box("right_tusk", (-3, -1, -7.5), (1, 2, 1), mat="tusk")
    head.child("left_ear", (3.5, -4, -3), rot=(0, 0, 35)).box("left_ear", (0, -1, -1), (1, 4, 2), mat="ear")
    head.child("right_ear", (-3.5, -4, -3), rot=(0, 0, -35)).box("right_ear", (-1, -1, -1), (1, 4, 2), mat="ear")
    body.child("tail", (0, -6, 7), rot=(-40, 0, 0)).box("tail", (-0.5, -0.5, 0), (1, 1, 3), mat="leg")
    return r


def anims() -> list[Anim]:
    walk = Anim("walk", 0.7, loop=True)
    for leg, phase in (("front_left", 0), ("back_right", 0), ("front_right", 1), ("back_left", 1)):
        a, b = (28, -28) if phase == 0 else (-28, 28)
        walk.rot(f"{leg}_leg", (0, a, 0, 0), (0.35, b, 0, 0), (0.7, a, 0, 0))
    walk.pos("body", (0, 0, 0, 0), (0.175, 0, 0.5, 0), (0.35, 0, 0, 0), (0.525, 0, 0.5, 0), (0.7, 0, 0, 0))
    walk.rot("head", (0, 4, 0, 0), (0.175, -2, 0, 0), (0.35, 4, 0, 0), (0.525, -2, 0, 0), (0.7, 4, 0, 0))
    walk.rot("left_ear", (0, 0, 0, -6), (0.35, 0, 0, 8), (0.7, 0, 0, -6))
    walk.rot("right_ear", (0, 0, 0, 6), (0.35, 0, 0, -8), (0.7, 0, 0, 6))
    walk.rot("garden", (0, 0, 0, 3), (0.35, 0, 0, -3), (0.7, 0, 0, 3))

    idle = Anim("idle", 4.0, loop=True)
    idle.scale("body", (0, 1, 1, 1), (2.0, 1.02, 1.03, 1.0), (4.0, 1, 1, 1))
    idle.rot("left_ear", (0, 0, 0, 0), (1.2, 0, 0, 0), (1.3, 0, 0, 25), (1.45, 0, 0, -5), (1.6, 0, 0, 0), (4.0, 0, 0, 0))
    idle.rot("right_ear", (0, 0, 0, 0), (2.8, 0, 0, 0), (2.9, 0, 0, -25), (3.05, 0, 0, 5), (3.2, 0, 0, 0), (4.0, 0, 0, 0))
    idle.rot("tail", (0, 0, -20, 0), (0.25, 0, 20, 0), (0.5, 0, -20, 0), (0.75, 0, 20, 0), (1.0, 0, 0, 0), (4.0, 0, 0, 0))
    idle.rot("head", (0, 0, 0, 0), (2.0, 3, 6, 0), (4.0, 0, 0, 0))

    sniff = Anim("sniff", 1.4)
    sniff.rot("head", (0, 0, 0, 0), (0.25, 32, 0, 0), (0.4, 30, 6, 0), (0.55, 32, -6, 0), (0.7, 30, 6, 0), (0.85, 32, -6, 0),
              (1.1, 28, 0, 0), (1.4, 0, 0, 0))
    sniff.pos("head", (0, 0, 0, 0), (0.4, 0, 0, 0), (0.48, 0, 0.3, -0.3), (0.56, 0, 0, 0), (0.64, 0, 0.3, -0.3),
              (0.72, 0, 0, 0), (1.4, 0, 0, 0))
    sniff.rot("body", (0, 0, 0, 0), (0.3, 6, 0, 0), (1.1, 6, 0, 0), (1.4, 0, 0, 0))
    sniff.rot("left_ear", (0, 0, 0, 0), (0.3, -20, 0, -10), (1.1, -20, 0, -10), (1.4, 0, 0, 0))
    sniff.rot("right_ear", (0, 0, 0, 0), (0.3, -20, 0, 10), (1.1, -20, 0, 10), (1.4, 0, 0, 0))

    dig = Anim("dig", 1.6)
    dig.rot("body", (0, 0, 0, 0), (0.2, 12, 0, 0), (1.3, 12, 0, 0), (1.6, 0, 0, 0))
    dig.rot("head", (0, 0, 0, 0), (0.2, 40, 0, 0), (0.35, 52, 0, -6), (0.5, 38, 0, 0), (0.65, 54, 0, 6), (0.8, 38, 0, 0),
            (0.95, 52, 0, -6), (1.1, 38, 0, 0), (1.3, 30, 0, 0), (1.6, 0, 0, 0))
    dig.rot("front_left_leg", (0, 0, 0, 0), (0.3, -40, 0, 0), (0.45, 10, 0, 0), (0.7, -40, 0, 0), (0.85, 10, 0, 0),
            (1.1, -30, 0, 0), (1.3, 0, 0, 0))
    dig.rot("front_right_leg", (0, 0, 0, 0), (0.4, 10, 0, 0), (0.55, -40, 0, 0), (0.8, 10, 0, 0), (0.95, -40, 0, 0),
            (1.2, 0, 0, 0))
    dig.rot("tail", (0, 0, 0, 0), (0.3, 0, 25, 0), (0.5, 0, -25, 0), (0.7, 0, 25, 0), (0.9, 0, -25, 0), (1.1, 0, 0, 0))
    return [walk, idle, sniff, dig]


# ---- textures ---------------------------------------------------------------------------------------------------

FUR = fuzz(BOAR, seed=91, base=0.45)
CAP_BROWN = cap(BROWNCAP, None, 0, seed=92, gloss=False)
CAP_GOLD = cap(CHANTERELLE, None, 0, seed=93, gloss=False)


def _hide(px: Px):
    """Bristly brown hide; a cushion of moss along the back and the top of the head."""
    if px.face == "top" or (px.face in ("left", "right", "back") and px.v < 0.3 and px.cube.name == "torso"):
        n = clump(px, 94, 2.2) + (0.3 - (px.v if px.face != "top" else 0.0))
        if px.cube.name == "skull":
            n -= 0.2 + px.v * 0.4   # only a tuft of moss at the back of the head
        if n > 0.05:
            return quant(MOSS, 0.35 + n * 1.3 + px.light * 0.1)
    if px.cube.name == "skull" and px.face == "front":
        for ex in (1, 6):
            c = eye(px, ex, 2, 1, False)
            if c:
                return c
        if px.y == 1 and px.x in (1, 6):
            return quant(BOAR, 0.1)   # brow
    return FUR(px)


def textures(r: Rig) -> dict:
    shroom_stem = stem(PUFFBALL, seed=95)

    def painter(px: Px):
        mat = px.cube.mat
        if mat == "hide":
            return _hide(px)
        if mat == "leg":
            return quant(BOAR, 0.3 + px.light * 0.1 - px.v * 0.15) if px.face != "bottom" else quant(BOAR, 0.05)
        if mat == "snout":
            if px.face == "front" and px.y == 1 and px.x in (1, 2):
                return quant(SNOUT, 0.0)      # nostrils
            return quant(SNOUT, 0.55 + px.light * 0.12)
        if mat == "tusk":
            return quant(TUSK, 0.8 - px.v * 0.5)
        if mat == "ear":
            return quant(SNOUT, 0.35) if px.face in ("right", "left") and px.cube.name == "left_ear" and px.face == "right" \
                else quant(BOAR, 0.4 + px.light * 0.1)
        if mat == "cap_brown":
            return CAP_BROWN(px)
        if mat == "cap_gold":
            return CAP_GOLD(px)
        if mat == "puff":
            return quant(PUFFBALL, 0.7 + px.light * 0.12)
        return shroom_stem(px)

    base, _ = paint(r, painter)
    return {"truffler": base}


def data(out) -> None:
    out.tr("entity.spore_and_stem.truffler", "Truffler")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "minecraft:porkchop", "functions": [
                {"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 3}},
                {"function": "minecraft:furnace_smelt", "conditions": [{"condition": "minecraft:entity_properties", "entity": "this",
                                                                         "predicate": {"flags": {"is_on_fire": True}}}]},
                {"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                 "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]},
            {"rolls": 1, "conditions": [{"condition": "minecraft:random_chance", "chance": 0.4}],
             "entries": [{"type": "minecraft:item", "name": "spore_and_stem:morel"}]},
        ],
        "random_sequence": "spore_and_stem:entities/truffler",
    })
