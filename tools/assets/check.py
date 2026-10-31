#!/usr/bin/env python3
"""Validates the generated resources against the mod's real registries.

The registry dump is written by the game in a development run (dev/RegistryDump.java) to
1.21.1/<loader>/runs/<side>/spore_and_stem_registry.json; the newest one is used. Start a dev server once after
adding content, then:

  python3 tools/assets/check.py            # errors fail the run (exit 1), warnings are printed
  SS_VANILLA_ASSETS=/path/to/extracted/jar python3 tools/assets/check.py   # also resolve vanilla parent models

Checks: every block state combination is covered by its blockstate file; every model, texture, item model, loot
table, language key, sound file, subtitle, particle sprite, effect icon, armor layer and Java tag exists; recipes,
loot tables and advancements only name items that exist; every JSON parses.
"""
from __future__ import annotations

import itertools
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from ss.paths import GENERATED, MAIN_RESOURCES, MOD_ID, WORKSPACE  # noqa: E402

ROOTS = [GENERATED, MAIN_RESOURCES]
VANILLA = os.environ.get("SS_VANILLA_ASSETS")
errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def find(rel: str) -> Path | None:
    for root in ROOTS:
        p = root / rel
        if p.exists():
            return p
    return None


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        err(f"bad JSON {path}: {e}")
        return None


def split(ref: str, default_ns: str = "minecraft") -> tuple[str, str]:
    if ":" in ref:
        ns, _, path = ref.partition(":")
        return ns, path
    return default_ns, ref


def newest_dump() -> dict:
    dumps = sorted(WORKSPACE.glob(f"*/runs/*/{MOD_ID}_registry.json"), key=lambda p: p.stat().st_mtime)
    if not dumps:
        print("No registry dump found. Start a dev server or client once (tools/qa/devrun.sh start-server 1.21.1 fabric).")
        sys.exit(2)
    print(f"registry dump: {dumps[-1].relative_to(WORKSPACE.parent)}")
    return json.loads(dumps[-1].read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------------------------------- models

checked_models: dict[str, set[str]] = {}


def model_file(ref: str) -> Path | None:
    ns, path = split(ref)
    if ns == MOD_ID:
        return find(f"assets/{MOD_ID}/models/{path}.json")
    if ns == "minecraft" and VANILLA:
        p = Path(VANILLA) / "assets" / "minecraft" / "models" / f"{path}.json"
        return p if p.exists() else None
    return None


def check_model(ref: str, where: str) -> set[str]:
    """Returns the texture variables the model chain leaves unresolved (for parents that expect them)."""
    ref = ref if ":" in ref else f"minecraft:{ref}"
    if ref in checked_models:
        return checked_models[ref]
    checked_models[ref] = set()
    ns, _ = split(ref)
    path = model_file(ref)
    if path is None:
        if ns == MOD_ID:
            err(f"missing model {ref} (used by {where})")
        return set()
    model = load_json(path)
    if model is None:
        return set()
    textures = model.get("textures", {})
    for var, tex in textures.items():
        if tex.startswith("#"):
            continue
        tns, tpath = split(tex)
        if tns == MOD_ID and not find(f"assets/{MOD_ID}/textures/{tpath}.png"):
            err(f"missing texture {tex} (model {ref})")
    if ns == MOD_ID and "parent" not in model and "elements" in model and "particle" not in textures:
        warn(f"model {ref} has elements but no particle texture")
    if ns == MOD_ID:
        for el in model.get("elements", []):
            for face, f in el.get("faces", {}).items():
                t = f.get("texture", "")
                if t.startswith("#") and t[1:] not in textures and "parent" not in model:
                    err(f"model {ref}: face {face} uses undefined texture {t}")
    if "parent" in model:
        check_model(model["parent"], ref)
    return set()


# ---------------------------------------------------------------------------------------------------- states

def state_matches(state: dict, key: str) -> bool:
    if key in ("", "normal"):
        return True
    for part in key.split(","):
        k, _, v = part.partition("=")
        if state.get(k) != v:
            return False
    return True


def when_matches(state: dict, when) -> bool:
    if when is None:
        return True
    if "OR" in when:
        return any(when_matches(state, w) for w in when["OR"])
    if "AND" in when:
        return all(when_matches(state, w) for w in when["AND"])
    for k, v in when.items():
        if state.get(k) not in str(v).split("|"):
            return False
    return True


def models_of(entry) -> list[str]:
    entries = entry if isinstance(entry, list) else [entry]
    return [e["model"] for e in entries if "model" in e]


def check_blockstate(block: dict) -> None:
    bid = block["id"]
    path = find(f"assets/{MOD_ID}/blockstates/{bid}.json")
    if path is None:
        err(f"missing blockstate {bid}")
        return
    bs = load_json(path)
    if bs is None:
        return
    props = block["properties"]
    names = sorted(props)
    combos = [dict(zip(names, values)) for values in itertools.product(*(props[n] for n in names))]
    used: set[str] = set()
    if "variants" in bs:
        for key, entry in bs["variants"].items():
            for k in key.split(","):
                if k and k != "normal" and k.partition("=")[0] not in props:
                    err(f"blockstate {bid}: unknown property in variant '{key}'")
            used.update(models_of(entry))
        for state in combos:
            hits = [k for k in bs["variants"] if state_matches(state, k)]
            if not hits:
                err(f"blockstate {bid}: no variant for {state}")
                break
            if len(hits) > 1:
                err(f"blockstate {bid}: ambiguous variants {hits} for {state}")
                break
    elif "multipart" in bs:
        for part in bs["multipart"]:
            used.update(models_of(part["apply"]))
        for state in combos:
            if not any(when_matches(state, part.get("when")) for part in bs["multipart"]):
                err(f"blockstate {bid}: no multipart applies to {state}")
                break
    else:
        err(f"blockstate {bid}: neither variants nor multipart")
    for model in sorted(used):
        check_model(model, f"blockstate {bid}")


# ---------------------------------------------------------------------------------------------------- data refs

def collect_item_ids(obj, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            if k in ("item", "id", "name") and isinstance(v, str) and v.startswith(MOD_ID + ":"):
                out.add(v.split(":", 1)[1])
            elif k == "items" and isinstance(v, (str, list)):
                for it in ([v] if isinstance(v, str) else v):
                    if isinstance(it, str) and it.startswith(MOD_ID + ":"):
                        out.add(it.split(":", 1)[1])
            else:
                collect_item_ids(v, out)
    elif isinstance(obj, list):
        for v in obj:
            collect_item_ids(v, out)


def main() -> int:
    dump = newest_dump()
    lang_path = find(f"assets/{MOD_ID}/lang/en_us.json")
    lang = load_json(lang_path) if lang_path else {}
    if lang_path is None:
        err("missing lang/en_us.json")
    used_lang: set[str] = set()

    def need_lang(key: str, what: str) -> None:
        used_lang.add(key)
        if key not in lang:
            err(f"missing lang {key} ({what})")

    # Every generated JSON parses.
    for p in GENERATED.rglob("*.json"):
        load_json(p)

    item_ids = {i["id"] for i in dump["items"]}
    block_ids = {b["id"] for b in dump["blocks"]}

    for block in dump["blocks"]:
        check_blockstate(block)
        need_lang(block["description"], f"block {block['id']}")
        lt = block["loot_table"]
        if lt != "minecraft:empty":
            ns, path = split(lt)
            if ns == MOD_ID and not find(f"data/{MOD_ID}/loot_table/{path}.json"):
                err(f"missing loot table {lt}")

    for item in dump["items"]:
        model = find(f"assets/{MOD_ID}/models/item/{item['id']}.json")
        if model is None:
            err(f"missing item model {item['id']}")
        else:
            check_model(f"{MOD_ID}:item/{item['id']}", f"item {item['id']}")
        need_lang(item["description"], f"item {item['id']}")

    for entity in dump["entity_types"]:
        need_lang(entity["description"], f"entity {entity['id']}")
        if entity["living"]:
            ns, path = split(entity["loot_table"])
            if not find(f"data/{MOD_ID}/loot_table/{path}.json"):
                err(f"missing loot table {entity['loot_table']}")

    sounds_path = find(f"assets/{MOD_ID}/sounds.json")
    sounds = load_json(sounds_path) if sounds_path else {}
    for event in dump["sound_events"]:
        entry = (sounds or {}).get(event)
        if entry is None:
            err(f"sound event {event} not in sounds.json")
            continue
        if "subtitle" in entry:
            need_lang(entry["subtitle"], f"subtitle {event}")
        else:
            warn(f"sound event {event} has no subtitle")
        for s in entry.get("sounds", []):
            name = s["name"] if isinstance(s, dict) else s
            if isinstance(s, dict) and s.get("type") == "event":
                continue
            ns, path = split(name)
            if ns == MOD_ID and not find(f"assets/{MOD_ID}/sounds/{path}.ogg"):
                err(f"missing sound file {name}.ogg ({event})")

    for effect in dump["mob_effects"]:
        need_lang(f"effect.{MOD_ID}.{effect}", f"effect {effect}")
        if not find(f"assets/{MOD_ID}/textures/mob_effect/{effect}.png"):
            err(f"missing effect icon {effect}")

    for particle in dump["particle_types"]:
        p = find(f"assets/{MOD_ID}/particles/{particle}.json")
        if p is None:
            err(f"missing particle definition {particle}")
            continue
        for tex in (load_json(p) or {}).get("textures", []):
            ns, path = split(tex)
            if ns == MOD_ID and not find(f"assets/{MOD_ID}/textures/particle/{path}.png"):
                err(f"missing particle texture {tex}")

    for material in dump["armor_materials"]:
        for layer in (1, 2):
            if not find(f"assets/{MOD_ID}/textures/models/armor/{material}_layer_{layer}.png"):
                err(f"missing armor texture {material}_layer_{layer}")

    for tag in dump["tags"]:
        ns, path = split(tag["id"])
        registry = tag["registry"]
        if not find(f"data/{ns}/tags/{registry}/{path}.json"):
            err(f"missing tag {registry} #{tag['id']}")

    for folder in ("recipe", "loot_table", "advancement"):
        base = GENERATED / "data" / MOD_ID / folder
        for p in base.rglob("*.json") if base.exists() else []:
            obj = load_json(p)
            refs: set[str] = set()
            collect_item_ids(obj, refs)
            for ref in refs:
                if ref not in item_ids and ref not in block_ids:
                    err(f"{p.relative_to(GENERATED)} names unknown {MOD_ID}:{ref}")

    for key in sorted(set(lang) - used_lang):
        if not key.startswith(("subtitles.", "advancements.", "item.spore_and_stem.", "tooltip.", "itemGroup.",
                               "death.", "gui.", "message.", "jei.", "effect.", "entity.", "block.")):
            warn(f"lang key {key} is not used by any registry entry")

    for w in warnings:
        print(f"warning: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    print(f"{len(dump['blocks'])} blocks, {len(dump['items'])} items, {len(dump['entity_types'])} entity types, "
          f"{len(dump['sound_events'])} sounds: {len(errors)} errors, {len(warnings)} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
