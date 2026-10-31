#!/usr/bin/env python3
"""Review helpers: contact sheets of textures and 3D renders of block models.

  python3 tools/assets/preview.py textures block            # every texture in textures/block, 8x
  python3 tools/assets/preview.py textures item --scale 10
  python3 tools/assets/preview.py models glowcap bouncecap  # 3D renders of models/block/<name>.json
Output goes to tools/assets/build/previews/. Set SS_VANILLA_ASSETS to resolve vanilla parent models.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from PIL import Image  # noqa: E402

from ss.paths import BUILD, TEXTURES  # noqa: E402
from ss.pixel import sheet  # noqa: E402


def textures(folder: str, scale: int) -> Path:
    files = sorted((TEXTURES / folder).glob("*.png"))
    images = [Image.open(f).convert("RGBA") for f in files]
    images = [i.crop((0, 0, i.width, min(i.height, i.width))) for i in images]  # first frame of animations
    out = BUILD / "previews" / f"textures_{folder.replace('/', '_')}.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    sheet(images, factor=scale, columns=10).save(out)
    print(out, f"({len(images)} textures)")
    return out


def models(names: list[str]) -> Path:
    from ss import render3d
    cells = [(n, render3d.render_image(n if ":" in n else f"spore_and_stem:block/{n}", scale=12)) for n in names]
    out = BUILD / "previews" / ("models_" + "_".join(n.split("/")[-1] for n in names[:4]) + ".png")
    out.parent.mkdir(parents=True, exist_ok=True)
    render3d.label_sheet(cells, out)
    print(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", choices=["textures", "models"])
    ap.add_argument("names", nargs="+")
    ap.add_argument("--scale", type=int, default=8)
    a = ap.parse_args()
    if a.kind == "textures":
        for n in a.names:
            textures(n, a.scale)
    else:
        models(a.names)
