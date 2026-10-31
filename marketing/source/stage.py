"""Shared staging helpers for capture.py (and for exploring camera positions interactively)."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools' / 'qa'))
from client import PLAYER, Session  # noqa: E402

OUT = ROOT / 'marketing' / 'images' / 'screenshots'
GIFS = ROOT / 'marketing' / 'images' / 'gifs'
WORK = Path(os.environ.get('SS_CAPTURE_WORK', '/tmp/spore-and-stem-capture'))
_s: Session | None = None


def s() -> Session:
    global _s
    if _s is None:
        _s = Session()
    return _s


def cmd(*commands):
    return s().cmd(*commands)


def view(x, y, z, tx, ty, tz, wait=3.0):
    s().tp(x, y, z, facing=(tx, ty, tz))
    time.sleep(wait)


def grab(name, hud=False) -> Path:
    """A raw capture into the work folder (for exploring)."""
    s().hud(hud)
    time.sleep(0.4)
    WORK.mkdir(parents=True, exist_ok=True)
    png = s().shot(WORK / f'{name}.png')
    s().hud(True)
    return png


def shot(name, hud=False) -> Path:
    """A final capture: marketing/images/screenshots/<name>.jpg."""
    png = grab(name, hud)
    from PIL import Image
    OUT.mkdir(parents=True, exist_ok=True)
    out = OUT / f'{name}.jpg'
    Image.open(png).convert('RGB').save(out, quality=90, optimize=True, progressive=True)
    print('captured', name)
    return out


def record(name, seconds, crop, width, fps, action, skip=0.3):
    """Records the screen while `action` runs, then encodes a palette-optimised GIF of the cropped region."""
    WORK.mkdir(parents=True, exist_ok=True)
    mp4 = WORK / f'{name}.mp4'
    rec = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'x11grab', '-framerate', '20', '-video_size', '1920x1080',
                            '-i', s().env['DISPLAY'] + '.0', '-t', str(seconds), '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '12',
                            str(mp4)], env=s().env)
    time.sleep(0.6)
    action()
    rec.wait()
    GIFS.mkdir(parents=True, exist_ok=True)
    w, h, x, y = crop
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-ss', str(skip), '-i', str(mp4), '-vf',
                    f'crop={w}:{h}:{x}:{y},fps={fps},scale={width}:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=160:stats_mode=diff[p];'
                    '[b][p]paletteuse=dither=bayer:bayer_scale=4:diff_mode=rectangle', str(GIFS / f'{name}.gif')], check=True)
    print('recorded', name)


def still(entity, x, y, z, yaw, extra=''):
    """A creature that holds still (NoAI) and never despawns."""
    cmd(f'summon {entity} {x} {y} {z} {{NoAI:1b,PersistenceRequired:1b,Rotation:[{yaw}f,0f]{extra}}}')


def place(feature, x, y, z):
    return cmd(f'place feature spore_and_stem:{feature} {x} {y} {z}')


def surface(x, z) -> int:
    """The y of the first air block above the ground at x, z (loads the chunk)."""
    cmd(f'forceload add {x} {z}')
    for y in range(140, -60, -1):
        if 'passed' in cmd(f'execute if block {x} {y - 1} {z} #minecraft:air') and 'passed' not in cmd(f'execute if block {x} {y - 2} {z} #minecraft:air'):
            return y - 1
    return 64


def setup():
    cmd('gamerule doDaylightCycle false', 'gamerule doWeatherCycle false', 'weather clear 1000000', 'gamerule doMobSpawning false',
        f'gamemode spectator {PLAYER}', f'effect clear {PLAYER}', 'gamerule sendCommandFeedback false')
    s().focus()


def contact(paths, out, width=960):
    """Downscaled 2-column sheet of captures, for reviewing many camera positions at once."""
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert('RGB') for p in paths]
    w = width // 2
    h = round(w * 1080 / 1920)
    rows = (len(ims) + 1) // 2
    sheet = Image.new('RGB', (width, rows * h), (20, 20, 24))
    for i, (p, im) in enumerate(zip(paths, ims)):
        x, y = (i % 2) * w, (i // 2) * h
        sheet.paste(im.resize((w, h)), (x, y))
        ImageDraw.Draw(sheet).text((x + 6, y + 4), Path(p).stem, fill=(255, 255, 0))
    sheet.save(out)
    return out
