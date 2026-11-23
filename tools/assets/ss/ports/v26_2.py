"""Port step: derives the 26.2 resource tree (Fabric + NeoForge, unobfuscated Minecraft) from the 1.21.1 tree.

What changes between the two versions, as far as Spore & Stem's resources are concerned:

- every item needs a client item definition (assets/<ns>/items/<id>.json) that names its model;
- spawn eggs are no longer tinted by the item class: they share one two-layer model (item/spawn_egg, drawn here)
  and their colours move into constant tints in the item definitions;
- armour is drawn from equipment assets (assets/<ns>/equipment/<material>.json) with the textures under
  textures/entity/equipment/humanoid[_leggings]/ instead of textures/models/armor/<material>_layer_1|2.png;
- repair materials are item tags (spore_and_stem:mycoleather_repairs, spore_and_stem:bloom_repairs) named by the
  armour and tool materials in Java;
- recipe ingredients are plain ids, "#tag" strings or lists of ids instead of {"item": ...} / {"tag": ...} objects;
- minecraft:random_patch is gone: a patch's configured feature is its inner feature, and the patch spread (tries,
  xz/y spread as triangular distributions) moves onto the placed feature as count + random_offset modifiers;
- the copper update renamed the chain (minecraft:chain -> minecraft:iron_chain, the texture likewise);
- advancement backgrounds name a texture without "textures/" and ".png".

Everything else (blockstates, models, loot tables, tags, biome modifiers, data maps) is copied unchanged. The same
rules are used by the sibling Sprout & Soil port (tools/assetgen/sas/modern.py there). A recipe ingredient this port does not understand is an error, never a silent copy.

There is no vanilla 26.x reference check yet: validate() reports nothing, so a wrong vanilla id only shows in game.
"""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

from ..paths import MOD_ID, java, REFERENCE_WORKSPACE
from ..pixel import canvas, grid

RENAMED = {"minecraft:chain": "minecraft:iron_chain", "minecraft:block/chain": "minecraft:block/iron_chain"}

WORKSPACE = "26.2"
MINECRAFT = "26.2"

DATA_FOLDERS: dict[str, str] = {}
TAG_FOLDERS: dict[str, str] = {}

# Repair materials (Java: ModArmorMaterials and BloomreaverItem name these tags).
REPAIR_TAGS = {
    "mycoleather_repairs": [f"{MOD_ID}:mycoleather"],
    "bloom_repairs": [f"{MOD_ID}:lumen_spores"],
}

# An egg drawn for this mod: layer 0 is the shell (tinted with the base colour), layer 1 the spots (tinted with
# the spot colour). Grey levels shade the tint.
EGG_SHELL = """
................
......aaaa......
.....abbbba.....
....abbccbba....
....abccccba....
...abbccccbba...
...abcccccdba...
..abbcccccdbba..
..abcccccddcba..
..abccccdddcba..
..abcccddddcba..
..abbcddddcbba..
...abbddddbba...
....aabbbbaa....
......aaaa......
................
"""
EGG_SPOTS = """
................
................
................
.......e........
.....e..........
..........e.....
................
....ee..........
....e.....ee....
..........e.....
......e.........
.....ee.....e...
.........e......
................
................
................
"""
EGG_COLOURS = {"a": (70, 70, 70, 255), "b": (150, 150, 150, 255), "c": (230, 230, 230, 255),
               "d": (200, 200, 200, 255), "e": (240, 240, 240, 255)}


class PortError(Exception):
    pass


def fail(where: str, msg: str):
    raise PortError(f"[{MINECRAFT}] {where}: {msg}")


def ingredient(value, where: str):
    """1.21.1 ingredient -> 26.x ingredient ('id', '#tag' or [ids])."""
    if isinstance(value, dict):
        if set(value) == {"item"}:
            return value["item"]
        if set(value) == {"tag"}:
            return "#" + value["tag"]
        fail(where, f"unsupported ingredient {value!r}")
    if isinstance(value, list):
        out = [ingredient(v, where) for v in value]
        if any(v.startswith("#") for v in out):
            fail(where, f"a list ingredient may not mix in tags: {value!r}")
        return out[0] if len(out) == 1 else out
    if isinstance(value, str):
        return value
    fail(where, f"unsupported ingredient {value!r}")


def convert_recipe(recipe: dict, where: str) -> dict:
    kind = recipe.get("type")
    if kind == "minecraft:crafting_shaped":
        recipe["key"] = {k: ingredient(v, f"{where} key {k}") for k, v in recipe["key"].items()}
    elif kind == "minecraft:crafting_shapeless":
        recipe["ingredients"] = [ingredient(v, f"{where} ingredients") for v in recipe["ingredients"]]
    elif kind in ("minecraft:smelting", "minecraft:smoking", "minecraft:blasting", "minecraft:campfire_cooking"):
        recipe["ingredient"] = ingredient(recipe["ingredient"], f"{where} ingredient")
    else:
        fail(where, f"unsupported recipe type {kind}")
    return recipe


def renamed(node):
    if isinstance(node, dict):
        return {k: renamed(v) for k, v in node.items()}
    if isinstance(node, list):
        return [renamed(v) for v in node]
    if isinstance(node, str):
        prefix = "#" if node.startswith("#") else ""
        return prefix + RENAMED.get(node[len(prefix):], node[len(prefix):])
    return node


def advancement(body: dict) -> dict:
    background = body.get("display", {}).get("background")
    if background:
        ns, path = background.split(":", 1) if ":" in background else ("minecraft", background)
        if path.startswith("textures/") and path.endswith(".png"):
            body["display"]["background"] = f"{ns}:{path[len('textures/'):-len('.png')]}"
    return body


def trapezoid(spread: int) -> dict:
    return {"type": "minecraft:trapezoid", "min": -spread, "max": spread, "plateau": 0}


def spawn_egg_colours() -> dict[str, tuple[int, int]]:
    """Egg colours as the reference workspace's ModItems declares them: egg("name", type, 0xBASE, 0xSPOTS)."""
    text = (java(REFERENCE_WORKSPACE) / "registry" / "ModItems.java").read_text(encoding="utf-8")
    found = re.findall(r'egg\("([a-z_]+)",\s*[^,]+,\s*0x([0-9A-Fa-f]{6}),\s*0x([0-9A-Fa-f]{6})\)', text)
    if not found:
        fail("ModItems.java", "no spawn egg colours found")
    return {f"{name}_spawn_egg": (int(base, 16), int(spots, 16)) for name, base, spots in found}


def draw(art: str):
    img = canvas()
    for y, row in enumerate(grid(art)):
        for x, ch in enumerate(row):
            if ch in EGG_COLOURS:
                img.putpixel((x, y), EGG_COLOURS[ch])
    return img


class Port:
    def __init__(self, src: Path, dst: Path):
        self.src, self.dst = src, dst
        self.written: list[Path] = []
        self.notes: list[str] = []

    def json(self, rel: str, obj) -> None:
        path = self.dst / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        self.written.append(path)

    def read(self, path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def write(self, path: Path, obj) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        self.written.append(path)

    def run(self) -> "Port":
        if self.dst.exists():
            shutil.rmtree(self.dst)
        shutil.copytree(self.src, self.dst)
        for path in sorted(self.dst.rglob("*.json")):
            if "/lang/" in path.as_posix():
                continue
            body = self.read(path)
            new = renamed(body)
            if path.parent.name == "advancement" or "/advancement/" in path.as_posix():
                new = advancement(new)
            if new != body:
                self.write(path, new)
        self.split_patches()
        self.recipes()
        self.items()
        self.equipment()
        for name, values in REPAIR_TAGS.items():
            self.json(f"data/{MOD_ID}/tags/item/{name}.json", {"values": values})
        self.extra()
        self.written.extend(p for p in self.dst.rglob("*") if p.is_file() and p not in self.written)
        return self

    def extra(self) -> None:
        """Hook for later versions."""

    def split_patches(self) -> None:
        root = self.dst / "data" / MOD_ID / "worldgen"
        configured, placed = root / "configured_feature", root / "placed_feature"
        count = 0
        for path in sorted(configured.rglob("*.json")):
            body = self.read(path)
            if body.get("type") != "minecraft:random_patch":
                continue
            config = body["config"]
            if set(config) != {"tries", "xz_spread", "y_spread", "feature"}:
                fail(path.name, f"unsupported random_patch config {sorted(config)}")
            inner = config["feature"]
            self.write(path, inner["feature"])
            rel = path.relative_to(configured)
            for placed_path in sorted(placed.rglob("*.json")):
                placed_body = self.read(placed_path)
                if placed_body.get("feature") != f"{MOD_ID}:{rel.with_suffix('').as_posix()}":
                    continue
                placed_body["placement"] = placed_body.get("placement", []) + [
                    {"type": "minecraft:count", "count": config["tries"]},
                    {"type": "minecraft:random_offset", "xz_spread": trapezoid(config["xz_spread"]),
                     "y_spread": trapezoid(config["y_spread"])},
                ] + inner.get("placement", [])
                self.write(placed_path, placed_body)
            count += 1
        self.notes.append(f"{count} random_patch features split into feature + placement")

    def recipes(self) -> None:
        for path in sorted(self.dst.glob("data/*/recipe/**/*.json")):
            rel = path.relative_to(self.dst).as_posix()
            recipe = convert_recipe(json.loads(path.read_text(encoding="utf-8")), rel)
            path.write_text(json.dumps(recipe, indent=2) + "\n", encoding="utf-8")

    def items(self) -> None:
        assets = self.dst / "assets" / MOD_ID
        colours = spawn_egg_colours()
        for path in sorted((assets / "models" / "item").glob("*.json")):
            name = path.stem
            if name in colours:
                path.unlink()
                base, spots = colours[name]
                self.json(f"assets/{MOD_ID}/items/{name}.json", {"model": {
                    "type": "minecraft:model", "model": f"{MOD_ID}:item/spawn_egg",
                    "tints": [{"type": "minecraft:constant", "value": base},
                              {"type": "minecraft:constant", "value": spots}]}})
            else:
                model = json.loads(path.read_text(encoding="utf-8"))
                if "overrides" in model:
                    fail(path.name, "item model overrides need a select/range_dispatch item definition")
                self.json(f"assets/{MOD_ID}/items/{name}.json",
                          {"model": {"type": "minecraft:model", "model": f"{MOD_ID}:item/{name}"}})
        missing = set(colours) - {p.stem for p in (assets / "items").glob("*.json")}
        if missing:
            fail("spawn eggs", f"no item model for {sorted(missing)}")
        self.json(f"assets/{MOD_ID}/models/item/spawn_egg.json", {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"{MOD_ID}:item/spawn_egg", "layer1": f"{MOD_ID}:item/spawn_egg_overlay"}})
        for name, art in (("spawn_egg", EGG_SHELL), ("spawn_egg_overlay", EGG_SPOTS)):
            out = assets / "textures" / "item" / f"{name}.png"
            out.parent.mkdir(parents=True, exist_ok=True)
            draw(art).save(out)
            self.written.append(out)
        self.notes.append(f"{len(colours)} spawn eggs share item/spawn_egg with constant tints")

    def equipment(self) -> None:
        assets = self.dst / "assets" / MOD_ID
        armor = assets / "textures" / "models" / "armor"
        materials = sorted({p.stem.rsplit("_layer_", 1)[0] for p in armor.glob("*_layer_*.png")})
        for material in materials:
            for layer, folder in (("1", "humanoid"), ("2", "humanoid_leggings")):
                src = armor / f"{material}_layer_{layer}.png"
                if not src.exists():
                    fail(material, f"missing {src.name}")
                out = assets / "textures" / "entity" / "equipment" / folder / f"{material}.png"
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(src, out)
                self.written.append(out)
            self.json(f"assets/{MOD_ID}/equipment/{material}.json", {"layers": {
                "humanoid": [{"texture": f"{MOD_ID}:{material}"}],
                "humanoid_leggings": [{"texture": f"{MOD_ID}:{material}"}]}})
        shutil.rmtree(assets / "textures" / "models", ignore_errors=True)
        self.notes.append(f"equipment assets: {', '.join(materials)}")

    def summary(self) -> list[str]:
        return list(self.notes)


def convert(src: Path, dst: Path, vanilla=None) -> Port:
    return Port(src, dst).run()


def validate(dst: Path, vanilla) -> list[str]:
    """Format checks only (there is no vanilla 26.x reference check yet)."""
    problems = []
    for path in dst.glob("data/*/recipe/**/*.json"):
        body = json.loads(path.read_text(encoding="utf-8"))
        fields = [body.get("ingredient")] + list(body.get("key", {}).values()) + list(body.get("ingredients", []))
        if any(isinstance(f, dict) for f in fields):
            problems.append(f"{path.name}: object ingredient left")
    for path in dst.rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        if "minecraft:random_patch" in text or '"minecraft:chain"' in text or "minecraft:block/chain" in text:
            problems.append(f"{path.relative_to(dst)} has a pre-26 reference")
    assets = dst / "assets" / MOD_ID
    for model in (assets / "models" / "item").glob("*.json"):
        if model.stem != "spawn_egg" and not (assets / "items" / model.name).exists():
            problems.append(f"no item definition for {model.stem}")
    if (assets / "textures" / "models" / "armor").exists():
        problems.append("old armor layer textures left")
    return problems
