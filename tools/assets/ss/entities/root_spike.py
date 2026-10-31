"""Root Spike: a cluster of sharp roots that bursts out of the ground (the Myceliarch's Root Eruption and Slam),
hits at tick 6 and sinks back. 64×32 texture with a glowing vein up each root and glowing tips."""
from __future__ import annotations

from ..palette import DIRT, GLOW, MYCELIUM, ROOT
from .anim import Anim
from .paint import Px, paint, value_noise
from .rig import Rig

NAME = "root_spike"
CLASS = "RootSpike"


def rig() -> Rig:
    r = Rig(NAME, (64, 32))
    spikes = r.root.child("spikes", (0, 0, 0))
    spikes.box("main", (-2, -14, -2), (4, 14, 4), mat="root")
    spikes.box("main_tip", (-1, -19, -1), (2, 5, 2), mat="tip")
    a = spikes.child("side_a", (2, 0, 1), rot=(0, 0, -24))
    a.box("side_a", (-1.5, -10, -1.5), (3, 10, 3), mat="root")
    a.box("side_a_tip", (-0.5, -13, -0.5), (1, 3, 1), mat="tip")
    b = spikes.child("side_b", (-2, 0, -1.5), rot=(20, 0, 20))
    b.box("side_b", (-1.5, -8, -1.5), (3, 8, 3), mat="root")
    b.box("side_b_tip", (-0.5, -11, -0.5), (1, 3, 1), mat="tip")
    c = spikes.child("side_c", (-1, 0, 2.5), rot=(-26, 0, 6))
    c.box("side_c", (-1, -7, -1), (2, 7, 2), mat="root")
    clods = r.root.child("clods", (0, 0, 0))
    clods.box("clod_a", (-5, -2, -4), (5, 2, 4), mat="clod")
    clods.box("clod_b", (1, -1.5, -3), (4, 2, 5), mat="clod")
    clods.box("clod_c", (-3, -1.5, 1.5), (5, 2, 3), mat="clod")
    return r


def _pick(ramp, value):
    return ramp[max(0, min(len(ramp) - 1, int(value * len(ramp))))]


def _vein(px: Px) -> bool:
    return px.cube.mat == "root" and px.face not in ("top", "bottom") and px.x == px.w // 2 and px.y % 5 in (1, 2)


def _paint(px: Px):
    if px.cube.mat == "clod":
        if px.face == "top" and (px.x + 2 * px.y) % 5 == 0:
            return MYCELIUM[2]   # threads of mycelium torn up with the soil
        return _pick(DIRT, 0.4 + px.light * 0.3)
    if px.cube.mat == "tip":
        return MYCELIUM[2] if px.face == "top" or px.v < 0.4 else ROOT[3]
    if _vein(px):
        return GLOW[1]
    t = 0.5 + px.light * 0.25 + (1 - px.v) * 0.15 + (value_noise(px.x, px.y * 0.15, 5, 1.0) - 0.5) * 0.25
    return _pick(ROOT[0:4], t)


def _glow(px: Px):
    if _vein(px):
        return GLOW[2]
    if px.cube.mat == "tip" and (px.face == "top" or px.v < 0.4):
        return GLOW[1]
    return None


def textures(r: Rig) -> dict:
    base, glow = paint(r, _paint, _glow)
    return {"root_spike": base, "root_spike_glow": glow}


def anims() -> list[Anim]:
    # 22 ticks: bursts up with an overshoot, hits at tick 6, holds, then sinks back into the earth.
    a = Anim("erupt", 1.1)
    a.pos("spikes", (0.0, 0, -21, 0), (0.12, 0, 3, 0, "linear"), (0.22, 0, -0.5, 0), (0.3, 0, 0, 0),
          (0.8, 0, 0, 0), (1.1, 0, -22, 0))
    a.rot("spikes", (0.0, 0, 0, 0), (0.12, 4, 12, -3), (0.3, 0, 8, 0), (0.8, 0, 8, 0), (1.1, -6, 20, 4))
    a.rot("side_a", (0.0, 0, 0, 14), (0.15, 0, 0, -10), (0.3, 0, 0, 0), (1.1, 0, 0, 10))
    a.rot("side_b", (0.0, -12, 0, 0), (0.15, 8, 0, 0), (0.3, 0, 0, 0), (1.1, -10, 0, 0))
    a.scale("clods", (0.0, 0.2, 0.2, 0.2), (0.12, 1.25, 1.6, 1.25, "linear"), (0.25, 1.0, 1.0, 1.0),
            (0.85, 1.0, 1.0, 1.0), (1.1, 0.3, 0.3, 0.3))
    a.pos("clods", (0.0, 0, 0, 0), (0.12, 0, 1.5, 0), (0.25, 0, 0, 0), (1.1, 0, -1, 0))
    return [a]


def data(out) -> None:
    out.tr("entity.spore_and_stem.root_spike", "Root Spike")
