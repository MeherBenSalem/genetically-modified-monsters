"""Shared creature materials: caps with soft gradients, clean spots and gill lines; fibrous stems and limbs; clumped
hides and moss; continuous mycelial threads; crisp eyes.

Structure over noise: every material picks whole ramp steps (``quant``, no ordered dithering) from a value built of
form lighting plus a *shaped* variation (streaks stretched along a limb, clumps, rings), so large faces read as
fibre, cap or fur rather than speckle. Light comes from the top-left; on side faces the upper rows are lighter.
Ramps are dark -> light; 3-4 of their steps are used per material.
"""
from __future__ import annotations

import math
import zlib

from ..palette import (BARK, DIRT, GLOW, INK, MYCELIUM, MYCOSIS, PUFFBALL, SPORE)
from .paint import Px, as_rgba, dither, fbm, mix, value_noise

# Creature-only ramps (kept here so the shared palette stays owned by the block/item art).
SPOREMAW_CAP = ["#2a1730", "#43264d", "#5d3769", "#7a4c85", "#9a68a3", "#b98cc0"]
SPOREMAW_FLESH = ["#4a2a35", "#6f3f4d", "#94566a", "#b8738a", "#d895ab"]
MAW_GLOW = ["#7a2f61", "#c0508f", "#f07fb8", "#ffc2de", "#fff0f7"]
AMANITA = ["#4a0f12", "#76171a", "#a52722", "#cf3b2b", "#ec6446", "#f9967a"]
BROWNCAP = ["#3a2418", "#5a3a26", "#7d5638", "#a07650", "#c29a72", "#dcbf98"]
MOTH_WING = ["#141a24", "#1f2836", "#2c394b", "#3d4e63", "#55697f"]
MOTH_FUZZ = ["#3b3a3f", "#56545a", "#77737a", "#9d98a0", "#c4bfc6"]
BOAR = ["#2e1f1a", "#47302a", "#62453a", "#7f5d4d", "#9c7865", "#b9967f"]
MOSS = ["#2f3b1c", "#435326", "#5b6e30", "#78893e", "#97a653"]
SNOUT = ["#5e3b3a", "#86555a", "#ae7378", "#cf979b", "#e9bdbf"]
TUSK = ["#a99c84", "#cfc4ad", "#ece4d1", "#fffaf0"]
SHAMBLER_SKIN = ["#2b2220", "#3f312d", "#56443d", "#6e5a50", "#8a7466", "#a99282"]
SHAMBLER_CAP = ["#3a2a22", "#56402f", "#77583e", "#9a7550", "#b99568", "#d6b98f"]
CHITIN = ["#1c1210", "#2e1d18", "#452c22", "#5f3e2e", "#7b5440"]
EYE_DARK = "#140d12"
EYE_GLINT = "#f6f2ff"


def quant(ramp, value: float):
    """The ramp step nearest to value (0..1). No dithering: flat, clean steps."""
    ramp = [as_rgba(c) for c in ramp]
    return ramp[max(0, min(len(ramp) - 1, int(round(max(0.0, min(1.0, value)) * (len(ramp) - 1)))))]


def lit(px: Px, base: float, strength: float = 0.12) -> float:
    """Ramp position with face lighting and a top-to-bottom gradient on side faces."""
    v = base + px.light * strength
    if px.face in ("front", "back", "left", "right"):
        v += (0.5 - px.v) * strength * 1.4
    return v


def streak(px: Px, seed: int, along_y: bool = True, width: float = 1.6, length: float = 7.0) -> float:
    """Smooth noise stretched along a limb (fibres): -0.5..0.5. Continuous across a face's texels."""
    if px.face in ("top", "bottom"):
        return value_noise(px.gx, px.gy, seed, 2.5) - 0.5
    if along_y:
        return value_noise(px.gx / width * 2.0, px.gy / length * 2.0, seed, 2.0) - 0.5
    return value_noise(px.gx / length * 2.0, px.gy / width * 2.0, seed, 2.0) - 0.5


def clump(px: Px, seed: int, scale: float = 3.0) -> float:
    """Blobby clumps (fur tufts, moss cushions, puffball warts): -0.5..0.5."""
    return fbm(px.gx, px.gy, seed, 2, scale) - 0.5


def spot_at(px: Px, seed: int, density: float, cell: int = 3, big: bool = False) -> float | None:
    """Crisp round spots on a coarse grid (one candidate per cell). Returns 0 (centre) or 0.6 (edge) inside a spot."""
    gx, gy = px.gx, px.gy
    cx, cy = gx // cell, gy // cell
    h = zlib.crc32(f"{seed}/{cx}/{cy}".encode())
    if (h & 0xFFFF) / 0xFFFF > density:
        return None
    ox = cell * cx + ((h >> 16) & 0xFF) % max(1, cell - 1)
    oy = cell * cy + ((h >> 24) & 0xFF) % max(1, cell - 1)
    size = 2 if big and (h >> 8) & 1 else 1
    if ox <= gx < ox + size and oy <= gy < oy + size:
        return 0.0 if (gx, gy) == (ox, oy) else 0.6
    return None


def cap(ramp, spots=None, spot_density: float = 0.0, seed: int = 1, gloss: bool = True, rim_dark: bool = True,
        gills=None, gill_ramp=None, tiers: dict | None = None):
    """A mushroom cap. Top: a soft radial gradient lit toward the back-left with a one-texel gloss on the crown;
    sides: lighter at the top, a crisp dark rim at the bottom; bottom: gill lines radiating from the centre (or flat).
    spots: a ramp for a few clean raised spots. tiers: per-cube base offsets (lighter crown, darker brim)."""
    tiers = tiers or {}

    def paint(px: Px):
        bias = tiers.get(px.cube.name, 0.0)
        if px.face == "bottom":
            if gill_ramp:
                cx, cy = (px.w - 1) / 2, (px.h - 1) / 2
                ang = math.atan2(px.y - cy, px.x - cx)
                spokes = max(8, (px.w + px.h) // 2)
                line = math.cos(ang * spokes) > 0.35
                r = math.hypot((px.x - cx) / max(1, cx), (px.y - cy) / max(1, cy))
                if r < 0.25:
                    return quant(gill_ramp, 0.15)
                return quant(gill_ramp, (0.7 if line else 0.35) - r * 0.15)
            return quant(ramp, 0.12)
        if px.face == "top":
            d = math.hypot(px.u - 0.35, px.v - 0.35)
            value = 0.78 - d * 0.42 + bias + streak(px, seed, False) * 0.06
        else:
            value = lit(px, 0.52, 0.16) + bias + streak(px, seed) * 0.08
            if rim_dark and px.y == px.h - 1:
                value -= 0.22
            if px.y == 0 and px.face != "back":
                value += 0.08
        if spots and spot_density > 0 and not (px.face != "top" and px.y == px.h - 1):
            s = spot_at(px, seed + 99, spot_density, 3, big=px.face == "top")
            if s is not None:
                return quant(spots, 0.85 - s * 0.5 + px.light * 0.05)
        c = quant(ramp, value)
        if gloss and px.face == "top" and px.cube.name == "crown" and (px.x, px.y) == (1, 1):
            return mix(c, "#ffffff", 0.4)
        return c
    return paint


def stem(ramp, seed: int = 3, streak_amount: float = 0.22):
    """Fibrous stem: long vertical fibres, lit from the top-left, darker toward the bottom."""
    def paint(px: Px):
        if px.face in ("top", "bottom"):
            r = math.hypot(px.u - 0.5, px.v - 0.5)
            return quant(ramp, 0.62 - r * 0.35 + px.light * 0.08)
        return quant(ramp, lit(px, 0.55, 0.14) + streak(px, seed) * streak_amount)
    return paint


def fibre(ramp, seed: int = 5, amount: float = 0.3, base: float = 0.5, along_y: bool = True):
    """Braided fibre for limbs and torsos: pronounced long streaks."""
    def paint(px: Px):
        return quant(ramp, lit(px, base, 0.14) + streak(px, seed, along_y) * amount)
    return paint


def hide(ramp, seed: int = 5, amount: float = 0.25, scale: float = 3.0, base: float = 0.5):
    """A hide in soft clumps."""
    def paint(px: Px):
        return quant(ramp, lit(px, base, 0.14) + clump(px, seed, scale) * amount * 2)
    return paint


def fuzz(ramp, seed: int = 7, base: float = 0.5):
    """Soft fur: short tufts (clumps stretched downward)."""
    def paint(px: Px):
        tuft = value_noise(px.gx * 1.0, px.gy / 2.0, seed, 1.5) - 0.5
        return quant(ramp, lit(px, base, 0.12) + tuft * 0.45)
    return paint


def patches(base_fn, patch_ramp, threshold: float = 0.6, seed: int = 11, scale: float = 3.5,
            faces=("top", "front", "back", "left", "right")):
    """Organic cushions (moss, mycelium) where clumped noise exceeds a threshold; lighter toward their middle."""
    def paint(px: Px):
        if px.face in faces:
            n = fbm(px.gx, px.gy, seed, 2, scale)
            if px.face != "top":
                n -= px.v * 0.25
            if n > threshold:
                return quant(patch_ramp, 0.35 + (n - threshold) * 2.5 + px.light * 0.1)
        return base_fn(px)
    return paint


def threads(base_fn, seed: int = 13, spacing: float = 5.0, ramp=None):
    """A few continuous mycelial threads winding diagonally around a limb (not speckle)."""
    ramp = ramp or MYCELIUM

    def paint(px: Px):
        if px.face in ("front", "back", "left", "right"):
            wobble = (value_noise(px.gx * 0.5, px.gy * 0.5, seed, 2.0) - 0.5) * 3.0
            phase = (px.gx * 0.55 + px.gy * 0.35 + wobble) % spacing
            if phase < 0.45:
                return quant(ramp, 0.45 + px.light * 0.1)
        return base_fn(px)
    return paint


def eye(px: Px, x: int, y: int, size: int = 1, glint: bool = True, color: str = EYE_DARK):
    """A dark eye at (x, y) (size 1 or 2) with a one-texel glint top-left; returns a colour or None."""
    if x <= px.x < x + size and y <= px.y < y + size:
        if glint and size == 2 and px.x == x and px.y == y:
            return as_rgba(EYE_GLINT)
        return as_rgba(color)
    return None


__all__ = ["BARK", "DIRT", "GLOW", "INK", "MYCELIUM", "MYCOSIS", "PUFFBALL", "SPORE", "cap", "stem", "fibre", "hide",
           "fuzz", "patches", "threads", "eye", "lit", "quant", "streak", "clump", "dither"]
