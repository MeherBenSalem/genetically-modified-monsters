"""Tiny software renderer for Minecraft Java block-model JSON (review tool). Adapted from Sprout & Soil's assetgen.

It resolves ``parent`` chains (our ``assets/spore_and_stem/models`` first, then the
extracted vanilla reference assets), merges ``textures`` / ``display``, resolves ``#var``
texture references and rasterises every element face with an orthographic camera:

* per-face ``uv`` (explicit or Minecraft's automatic UV), face ``rotation``, mirrored UVs
* element ``rotation`` (origin / axis / angle / rescale)
* cutout alpha (texels with alpha < 128 are skipped), back-face culling
* Minecraft-like directional shading (up 1.0, north/south 0.8, east/west 0.6, down 0.5)
* faces sorted back-to-front (painter's algorithm) plus a depth buffer so intersecting
  or interpenetrating elements still resolve correctly

Public API::

    render(model_path_or_id, out_png, textures_overrides=None, yaw=225, pitch=30, scale=8)
    render_image(...) -> PIL.Image          # same, without saving
    render_gui(model, out_png=None, ppu=4)   # what the item looks like in an inventory slot
    load_model(model) -> ResolvedModel       # merged textures/elements/display
    validate_model(path_or_dict, provided_vars=()) -> list[str]

``model_path_or_id`` may be a filesystem path, ``"spore_and_stem:block/cooking_pot"``,
``"minecraft:block/cake"`` or a bare id (``"cooking_pot"`` -> ``spore_and_stem:block/cooking_pot``).
``textures_overrides`` maps texture variables to references or file paths and is applied on top
of the resolved model (handy for previewing templates such as ``template_pie_0``).
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

from .paths import ASSETS, VANILLA_REF

MOD_ID = "spore_and_stem"

def vanilla_root() -> Path | None:
    for cand in (VANILLA_REF,):
        if cand and Path(cand).is_dir():
            p = Path(cand)
            # accept either .../assets/minecraft or .../assets or the extracted jar root
            for sub in (p, p / "minecraft", p / "assets" / "minecraft"):
                if (sub / "models").is_dir():
                    return sub
    return None


def _ns_root(ns: str) -> Path | None:
    if ns == MOD_ID:
        return ASSETS
    if ns == "minecraft":
        return vanilla_root()
    return None


def _split(ref: str, default_ns: str = "minecraft") -> tuple[str, str]:
    if ":" in ref:
        ns, p = ref.split(":", 1)
        return ns, p
    return default_ns, ref


# --------------------------------------------------------------------------- model loading


@dataclass
class ResolvedModel:
    name: str
    textures: dict[str, str] = field(default_factory=dict)
    elements: list[dict] = field(default_factory=list)
    display: dict[str, dict] = field(default_factory=dict)
    chain: list[str] = field(default_factory=list)
    ambientocclusion: bool = True

    def texture_ref(self, var_or_ref: str, _depth: int = 0) -> str | None:
        """Resolve ``#var`` chains to a final texture reference (or None)."""
        if _depth > 16:
            return None
        if var_or_ref.startswith("#"):
            key = var_or_ref[1:]
            if key not in self.textures:
                return None
            return self.texture_ref(self.textures[key], _depth + 1)
        return var_or_ref


def _model_file(ref: str | Path, default_ns: str) -> Path:
    if isinstance(ref, Path) or (isinstance(ref, str) and (ref.endswith(".json") or os.sep in ref and Path(ref).exists())):
        return Path(ref)
    ns, p = _split(ref, default_ns)
    root = _ns_root(ns)
    if root is None:
        raise FileNotFoundError(f"no asset root for namespace {ns!r} (set SS_VANILLA_ASSETS for minecraft)")
    return root / "models" / f"{p}.json"


def _ref_name(ref: str | Path) -> str:
    if isinstance(ref, Path):
        return ref.stem
    return ref


def load_model(model: str | Path | dict, textures_overrides: dict[str, str] | None = None) -> ResolvedModel:
    """Load a model and merge its parent chain."""
    if isinstance(model, str) and ":" not in model and "/" not in model and not model.endswith(".json"):
        model = f"{MOD_ID}:block/{model}"
    chain_data: list[tuple[str, dict]] = []
    if isinstance(model, dict):
        data, name, default_ns = model, "<dict>", MOD_ID
    else:
        path = _model_file(model, MOD_ID)
        data, name = json.loads(Path(path).read_text()), _ref_name(model)
        default_ns = "minecraft" if "minecraft" in str(path) and MOD_ID not in str(path) else MOD_ID
    chain_data.append((name, data))
    seen = {name}
    while "parent" in data:
        parent = data["parent"]
        if parent.startswith("builtin/"):
            break
        # bare parents inside vanilla files mean minecraft:, inside ours we always namespace
        ns, p = _split(parent, "minecraft")
        pref = f"{ns}:{p}"
        if pref in seen:
            raise ValueError(f"parent cycle at {pref}")
        seen.add(pref)
        data = json.loads(_model_file(pref, "minecraft").read_text())
        chain_data.append((pref, data))
    rm = ResolvedModel(name=name, chain=[n for n, _ in chain_data])
    for n, d in reversed(chain_data):          # root parent first, child last wins
        rm.textures.update(d.get("textures", {}))
        for k, v in d.get("display", {}).items():
            rm.display[k] = v
        if "ambientocclusion" in d:
            rm.ambientocclusion = d["ambientocclusion"]
    for n, d in chain_data:                    # nearest elements win
        if "elements" in d:
            rm.elements = d["elements"]
            break
    if textures_overrides:
        rm.textures.update(textures_overrides)
    return rm


# --------------------------------------------------------------------------- textures

_TEX_CACHE: dict[str, np.ndarray] = {}


def _missing_texture() -> np.ndarray:
    a = np.zeros((16, 16, 4), np.uint8)
    a[..., 3] = 255
    for y in range(16):
        for x in range(16):
            if (x // 8 + y // 8) % 2 == 0:
                a[y, x, :3] = (248, 0, 248)
    return a


def load_texture(ref: str) -> np.ndarray:
    """``ref`` is ``ns:path`` (relative to textures/, no extension) or a file path."""
    if ref in _TEX_CACHE:
        return _TEX_CACHE[ref]
    path: Path | None
    if ref.endswith(".png") or os.sep in ref and Path(ref).exists():
        path = Path(ref)
    else:
        ns, p = _split(ref, "minecraft")
        root = _ns_root(ns)
        path = root / "textures" / f"{p}.png" if root else None
    if path is None or not path.exists():
        arr = _missing_texture()
    else:
        im = Image.open(path).convert("RGBA")
        w, h = im.size
        if h > w and h % w == 0:     # animated strip -> first frame
            im = im.crop((0, 0, w, w))
        arr = np.array(im)
    _TEX_CACHE[ref] = arr
    return arr


def clear_texture_cache() -> None:
    _TEX_CACHE.clear()


def texture_exists(ref: str) -> bool:
    ns, p = _split(ref, "minecraft")
    root = _ns_root(ns)
    return bool(root and (root / "textures" / f"{p}.png").exists())


# --------------------------------------------------------------------------- geometry

DIRS = ("down", "up", "north", "south", "west", "east")
NORMALS = {"down": (0, -1, 0), "up": (0, 1, 0), "north": (0, 0, -1), "south": (0, 0, 1),
           "west": (-1, 0, 0), "east": (1, 0, 0)}


def face_corners(f, t, d):
    """Corners TL, TR, BL of a face in texture orientation (BR = TR + BL - TL)."""
    (x1, y1, z1), (x2, y2, z2) = f, t
    if d == "north":
        return (x2, y2, z1), (x1, y2, z1), (x2, y1, z1)
    if d == "south":
        return (x1, y2, z2), (x2, y2, z2), (x1, y1, z2)
    if d == "west":
        return (x1, y2, z1), (x1, y2, z2), (x1, y1, z1)
    if d == "east":
        return (x2, y2, z2), (x2, y2, z1), (x2, y1, z2)
    if d == "up":
        return (x1, y2, z1), (x2, y2, z1), (x1, y2, z2)
    if d == "down":
        return (x1, y1, z2), (x2, y1, z2), (x1, y1, z1)
    raise ValueError(d)


def auto_uv(f, t, d):
    (x1, y1, z1), (x2, y2, z2) = f, t
    return {
        "down": [x1, 16 - z2, x2, 16 - z1],
        "up": [x1, z1, x2, z2],
        "north": [16 - x2, 16 - y2, 16 - x1, 16 - y1],
        "south": [x1, 16 - y2, x2, 16 - y1],
        "west": [z1, 16 - y2, z2, 16 - y1],
        "east": [16 - z2, 16 - y2, 16 - z1, 16 - y1],
    }[d]


def _axis_rot(axis: str, deg: float) -> np.ndarray:
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    if axis == "x":
        return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if axis == "y":
        return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def euler_xyz(rx: float, ry: float, rz: float) -> np.ndarray:
    """Matrix for Minecraft display rotation (JOML rotationXYZ: v' = Rx Ry Rz v)."""
    return _axis_rot("x", rx) @ _axis_rot("y", ry) @ _axis_rot("z", rz)


def element_transform(el: dict):
    """Return (fn(points)->points, normal_matrix) for an element's rotation."""
    rot = el.get("rotation")
    if not rot or not rot.get("angle"):
        return (lambda p: p), np.eye(3)
    axis, ang = rot["axis"], float(rot["angle"])
    o = np.array(rot.get("origin", [8, 8, 8]), float)
    R = _axis_rot(axis, ang)
    scale = np.ones(3)
    if rot.get("rescale"):
        k = 1 / math.cos(math.radians(abs(ang)))
        scale = np.array([1.0 if axis == "x" else k, 1.0 if axis == "y" else k, 1.0 if axis == "z" else k])

    def fn(p):
        return ((np.asarray(p, float) - o) @ R.T) * scale + o

    return fn, R


def shade_for(n) -> float:
    """Minecraft-style diffuse shading for an (approximately unit) model-space normal."""
    x, y, z = n
    return min(1.0, x * x * 0.6 + y * y * ((3 + y) / 4) + z * z * 0.8)


@dataclass
class _Face:
    A: np.ndarray       # screen (x, y, depth) of TL
    U: np.ndarray       # TR - TL
    V: np.ndarray       # BL - TL
    tex: np.ndarray
    uv: tuple[float, float, float, float]
    rot: int
    shade: float
    order: int

    @property
    def depth(self) -> float:
        return float(self.A[2] + 0.5 * self.U[2] + 0.5 * self.V[2])


def collect_faces(rm: ResolvedModel, view: np.ndarray, warn: list[str] | None = None,
                  offset=(8.0, 8.0, 8.0), post_scale=(1.0, 1.0, 1.0), translation=(0.0, 0.0, 0.0)):
    """Transform every face into view space (x right, y up, z toward the camera)."""
    faces: list[_Face] = []
    order = 0
    off = np.array(offset, float)
    ps = np.array(post_scale, float)
    tr = np.array(translation, float)
    for el in rm.elements:
        fn, nR = element_transform(el)
        f, t = el["from"], el["to"]
        for d, face in el.get("faces", {}).items():
            order += 1
            tl, tr_, bl = (fn(np.array(c, float)) for c in face_corners(f, t, d))
            pts = np.stack([tl, tr_, bl])
            n_model = nR @ np.array(NORMALS[d], float)
            v = ((pts - off) * ps) @ view.T + tr
            n_view = view @ n_model
            if n_view[2] <= 1e-6:      # back-face culling
                continue
            ref = rm.texture_ref(face.get("texture", ""))
            if ref is None:
                if warn is not None:
                    warn.append(f"unresolved texture {face.get('texture')} on {d}")
                tex = _missing_texture()
            else:
                tex = load_texture(ref)
            uv = face.get("uv") or auto_uv(f, t, d)
            sh = shade_for(n_model) if face.get("shade", el.get("shade", True)) else 1.0
            faces.append(_Face(v[0], v[1] - v[0], v[2] - v[0], tex, tuple(uv), int(face.get("rotation", 0)) % 360,
                               sh, order))
    return faces


def _rasterise(faces: list[_Face], w: int, h: int, ppu: float, cx: float, cy: float,
               bg=(0, 0, 0, 0)) -> Image.Image:
    """Screen mapping: px = cx + x * ppu, py = cy - y * ppu."""
    col = np.zeros((h, w, 4), np.float32)
    col[...] = bg
    zbuf = np.full((h, w), -1e9, np.float32)
    faces = sorted(faces, key=lambda fc: (fc.depth, fc.order))
    for fc in faces:
        A = np.array([cx + fc.A[0] * ppu, cy - fc.A[1] * ppu])
        U = np.array([fc.U[0] * ppu, -fc.U[1] * ppu])
        V = np.array([fc.V[0] * ppu, -fc.V[1] * ppu])
        det = U[0] * V[1] - U[1] * V[0]
        if abs(det) < 1e-6:
            continue
        xs = [A[0], A[0] + U[0], A[0] + V[0], A[0] + U[0] + V[0]]
        ys = [A[1], A[1] + U[1], A[1] + V[1], A[1] + U[1] + V[1]]
        x0, x1 = max(0, int(math.floor(min(xs)))), min(w, int(math.ceil(max(xs))) + 1)
        y0, y1 = max(0, int(math.floor(min(ys)))), min(h, int(math.ceil(max(ys))) + 1)
        if x0 >= x1 or y0 >= y1:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1) + 0.5, np.arange(y0, y1) + 0.5)
        dx, dy = gx - A[0], gy - A[1]
        s = (dx * V[1] - dy * V[0]) / det
        t = (U[0] * dy - U[1] * dx) / det
        inside = (s >= 0) & (s < 1) & (t >= 0) & (t < 1)
        if not inside.any():
            continue
        depth = fc.A[2] + s * fc.U[2] + t * fc.V[2]
        # texture rotation (clockwise)
        if fc.rot == 90:
            su, tv = t, 1 - s
        elif fc.rot == 180:
            su, tv = 1 - s, 1 - t
        elif fc.rot == 270:
            su, tv = 1 - t, s
        else:
            su, tv = s, t
        u1, v1, u2, v2 = fc.uv
        u = u1 + su * (u2 - u1)
        v = v1 + tv * (v2 - v1)
        th, tw = fc.tex.shape[:2]
        # nudge toward the inside of the sampled rectangle to avoid bleeding on exact edges
        ix = np.clip(np.floor(u * tw / 16 - 1e-4 * np.sign(u2 - u1)), 0, tw - 1).astype(int)
        iy = np.clip(np.floor(v * th / 16 - 1e-4 * np.sign(v2 - v1)), 0, th - 1).astype(int)
        texel = fc.tex[iy, ix].astype(np.float32)
        sub_z = zbuf[y0:y1, x0:x1]
        mask = inside & (texel[..., 3] >= 128) & (depth >= sub_z - 1e-3)
        if not mask.any():
            continue
        rgb = texel[..., :3] * fc.shade
        sub_c = col[y0:y1, x0:x1]
        sub_c[mask, :3] = rgb[mask]
        sub_c[mask, 3] = 255
        sub_z[mask] = depth[mask]
    return Image.fromarray(np.clip(col, 0, 255).astype(np.uint8), "RGBA")


def _downsample(im: Image.Image, f: int) -> Image.Image:
    if f == 1:
        return im
    a = np.asarray(im).astype(np.float32)
    h, w = a.shape[0] // f, a.shape[1] // f
    a = a[:h * f, :w * f].reshape(h, f, w, f, 4)
    alpha = a[..., 3:4] / 255.0
    prem = (a[..., :3] * alpha).sum(axis=(1, 3))
    asum = alpha.sum(axis=(1, 3))
    rgb = np.where(asum > 0, prem / np.maximum(asum, 1e-6), 0)
    out = np.concatenate([rgb, asum / (f * f) * 255], axis=-1)
    return Image.fromarray(np.clip(out + 0.5, 0, 255).astype(np.uint8), "RGBA")


def _bounds(faces: list[_Face]):
    pts = []
    for fc in faces:
        for p in (fc.A, fc.A + fc.U, fc.A + fc.V, fc.A + fc.U + fc.V):
            pts.append(p[:2])
    if not pts:
        return -8, -8, 8, 8
    arr = np.array(pts)
    return arr[:, 0].min(), arr[:, 1].min(), arr[:, 0].max(), arr[:, 1].max()


def render_image(model, textures_overrides=None, yaw: float = 225, pitch: float = 30, scale: int = 8,
                 ss: int = 2, margin: int = 6, bg=(0, 0, 0, 0), warn: list[str] | None = None,
                 size: tuple[int, int] | None = None) -> Image.Image:
    """Isometric-style render auto-fitted to its own bounding box.

    ``scale`` is output pixels per model unit (1/16 block). ``size`` forces a canvas size
    (the model is centred) so several renders can share a common scale.
    """
    rm = model if isinstance(model, ResolvedModel) else load_model(model, textures_overrides)
    if isinstance(model, ResolvedModel) and textures_overrides:
        rm.textures.update(textures_overrides)
    view = euler_xyz(pitch, yaw, 0)
    faces = collect_faces(rm, view, warn)
    x0, y0, x1, y1 = _bounds(faces)
    ppu = scale * ss
    if size is None:
        w = int(math.ceil((x1 - x0) * scale)) + 2 * margin
        h = int(math.ceil((y1 - y0) * scale)) + 2 * margin
    else:
        w, h = size
    W, H = w * ss, h * ss
    cx = W / 2 - (x0 + x1) / 2 * ppu
    cy = H / 2 + (y0 + y1) / 2 * ppu
    im = _rasterise(faces, W, H, ppu, cx, cy, bg)
    return _downsample(im, ss)


def render(model_path_or_id, out_png, textures_overrides=None, yaw: float = 225, pitch: float = 30,
           scale: int = 8, ss: int = 2, bg=(0, 0, 0, 0)) -> Path:
    im = render_image(model_path_or_id, textures_overrides, yaw=yaw, pitch=pitch, scale=scale, ss=ss, bg=bg)
    out = Path(out_png)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out)
    return out


def render_display(model, context: str = "gui", textures_overrides=None, ppu: int = 4, ss: int = 1,
                   bg=(0, 0, 0, 0)) -> Image.Image:
    """Render the model through its ``display.<context>`` transform into a 16x16-unit frame
    (an inventory slot for ``gui``), ``ppu`` output pixels per slot pixel."""
    rm = model if isinstance(model, ResolvedModel) else load_model(model, textures_overrides)
    disp = rm.display.get(context, {})
    rot = disp.get("rotation", [0, 0, 0])
    tr = disp.get("translation", [0, 0, 0])
    sc = disp.get("scale", [1, 1, 1])
    view = euler_xyz(*rot)
    faces = collect_faces(rm, view, post_scale=sc, translation=tr)
    W = H = 16 * ppu * ss
    im = _rasterise(faces, W, H, ppu * ss, W / 2, H / 2, bg)
    return _downsample(im, ss)


def render_gui(model, out_png=None, textures_overrides=None, ppu: int = 4) -> Image.Image:
    im = render_display(model, "gui", textures_overrides, ppu=ppu)
    if out_png:
        Path(out_png).parent.mkdir(parents=True, exist_ok=True)
        im.save(out_png)
    return im


def combine(parts: list[tuple], name: str = "scene") -> ResolvedModel:
    """Merge several models into one scene: ``parts`` = [(model, (dx, dy, dz)[, overrides]), ...].

    Texture variables are namespaced per part so they cannot clash; element rotations are
    offset along with the geometry. Useful for previews such as a pot standing on a campfire."""
    out = ResolvedModel(name=name)
    for i, part in enumerate(parts):
        model, off = part[0], part[1]
        over = part[2] if len(part) > 2 else None
        rm = model if isinstance(model, ResolvedModel) else load_model(model, over)
        prefix = f"p{i}_"
        for k in rm.textures:
            ref = rm.texture_ref("#" + k)
            if ref is not None:
                out.textures[prefix + k] = ref
        for el in rm.elements:
            e = json.loads(json.dumps(el))
            e["from"] = [c + o for c, o in zip(el["from"], off)]
            e["to"] = [c + o for c, o in zip(el["to"], off)]
            if e.get("rotation"):
                e["rotation"]["origin"] = [c + o for c, o in zip(e["rotation"].get("origin", [8, 8, 8]), off)]
            for f in e.get("faces", {}).values():
                t = f.get("texture", "")
                if t.startswith("#"):
                    f["texture"] = "#" + prefix + t[1:]
                if "uv" not in f:   # keep the auto-UV of the original position
                    d = [k for k, v in e["faces"].items() if v is f][0]
                    f["uv"] = auto_uv(el["from"], el["to"], d)
            out.elements.append(e)
    return out


# --------------------------------------------------------------------------- display fitting


def model_corners(elements: list[dict]) -> np.ndarray:
    pts = []
    for el in elements:
        fn, _ = element_transform(el)
        (x1, y1, z1), (x2, y2, z2) = el["from"], el["to"]
        for x in (x1, x2):
            for y in (y1, y2):
                for z in (z1, z2):
                    pts.append(fn(np.array([x, y, z], float)))
    return np.array(pts)


def fit_display(elements: list[dict], rotation, extent: float = 14.0, max_scale: float = 1.0,
                center=(0.0, 0.0)) -> dict:
    """Compute a display entry (rotation/translation/scale) that fits the model's projected
    bounding box into ``extent`` slot pixels, centred on ``center`` (x, y in slot pixels)."""
    view = euler_xyz(*rotation)
    pts = (model_corners(elements) - 8.0) @ view.T
    x0, y0 = pts[:, 0].min(), pts[:, 1].min()
    x1, y1 = pts[:, 0].max(), pts[:, 1].max()
    s = min(max_scale, extent / max(x1 - x0, y1 - y0))
    s = math.floor(s * 1000) / 1000
    tx = center[0] - (x0 + x1) / 2 * s
    ty = center[1] - (y0 + y1) / 2 * s
    return {"rotation": [float(r) for r in rotation], "translation": [round(tx, 2), round(ty, 2), 0],
            "scale": [s, s, s]}


# --------------------------------------------------------------------------- validation


def validate_model(model: Path | str | dict, provided_vars=(), check_files: bool = True) -> list[str]:
    """Structural checks: JSON loads, coordinates in -16..32, uv in 0..16, rotations legal,
    every face texture resolves (``provided_vars`` lists vars a child model will supply)."""
    errs: list[str] = []
    try:
        if isinstance(model, dict):
            data = model
        else:
            data = json.loads(Path(model).read_text())
    except Exception as e:  # noqa: BLE001
        return [f"invalid JSON: {e}"]
    try:
        rm = load_model(data if isinstance(model, dict) else Path(model))
    except Exception as e:  # noqa: BLE001
        return [f"cannot resolve parents: {e}"]
    tex = dict(rm.textures)
    for v in provided_vars:
        tex.setdefault(v, f"{MOD_ID}:__provided__/{v}")
    rm.textures = tex
    if "particle" not in tex:
        errs.append("no particle texture")
    if not rm.elements:
        errs.append("no elements")
    for i, el in enumerate(rm.elements):
        for k in ("from", "to"):
            if any(not (-16 <= c <= 32) for c in el[k]):
                errs.append(f"element {i}: {k} out of range {el[k]}")
        if any(a > b for a, b in zip(el["from"], el["to"])):
            errs.append(f"element {i}: from > to")
        rot = el.get("rotation")
        if rot:
            if rot.get("axis") not in ("x", "y", "z"):
                errs.append(f"element {i}: bad rotation axis")
            if rot.get("angle") not in (-45, -22.5, 0, 22.5, 45):
                errs.append(f"element {i}: bad rotation angle {rot.get('angle')}")
        if not el.get("faces"):
            errs.append(f"element {i}: no faces")
        for d, face in el.get("faces", {}).items():
            if d not in DIRS:
                errs.append(f"element {i}: bad face {d}")
            uv = face.get("uv")
            if uv is not None and (len(uv) != 4 or any(not (0 <= c <= 16) for c in uv)):
                errs.append(f"element {i} {d}: uv out of range {uv}")
            if face.get("rotation", 0) not in (0, 90, 180, 270):
                errs.append(f"element {i} {d}: bad face rotation")
            ref = rm.texture_ref(face.get("texture", ""))
            if ref is None:
                errs.append(f"element {i} {d}: unresolved texture {face.get('texture')}")
            elif check_files and "__provided__" not in ref and not texture_exists(ref):
                errs.append(f"element {i} {d}: missing texture file for {ref}")
    pref = rm.texture_ref("#particle")
    if pref is None:
        errs.append("particle unresolved")
    elif check_files and "__provided__" not in pref and not texture_exists(pref):
        errs.append(f"missing particle texture {pref}")
    for k in ("gui", "ground", "fixed", "thirdperson_righthand", "firstperson_righthand", "head"):
        if k not in rm.display:
            errs.append(f"display.{k} missing")
    return errs


# --------------------------------------------------------------------------- sheets


def label_sheet(cells: list[tuple[str, Image.Image]], out: Path, cols: int = 4, bg=(52, 54, 60, 255),
                pad: int = 10, title: str | None = None) -> Path:
    cw = max(im.width for _, im in cells) + pad * 2
    ch = max(im.height for _, im in cells) + pad * 2 + 14
    rows = (len(cells) + cols - 1) // cols
    top = 20 if title else 0
    sheet = Image.new("RGBA", (cw * cols, ch * rows + top), bg)
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad, 4), title, fill=(235, 235, 235, 255))
    for i, (name, im) in enumerate(cells):
        x = (i % cols) * cw + (cw - im.width) // 2
        y = top + (i // cols) * ch + pad + (ch - pad * 2 - 14 - im.height) // 2
        sheet.alpha_composite(im, (x, y))
        d.text(((i % cols) * cw + pad, top + (i // cols) * ch + ch - 16), name, fill=(220, 220, 220, 255))
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(out)
    return out


if __name__ == "__main__":  # quick smoke test against vanilla models
    import sys

    from .paths import BUILD

    target = sys.argv[1] if len(sys.argv) > 1 else "minecraft:block/cauldron"
    out = BUILD / "previews" / "render3d_test.png"
    render(target, out)
    print(out)
