"""Sporeling: a little walking mushroom. A plump stem body with two dot eyes, stubby arms and feet, and a big
three-tier cap that lags behind every move. Four cap variants: glowcap (glows), bouncecap, inkcap and chanterelle."""
from __future__ import annotations

from ..palette import (BOUNCECAP_CAP, BOUNCECAP_SPOT, BOUNCECAP_STEM, CHANTERELLE, GLOW, GLOWCAP_CAP, GLOWCAP_RIM,
                       GLOWCAP_STEM, INK, INKCAP_CAP, INKCAP_STEM, SPORE)
from .anim import Anim
from .kit import cap, eye, quant, stem, streak
from .paint import Px, as_rgba, dither, paint, value_noise
from .rig import Rig

NAME = "sporeling"
CLASS = "Sporeling"
VARIANTS = ("glowcap", "bouncecap", "inkcap", "chanterelle")


def rig() -> Rig:
    r = Rig(NAME, (64, 32))
    for side, x in (("left", 1.6), ("right", -1.6)):
        r.root.child(f"{side}_foot", (x, -2, 0)).box(f"{side}_foot", (-1, 0, -1.5), (2, 2, 3), mat="foot")
    body = r.root.child("body", (0, -2, 0))
    body.box("torso", (-3, -4, -2.5), (6, 4, 5), mat="torso")
    body.child("left_arm", (3, -3.5, 0)).box("left_arm", (0, 0, -0.5), (1, 2, 1), mat="foot")
    body.child("right_arm", (-3, -3.5, 0)).box("right_arm", (-1, 0, -0.5), (1, 2, 1), mat="foot")
    c = body.child("cap", (0, -4, 0))
    c.box("brim", (-5, -2, -5), (10, 2, 10), mat="cap")
    c.box("dome", (-4, -4, -4), (8, 2, 8), mat="cap")
    c.box("crown", (-2, -5, -2), (4, 1, 4), mat="cap")
    return r


def anims() -> list[Anim]:
    idle = Anim("idle", 2.4, loop=True)
    idle.scale("body", (0, 1, 1, 1), (1.2, 1.03, 0.97, 1.03), (2.4, 1, 1, 1))
    idle.rot("cap", (0, 0, 0, 2), (0.6, 1, 0, 0), (1.2, 0, 0, -2), (1.8, -1, 0, 0), (2.4, 0, 0, 2))
    idle.pos("cap", (0, 0, 0, 0), (1.2, 0, 0.3, 0), (2.4, 0, 0, 0))
    idle.rot("left_arm", (0, 0, 0, -4), (1.2, 0, 0, -10), (2.4, 0, 0, -4))
    idle.rot("right_arm", (0, 0, 0, 4), (1.2, 0, 0, 10), (2.4, 0, 0, 4))

    walk = Anim("walk", 0.6, loop=True)
    walk.rot("left_foot", (0, -35, 0, 0), (0.3, 35, 0, 0), (0.6, -35, 0, 0))
    walk.rot("right_foot", (0, 35, 0, 0), (0.3, -35, 0, 0), (0.6, 35, 0, 0))
    walk.rot("body", (0, 0, 0, 7), (0.15, 3, 0, 0), (0.3, 0, 0, -7), (0.45, 3, 0, 0), (0.6, 0, 0, 7))
    walk.pos("body", (0, 0, 0, 0), (0.15, 0, 0.7, 0), (0.3, 0, 0, 0), (0.45, 0, 0.7, 0), (0.6, 0, 0, 0))
    # The cap lags a quarter cycle behind the body's roll.
    walk.rot("cap", (0, 4, 0, -2), (0.15, 6, 0, 5), (0.3, 4, 0, 2), (0.45, 6, 0, -5), (0.6, 4, 0, -2))
    walk.rot("left_arm", (0, 30, 0, -8), (0.3, -30, 0, -8), (0.6, 30, 0, -8))
    walk.rot("right_arm", (0, -30, 0, 8), (0.3, 30, 0, 8), (0.6, -30, 0, 8))

    sneeze = Anim("sneeze", 1.3)
    sneeze.rot("body", (0, 0, 0, 0), (0.45, -10, 0, 0), (0.55, -12, 0, 0), (0.62, 16, 0, 0), (0.85, -3, 0, 0), (1.3, 0, 0, 0))
    sneeze.scale("body", (0, 1, 1, 1), (0.5, 1.08, 1.06, 1.08), (0.62, 0.94, 0.95, 0.94), (0.9, 1.02, 1.0, 1.02), (1.3, 1, 1, 1))
    sneeze.rot("cap", (0, 0, 0, 0), (0.5, -14, 0, 0), (0.64, 12, 0, 0), (0.8, -6, 0, 0), (1.0, 3, 0, 0), (1.3, 0, 0, 0))
    sneeze.pos("cap", (0, 0, 0, 0), (0.5, 0, 0.4, 0), (0.64, 0, 1.2, 0), (0.85, 0, 0, 0), (1.3, 0, 0, 0))
    sneeze.rot("left_arm", (0, 0, 0, 0), (0.5, -40, 0, -20), (0.65, 20, 0, 0), (1.3, 0, 0, 0))
    sneeze.rot("right_arm", (0, 0, 0, 0), (0.5, -40, 0, 20), (0.65, 20, 0, 0), (1.3, 0, 0, 0))

    happy = Anim("happy", 1.1)
    for part in ("body", "left_foot", "right_foot"):
        happy.pos(part, (0, 0, 0, 0), (0.15, 0, 2.6, 0), (0.3, 0, 0, 0), (0.45, 0, 2.6, 0), (0.6, 0, 0, 0), (1.1, 0, 0, 0))
    happy.rot("left_arm", (0, 0, 0, 0), (0.12, 0, 0, -130), (0.3, 0, 0, -100), (0.45, 0, 0, -140), (0.8, 0, 0, -60), (1.1, 0, 0, 0))
    happy.rot("right_arm", (0, 0, 0, 0), (0.12, 0, 0, 130), (0.3, 0, 0, 100), (0.45, 0, 0, 140), (0.8, 0, 0, 60), (1.1, 0, 0, 0))
    happy.rot("cap", (0, 0, 0, 0), (0.15, -10, 0, 0), (0.3, 8, 0, 0), (0.45, -10, 0, 0), (0.6, 8, 0, 0), (0.8, -3, 0, 0), (1.1, 0, 0, 0))
    happy.rot("body", (0, 0, 0, 0), (0.6, 0, 360, 0, "linear"), (1.1, 0, 360, 0))

    sit = Anim("sit", 2.4, loop=True)
    sit.pos("body", (0, 0, -1.0, 0), (2.4, 0, -1.0, 0))
    sit.scale("body", (0, 1.04, 0.96, 1.04), (1.2, 1.07, 0.94, 1.07), (2.4, 1.04, 0.96, 1.04))
    for side in ("left", "right"):
        sit.rot(f"{side}_foot", (0, -80, 0, 0), (2.4, -80, 0, 0))
        sit.pos(f"{side}_foot", (0, 0, -0.2, -1.5), (2.4, 0, -0.2, -1.5))
    sit.rot("cap", (0, -8, 0, 0), (1.2, -6, 0, 1), (2.4, -8, 0, 0))
    sit.rot("left_arm", (0, -25, 0, -6), (2.4, -25, 0, -6))
    sit.rot("right_arm", (0, -25, 0, 6), (2.4, -25, 0, 6))
    return [idle, walk, sneeze, happy, sit]


# ---- textures ---------------------------------------------------------------------------------------------------

def _inkcap_cap(px: Px):
    """Shaggy white bell that turns to ink at the fringe."""
    base = cap(INKCAP_CAP, None, 0, seed=21, gloss=False, gill_ramp=INK, tiers=TIERS)
    c = base(px)
    if px.face in ("front", "back", "left", "right") and px.cube.name == "brim" and px.y == px.h - 1:
        return quant(INK, 0.35 + (px.x % 3 == 0) * 0.3)
    if px.face in ("front", "back", "left", "right") and streak(px, 23, True, 1.0, 3.0) > 0.22:
        return quant(INKCAP_CAP, 0.3)   # shaggy fibres hanging down the bell
    return c


TIERS = {"crown": 0.1, "dome": 0.04, "brim": -0.06}
CAPS = {
    "glowcap": cap(GLOWCAP_CAP, GLOWCAP_RIM, 0.5, seed=11, gill_ramp=GLOW, tiers=TIERS),
    "bouncecap": cap(BOUNCECAP_CAP, BOUNCECAP_SPOT, 0.7, seed=12, gill_ramp=BOUNCECAP_STEM, tiers=TIERS),
    "inkcap": _inkcap_cap,
    "chanterelle": cap(CHANTERELLE, None, 0, seed=14, gill_ramp=CHANTERELLE[1:], tiers=TIERS),
}
STEMS = {"glowcap": GLOWCAP_STEM, "bouncecap": BOUNCECAP_STEM, "inkcap": INKCAP_STEM, "chanterelle": SPORE + ["#fffaf0"]}


def _face(px: Px, ramp):
    """Two glossy dot eyes and soft cheeks on the torso front."""
    if px.cube.name != "torso" or px.face != "front":
        return None
    for ex in (1, 4):
        c = eye(px, ex, 0, 1, False)
        if c and px.y == 0:
            return c
        if px.x == ex and px.y == 1:
            return as_rgba("#2a1f2a")
    if px.y == 2 and px.x in (0, 5):
        return as_rgba("#e5a3a0")
    return None


def textures(r: Rig) -> dict:
    out = {}
    for variant in VARIANTS:
        stem_ramp = STEMS[variant]
        torso = stem(stem_ramp, seed=31)
        foot = stem(stem_ramp, seed=32)
        cap_fn = CAPS[variant]

        def painter(px: Px, cap_fn=cap_fn, torso=torso, foot=foot, stem_ramp=stem_ramp):
            if px.cube.mat == "cap":
                return cap_fn(px)
            face = _face(px, stem_ramp)
            if face:
                return face
            if px.cube.mat == "foot":
                return quant(stem_ramp, 0.35 + px.light * 0.1) if px.face != "top" else foot(px)
            # The top of the torso sits in the cap's shadow.
            if px.face in ("front", "back", "left", "right") and px.y == 0:
                return quant(stem_ramp, 0.2)
            return torso(px)

        glow = None
        if variant == "glowcap":
            def glow(px: Px):
                if px.cube.mat != "cap":
                    return None
                if px.face == "bottom":
                    return quant(GLOW, 0.45)
                c = cap_fn(px)
                # Spots and the rim glow.
                if c[:3] in [as_rgba(x)[:3] for x in GLOWCAP_RIM]:
                    return quant(GLOW, 0.5)
                if px.face != "top" and px.y == px.h - 1 and px.cube.name == "brim" and px.x % 2 == 0:
                    return quant(GLOW, 0.05)
                return None
        base, emissive = paint(r, painter, glow)
        out[f"sporeling_{variant}"] = base
        if emissive is not None:
            out[f"sporeling_{variant}_glow"] = emissive
    return out


def data(out) -> None:
    out.tr("entity.spore_and_stem.sporeling", "Sporeling")
    # A Sporeling drops one mushroom of its own variant, rolled in SporelingEntity (variants are not visible to loot
    # predicates). The table stays so datapacks can add to it.
    out.loot_table("entities", NAME, {"type": "minecraft:entity", "pools": [],
                                      "random_sequence": "spore_and_stem:entities/sporeling"})
