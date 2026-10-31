"""Small pixel-art toolkit shared by every texture generator.

Adapted from Sprout & Soil's assetgen. Conventions (see tools/assets/STYLE.md):
* colours are ``(r, g, b, a)`` tuples; ``hexc("#rrggbb")`` converts
* ``ramp(base)`` builds a hue-shifted 5-step ramp: shadows drift cool, highlights warm
* sprites are built from ASCII rows + a palette dict, then outlined with ``outline()``
"""
from __future__ import annotations

import colorsys
from pathlib import Path
from typing import Callable, Iterable

from PIL import Image

Color = tuple[int, int, int, int]
CLEAR: Color = (0, 0, 0, 0)


# --------------------------------------------------------------------------- colour


def hexc(value: str, alpha: int = 255) -> Color:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def to_hex(c: Color) -> str:
    return "#%02x%02x%02x" % c[:3]


def _hls(c: Color):
    return colorsys.rgb_to_hls(c[0] / 255, c[1] / 255, c[2] / 255)


def _rgb(h, l, s, a=255) -> Color:
    r, g, b = colorsys.hls_to_rgb(h % 1.0, max(0.0, min(1.0, l)), max(0.0, min(1.0, s)))
    return (round(r * 255), round(g * 255), round(b * 255), a)


def shade(c: Color | str, amount: float, hue_shift: float = 0.035, sat: float = 0.0) -> Color:
    """Lighten (amount>0) or darken (amount<0) with pixel-art hue shifting.

    Darker tones rotate toward blue/purple, lighter ones toward yellow, which keeps
    shading lively instead of muddy.
    """
    if isinstance(c, str):
        c = hexc(c)
    h, l, s = _hls(c)
    # hue rotation toward 60deg (yellow) when lightening, toward 240deg (blue) when darkening
    target = 1 / 6 if amount > 0 else 2 / 3
    delta = ((target - h + 0.5) % 1.0) - 0.5
    h += max(-abs(hue_shift * amount * 4), min(abs(hue_shift * amount * 4), delta))
    l += amount
    s += sat + (0.05 * -amount if amount < 0 else -0.04 * amount)
    return _rgb(h, l, s, c[3])


def ramp(base: Color | str, steps: int = 5, spread: float = 0.13) -> list[Color]:
    """Return ``steps`` colours darkest -> lightest centred on ``base``."""
    if isinstance(base, str):
        base = hexc(base)
    mid = steps // 2
    return [shade(base, (i - mid) * spread) for i in range(steps)]


def mix(a: Color, b: Color, t: float) -> Color:
    return tuple(round(a[i] + (b[i] - a[i]) * t) for i in range(4))  # type: ignore


def with_alpha(c: Color, a: int) -> Color:
    return (c[0], c[1], c[2], a)


# --------------------------------------------------------------------------- sprite


class Sprite:
    def __init__(self, w: int = 16, h: int = 16):
        self.w, self.h = w, h
        self.px: list[list[Color]] = [[CLEAR] * w for _ in range(h)]

    # ---- construction
    @classmethod
    def from_rows(cls, rows: Iterable[str], palette: dict[str, Color | str | None]) -> "Sprite":
        rows = list(rows)
        s = cls(max(len(r) for r in rows), len(rows))
        for y, row in enumerate(rows):
            for x, ch in enumerate(row):
                col = palette.get(ch)
                if col is None:
                    continue
                s.px[y][x] = hexc(col) if isinstance(col, str) else col
        return s

    @classmethod
    def load(cls, path: Path | str) -> "Sprite":
        im = Image.open(path).convert("RGBA")
        s = cls(*im.size)
        for y in range(s.h):
            for x in range(s.w):
                s.px[y][x] = im.getpixel((x, y))
        return s

    def copy(self) -> "Sprite":
        s = Sprite(self.w, self.h)
        s.px = [row[:] for row in self.px]
        return s

    # ---- pixel ops
    def inside(self, x: int, y: int) -> bool:
        return 0 <= x < self.w and 0 <= y < self.h

    def get(self, x: int, y: int) -> Color:
        return self.px[y][x] if self.inside(x, y) else CLEAR

    def set(self, x: int, y: int, c: Color | str | None) -> None:
        if c is None or not self.inside(x, y):
            return
        if isinstance(c, str):
            c = hexc(c)
        if c[3] == 255 or c[3] == 0:
            self.px[y][x] = c
        else:  # alpha blend over existing
            base = self.px[y][x]
            if base[3] == 0:
                self.px[y][x] = c
            else:
                t = c[3] / 255
                self.px[y][x] = (round(base[0] + (c[0] - base[0]) * t), round(base[1] + (c[1] - base[1]) * t),
                                 round(base[2] + (c[2] - base[2]) * t), max(base[3], c[3]))

    def opaque(self, x: int, y: int) -> bool:
        return self.get(x, y)[3] > 0

    def fill_rect(self, x0, y0, x1, y1, c) -> None:
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                self.set(x, y, c)

    def line(self, x0, y0, x1, y1, c) -> None:
        dx, dy = abs(x1 - x0), -abs(y1 - y0)
        sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def ellipse(self, cx: float, cy: float, rx: float, ry: float, c, fill: bool = True) -> None:
        for y in range(self.h):
            for x in range(self.w):
                d = ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2
                if (fill and d <= 1.0) or (not fill and 0.75 <= d <= 1.0):
                    self.set(x, y, c)

    def map(self, fn: Callable[[int, int, Color], Color | None]) -> None:
        for y in range(self.h):
            for x in range(self.w):
                c = self.px[y][x]
                if c[3]:
                    out = fn(x, y, c)
                    if out is not None:
                        self.px[y][x] = out

    def paste(self, other: "Sprite", ox: int = 0, oy: int = 0) -> "Sprite":
        for y in range(other.h):
            for x in range(other.w):
                c = other.px[y][x]
                if c[3]:
                    self.set(x + ox, y + oy, c)
        return self

    def flip_h(self) -> "Sprite":
        s = self.copy()
        s.px = [list(reversed(r)) for r in self.px]
        return s

    def shift(self, dx: int, dy: int) -> "Sprite":
        s = Sprite(self.w, self.h)
        return s.paste(self, dx, dy)

    # ---- shading helpers
    def outline(self, color: Color | str | Callable[[Color], Color], diagonal: bool = False) -> "Sprite":
        """Add a 1px outline outside the opaque silhouette.

        ``color`` may be a callable deriving the outline colour from the
        neighbouring pixel (selective outlining, e.g. ``lambda c: shade(c, -0.35)``).
        """
        out = self.copy()
        dirs = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        if diagonal:
            dirs += [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        for y in range(self.h):
            for x in range(self.w):
                if self.opaque(x, y):
                    continue
                for dx, dy in dirs:
                    if self.opaque(x + dx, y + dy):
                        src = self.get(x + dx, y + dy)
                        col = color(src) if callable(color) else (hexc(color) if isinstance(color, str) else color)
                        out.px[y][x] = col
                        break
        return out

    def inner_light(self, light: Color, dark: Color | None = None) -> "Sprite":
        """Top-left rim light / bottom-right rim shadow on the silhouette edge."""
        out = self.copy()
        for y in range(self.h):
            for x in range(self.w):
                if not self.opaque(x, y):
                    continue
                if not self.opaque(x - 1, y) or not self.opaque(x, y - 1):
                    out.px[y][x] = light
                elif dark is not None and (not self.opaque(x + 1, y) or not self.opaque(x, y + 1)):
                    out.px[y][x] = dark
        return out

    # ---- io
    def image(self) -> Image.Image:
        im = Image.new("RGBA", (self.w, self.h))
        for y in range(self.h):
            for x in range(self.w):
                im.putpixel((x, y), self.px[y][x])
        return im

    def save(self, path: Path | str) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.image().save(path, optimize=True)
        return path


def sphere_shade(s: Sprite, cx: float, cy: float, r: float, ramp_: list[Color], mask: Callable[[int, int], bool] | None = None,
                 light=(-0.55, -0.6)) -> None:
    """Fill a disc with ramp colours using a top-left light direction (cel shaded)."""
    lx, ly = light
    for y in range(s.h):
        for x in range(s.w):
            dx, dy = (x + 0.5 - cx) / r, (y + 0.5 - cy) / r
            d2 = dx * dx + dy * dy
            if d2 > 1.0 or (mask and not mask(x, y)):
                continue
            dz = (1 - d2) ** 0.5
            lit = max(0.0, -(dx * lx + dy * ly) + dz * 0.55)
            idx = min(len(ramp_) - 1, int(lit * (len(ramp_) - 0.2)))
            s.set(x, y, ramp_[idx])


# --------------------------------------------------------------------------- previews


def contact_sheet(paths: list[Path], out: Path, scale: int = 6, cols: int = 12, bg=(52, 54, 60, 255),
                  label: bool = True) -> Path:
    from PIL import ImageDraw

    cell = 16 * scale + 8
    rows = (len(paths) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cell, rows * (cell + (12 if label else 0))), bg)
    draw = ImageDraw.Draw(sheet)
    for i, p in enumerate(paths):
        im = Image.open(p).convert("RGBA")
        w, h = im.size
        f = (16 * scale) // max(w, h)
        im = im.resize((w * f, h * f), Image.NEAREST)
        x = (i % cols) * cell + 4
        y = (i // cols) * (cell + (12 if label else 0)) + 4
        sheet.alpha_composite(im, (x, y))
        if label:
            draw.text((x, y + 16 * scale + 1), Path(p).stem[:18], fill=(220, 220, 220, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out
