"""Painting creature textures onto a rig's UV layout.

A painter is called for every texel of every face of every cube:

    def painter(px: Px) -> color | None          # base texture (None leaves the texel clear)

``Px`` gives the cube, the face name, the texel position inside the face (x to the right, y down, as seen from
outside the box), the face size, normalised coordinates and a stable per-texel random number. ``paint`` also takes an
optional ``glow`` painter for the emissive layer (drawn additively by an eyes-style render layer: black = no light).

Helpers below make good-looking pixel materials quickly: Bayer-dithered ramps, value noise, face lighting.
"""
from __future__ import annotations

import math
import zlib
from dataclasses import dataclass
from typing import Callable

from PIL import Image

from ..palette import hex2rgba
from .rig import Cube, Rig

Color = tuple[int, int, int, int]
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]
# Face lighting (ramp steps added): light from above and the front-left, like the block renderer.
FACE_LIGHT = {"top": 1.0, "front": 0.25, "right": 0.0, "left": -0.25, "back": -0.5, "bottom": -1.5}


@dataclass
class Px:
    cube: Cube
    face: str
    x: int
    y: int
    w: int
    h: int
    gx: int   # texture coordinates
    gy: int

    @property
    def u(self) -> float:
        """0..1 across the face."""
        return (self.x + 0.5) / self.w

    @property
    def v(self) -> float:
        """0..1 down the face."""
        return (self.y + 0.5) / self.h

    def rand(self, salt: str = "") -> float:
        """A stable random number in [0, 1) for this texel."""
        return (zlib.crc32(f"{self.cube.name}/{self.face}/{self.x}/{self.y}/{salt}".encode()) & 0xFFFFFF) / 0x1000000

    def edge(self) -> int:
        """Distance in texels to the nearest edge of the face."""
        return min(self.x, self.y, self.w - 1 - self.x, self.h - 1 - self.y)

    @property
    def light(self) -> float:
        return FACE_LIGHT[self.face]


def as_rgba(c) -> Color:
    if isinstance(c, str):
        return hex2rgba(c)
    return c if len(c) == 4 else (*c, 255)


def dither(ramp: list, value: float, x: int, y: int) -> Color:
    """Picks from a dark→light ramp at value 0..1 with 4×4 ordered dithering between neighbouring steps."""
    ramp = [as_rgba(c) for c in ramp]
    pos = max(0.0, min(1.0, value)) * (len(ramp) - 1)
    lo = int(math.floor(pos))
    frac = pos - lo
    threshold = (BAYER4[y % 4][x % 4] + 0.5) / 16
    return ramp[min(len(ramp) - 1, lo + (1 if frac > threshold else 0))]


def step(ramp: list, index: float) -> Color:
    ramp = [as_rgba(c) for c in ramp]
    return ramp[max(0, min(len(ramp) - 1, int(round(index))))]


def value_noise(x: float, y: float, seed: int = 0, scale: float = 4.0) -> float:
    """Smooth 2D value noise in [0, 1)."""
    def h(ix, iy):
        return (zlib.crc32(f"{seed}/{ix}/{iy}".encode()) & 0xFFFF) / 0x10000
    fx, fy = x / scale, y / scale
    ix, iy = math.floor(fx), math.floor(fy)
    tx, ty = fx - ix, fy - iy
    tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
    a, b = h(ix, iy), h(ix + 1, iy)
    c, d = h(ix, iy + 1), h(ix + 1, iy + 1)
    return a + (b - a) * tx + (c - a) * ty + (a - b - c + d) * tx * ty


def fbm(x: float, y: float, seed: int = 0, octaves: int = 3, scale: float = 6.0) -> float:
    total, amp, norm = 0.0, 1.0, 0.0
    for o in range(octaves):
        total += value_noise(x, y, seed + o * 31, scale / (2 ** o)) * amp
        norm += amp
        amp *= 0.5
    return total / norm


def mix(a, b, t: float) -> Color:
    a, b = as_rgba(a), as_rgba(b)
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(4))


def material(ramp: list, base: float = 0.5, noise: float = 0.18, seed: int = 1, scale: float = 5.0,
             light: float = 0.12) -> Callable[[Px], Color]:
    """A general matte material: ramp position = base + face light + fbm noise, Bayer dithered."""
    def paint(px: Px) -> Color:
        n = fbm(px.gx, px.gy, seed, 3, scale) - 0.5
        return dither(ramp, base + px.light * light + n * noise * 2, px.gx, px.gy)
    return paint


def paint(rig: Rig, painter: Callable[[Px], Color | None],
          glow: Callable[[Px], Color | None] | None = None) -> tuple[Image.Image, Image.Image | None]:
    """Paints the base texture (and the emissive layer if a glow painter is given)."""
    base = Image.new("RGBA", rig.tex, (0, 0, 0, 0))
    emissive = Image.new("RGBA", rig.tex, (0, 0, 0, 0)) if glow else None
    for _, cube in rig.cubes():
        for face, (x0, y0, w, h) in cube.regions().items():
            for y in range(h):
                for x in range(w):
                    px = Px(cube, face, x, y, w, h, x0 + x, y0 + y)
                    c = painter(px)
                    if c is not None:
                        base.putpixel((x0 + x, y0 + y), as_rgba(c))
                    if glow is not None:
                        g = glow(px)
                        if g is not None:
                            emissive.putpixel((x0 + x, y0 + y), as_rgba(g))
    return base, emissive


def stamp_face(px: Px, art: str, palette: dict, anchor: str = "center", dx: int = 0, dy: int = 0) -> Color | None:
    """Looks up ASCII art (rows; '.' = no paint) placed on a face; returns the colour under this texel or None.
    anchor: 'center', 'top', 'bottom'."""
    rows = [r for r in art.strip("\n").split("\n")]
    ah, aw = len(rows), max(len(r) for r in rows)
    ox = (px.w - aw) // 2 + dx
    if anchor == "top":
        oy = dy
    elif anchor == "bottom":
        oy = px.h - ah + dy
    else:
        oy = (px.h - ah) // 2 + dy
    ax, ay = px.x - ox, px.y - oy
    if 0 <= ay < ah and 0 <= ax < len(rows[ay]):
        ch = rows[ay][ax]
        if ch not in ". ":
            return as_rgba(palette[ch])
    return None
