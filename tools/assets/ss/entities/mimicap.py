"""Mimicap: it looks exactly like a big toadstool (red with white spots, or brown) until you are close enough. Then
the cap lifts, six jointed legs unfold from underneath, two mandibles flare, and a row of ember eyes lights up on the
stem. It scuttles on a tripod gait, bites, and settles back into its disguise when it loses you."""
from __future__ import annotations

from ..palette import EMBER, PUFFBALL
from .anim import Anim
from .kit import AMANITA, BROWNCAP, CHITIN, cap, quant, stem
from .paint import Px, as_rgba, paint
from .rig import Rig

NAME = "mimicap"
CLASS = "Mimicap"
LEGS = (("front", -2.2, -30), ("mid", 0.0, 0), ("back", 2.2, 30))   # name, z, splay (degrees)
TIERS = {"crown": 0.1, "dome": 0.04, "brim": -0.05}


def rig() -> Rig:
    r = Rig(NAME, (128, 64))
    body = r.root.child("body", (0, -5, 0))
    body.box("stem", (-3, -4, -3), (6, 5, 6), mat="stem")
    c = body.child("cap", (0, -4, 0))
    c.box("brim", (-7, -2, -7), (14, 2, 14), mat="cap")
    c.box("dome", (-6, -4, -6), (12, 2, 12), mat="cap")
    c.box("crown", (-4, -5, -4), (8, 1, 8), mat="cap")
    for side, sign in (("left", 1), ("right", -1)):
        body.child(f"{side}_fang", (sign * 1.5, 0, -3), rot=(0, 0, sign * 10)).box(f"{side}_fang", (-0.5, 0, -0.5), (1, 3, 1),
                                                                                  mat="fang")
        for name, z, splay in LEGS:
            upper = body.child(f"{side}_{name}_leg", (sign * 3, -1, z), rot=(0, sign * splay, sign * -25))
            upper.box(f"{side}_{name}_upper", (0 if sign > 0 else -6, -0.5, -0.5), (6, 1, 1), mat="leg")
            lower = upper.child(f"{side}_{name}_shin", (sign * 6, 0, 0), rot=(0, 0, sign * 60))
            lower.box(f"{side}_{name}_lower", (-0.5, 0, -0.5), (1, 8, 1), mat="leg")
    return r


def _legs(anim: Anim, t: float, upper=None, shin=None, groups=None):
    """Sets every leg's offsets at time t. upper/shin: (x, y, z) degrees, mirrored for the right side."""
    for side, sign in (("left", 1), ("right", -1)):
        for name, _, _ in LEGS:
            u = (groups or {}).get((side, name), upper) if groups else upper
            if u is not None:
                anim.rot(f"{side}_{name}_leg", (t, u[0], u[1] * sign, u[2] * sign))
            if shin is not None:
                anim.rot(f"{side}_{name}_shin", (t, shin[0], shin[1] * sign, shin[2] * sign))


def _leg_scale(anim: Anim, *keys):
    """Legs draw in under the cap in disguise (scaled toward the hip), and stretch out as it wakes."""
    for side in ("left", "right"):
        for name, _, _ in LEGS:
            anim.scale(f"{side}_{name}_leg", *[(t, v, v, v) for t, v in keys])


def anims() -> list[Anim]:
    # Disguised: body down so the stem stands on the ground, legs folded flat under the cap.
    hidden = Anim("hidden", 3.0, loop=True)
    hidden.pos("body", (0, 0, -4, 0), (1.5, 0, -3.85, 0), (3.0, 0, -4, 0))
    for t in (0.0, 3.0):
        _legs(hidden, t, upper=(0, 0, 40), shin=(0, 0, 75))
    _leg_scale(hidden, (0.0, 0.4), (3.0, 0.4))
    hidden.rot("left_fang", (0, 0, 0, -20), (3.0, 0, 0, -20))
    hidden.rot("right_fang", (0, 0, 0, 20), (3.0, 0, 0, 20))

    wake = Anim("wake", 0.8)
    wake.pos("body", (0, 0, -4, 0), (0.15, 0, -4.2, 0), (0.45, 0, 1.2, 0), (0.6, 0, -0.4, 0), (0.8, 0, 0, 0))
    _legs(wake, 0.0, upper=(0, 0, 40), shin=(0, 0, 75))
    _legs(wake, 0.25, upper=(0, 0, 25), shin=(0, 0, 40))
    _legs(wake, 0.45, upper=(0, 0, -10), shin=(0, 0, -10))
    _legs(wake, 0.6, upper=(0, 0, 5), shin=(0, 0, -5))
    _legs(wake, 0.8, upper=(0, 0, 0), shin=(0, 0, 0))
    _leg_scale(wake, (0.0, 0.4), (0.2, 0.55), (0.45, 1.05), (0.6, 1.0), (0.8, 1.0))
    wake.rot("cap", (0, 0, 0, 0), (0.3, 0, 0, 0), (0.45, -14, 0, 0), (0.62, 6, 0, 0), (0.8, 0, 0, 0))
    wake.rot("left_fang", (0, 0, 0, -20), (0.5, 0, 0, 25), (0.65, 0, 0, -5), (0.8, 0, 0, 0))
    wake.rot("right_fang", (0, 0, 0, 20), (0.5, 0, 0, -25), (0.65, 0, 0, 5), (0.8, 0, 0, 0))

    settle = Anim("settle", 1.0)
    settle.pos("body", (0, 0, 0, 0), (0.3, 0, 0.6, 0), (0.85, 0, -4.2, 0), (1.0, 0, -4, 0))
    _legs(settle, 0.0, upper=(0, 0, 0), shin=(0, 0, 0))
    _legs(settle, 0.4, upper=(0, 0, 20), shin=(0, 0, 30))
    _legs(settle, 0.85, upper=(0, 0, 40), shin=(0, 0, 75))
    _legs(settle, 1.0, upper=(0, 0, 40), shin=(0, 0, 75))
    _leg_scale(settle, (0.0, 1.0), (0.4, 0.9), (0.85, 0.4), (1.0, 0.4))
    settle.rot("left_fang", (0, 0, 0, 0), (1.0, 0, 0, -20))
    settle.rot("right_fang", (0, 0, 0, 0), (1.0, 0, 0, 20))

    # Tripod gait: left-front, right-mid, left-back step together, then the other three.
    walk = Anim("walk", 0.5, loop=True)
    a = {("left", "front"), ("right", "mid"), ("left", "back")}
    for t, phase in ((0.0, 0), (0.125, 1), (0.25, 2), (0.375, 3), (0.5, 0)):
        for side, sign in (("left", 1), ("right", -1)):
            for name, _, _ in LEGS:
                p = phase if (side, name) in a else (phase + 2) % 4
                swing = (22, 0, -22, 0)[p]
                lift = (0, -14, 0, 0)[p]
                walk.rot(f"{side}_{name}_leg", (t, 0, swing * sign, lift * sign))
    walk.pos("body", (0, 0, 0, 0), (0.125, 0, 0.5, 0), (0.25, 0, 0, 0), (0.375, 0, 0.5, 0), (0.5, 0, 0, 0))
    walk.rot("cap", (0, 0, 0, 3), (0.25, 0, 0, -3), (0.5, 0, 0, 3))

    idle = Anim("idle", 1.6, loop=True)
    idle.rot("left_fang", (0, 0, 0, 0), (0.4, 0, 0, 14), (0.55, 0, 0, 0), (1.6, 0, 0, 0))
    idle.rot("right_fang", (0, 0, 0, 0), (0.4, 0, 0, -14), (0.55, 0, 0, 0), (1.6, 0, 0, 0))
    idle.pos("body", (0, 0, 0, 0), (0.8, 0, 0.3, 0), (1.6, 0, 0, 0))
    idle.rot("left_front_leg", (0, 0, 0, 0), (1.0, 0, 0, 0), (1.1, 0, -8, -10), (1.25, 0, 0, 0), (1.6, 0, 0, 0))

    bite = Anim("bite", 0.5)
    bite.rot("body", (0, 0, 0, 0), (0.12, -14, 0, 0), (0.24, 18, 0, 0), (0.5, 0, 0, 0))
    bite.pos("body", (0, 0, 0, 0), (0.12, 0, 0.5, 1.0), (0.24, 0, -0.5, -2.0), (0.5, 0, 0, 0))
    bite.rot("left_fang", (0, 0, 0, 0), (0.14, 0, 0, 35), (0.24, 0, 0, -12), (0.5, 0, 0, 0))
    bite.rot("right_fang", (0, 0, 0, 0), (0.14, 0, 0, -35), (0.24, 0, 0, 12), (0.5, 0, 0, 0))
    bite.rot("cap", (0, 0, 0, 0), (0.12, 8, 0, 0), (0.26, -10, 0, 0), (0.5, 0, 0, 0))
    return [hidden, wake, settle, walk, idle, bite]


# ---- textures ---------------------------------------------------------------------------------------------------

CAPS = {
    "red": cap(AMANITA, PUFFBALL[3:], 0.55, seed=71, gill_ramp=PUFFBALL[1:4], tiers=TIERS),
    "brown": cap(BROWNCAP, None, 0.0, seed=72, gill_ramp=PUFFBALL[1:4], tiers=TIERS),
}
STEM = stem(PUFFBALL, seed=73)
EYES = (0, 2, 3, 5)


def _stem(px: Px):
    if px.cube.name == "stem" and px.face == "front" and px.y == 1 and px.x in EYES:
        return as_rgba("#3a1712")      # eye slits (lit by the glow layer when awake)
    if px.face in ("front", "back", "left", "right") and px.y == 0:
        return quant(PUFFBALL, 0.15)    # shadow under the cap
    return STEM(px)


def textures(r: Rig) -> dict:
    out = {}
    for variant, cap_fn in CAPS.items():
        def painter(px: Px, cap_fn=cap_fn):
            mat = px.cube.mat
            if mat == "cap":
                return cap_fn(px)
            if mat == "leg":
                return quant(CHITIN, 0.45 + px.light * 0.12 - px.v * 0.2)
            if mat == "fang":
                return quant(CHITIN, 0.9 - px.v * 0.6)
            return _stem(px)
        base, _ = paint(r, painter)
        out[f"mimicap_{variant}"] = base

    def glow(px: Px):
        if px.cube.name == "stem" and px.face == "front" and px.y == 1 and px.x in EYES:
            return quant(EMBER, 0.85 if px.x in (2, 3) else 0.65)
        return None
    _, emissive = paint(r, lambda px: None, glow)
    out["mimicap_glow"] = emissive
    return out


def data(out) -> None:
    out.tr("entity.spore_and_stem.mimicap", "Mimicap")
    out.loot_table("entities", NAME, {
        "type": "minecraft:entity",
        "pools": [
            {"rolls": 1, "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_thread",
                                      "functions": [{"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": 0, "max": 2}},
                                                    {"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                                                     "count": {"type": "minecraft:uniform", "min": 0, "max": 1}}]}]},
            {"rolls": 1, "conditions": [{"condition": "minecraft:killed_by_player"},
                                        {"condition": "minecraft:random_chance_with_enchanted_bonus", "enchantment": "minecraft:looting",
                                         "unenchanted_chance": 0.08, "enchanted_chance": {"type": "minecraft:linear", "base": 0.09, "per_level_above_first": 0.01}}],
             "entries": [{"type": "minecraft:item", "name": "spore_and_stem:mycelial_core"}]},
        ],
        "random_sequence": "spore_and_stem:entities/mimicap",
    })
