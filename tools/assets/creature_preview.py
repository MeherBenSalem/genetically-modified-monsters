#!/usr/bin/env python3
"""Previews a creature without the game: the rest pose from four sides and every animation as a frame strip.

  python3 tools/assets/creature_preview.py sporeling                 # all animations
  python3 tools/assets/creature_preview.py sporeling --anims walk idle --frames 10 --gif

Output: tools/assets/build/previews/entities/<name>_*.png (and .gif with --gif).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ss.entities import build, load  # noqa: E402
from ss.entities.render import frames, render, strip  # noqa: E402
from ss.paths import BUILD  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("creature")
    ap.add_argument("--anims", nargs="*")
    ap.add_argument("--frames", type=int, default=8)
    ap.add_argument("--texture", help="texture key from textures(), default: the first")
    ap.add_argument("--gif", action="store_true")
    a = ap.parse_args()
    module = load(a.creature)
    rig, anims = build(module)
    textures = module.textures(rig)
    key = a.texture or next(k for k in textures if not k.endswith("_glow"))
    base = textures[key]
    glow = textures.get(key + "_glow") or textures.get(f"{module.NAME}_glow")
    out = BUILD / "previews" / "entities"
    out.mkdir(parents=True, exist_ok=True)
    views = [render(rig, base, glow, yaw=y, pitch=p, size=360) for y, p in ((-35, 15), (35, 15), (180, 10), (-90, 60))]
    strip(views).save(out / f"{module.NAME}_rest.png")
    base.resize((base.width * 6, base.height * 6), 0).save(out / f"{module.NAME}_texture.png")
    print(out / f"{module.NAME}_rest.png")
    for anim in anims:
        if a.anims and anim.name not in a.anims:
            continue
        imgs = frames(rig, base, glow, anim, n=a.frames, size=260)
        strip(imgs).save(out / f"{module.NAME}_{anim.name}.png")
        if a.gif:
            imgs[0].save(out / f"{module.NAME}_{anim.name}.gif", save_all=True, append_images=imgs[1:],
                         duration=int(anim.length * 1000 / a.frames), loop=0, disposal=2)
        print(out / f"{module.NAME}_{anim.name}.png")


if __name__ == "__main__":
    main()
