"""Port step: derives the 26.3 resource tree from the 1.21.1 tree: everything the 26.2 port does (v26_2), then the
26.3 data-pack changes:

- loot conditions and functions are keyed by "type"; a "condition" field holds one condition (several are wrapped
  in minecraft:all_of), "functions" became "modifier", rolls and set_count counts are integer providers, and
  block_state_property became match_block ("blocks" and "state"); advancement criteria conditions likewise;
- configured features live in worldgen/feature with their config flattened into the feature object, block states
  are {"id", "properties"}, simple state providers are the bare state, random_offset became minecraft:offset;
- block model elements: "shade": false became "shade_direction_override": "up" (a true shade is the default);
- NeoForge add_spawns: "spawners" is a list of {"type", "weight", "count"} where count is an int or an int provider;
- compost chances are an item component (set in Java, ModItems), so NeoForge's compostables data map is dropped.

The same rules are used by the sibling Sprout & Soil and Christmas Ginger House 26.3 ports.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from ..paths import MOD_ID
from . import v26_2

WORKSPACE = "26.3"
MINECRAFT = "26.3"

DATA_FOLDERS = v26_2.DATA_FOLDERS
TAG_FOLDERS = v26_2.TAG_FOLDERS


def is_condition_list(value) -> bool:
    return isinstance(value, list) and bool(value) and all(isinstance(v, dict) and isinstance(v.get("condition"), str)
                                                          for v in value)


def condition(cond: dict) -> dict:
    cond = dict(cond)
    if cond["condition"] == "minecraft:block_state_property":
        cond = {"condition": "minecraft:match_block", "blocks": cond["block"],
                **({"state": cond["properties"]} if "properties" in cond else {})}
    out = {"type": cond.pop("condition")}
    for key, value in cond.items():
        if key == "terms":
            out[key] = [condition(t) for t in value]
        elif key == "term":
            out[key] = condition(value)
        else:
            out[key] = value
    return out


def conditions(conds: list) -> dict:
    terms = [condition(c) for c in conds]
    return terms[0] if len(terms) == 1 else {"type": "minecraft:all_of", "terms": terms}


def int_provider(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, dict):
        return {k: int_provider(v) if k in ("min", "max", "value") else v for k, v in value.items()}
    return value


def function(fn: dict) -> dict:
    out = {"type": fn["function"]}
    for key, value in fn.items():
        if key == "function":
            continue
        if key == "conditions":
            out["condition"] = conditions(value)
        elif fn["function"] == "minecraft:set_count" and key == "count":
            out[key] = int_provider(value)
        else:
            out[key] = value
    return out


def loot(node):
    if isinstance(node, list):
        return [loot(v) for v in node]
    if not isinstance(node, dict):
        return node
    out = {}
    for key, value in node.items():
        if key == "conditions" and is_condition_list(value):
            out["condition"] = conditions(value)
        elif key == "functions":
            out["modifier"] = [function(f) for f in value]
        elif key == "rolls":
            out[key] = int_provider(value)
        else:
            out[key] = loot(value)
    return out


def advancement(body: dict) -> dict:
    for criterion in body.get("criteria", {}).values():
        conds = criterion.get("conditions", {})
        for key, value in list(conds.items()):
            if is_condition_list(value):
                conds[key] = conditions(value)
    return body


def block_states(node):
    if isinstance(node, list):
        return [block_states(v) for v in node]
    if not isinstance(node, dict):
        return node
    if isinstance(node.get("Name"), str) and set(node) <= {"Name", "Properties"}:
        state = {"id": node["Name"]}
        if "Properties" in node:
            state["properties"] = node["Properties"]
        return state
    if node.get("type") == "minecraft:simple_state_provider" and "state" in node:
        return block_states(node["state"])
    if node.get("type") == "minecraft:random_offset":
        xz, y = node.get("xz_spread", 0), node.get("y_spread", 0)
        return {"type": "minecraft:offset", "x": xz, "y": y, "z": xz}
    return {k: block_states(v) for k, v in node.items()}


def model(body: dict) -> dict:
    for element in body.get("elements", []) if isinstance(body.get("elements"), list) else []:
        if isinstance(element, dict) and isinstance(element.get("shade"), bool):
            if not element.pop("shade"):
                element.setdefault("shade_direction_override", "up")
    return body


def spawners(body: dict, where: str) -> dict:
    entries = body["spawners"] if isinstance(body["spawners"], list) else [body["spawners"]]
    out = []
    for e in entries:
        if set(e) != {"type", "weight", "minCount", "maxCount"}:
            v26_2.fail(where, f"unsupported spawner {e!r}")
        lo, hi = e["minCount"], e["maxCount"]
        count = lo if lo == hi else {"type": "minecraft:uniform", "min_inclusive": lo, "max_inclusive": hi}
        out.append({"type": e["type"], "count": count, "weight": e["weight"]})
    body["spawners"] = out
    return body


class Port(v26_2.Port):
    def extra(self) -> None:
        data = self.dst / "data"
        for path in sorted(data.rglob("*.json")):
            rel = path.relative_to(data).as_posix()
            parts = rel.split("/")
            folder = parts[1] if len(parts) > 2 else ""
            body = self.read(path)
            if folder == "loot_table":
                new = loot(body)
            elif folder == "advancement":
                new = advancement(self.read(path))
            elif folder == "neoforge" and body.get("type") == "neoforge:add_spawns":
                new = spawners(self.read(path), rel)
            else:
                continue
            if new != body:
                self.write(path, new)
        root = data / MOD_ID / "worldgen"
        configured = root / "configured_feature"
        for path in sorted(configured.rglob("*.json")):
            body = self.read(path)
            flat = {"type": body["type"], **body.get("config", {})}
            self.write(root / "feature" / path.relative_to(configured), block_states(flat))
        shutil.rmtree(configured)
        for path in sorted((root / "placed_feature").rglob("*.json")):
            self.write(path, block_states(self.read(path)))
        compost = data / "neoforge" / "data_maps" / "item" / "compostables.json"
        if compost.exists():
            compost.unlink()
            for d in (compost.parent, compost.parent.parent, data / "neoforge"):
                if d.exists() and not any(d.iterdir()):
                    d.rmdir()
        for path in sorted((self.dst / "assets" / MOD_ID / "models").rglob("*.json")):
            body = self.read(path)
            new = model(self.read(path))
            if new != body:
                self.write(path, new)
        self.notes.append("26.3 loot/advancement conditions, flattened features, spawner lists, model shading")


def convert(src: Path, dst: Path, vanilla=None) -> Port:
    return Port(src, dst).run()


def validate(dst: Path, vanilla) -> list[str]:
    problems = []
    for path in dst.rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        if '"condition": "' in text or '"function": "' in text or '"Name":' in text or "minecraft:random_patch" in text:
            problems.append(f"{path.relative_to(dst)} still has a pre-26.3 loot, block-state or patch shape")
    if (dst / "data" / MOD_ID / "worldgen" / "configured_feature").exists():
        problems.append("worldgen/configured_feature left behind")
    return problems
