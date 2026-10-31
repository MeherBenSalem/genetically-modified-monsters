"""Bloatshroom: a waddling puffball balloon with a pursed little face and a sprig of a cap. It swells when you get
close and bursts into a cloud of spores. The balloon is rounded from three crossing boxes around a core, and it
scales from its centre so it inflates evenly."""
from __future__ import annotations

from ..palette import DEATHCAP_CAP, MYCOSIS, PUFFBALL
from .anim import Anim
from .kit import cap, clump, eye, quant, spot_at, stem
from .paint import Px, as_rgba, dither, fbm, value_noise, paint
from .rig import Rig

NAME = "bloatshroom"
CLASS = "Bloatshroom"


def rig() -> Rig:
    r = Rig(NAME, (128, 64))
    for side, x in (("left", 2.5), ("right", -2.5)):
        r.root.child(f"{side}_leg", (x, -3, 0)).box(f"{side}_leg", (-1.5, 0, -1.5), (3, 3, 3), mat="leg")
    body = r.root.child("body", (0, -3, 0))
    puff = body.child("puff", (0, -6, 0))
    puff.box("core", (-5, -5, -5), (10, 10, 10), mat="puff")
    puff.box("bulge_x", (-6, -4, -4), (12, 8, 8), mat="puff")
    puff.box("bulge_z", (-4, -4, -6), (8, 8, 12), mat="puff")
    puff.box("bulge_y", (-4, -6, -4), (8, 12, 8), mat="puff")
    sprig = puff.child("sprig", (0, -6, 0))
    sprig.box("sprig_stem", (-1, -2, -1), (2, 2, 2), mat="stem")
    sprig.box("brim", (-3, -4, -3), (6, 2, 6), mat="cap")
    sprig.box("crown", (-2, -5, -2), (4, 1, 4), mat="cap")
    return r


def anims() -> list[Anim]:
    idle = Anim("idle", 2.0, loop=True)
    idle.scale("puff", (0, 1, 1, 1), (1.0, 1.04, 1.05, 1.04), (2.0, 1, 1, 1))
    idle.rot("sprig", (0, 0, 0, 4), (1.0, 3, 0, -3), (2.0, 0, 0, 4))

    walk = Anim("walk", 0.8, loop=True)
    walk.rot("left_leg", (0, -30, 0, 0), (0.4, 30, 0, 0), (0.8, -30, 0, 0))
    walk.rot("right_leg", (0, 30, 0, 0), (0.4, -30, 0, 0), (0.8, 30, 0, 0))
    walk.rot("body", (0, 0, 0, 6), (0.2, 2, 0, 0), (0.4, 0, 0, -6), (0.6, 2, 0, 0), (0.8, 0, 0, 6))
    walk.pos("body", (0, 0, 0, 0), (0.2, 0, 0.8, 0), (0.4, 0, 0, 0), (0.6, 0, 0.8, 0), (0.8, 0, 0, 0))
    walk.scale("puff", (0, 1.03, 0.97, 1.03), (0.2, 0.98, 1.03, 0.98), (0.4, 1.03, 0.97, 1.03), (0.6, 0.98, 1.03, 0.98),
               (0.8, 1.03, 0.97, 1.03))
    walk.rot("sprig", (0, 0, 0, -8), (0.2, 0, 0, 0), (0.4, 0, 0, 8), (0.6, 0, 0, 0), (0.8, 0, 0, -8))

    # Driven by the fuse progress (0..1), so it must read well at every instant.
    swell = Anim("swell", 1.5)
    keys = [(0.0, 1.0), (0.4, 1.1), (0.8, 1.22), (1.1, 1.33), (1.35, 1.42), (1.5, 1.55)]
    swell.scale("puff", *[(t, s, s * 1.02, s) for t, s in keys])
    swell.rot("body", (0, 0, 0, 0), (0.5, 0, 0, 2), (0.7, 0, 0, -2), (0.9, 0, 0, 3), (1.05, 0, 0, -3), (1.2, 0, 0, 4),
              (1.3, 0, 0, -4), (1.4, 0, 0, 4), (1.5, 0, 0, -3))
    swell.rot("sprig", (0, 0, 0, 0), (0.8, -12, 0, 0), (1.3, -20, 0, 8), (1.5, -28, 0, -10))
    swell.pos("sprig", (0, 0, 0, 0), (1.5, 0, 1.5, 0))
    swell.rot("left_leg", (0, 0, 0, 0), (1.5, 0, 0, -20))
    swell.rot("right_leg", (0, 0, 0, 0), (1.5, 0, 0, 20))
    return [idle, walk, swell]


# ---- textures ---------------------------------------------------------------------------------------------------

SPRIG_CAP = cap(DEATHCAP_CAP, MYCOSIS[2:], 0.3, seed=41, gill_ramp=MYCOSIS[1:4])


def _puff(px: Px):
    """Soft cream puffball skin: a smooth form gradient in clean steps, raised warts, a few olive spore pores."""
    if px.face == "top":
        value = 0.8 - ((px.u - 0.35) ** 2 + (px.v - 0.35) ** 2) * 1.1
    elif px.face == "bottom":
        value = 0.22
    else:
        value = 0.74 - px.v * 0.45 + px.light * 0.08
    value += clump(px, 43, 2.5) * 0.16
    if px.face != "bottom":
        if spot_at(px, 45, 0.18, 4) is not None and px.face != "front":
            return quant(MYCOSIS, 0.25)
        if spot_at(px, 44, 0.35, 3) is not None:
            return quant(PUFFBALL, value + 0.2)
    return quant(PUFFBALL, value)


def _face(px: Px):
    """On the front bulge (8x8): wide-set eyes and a small round pursed mouth, with a blush."""
    if px.cube.name != "bulge_z" or px.face != "front":
        return None
    for ex in (1, 5):
        c = eye(px, ex, 2, 2, True)
        if c:
            return c
    # Slanted brows: the inner ends dip, so it always looks a little cross.
    if (px.x, px.y) in ((1, 0), (2, 1), (6, 0), (5, 1)):
        return as_rgba("#4a3a2e")
    if px.x in (3, 4) and px.y in (5, 6):
        return as_rgba("#6b2f3a") if (px.x, px.y) != (3, 5) else as_rgba("#8d4450")
    if px.y == 4 and px.x in (0, 7):
        return as_rgba("#e6b0a6")
    return None


def textures(r: Rig) -> dict:
    stem_fn = stem(PUFFBALL, seed=46)

    def painter(px: Px):
        mat = px.cube.mat
        if mat == "cap":
            return SPRIG_CAP(px)
        if mat in ("stem", "leg"):
            c = stem_fn(px)
            return quant(PUFFBALL, 0.35 + px.light * 0.1) if mat == "leg" and px.face != "top" else c
        return _face(px) or _puff(px)

    base, _ = paint(r, painter)
    return {"bloatshroom": base}


def data(out) -> None:
    out.tr("entity.spore_and_stem.bloatshroom", "Bloatshroom")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [{
            "rolls": 1,
            "entries": [{"type": "minecraft:item", "name": "spore_and_stem:puffball",
                         "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 1, "max": 2}},
                                       {"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                                        "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}],
        }],
        "random_sequence": "spore_and_stem:entities/bloatshroom",
    })
