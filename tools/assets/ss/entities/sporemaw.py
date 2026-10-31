"""Sporemaw: an ambush fungus. A fleshy stalk with root tendrils splayed on the ground, crowned by a broad violet
hood whose fanged front rim lifts back to bare a glowing pink maw. It lies burrowed with only the hood's crown
showing, rises when you come near, lobs spore globs, and sinks away to resurface somewhere else."""
from __future__ import annotations

from .anim import Anim
from .kit import MAW_GLOW, SPOREMAW_CAP, SPOREMAW_FLESH, TUSK, cap, eye, fibre, quant, streak
from .paint import Px, as_rgba, paint
from .rig import Rig

NAME = "sporemaw"
CLASS = "Sporemaw"
SUNK = 17  # how far the body sinks when burrowed (only the hood's crown stays above ground)


def rig() -> Rig:
    r = Rig(NAME, (128, 64))
    roots = r.root.child("roots", (0, 0, 0))
    roots.box("root_n", (-1, -1, -9), (2, 1, 6), mat="root")
    roots.box("root_s", (-1, -1, 3), (2, 1, 6), mat="root")
    roots.box("root_e", (3, -1, -1), (6, 1, 2), mat="root")
    roots.box("root_w", (-9, -1, -1), (6, 1, 2), mat="root")
    body = r.root.child("body", (0, 0, 0))
    body.box("base", (-4, -4, -4), (8, 4, 8), mat="flesh")
    body.box("stalk", (-3, -12, -3), (6, 8, 6), mat="flesh")
    head = body.child("head", (0, -12, 0))
    head.box("maw", (-3.5, -3, -3.5), (7, 3, 7), mat="maw")
    hood = head.child("hood", (0, -3, 3))
    hood.box("hood_brim", (-7, -3, -10), (14, 3, 14), mat="cap")
    hood.box("dome", (-5.5, -5, -8.5), (11, 2, 11), mat="cap")
    hood.box("crown", (-3, -6, -6), (6, 1, 6), mat="cap")
    for i, x in enumerate((-5, -2, 1, 4)):
        z = -9.5 if i in (0, 3) else -10
        hood.box(f"fang_{i}", (x, 0, z), (1, 2, 1), mat="fang")
    return r


def anims() -> list[Anim]:
    idle = Anim("idle", 2.4, loop=True)
    idle.rot("body", (0, 0, 0, -3), (1.2, 2, 0, 3), (2.4, 0, 0, -3))
    idle.rot("head", (0, 2, 0, 0), (1.2, -2, 4, 0), (2.4, 2, 0, 0))
    idle.rot("hood", (0, 0, 0, 0), (0.9, -7, 0, 0), (1.3, -9, 0, 0), (2.0, -1, 0, 0), (2.4, 0, 0, 0))
    idle.scale("base", (0, 1, 1, 1), (1.2, 1.05, 0.96, 1.05), (2.4, 1, 1, 1))

    burrowed = Anim("burrowed", 3.0, loop=True)
    burrowed.pos("body", (0, 0, -SUNK, 0), (1.5, 0, -SUNK + 0.4, 0), (3.0, 0, -SUNK, 0))
    burrowed.rot("hood", (0, 0, 0, 0), (1.5, -3, 0, 0), (3.0, 0, 0, 0))
    burrowed.scale("roots", (0, 0.6, 1, 0.6), (3.0, 0.6, 1, 0.6))

    emerge = Anim("emerge", 1.0)
    emerge.pos("body", (0, 0, -SUNK, 0), (0.15, 0, -SUNK + 1, 0), (0.55, 0, -2, 0), (0.75, 0, 1.2, 0), (0.88, 0, -0.4, 0),
               (1.0, 0, 0, 0))
    emerge.rot("body", (0, 0, 0, 0), (0.3, 0, 0, 8), (0.5, 0, 0, -8), (0.7, 0, 0, 5), (0.85, 0, 0, -2), (1.0, 0, 0, 0))
    emerge.rot("hood", (0, 0, 0, 0), (0.7, 0, 0, 0), (0.8, -30, 0, 0), (1.0, 0, 0, 0))
    emerge.scale("roots", (0, 0.6, 1, 0.6), (0.6, 1.1, 1, 1.1), (1.0, 1, 1, 1))

    burrow = Anim("burrow", 0.8)
    burrow.pos("body", (0, 0, 0, 0), (0.15, 0, 1, 0), (0.6, 0, -SUNK + 1, 0), (0.8, 0, -SUNK, 0))
    burrow.rot("body", (0, 0, 0, 0), (0.2, 0, 0, -6), (0.4, 0, 0, 6), (0.6, 0, 0, -3), (0.8, 0, 0, 0))
    burrow.scale("roots", (0, 1, 1, 1), (0.8, 0.6, 1, 0.6))

    # The glob leaves at 0.35 s, at the bottom of the lunge.
    spit = Anim("spit", 0.75)
    spit.rot("body", (0, 0, 0, 0), (0.22, -14, 0, 0), (0.36, 16, 0, 0), (0.5, -4, 0, 0), (0.75, 0, 0, 0))
    spit.rot("head", (0, 0, 0, 0), (0.22, -10, 0, 0), (0.36, 12, 0, 0), (0.75, 0, 0, 0))
    spit.rot("hood", (0, 0, 0, 0), (0.18, -38, 0, 0), (0.3, -46, 0, 0), (0.42, -10, 0, 0), (0.55, -18, 0, 0), (0.75, 0, 0, 0))
    spit.scale("stalk", (0, 1, 1, 1), (0.22, 1.12, 0.92, 1.12), (0.36, 0.9, 1.1, 0.9), (0.75, 1, 1, 1))
    return [idle, burrowed, emerge, burrow, spit]


# ---- textures ---------------------------------------------------------------------------------------------------

CAP = cap(SPOREMAW_CAP, MAW_GLOW[1:4], 0.4, seed=61, gill_ramp=SPOREMAW_FLESH[:4],
          tiers={"crown": 0.1, "dome": 0.04, "hood_brim": -0.05})
FLESH = fibre(SPOREMAW_FLESH, seed=62, amount=0.32, base=0.48)


def _maw(px: Px):
    if px.face == "top":
        # Rings of glowing spore sacs around a dark throat.
        r = ((px.u - 0.5) ** 2 + (px.v - 0.5) ** 2) ** 0.5
        if r < 0.18:
            return as_rgba("#2a0f22")
        return quant(MAW_GLOW, 0.75 - r * 0.6 if (int(r * 10) % 2 == 0) else 0.45 - r * 0.3)
    return quant(SPOREMAW_FLESH, 0.35 + px.light * 0.1)


def _root(px: Px):
    return quant(SPOREMAW_FLESH, 0.25 + px.light * 0.1 + streak(px, 63, False) * 0.3)


def _hood(px: Px):
    # The front of the brim carries a row of small dark eyes above the fangs.
    if px.cube.name == "hood_brim" and px.face == "front":
        for ex in (3, 6, 7, 10):
            c = eye(px, ex, 1, 1, False, "#1a0a16")
            if c:
                return as_rgba("#ffc2de") if ex in (6, 7) else c
    return CAP(px)


def textures(r: Rig) -> dict:
    def painter(px: Px):
        mat = px.cube.mat
        if mat == "cap":
            return _hood(px)
        if mat == "maw":
            return _maw(px)
        if mat == "fang":
            return quant(TUSK, 0.75 - px.v * 0.5 + px.light * 0.1)
        if mat == "root":
            return _root(px)
        return FLESH(px)

    def glow(px: Px):
        if px.cube.mat == "maw" and px.face == "top":
            c = _maw(px)
            return c if c[:3] != (0x2a, 0x0f, 0x22) else None
        if px.cube.mat == "cap" and px.face == "bottom":
            return quant(MAW_GLOW, 0.2)
        if px.cube.name == "hood_brim" and px.face == "front" and px.y == 1 and px.x in (6, 7):
            return as_rgba("#ffc2de")
        return None

    base, emissive = paint(r, painter, glow)
    return {"sporemaw": base, "sporemaw_glow": emissive}


def data(out) -> None:
    out.tr("entity.spore_and_stem.sporemaw", "Sporemaw")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_thread",
                                      "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 2}},
                                                    {"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                                                     "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]},
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "spore_and_stem:deathcap",
                                      "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]},
            {"rolls": 1, "conditions": [{"condition": "minecraft:killed_by_player"},
                                        {"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting",
                                         "unenchanted_chance": 0.04, "enchanted_chance": {"type": "minecraft:linear", "base": 0.05, "per_level_above_first": 0.01}}],
             "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_core"}]},
        ],
        "random_sequence": "spore_and_stem:entities/sporemaw",
    })
