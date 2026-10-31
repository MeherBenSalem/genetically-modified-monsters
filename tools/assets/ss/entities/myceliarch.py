"""The Myceliarch: the ruler of the mycelium. A towering walker of braided stems under a vast glowing cap, with root
legs, long root-clawed arms, shelf fungus on its shoulders and mycelial threads hanging from its rim.

Texture: 256×256 base, plus two emissive layers (``_glow`` for the first bloom, ``_bloom_glow`` for the second,
where the veins and gills burn brighter). Animation names match MyceliarchEntity's states.
"""
from __future__ import annotations

import math

from ..palette import BARK, GLOW, GLOWCAP_CAP, GLOWCAP_RIM, MYCELIUM, ROOT, SHELF
from .anim import Anim
from .paint import Px, mix, paint, value_noise
from .rig import Rig

NAME = "myceliarch"
CLASS = "Myceliarch"

CAP_FIN_COUNT = 6
THREADS = [  # (x, z, yaw, length)
    (-15.0, -9.0, 20.0, 9), (-6.0, -16.5, -10.0, 11), (8.0, -15.5, 15.0, 8),
    (16.0, -4.0, 70.0, 10), (13.0, 11.0, 30.0, 9), (-12.0, 13.0, -35.0, 10),
]


# ---------------------------------------------------------------------------------------------------- geometry

def rig() -> Rig:
    r = Rig(NAME, (256, 256))
    body = r.root.child("body", (0, -25, 0))
    body.box("hips", (-7.5, -4, -5.5), (15, 7, 11), mat="knot")
    body.box("hip_wrap", (-6.5, -1, -6.5), (13, 2, 13), mat="thread_band")

    for side, sx in (("left", 1), ("right", -1)):
        thigh = body.child(f"{side}_thigh", (5.5 * sx, 0, 0))
        thigh.box(f"{side}_thigh", (-3.5, -1, -3.5), (7, 12, 7), mat="root")
        thigh.box(f"{side}_knee", (-3, 8, -4.5), (6, 4, 2), mat="knot")
        shin = thigh.child(f"{side}_shin", (0, 11, 0))
        shin.box(f"{side}_shin", (-3, -1, -3), (6, 11, 6), mat="root")
        foot = shin.child(f"{side}_foot", (0, 10, 0))
        foot.box(f"{side}_foot", (-4, 0, -6), (8, 4, 10), mat="root")
        foot.box(f"{side}_toe_a", (-4.5 * sx - (2 if sx < 0 else 0), 2, -9.5), (2, 2, 4), mat="claw")
        foot.box(f"{side}_toe_b", (-1, 2, -10.5), (2, 2, 5), mat="claw")
        foot.box(f"{side}_toe_c", (2.5 * sx - (2 if sx < 0 else 0), 2, -9.5), (2, 2, 4), mat="claw")
        foot.box(f"{side}_heel", (-1, 2, 3.5), (2, 2, 3), mat="claw")

    torso = body.child("torso", (0, -3, 0), rot=(6, 0, 0))
    torso.box("waist", (-5, -9, -4.5), (10, 10, 9), mat="bark")
    torso.box("chest", (-8.5, -19, -6), (17, 11, 12), mat="bark")
    torso.box("collar", (-6, -21, -4.5), (12, 3, 9), mat="knot")
    for name, pivot, rz, depth in (("braid_a", (-3, -1, -5), 13, -1.6), ("braid_b", (3, -1, -5), -13, -1.6),
                                   ("braid_c", (0, -1, 5), 9, -0.4)):
        b = torso.child(name, pivot, rot=(0, 0, rz))
        b.box(name, (-1.5, -18, depth), (3, 18, 2), mat="braid")
    shelf_back = torso.child("shelf_back", (0, -11, 6))
    shelf_back.box("shelf_back_a", (-5, 0, 0), (10, 2, 5), mat="shelf")
    shelf_back.box("shelf_back_b", (-3, 4, 0), (7, 2, 4), mat="shelf")

    for side, sx in (("left", 1), ("right", -1)):
        shelf = torso.child(f"shelf_{side}", (8.0 * sx, -18, 0), rot=(0, 0, -14 * sx))
        shelf.box(f"shelf_{side}_a", (0 if sx > 0 else -7, -1, -5.5), (7, 2, 11), mat="shelf")
        shelf.box(f"shelf_{side}_b", (0 if sx > 0 else -5, 3, -4), (5, 2, 8), mat="shelf")
        arm = torso.child(f"{side}_arm", (11.5 * sx, -16, 0), rot=(0, 0, -13 * sx))
        arm.box(f"{side}_upper_arm", (-3, -2, -3), (6, 15, 6), mat="bark")
        arm.box(f"{side}_elbow", (-3.5, 10, -3.5), (7, 3, 7), mat="thread_band")
        fore = arm.child(f"{side}_forearm", (0, 13, 0), rot=(-8, 0, 0))
        fore.box(f"{side}_forearm", (-3.5, 0, -3.5), (7, 14, 7), mat="bark")
        fore.box(f"{side}_wrist", (-4, 10, -4), (8, 4, 8), mat="knot")
        hand = fore.child(f"{side}_hand", (0, 14, 0))
        hand.box(f"{side}_palm", (-4, 0, -4), (8, 4, 8), mat="root")
        for claw, (cx, cz, rx, rz) in (("a", (-2.5, -2.5, -22, 16)), ("b", (2.5, -2.5, -22, -16)), ("c", (0, 2.5, 26, 0))):
            c = hand.child(f"{side}_claw_{claw}", (cx * sx, 3, cz), rot=(rx, 0, rz * sx))
            c.box(f"{side}_claw_{claw}", (-1, 0, -1), (2, 8, 2), mat="claw")

    neck = torso.child("neck", (0, -20, -0.5))
    neck.box("neck", (-3.5, -5, -3.5), (7, 6, 7), mat="bark")
    head = neck.child("head", (0, -5, -0.5))
    head.box("face", (-4.5, -6, -5), (9, 7, 9), mat="face")
    head.box("brow", (-5, -7, -5.5), (10, 2, 3), mat="knot")

    cap = head.child("cap", (0, -6, 0))
    cap.box("cap_main", (-20, -3, -20), (40, 3, 40), mat="cap")
    cap.box("cap_upper", (-16, -5, -16), (32, 2, 32), mat="cap")
    cap.box("cap_crown", (-11, -7, -11), (22, 2, 22), mat="cap")
    cap.box("cap_dome", (-6, -9, -6), (12, 2, 12), mat="cap")
    cap.box("cap_umbo", (-3, -11, -3), (6, 2, 6), mat="cap")
    for i, (sx, sz, base, h) in enumerate(((7, 6, -7, 3), (-13, 4, -5, 2), (3, -13, -5, 2), (-4, 9, -7, 2))):
        cap.box(f"sprout_stem_{i}", (sx, base - h, sz), (1, h, 1), mat="sprout_stem")
        cap.box(f"sprout_cap_{i}", (sx - 1, base - h - 1, sz - 1), (3, 1, 3), mat="sprout_cap")
    for name, pivot, yaw in (("rim_n", (0, 0, -18), 0), ("rim_s", (0, 0, 18), 180),
                             ("rim_e", (18, 0, 0), -90), ("rim_w", (-18, 0, 0), 90)):
        rim = cap.child(name, pivot, rot=(-16, yaw, 0))
        rim.box(name, (-19, -0.5, -2), (38, 3, 2), mat="rim")
    for i in range(CAP_FIN_COUNT):
        fin = cap.child(f"gill_{i}", (0, 0, 0), rot=(0, i * 180.0 / CAP_FIN_COUNT, 0))
        fin.box(f"gill_{i}", (-0.5, 0, -17), (1, 2, 34), mat="gill")
    for i, (x, z, yaw, length) in enumerate(THREADS):
        t = cap.child(f"thread_{i}", (x, 0, z), rot=(0, yaw, 0))
        t.box(f"thread_{i}", (-1.5, 0, 0), (3, length, 0), mat="thread")
    return r


# ---------------------------------------------------------------------------------------------------- painting
#
# Structure over noise: every material picks a few ramp steps from smooth fields (fibres stretched along the
# limbs, a soft radial gradient on the cap, concentric bands on the shelves) instead of dithering, and lets the
# face lighting do the shading.

def xyz(px: Px) -> tuple[float, float, float]:
    """The bone-space position of a texel's centre (see rig.py for the face orientations)."""
    ox, oy, oz = px.cube.origin
    w, h, d = px.cube.size
    x, y = px.x + 0.5, px.y + 0.5
    return {
        "top": (ox + x, oy, oz + d - y),
        "bottom": (ox + x, oy + h, oz + d - y),
        "front": (ox + x, oy + y, oz),
        "back": (ox + w - x, oy + y, oz + d),
        "right": (ox, oy + y, oz + d - x),
        "left": (ox + w, oy + y, oz + x),
    }[px.face]


def pick(ramp: list, value: float):
    """The ramp step at value 0..1 (no dithering)."""
    i = max(0, min(len(ramp) - 1, int(value * len(ramp))))
    return ramp[i]


def around(px: Px) -> float:
    """A coordinate running around a limb (continuous from face to face), for fibres that wrap without seams."""
    X, Y, Z = xyz(px)
    return {"front": X, "left": 10 + Z, "back": 20 - X, "right": 30 - Z}.get(px.face, X + Z)


# Spots on the cap: (x, z, radius). A few large pale scales, the inner ones glow faintly.
CAP_SPOTS = [(-4.5, -5.0, 1.6), (6.0, -3.0, 1.3), (1.0, 7.5, 1.5), (-9.0, 4.0, 1.2), (12.5, -9.0, 1.5),
             (-14.0, -11.0, 1.4), (15.0, 8.0, 1.3), (-6.0, 15.5, 1.4), (8.0, 15.0, 1.1), (-17.0, 2.0, 1.2),
             (3.0, -15.5, 1.4), (-1.5, -1.0, 1.0)]


def _spot(X: float, Z: float) -> float:
    """0..1 how deep inside a spot the point is (0 = outside)."""
    best = 0.0
    for sx, sz, sr in CAP_SPOTS:
        d = math.hypot(X - sx, Z - sz)
        if d < sr:
            best = max(best, 1.0 - d / sr)
    return best


def _cap(px: Px):
    X, Y, Z = xyz(px)
    r = math.hypot(X, Z)
    if px.face == "bottom":
        return _gills(px, X, Z, r)
    if px.face == "top":
        # A soft radial gradient: bright, almost glowing, at the umbo, deepening towards the margin.
        drift = (value_noise(X, Z, 7, 9.0) - 0.5) * 0.12
        t = 0.92 - r / 24.0 + drift
        if _spot(X, Z) > 0:
            return GLOWCAP_RIM[0] if _spot(X, Z) < 0.45 else GLOWCAP_RIM[1]
        return pick(GLOWCAP_CAP[1:5], t)
    # Sides of the tiers: a darker band with a pale lip on the bottom edge.
    if px.y == px.h - 1:
        return GLOWCAP_RIM[0]
    return pick(GLOWCAP_CAP[1:4], 0.45 + px.light * 0.25)


def _gills(px: Px, X: float, Z: float, r: float):
    if r < 4.5:
        return BARK[1]
    ang = math.atan2(Z, X)
    line = math.sin(ang * 28.0) > 0.35
    return GLOWCAP_CAP[2] if line else GLOWCAP_CAP[0]


def _gill_glow(px: Px, X: float, Z: float, r: float, bloom: bool):
    if r < 4.5:
        return None
    ang = math.atan2(Z, X)
    if math.sin(ang * 28.0) <= 0.35:
        return None
    if bloom:
        return GLOW[3] if r > 8 else GLOW[2]
    return GLOW[2] if r > 9 else GLOW[1]


def _fibres(px: Px, ramp: list, seed: int, grooves: float = 0.8):
    """Vertical fibres stretched along the limb, with a few darker grooves; 3-4 ramp steps."""
    X, Y, Z = xyz(px)
    s = around(px)
    t = 0.56 + px.light * 0.22
    t += (value_noise(s * 1.0, Y * 0.12, seed, 1.0) - 0.5) * 0.3
    if px.face in ("top", "bottom"):
        return pick(ramp[1:4], 0.5 + px.light * 0.25)
    if value_noise(s * 1.0, Y * 0.06, seed + 1, 1.0) > grooves:
        t -= 0.3
    return pick(ramp[0:4], t)


def _bark(px: Px):
    c = _fibres(px, BARK, 11)
    X, Y, Z = xyz(px)
    if px.face not in ("top", "bottom") and value_noise(around(px) * 1.0, Y * 0.1, 15, 1.0) > 0.9:
        c = MYCELIUM[1]   # a stray mycelial thread running along the stem
    return c


def _braid(px: Px):
    # A plaited strand: diagonal ridges with a lit upper edge.
    if px.face in ("top", "bottom"):
        return BARK[2]
    k = (px.y + px.x * 2) % 5
    return BARK[3] if k == 0 else BARK[1] if k == 4 else BARK[2]


def _root(px: Px):
    c = _fibres(px, ROOT, 19, grooves=0.74)
    X, Y, Z = xyz(px)
    if px.face not in ("top", "bottom") and int(Y) % 7 == 0 and value_noise(around(px), Y, 23, 2.0) > 0.55:
        c = ROOT[0]   # knotted growth rings
    return c


def _vein(px: Px, bloom: bool) -> bool:
    """A few continuous glowing veins running up the larger stems (more, and branching, in the second bloom)."""
    if px.face in ("top", "bottom") or px.h < 9 or px.w < 4:
        return False
    import zlib
    seed = zlib.crc32(f"{px.cube.name}/{px.face}".encode())
    count = (1 if px.w < 10 else 2) + (1 if bloom else 0)
    for i in range(count):
        col = 1 + (seed >> (i * 5)) % max(1, px.w - 2)
        phase = ((seed >> (i * 7 + 3)) % 100) / 16.0
        x = col + round(math.sin(px.y * 0.55 + phase) * 1.2)
        start = (seed >> (i * 3 + 11)) % 4
        if px.x == x and px.y >= start and (px.y + i) % 9 != 8:
            return True
        if bloom and px.y % 6 == 3 and px.x == x + (1 if i % 2 else -1):
            return True
    return False


def _eye(px: Px):
    # Two narrow, slanted eye-slits glowing in the shade of the cap (the face is 9 wide).
    slits = {(1, 2): "outer", (2, 2): "inner", (3, 2): "core", (2, 3): "outer",
             (7, 2): "outer", (6, 2): "inner", (5, 2): "core", (6, 3): "outer"}
    return slits.get((px.x, px.y))


def _face(px: Px):
    if px.face == "front":
        eye = _eye(px)
        if eye is not None:
            return GLOW[3] if eye == "core" else GLOW[2] if eye == "inner" else GLOW[0]
    # Deep in the shade of the cap: the two darkest bark steps.
    return pick(BARK[0:2], 0.5 + px.light * 0.3 - (0.3 if px.y < 2 else 0.0))


def _face_glow(px: Px, bloom: bool):
    if px.face != "front":
        return None
    eye = _eye(px)
    if eye is not None:
        return GLOW[4] if eye == "core" else GLOW[3] if eye == "inner" else GLOW[1]
    if bloom and px.x in (2, 6) and 4 <= px.y <= 5:
        return GLOW[1]   # the second bloom cracks the face with light
    return None


def _shelf(px: Px):
    X, Y, Z = xyz(px)
    if px.face == "bottom":
        return SHELF[5] if (px.x + px.y) % 4 else SHELF[4]   # pale pores
    # Turkey-tail: concentric bands out from the trunk.
    dist = abs(X) * 0.9 + abs(Z) * 0.25 if px.face == "top" else px.y + px.x * 0.25
    band = int(dist * 0.9) % 5
    c = SHELF[[1, 3, 2, 4, 2][band]]
    if px.face not in ("top",):
        c = SHELF[[1, 2, 1, 3, 1][band]]
    return c


def _claw(px: Px):
    # Dark root fading to a pale, bone-like tip.
    if px.cube.name.endswith(("toe_a", "toe_b", "toe_c", "heel")):
        return pick([ROOT[1], ROOT[2], MYCELIUM[1]], 0.25 + px.light * 0.4)
    if px.face == "bottom":
        return MYCELIUM[2]
    v = px.v + px.light * 0.15
    return ROOT[1] if v < 0.45 else ROOT[3] if v < 0.75 else MYCELIUM[1]


def _thread(px: Px):
    # Two thin strands of hanging mycelium of uneven length, each ending in a glowing bead.
    import zlib
    seed = zlib.crc32(px.cube.name.encode())
    lengths = {0: px.h - 1 - seed % 3, 2: px.h - 1 - (seed >> 3) % 4}
    end = lengths.get(px.x)
    if end is None or px.y > end or (px.y % 5 == 3 and px.x == 2):
        return None
    return "tip" if px.y >= end - 1 else "strand"


def _knot(px: Px):
    X, Y, Z = xyz(px)
    swirl = math.sin(math.hypot(X * 1.2, Y) * 1.3 + math.atan2(Y, X + 0.01) * 2.0)
    t = 0.45 + px.light * 0.22 + swirl * 0.18
    return pick(ROOT[0:4], t)


def _band(px: Px):
    # Mycelium wound round a joint: slightly slanted threads with bark showing between them.
    if px.face in ("top", "bottom"):
        return BARK[1]
    k = (px.y * 2 + int(around(px)) // 3) % 4
    if k == 3:
        return BARK[1]
    return MYCELIUM[3] if (k == 0 and px.light >= 0) else MYCELIUM[2] if k != 2 else MYCELIUM[1]


def base_painter(px: Px):
    m = px.cube.mat
    if m == "cap":
        return _cap(px)
    if m == "rim":
        if px.face == "back":
            return GLOWCAP_CAP[2] if px.x % 2 else GLOWCAP_CAP[0]   # gill edges on the inside
        if px.face == "bottom":
            return GLOWCAP_RIM[0]
        if px.y == px.h - 1:
            return GLOWCAP_RIM[0]
        return pick(GLOWCAP_CAP[1:4], 0.4 + px.light * 0.25 - px.v * 0.15)
    if m == "gill":
        return GLOWCAP_CAP[0] if px.y == px.h - 1 else GLOWCAP_CAP[1]
    if m == "bark":
        return _bark(px)
    if m == "braid":
        return _braid(px)
    if m == "root":
        return _root(px)
    if m == "knot":
        return _knot(px)
    if m == "thread_band":
        return _band(px)
    if m == "claw":
        return _claw(px)
    if m == "shelf":
        return _shelf(px)
    if m == "face":
        return _face(px)
    if m == "thread":
        kind = _thread(px)
        if kind is None:
            return None
        return GLOW[1] if kind == "tip" else (MYCELIUM[2] if px.v < 0.5 else MYCELIUM[1])
    if m == "sprout_stem":
        return MYCELIUM[2]
    if m == "sprout_cap":
        return GLOWCAP_CAP[4] if px.face == "top" else GLOWCAP_CAP[2]
    raise ValueError(m)


def glow_painter(bloom: bool):
    def glow(px: Px):
        m = px.cube.mat
        if m == "cap":
            X, Y, Z = xyz(px)
            r = math.hypot(X, Z)
            if px.face == "bottom":
                return _gill_glow(px, X, Z, r, bloom)
            if px.face == "top" and _spot(X, Z) >= 0.45 and (bloom or r < 12):
                return GLOW[1]   # the inner spots glow faintly
            return None
        if m == "rim" and px.face == "back":
            return (GLOW[2] if bloom else GLOW[1]) if px.x % 2 else None
        if m == "gill":
            return (GLOW[3] if bloom else GLOW[2]) if px.y < px.h - 1 else GLOW[1]
        if m == "face":
            return _face_glow(px, bloom)
        if m == "thread":
            return (GLOW[3] if bloom else GLOW[2]) if _thread(px) == "tip" else None
        if m == "sprout_cap" and px.face == "bottom":
            return GLOW[2]
        if (m in ("bark", "braid") or (m == "root" and bloom)) and _vein(px, bloom):
            return GLOW[2] if bloom else GLOW[1]
        return None
    return glow


def textures(r: Rig) -> dict:
    base, glow = paint(r, base_painter, glow_painter(False))
    _, bloom = paint(r, lambda px: None, glow_painter(True))
    return {"myceliarch": base, "myceliarch_glow": glow, "myceliarch_bloom_glow": bloom}


# ---------------------------------------------------------------------------------------------------- animation

def idle() -> Anim:
    a = Anim("idle", 4.0, loop=True)
    a.wave("torso", "rot", 0, 1.6, 4.0, base=0.0)
    a.wave("body", "pos", 1, 0.45, 4.0, phase=0.25)
    a.wave("left_arm", "rot", 2, 2.2, 4.0, phase=0.1)
    a.wave("right_arm", "rot", 2, -2.2, 4.0, phase=0.35)
    a.wave("left_forearm", "rot", 0, 3.0, 4.0, phase=0.3)
    a.wave("right_forearm", "rot", 0, 3.0, 4.0, phase=0.6)
    for side, ph in (("left", 0.0), ("right", 0.5)):
        for claw in "ab":
            a.wave(f"{side}_claw_{claw}", "rot", 0, 7.0, 2.0, phase=ph)
    a.wave("head", "rot", 1, 6.0, 4.0, phase=0.15)
    a.wave("cap", "rot", 2, 1.8, 4.0, phase=0.4)
    a.wave("cap", "rot", 0, 1.2, 4.0, phase=0.65)
    for i, rim in enumerate(("rim_n", "rim_e", "rim_s", "rim_w")):
        a.wave(rim, "rot", 0, 4.0, 2.0, phase=i * 0.25)
    for i in range(CAP_FIN_COUNT):
        a.wave(f"gill_{i}", "rot", 2, 2.0, 2.0, phase=i / CAP_FIN_COUNT)
    for i in range(len(THREADS)):
        a.wave(f"thread_{i}", "rot", 0, 10.0, 2.0, phase=i * 0.17)
        a.wave(f"thread_{i}", "rot", 2, 6.0, 4.0, phase=i * 0.29)
    return a


def walk() -> Anim:
    L = 1.6
    a = Anim("walk", L, loop=True)
    for side, off in (("left", 0.0), ("right", L / 2)):
        def k(t):
            return (t + off) % L
        thigh = [(0.0, -24), (0.4, -6), (0.8, 22), (1.2, 2), (1.6, -24)]
        shin = [(0.0, 6), (0.4, 2), (0.8, 10), (1.2, 42), (1.6, 6)]
        foot = [(0.0, 18), (0.4, 4), (0.8, -30), (1.2, -38), (1.6, 18)]
        for bone, keys in ((f"{side}_thigh", thigh), (f"{side}_shin", shin), (f"{side}_foot", foot)):
            # Shift the cycle by the leg's phase, then close the loop at both ends.
            pts = sorted({round(k(t), 4): v for t, v in keys}.items())
            seq = [(t, v, 0, 0) for t, v in pts]
            if seq[0][0] > 0:
                seq.insert(0, (0.0, *seq[-1][1:]))
            if seq[-1][0] < L:
                seq.append((L, *seq[0][1:]))
            a.rot(bone, *seq)
    # The body drops onto each planted foot and rolls over it.
    a.pos("body", (0.0, 0, -1.6, 0), (0.2, 0, -1.0, 0), (0.4, 0, 0.6, 0), (0.6, 0, -0.4, 0), (0.8, 0, -1.6, 0),
          (1.0, 0, -1.0, 0), (1.2, 0, 0.6, 0), (1.4, 0, -0.4, 0), (1.6, 0, -1.6, 0))
    a.rot("body", (0.0, 0, 0, -3.5), (0.4, 0, 0, 0), (0.8, 0, 0, 3.5), (1.2, 0, 0, 0), (1.6, 0, 0, -3.5))
    a.rot("torso", (0.0, 0, 5, 2), (0.4, 1.5, 0, 0), (0.8, 0, -5, -2), (1.2, 1.5, 0, 0), (1.6, 0, 5, 2))
    # Arms swing against the legs; forearms and claws trail behind.
    a.rot("left_arm", (0.0, 18, 0, 0), (0.8, -20, 0, 0), (1.6, 18, 0, 0))
    a.rot("right_arm", (0.0, -20, 0, 0), (0.8, 18, 0, 0), (1.6, -20, 0, 0))
    a.rot("left_forearm", (0.0, -4, 0, 0), (0.2, 6, 0, 0), (1.0, -14, 0, 0), (1.6, -4, 0, 0))
    a.rot("right_forearm", (0.0, -14, 0, 0), (0.2, -16, 0, 0), (1.0, 6, 0, 0), (1.6, -14, 0, 0))
    a.rot("head", (0.0, 3, 0, 0), (0.4, -2, 0, 0), (0.8, 3, 0, 0), (1.2, -2, 0, 0), (1.6, 3, 0, 0))
    # The cap lags each step and the rims flap.
    a.rot("cap", (0.0, -3, 0, 2), (0.2, -4, 0, 1), (0.6, 2, 0, -1), (0.8, -3, 0, -2), (1.0, -4, 0, -1),
          (1.4, 2, 0, 1), (1.6, -3, 0, 2))
    for i, rim in enumerate(("rim_n", "rim_e", "rim_s", "rim_w")):
        a.wave(rim, "rot", 0, 7.0, L / 2, phase=0.2 + i * 0.12)
    for i in range(len(THREADS)):
        a.wave(f"thread_{i}", "rot", 0, 16.0, L / 2, phase=0.3 + i * 0.1)
    return a


def emerge() -> Anim:
    # 0-3.0 s: underground while roots and spores rise; 3.0-5.4 s: it hauls itself out.
    a = Anim("emerge", 5.4)
    a.pos("body", (0.0, 0, -86, 0), (2.9, 0, -86, 0), (3.0, 0, -84, 0, "linear"), (3.5, 0, -52, 0), (3.7, 0, -55, 0),
          (4.2, 0, -20, 0), (4.4, 0, -23, 0), (4.85, 0, 1.2, 0), (5.05, 0, -0.6, 0), (5.4, 0, 0, 0))
    a.rot("body", (0.0, 0, 0, 0), (3.0, 0, 0, 4), (3.6, 0, 0, -5), (4.3, 0, 0, 4), (4.9, 0, 0, -1), (5.4, 0, 0, 0))
    a.rot("torso", (0.0, 35, 0, 0), (3.0, 35, 0, 0), (3.6, 24, 0, 0), (4.3, 28, 0, 0), (4.85, -14, 0, 0),
          (5.1, -18, 0, 0), (5.4, 0, 0, 0))
    a.rot("left_arm", (0.0, -165, 0, -15), (3.0, -165, 0, -15), (3.55, -55, 0, -25), (3.9, -170, 0, -10),
          (4.3, -60, 0, -30), (4.85, 30, 0, -40), (5.15, 20, 0, -45), (5.4, 0, 0, 0))
    a.rot("right_arm", (0.0, -150, 0, 20), (3.0, -150, 0, 20), (3.3, -172, 0, 12), (3.75, -55, 0, 28),
          (4.15, -165, 0, 12), (4.55, -60, 0, 30), (4.85, 30, 0, 40), (5.15, 20, 0, 45), (5.4, 0, 0, 0))
    a.rot("left_forearm", (0.0, -30, 0, 0), (3.55, -10, 0, 0), (4.3, -10, 0, 0), (4.85, -30, 0, 0), (5.4, 0, 0, 0))
    a.rot("right_forearm", (0.0, -30, 0, 0), (3.75, -10, 0, 0), (4.55, -10, 0, 0), (4.85, -30, 0, 0), (5.4, 0, 0, 0))
    a.rot("head", (0.0, 20, 0, 0), (4.4, 20, 0, 0), (4.9, -28, 0, 0), (5.15, -30, 0, 0), (5.4, 0, 0, 0))
    a.scale("cap", (0.0, 0.55, 0.8, 0.55), (3.0, 0.55, 0.8, 0.55), (4.4, 0.75, 0.9, 0.75), (4.85, 1.12, 1.05, 1.12),
            (5.1, 0.96, 1.0, 0.96), (5.4, 1.0, 1.0, 1.0))
    for rim in ("rim_n", "rim_e", "rim_s", "rim_w"):
        a.rot(rim, (0.0, 70, 0, 0), (4.4, 60, 0, 0), (4.85, -25, 0, 0), (5.1, 8, 0, 0), (5.4, 0, 0, 0))
    for side in ("left", "right"):
        a.rot(f"{side}_thigh", (0.0, -40, 0, 0), (4.4, -40, 0, 0), (4.85, -10, 0, 0), (5.4, 0, 0, 0))
        a.rot(f"{side}_shin", (0.0, 60, 0, 0), (4.4, 60, 0, 0), (4.85, 12, 0, 0), (5.4, 0, 0, 0))
    return a


def slam() -> Anim:
    # Impact at 0.75 s (tick 15).
    a = Anim("slam", 1.6)
    for side, sz in (("left", -1), ("right", 1)):
        a.rot(f"{side}_arm", (0.0, 0, 0, 0), (0.5, -168, 0, 12 * sz), (0.62, -172, 0, 14 * sz),
              (0.75, -32, 0, 4 * sz, "linear"), (0.95, -36, 0, 4 * sz), (1.6, 0, 0, 0))
        a.rot(f"{side}_forearm", (0.0, 0, 0, 0), (0.5, -28, 0, 0), (0.62, -32, 0, 0), (0.75, -6, 0, 0, "linear"),
              (0.95, -10, 0, 0), (1.6, 0, 0, 0))
        for claw, rz in (("a", 22), ("b", -22)):
            a.rot(f"{side}_claw_{claw}", (0.0, 0, 0, 0), (0.5, -10, 0, rz * -sz), (0.75, 20, 0, -rz * 0.3 * sz),
                  (1.6, 0, 0, 0))
        a.rot(f"{side}_thigh", (0.0, 0, 0, 0), (0.5, 6, 0, 0), (0.75, -26, 0, 0), (0.95, -28, 0, 0), (1.6, 0, 0, 0))
        a.rot(f"{side}_shin", (0.0, 0, 0, 0), (0.5, -4, 0, 0), (0.75, 40, 0, 0), (0.95, 42, 0, 0), (1.6, 0, 0, 0))
        a.rot(f"{side}_foot", (0.0, 0, 0, 0), (0.75, -14, 0, 0), (0.95, -14, 0, 0), (1.6, 0, 0, 0))
    a.rot("torso", (0.0, 0, 0, 0), (0.5, -15, 0, 0), (0.62, -17, 0, 0), (0.75, 22, 0, 0, "linear"), (0.95, 23, 0, 0),
          (1.6, 0, 0, 0))
    a.pos("body", (0.0, 0, 0, 0), (0.5, 0, 1.6, 0), (0.62, 0, 1.8, 0), (0.75, 0, -4.5, 0, "linear"),
          (0.95, 0, -4.2, 0), (1.6, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.5, -18, 0, 0), (0.75, -6, 0, 0), (0.95, -4, 0, 0), (1.6, 0, 0, 0))
    a.rot("cap", (0.0, 0, 0, 0), (0.55, -10, 0, 0), (0.75, -2, 0, 0), (0.88, 9, 0, 0), (1.15, -4, 0, 0), (1.6, 0, 0, 0))
    a.scale("cap", (0.0, 1, 1, 1), (0.75, 1, 1, 1), (0.82, 1.08, 0.9, 1.08), (1.0, 0.97, 1.03, 0.97), (1.6, 1, 1, 1))
    for i, rim in enumerate(("rim_n", "rim_e", "rim_s", "rim_w")):
        a.rot(rim, (0.0, 0, 0, 0), (0.6, -12, 0, 0), (0.85, 30, 0, 0), (1.1, -8, 0, 0), (1.6, 0, 0, 0))
    for i in range(len(THREADS)):
        a.rot(f"thread_{i}", (0.0, 0, 0, 0), (0.6, -20, 0, 0), (0.85, 35, 0, 0), (1.15, -12, 0, 0), (1.6, 0, 0, 0))
    return a


def erupt() -> Anim:
    # The right arm plunges into the ground at 0.7 s (tick 14) and the roots run.
    a = Anim("erupt", 1.8)
    a.rot("right_arm", (0.0, 0, 0, 0), (0.45, -150, 0, 12), (0.55, -158, 0, 14), (0.7, -42, 0, 4, "linear"),
          (0.85, -40, 0, 6), (1.0, -44, 0, 3), (1.15, -40, 0, 5), (1.3, -42, 0, 4), (1.8, 0, 0, 0))
    a.rot("right_forearm", (0.0, 0, 0, 0), (0.45, -30, 0, 0), (0.7, -4, 0, 0, "linear"), (1.3, -6, 0, 0), (1.8, 0, 0, 0))
    a.rot("left_arm", (0.0, 0, 0, 0), (0.45, 18, 0, -18), (0.7, -22, 0, -16), (1.3, -22, 0, -16), (1.8, 0, 0, 0))
    a.rot("torso", (0.0, 0, 0, 0), (0.45, -8, 16, 0), (0.55, -9, 18, 0), (0.7, 26, -10, 0, "linear"),
          (1.3, 26, -10, 0), (1.8, 0, 0, 0))
    a.pos("body", (0.0, 0, 0, 0), (0.45, 0, 1.0, 0), (0.7, 0, -3.0, 0), (1.3, 0, -3.0, 0), (1.8, 0, 0, 0))
    for side in ("left", "right"):
        a.rot(f"{side}_thigh", (0.0, 0, 0, 0), (0.7, -20, 0, 0), (1.3, -20, 0, 0), (1.8, 0, 0, 0))
        a.rot(f"{side}_shin", (0.0, 0, 0, 0), (0.7, 30, 0, 0), (1.3, 30, 0, 0), (1.8, 0, 0, 0))
    for claw, rz in (("a", 30), ("b", -30)):
        a.rot(f"right_claw_{claw}", (0.0, 0, 0, 0), (0.45, -20, 0, -rz), (0.7, 30, 0, rz * 0.2), (1.8, 0, 0, 0))
    a.rot("cap", (0.0, 0, 0, 0), (0.5, -6, 0, -4), (0.82, 14, 0, 3), (1.1, 6, 0, 0), (1.8, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.45, -8, 0, 0), (0.75, -4, 0, 0), (1.3, -4, 0, 0), (1.8, 0, 0, 0))
    return a


def nova() -> Anim:
    # Inhale (cap swells, arms spread) and release at 1.5 s (tick 30).
    a = Anim("nova", 2.4)
    a.rot("torso", (0.0, 0, 0, 0), (1.2, -13, 0, 0), (1.42, -15, 0, 0), (1.52, 14, 0, 0, "linear"), (1.75, 11, 0, 0),
          (2.4, 0, 0, 0))
    for side, sz in (("left", -1), ("right", 1)):
        a.rot(f"{side}_arm", (0.0, 0, 0, 0), (1.2, -24, 0, 76 * sz), (1.42, -28, 0, 80 * sz),
              (1.52, -62, 0, 42 * sz, "linear"), (1.75, -55, 0, 45 * sz), (2.4, 0, 0, 0))
        a.rot(f"{side}_forearm", (0.0, 0, 0, 0), (1.2, -20, 0, 0), (1.52, -5, 0, 0), (2.4, 0, 0, 0))
        a.rot(f"{side}_thigh", (0.0, 0, 0, 0), (1.4, 4, 0, 0), (1.55, -16, 0, 0), (2.4, 0, 0, 0))
        a.rot(f"{side}_shin", (0.0, 0, 0, 0), (1.4, -2, 0, 0), (1.55, 24, 0, 0), (2.4, 0, 0, 0))
    a.pos("body", (0.0, 0, 0, 0), (1.2, 0, 1.2, 0), (1.42, 0, 1.5, 0), (1.55, 0, -2.0, 0), (2.4, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (1.2, -16, 0, 0), (1.52, -2, 0, 0), (2.4, 0, 0, 0))
    a.scale("cap", (0.0, 1, 1, 1), (0.55, 1.12, 1.18, 1.12), (0.72, 1.08, 1.1, 1.08), (1.15, 1.24, 1.32, 1.24),
            (1.42, 1.3, 1.4, 1.3), (1.52, 0.86, 0.8, 0.86, "linear"), (1.7, 1.06, 1.05, 1.06), (2.0, 0.98, 1, 0.98),
            (2.4, 1, 1, 1))
    for rim in ("rim_n", "rim_e", "rim_s", "rim_w"):
        a.rot(rim, (0.0, 0, 0, 0), (1.2, -38, 0, 0), (1.42, -42, 0, 0), (1.55, 30, 0, 0, "linear"), (1.85, -8, 0, 0),
              (2.4, 0, 0, 0))
    for i in range(CAP_FIN_COUNT):
        a.rot(f"gill_{i}", (0.0, 0, 0, 0), (1.42, 0, 0, 6), (1.55, 0, 0, -8), (2.4, 0, 0, 0))
    for i in range(len(THREADS)):
        a.rot(f"thread_{i}", (0.0, 0, 0, 0), (1.42, -30, 0, 0), (1.6, 60, 0, 0), (1.9, -15, 0, 0), (2.4, 0, 0, 0))
    return a


def brood() -> Anim:
    # Calls the brood, then drives both palms into the ground at 0.9 s (tick 18).
    a = Anim("brood", 2.0)
    for side, sz in (("left", -1), ("right", 1)):
        a.rot(f"{side}_arm", (0.0, 0, 0, 0), (0.55, -40, 0, 62 * sz), (0.9, -52, 0, 8 * sz, "linear"),
              (1.4, -52, 0, 8 * sz), (2.0, 0, 0, 0))
        a.rot(f"{side}_forearm", (0.0, 0, 0, 0), (0.55, -40, 0, 0), (0.9, -4, 0, 0), (1.4, -4, 0, 0), (2.0, 0, 0, 0))
        a.rot(f"{side}_thigh", (0.0, 0, 0, 0), (0.55, 4, 0, 0), (0.9, -48, 0, 0), (1.4, -48, 0, 0), (2.0, 0, 0, 0))
        a.rot(f"{side}_shin", (0.0, 0, 0, 0), (0.55, -2, 0, 0), (0.9, 74, 0, 0), (1.4, 74, 0, 0), (2.0, 0, 0, 0))
        a.rot(f"{side}_foot", (0.0, 0, 0, 0), (0.9, -26, 0, 0), (1.4, -26, 0, 0), (2.0, 0, 0, 0))
        for claw in "ab":
            a.rot(f"{side}_claw_{claw}", (0.0, 0, 0, 0), (0.9, 25, 0, 0), (1.05, 10, 0, 0), (1.2, 28, 0, 0),
                  (1.4, 18, 0, 0), (2.0, 0, 0, 0))
    a.rot("torso", (0.0, 0, 0, 0), (0.55, -12, 0, 0), (0.9, 32, 0, 0, "linear"), (1.4, 30, 0, 0), (2.0, 0, 0, 0))
    a.pos("body", (0.0, 0, 0, 0), (0.55, 0, 1.0, 0), (0.9, 0, -6.0, 0, "linear"), (1.4, 0, -6.0, 0), (2.0, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.55, -24, 0, 0), (0.9, -8, 0, 0), (1.4, -8, 0, 0), (2.0, 0, 0, 0))
    a.rot("cap", (0.0, 0, 0, 0), (0.6, -10, 0, 0), (0.95, 12, 0, 0), (1.2, 4, 0, 0), (2.0, 0, 0, 0))
    for i in range(CAP_FIN_COUNT):
        a.rot(f"gill_{i}", (0.0, 0, 0, 0), (0.3, 0, 0, 8), (0.45, 0, 0, -8), (0.6, 0, 0, 8), (0.75, 0, 0, -6),
              (0.9, 0, 0, 0))
    return a


def roar() -> Anim:
    # The second bloom.
    a = Anim("roar", 2.0)
    a.rot("torso", (0.0, 0, 0, 0), (0.35, 16, 0, 0), (0.62, -24, 0, 0), (0.8, -22, 0, 3), (0.95, -22, 0, -3),
          (1.1, -22, 0, 3), (1.25, -22, 0, -3), (1.45, -20, 0, 0), (2.0, 0, 0, 0))
    for side, sz in (("left", -1), ("right", 1)):
        a.rot(f"{side}_arm", (0.0, 0, 0, 0), (0.35, 22, 0, 4 * sz), (0.62, 38, 0, 58 * sz), (1.45, 36, 0, 54 * sz),
              (2.0, 0, 0, 0))
        a.rot(f"{side}_forearm", (0.0, 0, 0, 0), (0.35, -25, 0, 0), (0.62, -8, 0, 0), (2.0, 0, 0, 0))
        for claw, rz in (("a", 28), ("b", -28)):
            a.rot(f"{side}_claw_{claw}", (0.0, 0, 0, 0), (0.62, -30, 0, rz * -sz), (1.45, -30, 0, rz * -sz),
                  (2.0, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.35, 16, 0, 0), (0.62, -28, 0, 0), (1.45, -26, 0, 0), (2.0, 0, 0, 0))
    a.rot("cap", (0.0, 0, 0, 0), (0.62, -8, 0, 0), (0.75, -6, 0, 5), (0.9, -6, 0, -5), (1.05, -6, 0, 5),
          (1.2, -6, 0, -5), (1.35, -6, 0, 4), (1.6, 0, 0, 0), (2.0, 0, 0, 0))
    a.scale("cap", (0.0, 1, 1, 1), (0.35, 0.94, 0.9, 0.94), (0.62, 1.16, 1.22, 1.16), (1.45, 1.12, 1.18, 1.12),
            (2.0, 1, 1, 1))
    a.pos("body", (0.0, 0, 0, 0), (0.35, 0, -1.5, 0), (0.62, 0, 1.0, 0), (1.45, 0, 1.0, 0), (2.0, 0, 0, 0))
    for rim in ("rim_n", "rim_e", "rim_s", "rim_w"):
        a.rot(rim, (0.0, 0, 0, 0), (0.62, -30, 0, 0), (0.8, -22, 0, 0), (0.95, -34, 0, 0), (1.1, -22, 0, 0),
              (1.45, -28, 0, 0), (2.0, 0, 0, 0))
    for i in range(len(THREADS)):
        a.rot(f"thread_{i}", (0.0, 0, 0, 0), (0.62, -45, 0, 0), (0.9, -30, 0, 10), (1.2, -40, 0, -10), (2.0, 0, 0, 0))
    return a


def rain() -> Anim:
    # A one-armed fling skyward; the globs leave at 0.6 s (tick 12).
    a = Anim("rain", 1.4)
    a.rot("left_arm", (0.0, 0, 0, 0), (0.35, 42, 0, -10), (0.6, -176, 0, -8, "linear"), (0.75, -168, 0, -10),
          (1.4, 0, 0, 0))
    a.rot("left_forearm", (0.0, 0, 0, 0), (0.35, -35, 0, 0), (0.6, -2, 0, 0), (1.4, 0, 0, 0))
    a.rot("torso", (0.0, 0, 0, 0), (0.35, 8, -14, 0), (0.6, -14, 10, 0), (0.75, -12, 8, 0), (1.4, 0, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.6, -25, 0, 0), (0.85, -22, 0, 0), (1.4, 0, 0, 0))
    a.scale("cap", (0.0, 1, 1, 1), (0.45, 1.1, 1.15, 1.1), (0.6, 0.92, 0.9, 0.92), (0.8, 1.03, 1.02, 1.03),
            (1.4, 1, 1, 1))
    for i in range(CAP_FIN_COUNT):
        a.rot(f"gill_{i}", (0.0, 0, 0, 0), (0.6, 0, 0, 7), (0.8, 0, 0, -5), (1.4, 0, 0, 0))
    return a


def death() -> Anim:
    a = Anim("death", 3.0)
    a.rot("torso", (0.0, 0, 0, 0), (0.45, -18, 0, 6), (1.35, 36, 0, -8), (3.0, 48, 0, -14))
    a.pos("body", (0.0, 0, 0, 0), (0.45, 0, 0.8, 0), (1.35, 0, -12, 0), (1.9, 0, -16, 0), (3.0, 0, -72, 0))
    a.rot("body", (0.0, 0, 0, 0), (1.35, 0, 0, 6), (3.0, 0, 0, 10))
    for side, sz in (("left", -1), ("right", 1)):
        a.rot(f"{side}_thigh", (0.0, 0, 0, 0), (0.45, 8, 0, 0), (1.35, -62, 0, 0), (3.0, -66, 0, 0))
        a.rot(f"{side}_shin", (0.0, 0, 0, 0), (0.45, -4, 0, 0), (1.35, 100, 0, 0), (3.0, 104, 0, 0))
        a.rot(f"{side}_foot", (0.0, 0, 0, 0), (1.35, -38, 0, 0), (3.0, -38, 0, 0))
        a.rot(f"{side}_arm", (0.0, 0, 0, 0), (0.45, -30, 0, 38 * sz), (1.35, -22, 0, 12 * sz), (3.0, -60, 0, 6 * sz))
        a.rot(f"{side}_forearm", (0.0, 0, 0, 0), (0.45, -20, 0, 0), (1.35, 22, 0, 0), (3.0, 14, 0, 0))
    a.rot("head", (0.0, 0, 0, 0), (0.45, -22, 0, 0), (1.35, 26, 0, 0), (3.0, 34, 0, 0))
    a.rot("cap", (0.0, 0, 0, 0), (0.45, -8, 0, 4), (1.35, 20, 0, 12), (3.0, 28, 0, 20))
    a.scale("cap", (0.0, 1, 1, 1), (0.45, 1.08, 1.12, 1.08), (1.35, 0.95, 0.9, 0.95), (3.0, 0.7, 0.55, 0.7))
    for rim in ("rim_n", "rim_e", "rim_s", "rim_w"):
        a.rot(rim, (0.0, 0, 0, 0), (0.45, -16, 0, 0), (1.35, 40, 0, 0), (3.0, 55, 0, 0))
    for i in range(len(THREADS)):
        a.rot(f"thread_{i}", (0.0, 0, 0, 0), (0.45, -25, 0, 0), (1.35, 10, 0, 0), (3.0, 0, 0, 0))
    return a


def anims() -> list[Anim]:
    return [idle(), walk(), emerge(), slam(), erupt(), nova(), brood(), roar(), rain(), death()]


# ---------------------------------------------------------------------------------------------------- data

def data(out) -> None:
    out.tr("entity.spore_and_stem.myceliarch", "The Myceliarch")
    out.tr("message.spore_and_stem.myceliarch.stirs", "The mycelium stirs beneath you...")
    out.tr("message.spore_and_stem.myceliarch.rises", "The Myceliarch rises")
    out.tr("message.spore_and_stem.myceliarch.second_bloom", "The Myceliarch blooms again!")
    out.tr("message.spore_and_stem.myceliarch.no_room", "There is no room here for the Myceliarch to rise")
    out.tr("message.spore_and_stem.myceliarch.already", "A Myceliarch already stirs nearby")
    out.tr("message.spore_and_stem.myceliarch.withers", "The Myceliarch withers back into the earth")

    def item(name, lo=None, hi=None, looting=0.0):
        entry = {"type": "minecraft:item", "name": f"spore_and_stem:{name}"}
        fns = []
        if lo is not None:
            fns.append({"function": "minecraft:set_count", "count": {"type": "minecraft:uniform", "min": lo, "max": hi}})
        if looting:
            fns.append({"function": "minecraft:enchanted_count_increase", "enchantment": "minecraft:looting",
                        "count": {"type": "minecraft:uniform", "min": 0, "max": looting}})
        if fns:
            entry["functions"] = fns
        return entry

    out.loot_table("entities", "myceliarch", {
        "type": "minecraft:entity",
        "pools": [
            {"rolls": 1, "entries": [item("spore_heart")]},
            {"rolls": 1, "entries": [item("mycoleather", 4, 8, 2)]},
            {"rolls": 1, "entries": [item("lumen_spores", 8, 16, 4)]},
        ],
        "random_sequence": "spore_and_stem:entities/myceliarch",
    })
