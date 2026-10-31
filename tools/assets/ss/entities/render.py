"""Software preview of a rig with its texture, posed by animations: the same box geometry, UV mapping, bone
transform order and keyframe maths as the game, rendered orthographically with simple face lighting.

  img = render(rig, base_tex, glow_tex, pose=pose_at(anims, 0.4), yaw=-30, pitch=15, size=420)
  frames(rig, base, glow, anim, n=8) -> list of images (a strip or GIF of an animation)
"""
from __future__ import annotations

import math

import numpy as np
from PIL import Image

from .rig import Rig

LIGHT = np.array([0.35, 0.8, -0.5])
LIGHT = LIGHT / np.linalg.norm(LIGHT)


def _rx(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[1, 0, 0, 0], [0, c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]], float)


def _ry(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]], float)


def _rz(a):
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], float)


def _t(x, y, z):
    m = np.eye(4)
    m[:3, 3] = (x, y, z)
    return m


def _s(x, y, z):
    return np.diag([x, y, z, 1.0])


def bone_matrices(rig: Rig, pose: dict | None = None) -> dict[str, np.ndarray]:
    pose = pose or {}
    out: dict[str, np.ndarray] = {}

    def visit(bone, parent_m):
        p = pose.get(bone.name, {})
        px, py, pz = bone.pivot
        dx, dy, dz = p.get("pos", (0.0, 0.0, 0.0))
        rx, ry, rz = (math.radians(a + b) for a, b in zip(bone.rot, p.get("rot", (0.0, 0.0, 0.0))))
        sx, sy, sz = p.get("scale", (1.0, 1.0, 1.0))
        # posVec flips y (animation +y is up, model space +y is down).
        m = parent_m @ _t((px + dx) / 16, (py - dy) / 16, (pz + dz) / 16) @ _rz(rz) @ _ry(ry) @ _rx(rx) @ _s(sx, sy, sz)
        out[bone.name] = m
        for c in bone.children:
            visit(c, m)

    visit(rig.root, np.eye(4))
    return out


def _faces(cube):
    """Face -> 4 corners (LT, RT, LB, RB) in bone space (pixels), matching the texture region orientation."""
    ox, oy, oz = cube.origin
    w, h, d = cube.size
    g = cube.inflate
    x0, y0, z0 = ox - g, oy - g, oz - g
    x1, y1, z1 = ox + w + g, oy + h + g, oz + d + g
    if cube.mirror:
        x0, x1 = x1, x0
    return {
        "top": [(x0, y0, z1), (x1, y0, z1), (x0, y0, z0), (x1, y0, z0)],
        "bottom": [(x0, y1, z1), (x1, y1, z1), (x0, y1, z0), (x1, y1, z0)],
        "front": [(x0, y0, z0), (x1, y0, z0), (x0, y1, z0), (x1, y1, z0)],
        "back": [(x1, y0, z1), (x0, y0, z1), (x1, y1, z1), (x0, y1, z1)],
        "right": [(x0, y0, z1), (x0, y0, z0), (x0, y1, z1), (x0, y1, z0)],
        "left": [(x1, y0, z0), (x1, y0, z1), (x1, y1, z0), (x1, y1, z1)],
    }


def render(rig: Rig, base: Image.Image, glow: Image.Image | None = None, pose: dict | None = None,
           yaw: float = -30.0, pitch: float = 18.0, size: int = 420, scale: float | None = None,
           bg=(44, 46, 54, 255), floor: bool = True, fit: tuple | None = None) -> Image.Image:
    """fit = (centre_x, centre_y, pixels_per_block, floor_y) fixes the framing (see frames())."""
    tex = np.asarray(base.convert("RGBA"), dtype=np.float32)
    gl = np.asarray(glow.convert("RGBA"), dtype=np.float32) if glow is not None else None
    th, tw = tex.shape[:2]
    mats = bone_matrices(rig, pose)
    # Model space -> world (the renderer scales by -1, -1, 1), then the camera.
    view = _rx(math.radians(-pitch)) @ _ry(math.radians(yaw)) @ _s(-1, -1, 1)
    quads = []
    for bone, cube in rig.cubes():
        m = view @ mats[bone.name]
        regions = cube.regions()
        for face, corners in _faces(cube).items():
            x0, y0, w, h = regions[face]
            if w == 0 or h == 0:
                continue
            pts = np.array([(m @ np.array([c[0] / 16, c[1] / 16, c[2] / 16, 1.0]))[:3] for c in corners])
            uv = np.array([(x0, y0), (x0 + w, y0), (x0, y0 + h), (x0 + w, y0 + h)], float)
            quads.append((pts, uv))
    if not quads:
        return Image.new("RGBA", (size, size), bg)
    allp = np.concatenate([q[0] for q in quads])
    if fit is None:
        fit = fit_of(allp, size, scale)
    centre = np.array(fit[:2])
    k = fit[2]
    lo_y = fit[3]
    img = np.zeros((size, size, 4), np.float32)
    img[:] = bg
    depth = np.full((size, size), np.inf, np.float32)
    if floor:
        # A soft contact shadow under the creature.
        yy, xx = np.mgrid[0:size, 0:size]
        fy = size / 2 + (centre[1] - lo_y) * k
        r = (allp[:, 0].max() - allp[:, 0].min()) * k * 0.55
        e = ((xx - size / 2) / max(r, 1)) ** 2 + ((yy - fy) / max(r * 0.28, 1)) ** 2
        img[..., :3] *= np.clip(0.55 + 0.45 * e, 0.55, 1.0)[..., None]

    def screen(p):
        # Viewer looks toward +z; screen right is world -x after the flip, screen down is -y.
        return np.array([size / 2 + (p[0] - centre[0]) * k, size / 2 - (p[1] - centre[1]) * k, p[2]])

    for pts, uv in quads:
        sp = np.array([screen(p) for p in pts])
        n = np.cross(pts[1] - pts[0], pts[2] - pts[0])
        nn = np.linalg.norm(n)
        shade = 1.0 if nn == 0 else 0.6 + 0.4 * abs(float(np.dot(n / nn, LIGHT)))
        for tri in ((0, 1, 3), (0, 3, 2)):
            a, b, c = (sp[i] for i in tri)
            ua, ub, uc = (uv[i] for i in tri)
            minx, maxx = int(max(0, math.floor(min(a[0], b[0], c[0])))), int(min(size - 1, math.ceil(max(a[0], b[0], c[0]))))
            miny, maxy = int(max(0, math.floor(min(a[1], b[1], c[1])))), int(min(size - 1, math.ceil(max(a[1], b[1], c[1]))))
            if minx > maxx or miny > maxy:
                continue
            ys, xs = np.mgrid[miny:maxy + 1, minx:maxx + 1]
            px, py = xs + 0.5, ys + 0.5
            den = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
            if abs(den) < 1e-9:
                continue
            l1 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / den
            l2 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / den
            l3 = 1 - l1 - l2
            inside = (l1 >= -1e-6) & (l2 >= -1e-6) & (l3 >= -1e-6)
            if not inside.any():
                continue
            z = l1 * a[2] + l2 * b[2] + l3 * c[2]
            u = l1 * ua[0] + l2 * ub[0] + l3 * uc[0]
            v = l1 * ua[1] + l2 * ub[1] + l3 * uc[1]
            ti = np.clip(np.floor(u - 1e-4).astype(int), 0, tw - 1)
            tj = np.clip(np.floor(v - 1e-4).astype(int), 0, th - 1)
            col = tex[tj, ti]
            sub = depth[miny:maxy + 1, minx:maxx + 1]
            ok = inside & (col[..., 3] >= 128) & (z < sub)
            if not ok.any():
                continue
            rgb = col[..., :3] * shade
            if gl is not None:
                g = gl[tj, ti]
                rgb = np.minimum(255, rgb + g[..., :3] * (g[..., 3:4] / 255.0))
            region = img[miny:maxy + 1, minx:maxx + 1]
            region[ok, :3] = rgb[ok]
            region[ok, 3] = 255
            sub[ok] = z[ok]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGBA")


def fit_of(points: np.ndarray, size: int, scale: float | None = None, margin: float = 0.82) -> tuple:
    lo, hi = points[:, :2].min(0), points[:, :2].max(0)
    span = max(hi - lo) or 1.0
    k = scale or (size * margin / span)
    c = (lo + hi) / 2
    return (float(c[0]), float(c[1]), float(k), float(lo[1]))


def _points(rig: Rig, pose, yaw, pitch) -> np.ndarray:
    mats = bone_matrices(rig, pose)
    view = _rx(math.radians(-pitch)) @ _ry(math.radians(yaw)) @ _s(-1, -1, 1)
    pts = []
    for bone, cube in rig.cubes():
        m = view @ mats[bone.name]
        for corners in _faces(cube).values():
            for c in corners:
                pts.append((m @ np.array([c[0] / 16, c[1] / 16, c[2] / 16, 1.0]))[:3])
    return np.array(pts)


def frames(rig: Rig, base, glow, anims, n: int = 8, length: float | None = None, yaw: float = -30.0,
           pitch: float = 18.0, size: int = 300, **kw) -> list[Image.Image]:
    """n evenly spaced frames of the animation(s), framed so the whole motion stays in view."""
    from .anim import pose_at
    anims = anims if isinstance(anims, list) else [anims]
    length = length or max(a.length for a in anims)
    poses = [pose_at(anims, length * i / n) for i in range(n)]
    allp = np.concatenate([_points(rig, p, yaw, pitch) for p in poses])
    fit = fit_of(allp, size, margin=0.86)
    return [render(rig, base, glow, pose=p, yaw=yaw, pitch=pitch, size=size, fit=fit, **kw) for p in poses]


def strip(images: list[Image.Image], gap: int = 4, bg=(30, 31, 36, 255)) -> Image.Image:
    w = sum(i.width for i in images) + gap * (len(images) + 1)
    h = max(i.height for i in images) + gap * 2
    out = Image.new("RGBA", (w, h), bg)
    x = gap
    for i in images:
        out.alpha_composite(i, (x, gap))
        x += i.width + gap
    return out
