"""Shared helpers for block and item art: deterministic tileable noise, ramp sampling with ordered dithering,
ASCII sprites and hue-shifted outlines. Everything is reproducible (no global randomness)."""
from __future__ import annotations

import math
import zlib

from PIL import Image

from .core import CLEAR, Sprite, hexc, mix, shade
from .palette import hex2rgba

BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]


def col(c) -> tuple[int, int, int, int]:
    if isinstance(c, str):
        return hex2rgba(c)
    if len(c) == 3:
        return (*c, 255)
    return tuple(c)


def ramp(hexes: list[str]) -> list[tuple[int, int, int, int]]:
    return [col(h) for h in hexes]


def seed_of(*parts) -> int:
    return zlib.crc32(repr(parts).encode("utf-8"))


def hash01(x: int, y: int, seed: int) -> float:
    h = (x * 374761393 + y * 668265263 + seed * 2246822519) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return (h & 0xFFFFFF) / float(0x1000000)


def vnoise(x: float, y: float, seed: int, cell: float = 4.0, period: int = 16) -> float:
    """Tileable value noise in [0,1). `period` is in pixels and must be a multiple of `cell`."""
    gx, gy = x / cell, y / cell
    n = max(1, round(period / cell))
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def g(ix, iy):
        return hash01(ix % n, iy % n, seed)

    a = g(x0, y0) + (g(x0 + 1, y0) - g(x0, y0)) * sx
    b = g(x0, y0 + 1) + (g(x0 + 1, y0 + 1) - g(x0, y0 + 1)) * sx
    return a + (b - a) * sy


def vnoise_a(x: float, y: float, seed: int, cx: float, cy: float, period: int = 16) -> float:
    """Anisotropic tileable value noise: cell size cx along x, cy along y (both dividing `period`)."""
    nx, ny = max(1, round(period / cx)), max(1, round(period / cy))
    gx, gy = x / cx, y / cy
    x0, y0 = math.floor(gx), math.floor(gy)
    fx, fy = gx - x0, gy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)

    def g(ix, iy):
        return hash01(ix % nx, iy % ny, seed)

    a = g(x0, y0) + (g(x0 + 1, y0) - g(x0, y0)) * sx
    b = g(x0, y0 + 1) + (g(x0 + 1, y0 + 1) - g(x0, y0 + 1)) * sx
    return a + (b - a) * sy


def fbm(x: float, y: float, seed: int, period: int = 16, cells=(8.0, 4.0, 2.0), weights=(0.55, 0.3, 0.15)) -> float:
    total = 0.0
    for i, (c, w) in enumerate(zip(cells, weights)):
        total += vnoise(x, y, seed + i * 101, c, period) * w
    return total / sum(weights)


def pick(rmp, t: float, x: int = 0, y: int = 0, dither: float = 0.0):
    """Ramp colour for t in [0,1]; with dither>0 the step boundaries are broken up by a Bayer pattern."""
    t = max(0.0, min(0.9999, t))
    if dither:
        t = max(0.0, min(0.9999, t + (BAYER4[y % 4][x % 4] / 16.0 - 0.47) * dither / len(rmp)))
    return rmp[int(t * len(rmp))]


def lerp(a, b, t):
    return mix(col(a), col(b), max(0.0, min(1.0, t)))


def blank(w: int = 16, h: int = 16) -> Sprite:
    return Sprite(w, h)


def fill(w: int, h: int, fn) -> Sprite:
    s = Sprite(w, h)
    for y in range(h):
        for x in range(w):
            c = fn(x, y)
            if c is not None:
                s.px[y][x] = col(c)
    return s


def from_ascii(art: str, palette: dict) -> Sprite:
    rows = [r for r in art.strip("\n").split("\n")]
    rows = [r.replace(" ", ".") for r in rows]
    w = max(len(r) for r in rows)
    s = Sprite(w, len(rows))
    for y, row in enumerate(rows):
        for x, ch in enumerate(row):
            if ch == "." or ch not in palette:
                continue
            s.px[y][x] = col(palette[ch])
    return s


def outlined(s: Sprite, amount: float = -0.34, extra_br: float = -0.1) -> Sprite:
    """Item outline: a dark hue-shifted copy of the neighbouring colour, darker on the bottom-right."""
    out = s.copy()
    for y in range(s.h):
        for x in range(s.w):
            if s.opaque(x, y):
                continue
            best = None
            # Pixels to the right/below of the art are its shadow side (-0.38); left/above are lit (-0.30).
            for dx, dy, side in ((-1, 0, -0.38), (0, -1, -0.38), (1, 0, -0.30), (0, 1, -0.30)):
                if s.opaque(x + dx, y + dy):
                    src = s.get(x + dx, y + dy)
                    if max(src[:3]) - min(src[:3]) < 40 and min(src[:3]) > 120:
                        # near-neutral colours: a cool grey outline (hue shifting would turn them orange)
                        best = mix(src, (60, 56, 74, 255), 0.6 if side < -0.35 else 0.5)
                    else:
                        best = _floor_lightness(shade(src, side, sat=0.06), 0.16)
                    break
            if best is not None:
                out.px[y][x] = (best[0], best[1], best[2], 255)
    return out


def _floor_lightness(c, minimum: float):
    """Keeps an outline from collapsing to black: lifts its HLS lightness to `minimum`, hue kept."""
    import colorsys
    h, l, sat = colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)
    if l >= minimum:
        return c
    r, g, b = colorsys.hls_to_rgb(h, minimum, min(1.0, sat + 0.1))
    return (round(r * 255), round(g * 255), round(b * 255), 255)


def image(s: Sprite) -> Image.Image:
    return s.image()


def to_sprite(img: Image.Image) -> Sprite:
    img = img.convert("RGBA")
    s = Sprite(*img.size)
    for y in range(s.h):
        for x in range(s.w):
            s.px[y][x] = img.getpixel((x, y))
    return s


def tint(c, amount: float):
    return shade(col(c), amount)


def darken_edges_vertical(s: Sprite, top: float = 0.0, bottom: float = -0.12) -> None:
    for y in range(s.h):
        t = y / max(1, s.h - 1)
        amt = top + (bottom - top) * t
        for x in range(s.w):
            c = s.px[y][x]
            if c[3] and abs(amt) > 0.01:
                s.px[y][x] = shade(c, amt)


def circle_mask(cx: float, cy: float, rx: float, ry: float):
    return lambda x, y: ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1.0


__all__ = ["CLEAR", "Sprite", "hexc", "mix", "shade", "col", "ramp", "seed_of", "hash01", "vnoise", "vnoise_a", "fbm", "pick", "lerp",
           "blank", "fill", "from_ascii", "outlined", "image", "to_sprite", "tint", "circle_mask", "darken_edges_vertical"]
