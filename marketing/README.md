# Marketing assets: 2.0 "First Bloom"

Listing copy and artwork for CurseForge and Modrinth. Nothing here ships in the mod JARs.

## Listing

| File | Use |
| --- | --- |
| [`curseforge/description.md`](curseforge/description.md) | Full project description (Markdown; also works on Modrinth) |
| [`curseforge/summary.txt`](curseforge/summary.txt) | Short project summary (193 characters) |
| [`../patchnotes/2.0.0.md`](../patchnotes/2.0.0.md) | File changelog for 2.0.0 |

Image and doc links in the description point at
`raw.githubusercontent.com/MeherBenSalem/genetically-modified-monsters/main/marketing/images/...` and
`github.com/MeherBenSalem/genetically-modified-monsters/blob/main/...`, so they resolve once this is on `main`. If the
repository is renamed, replace that prefix; to host on CurseForge instead, upload the images to the project gallery
and replace each URL.

The description leads with the pitch, then the giants, the fungal woods, the nine mushrooms, the undergrowth,
cultivation, the kitchen, Mycosis, the creatures, the Myceliarch, its spoils, configuration, everything else,
downloads and compatibility, the FAQ and a gallery.

## Adding a Minecraft version

The supported versions are listed in exactly two places:

1. `VERSIONS` at the top of [`source/render.cjs`](source/render.cjs). Add one line, for example
   `{ minecraft: '1.21.4', loaders: ['Fabric', 'NeoForge'] },`, then rerun the script for `banner`.
2. The table under **Downloads & Compatibility** in `curseforge/description.md`.

No other copy or artwork names a Minecraft version.

## Images

| File | Size | Use |
| --- | --- | --- |
| `images/banner.png` | 1800×600 | Description header: a Glowcap grove at night, the mod icon, "2.0 · First Bloom", loader pills and versions |
| `images/icon.png` | 512×512 | Project avatar: the mod icon, pixel-exact |
| `images/card-giants.png` | 1600×900 | The three huge fungi by day and by night |
| `images/card-woods.png` | 1600×900 | The cottage of the three fungal woods |
| `images/card-fungi.png` | 1600×900 | The nine small mushrooms with their in-game sprites and effects |
| `images/card-world.png` | 1600×900 | The grotto (veils, gills, shelf fungus, Glowmoths) and a Mushroom Fields island |
| `images/card-cultivation.png` | 1600×900 | Cultivation logs of seven fungi at every stage |
| `images/card-kitchen.png` | 1600×900 | The ten foods and drinks with their effects |
| `images/card-mycosis.png` | 1600×900 | The three effects, the Spore Bomb and the cures |
| `images/card-friends.png` | 1600×900 | Sporelings of all four caps, a Truffler, Glowmoths |
| `images/card-foes.png` | 1600×900 | Mimicap, Shambler, Bloatshroom and Sporemaw at dusk |
| `images/card-boss.png` | 1600×900 | The Myceliarch flaring its cap, first person, with its boss bar |
| `images/card-summon.png` | 1600×900 | Risen from a Fruiting Heart, and at dusk |
| `images/card-fight.png` | 1600×900 | A wind-up and a Root Eruption |
| `images/card-spoils.png` | 1600×900 | The inventory with the Crown and Mycoleather, and the boss's spoils |
| `images/card-config.png` | 1600×900 | `config/spore_and_stem.json` |
| `images/header-*.png` | 1400×120, transparent | 15 section headings for the description |
| `images/divider.png` | 1400×40, transparent | Section divider |
| `images/gifs/myceliarch-rises.gif` | 720×405 | A Fruiting Heart used on mycelium; the ritual and the Myceliarch rising |
| `images/screenshots/*.jpg` | 1920×1080 | 14 captures: gallery uploads and card art |

### How the screenshots were captured

Every screenshot is an unedited capture of the **1.21.1 Fabric development client** (Spore & Stem, default
configuration) with software rendering at 1920×1080 and GUI scale 3, on a fresh QA world (seed `spore-and-stem`).
[`source/capture.py`](source/capture.py) takes them all:

```bash
tools/qa/prepare_runs.sh 1.21.1 fabric tools/qa/options.txt
Xvfb :1 -screen 0 1920x1080x24 &
DISPLAY=:1 tools/qa/devrun.sh start-server 1.21.1 fabric
DISPLAY=:1 tools/qa/devrun.sh start-client 1.21.1 fabric
DISPLAY=:1 python3 marketing/source/capture.py studio          # builds the sets, once
DISPLAY=:1 python3 marketing/source/capture.py                 # every scene
DISPLAY=:1 python3 marketing/source/capture.py boss_duel summon_gif   # frames to pick from, and the GIF
```

- **Sets:** `studio` flattens two 48×48 plateaus in the plains south of spawn (x 0..95, z 380..427, y 80) and grows
  them with the mod's own worldgen features (`/place feature`) and blocks: a Glowcap glade, a Bouncecap meadow with a
  fairy ring, a cottage of the three woods, a cultivation farm and a grotto. The Mushroom Fields shot is natural
  terrain at 1344 70 3068.
- **Actors** are summoned with NoAI so they hold still; natural spawning, weather and the daylight cycle are off.
- **The fight:** `boss_duel` lets the Myceliarch fight the player (survival, Resistance and Regeneration so the camera
  survives) and saves frames to choose from; `myceliarch-nova`, `-windup` and `-roots` are three of them.
- **The GIF** is recorded from the X display with `ffmpeg -f x11grab` while a real Fruiting Heart is used, and
  encoded with a generated palette.
- **HUD:** hidden except in the fight frames (boss bar) and the inventory.

## Regenerating the artwork

The cards, banner, icon and headers are HTML rendered with Playwright from the screenshots, the mod's own textures
and the bundled fonts:

```bash
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs              # everything
NODE_PATH="$(npm root -g)" node marketing/source/render.cjs banner icon  # selected assets
```

- `source/backdrop.jpg` is the blurred background scene, a 1280×720 copy of `screenshots/glowcap-grove.jpg`.
- The icon is the mod logo (`1.21.1/common/src/main/resources/logo.png`, drawn by `tools/assets/ss/misc.py`).
- Item and effect sprites are read straight from the generated textures, so run `python3 tools/assets/build.py`
  first.
- `source/fonts/` holds Fraunces (titles) and Spectral (text) with their SIL Open Font License 1.1 texts.
- The feature cards are in [`source/cards.cjs`](source/cards.cjs). Card crops are pixel regions of the 1920×1080
  captures (`region()` calls), so new captures may need their crops adjusted.

## Wording

Every number in the copy and on the cards is a 2.0.0 default from `docs/DESIGN.md`, the config, a recipe, a loot
table or the code; update the copy when those change. The boss is **the Myceliarch**, the infection is **Mycosis**,
the boss's second phase is **the second bloom**.
