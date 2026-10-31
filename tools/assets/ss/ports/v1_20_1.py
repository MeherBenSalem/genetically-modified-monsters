"""Port step: derives the 1.20.1 resource tree (Fabric + Forge 47) from the freshly generated 1.21.1 tree.

What changes between the two versions, as far as Spore & Stem's resources are concerned:

- data folders were plural in 1.20.1 (recipes, loot_tables, advancements, structures, tags/blocks, tags/items, ...);
- recipe results are {"item": ...} (cooking recipes: a plain id); item and block predicates use "items"/"blocks"
  lists and a separate "tag" field; enchantment predicates are a list of {"enchantment": ...};
- loot: looting_enchant / random_chance_with_looting instead of the enchantment-generic 1.21 forms;
- advancement icons are {"item": ...};
- biome modifiers are Forge's (data/<ns>/forge/biome_modifier, forge:add_features / forge:add_spawns);
- block models carry Forge's element-level "forge_data" (block_light / sky_light / ambient_occlusion);
- NeoForge data maps do not exist (compostables are registered from Java, see ModCompostables);
- conventional tags: Forge's forge:* names and the Fabric 1.20.1 c:* names replace the 1.21 c:* names;
- the GameTest arena is written with 1.20.1's DataVersion.

Every file is converted by a strict handler: an unknown key, type or trigger is an error, never a silent copy.
Afterwards every minecraft: id, tag, block state, model and texture in the output is checked against the vanilla
1.20.1 client and its registry reports (ss/ports/vanilla.py).
"""
from __future__ import annotations

import copy
import json
import shutil
from collections import defaultdict
from pathlib import Path

from .. import gametest
from ..paths import BUILD, MOD_ID
from .vanilla import Vanilla

WORKSPACE = "1.20.1"
MINECRAFT = "1.20.1"
DATA_VERSION = 3465

DATA_FOLDERS = {"recipe": "recipes", "loot_table": "loot_tables", "advancement": "advancements",
                "structure": "structures"}
TAG_FOLDERS = {"block": "blocks", "item": "items", "entity_type": "entity_types", "fluid": "fluids",
               "game_event": "game_events"}

# Vanilla ids that were renamed after 1.20.1 (1.21.1 id -> 1.20.1 id). Applied to every string.
RENAMED = {
    "minecraft:short_grass": "minecraft:grass",
    "minecraft:turtle_scute": "minecraft:scute",
}

# Vanilla tags added after 1.20.1. In 1.20.1 the same information lives in the item classes (ArmorItem, DiggerItem,
# enchantment categories), so these files are dropped.
DROPPED_VANILLA_ITEM_TAGS = {"minecraft:head_armor", "minecraft:chest_armor", "minecraft:leg_armor",
                             "minecraft:foot_armor"}
DROPPED_VANILLA_ITEM_TAG_PREFIXES = ("minecraft:enchantable/",)

# 1.21 conventional tags -> their 1.20.1 names. forge:* are Forge 47's own tags; c:* are the names Fabric API's
# convention tags (v1) and the 1.20 Fabric community used. An empty list drops the tag (no 1.20.1 convention); a
# dropped tag that another tag references is inlined into it.
CONVENTIONAL: dict[tuple[str, str], list[tuple[str, str]]] = {
    ("item", "c:foods"): [("item", "c:foods")],
    ("item", "c:mushrooms"): [("item", "forge:mushrooms"), ("item", "c:mushrooms")],
    ("item", "c:leathers"): [("item", "forge:leather"), ("item", "c:leather")],
    ("item", "c:slime_balls"): [("item", "forge:slimeballs"), ("item", "c:slime_balls")],
    ("item", "c:strings"): [("item", "forge:string"), ("item", "c:string")],
    ("block", "c:stripped_logs"): [("block", "c:stripped_logs")],
    ("item", "c:stripped_logs"): [("item", "c:stripped_logs")],
    ("block", "c:stripped_woods"): [("block", "c:stripped_wood")],
    ("item", "c:stripped_woods"): [("item", "c:stripped_wood")],
    ("item", "c:drinks"): [],
    ("item", "c:foods/soup"): [],
    ("item", "c:foods/edible_when_placed"): [],
    ("item", "c:foods/food_poisoning"): [],
}

# NeoForge data maps the 1.20.1 Java registers itself.
DROPPED_DATA_MAPS = {"neoforge:item/compostables": "registered in Java (ModCompostables)"}

APPLY_BONUS_FORMULAS = {"minecraft:binomial_with_bonus_count", "minecraft:uniform_bonus_count", "minecraft:ore_drops"}
RENDER_TYPES = {"minecraft:solid", "minecraft:cutout", "minecraft:cutout_mipped", "minecraft:translucent",
                "minecraft:tripwire"}


class PortError(Exception):
    pass


def fail(where: str, msg: str):
    raise PortError(f"[{MINECRAFT}] {where}: {msg}")


def keys(obj: dict, allowed: set[str], where: str) -> None:
    if not isinstance(obj, dict):
        fail(where, f"expected an object, got {obj!r}")
    extra = set(obj) - allowed
    if extra:
        fail(where, f"unsupported keys {sorted(extra)}")


def rename(obj):
    if isinstance(obj, str):
        if obj.startswith("#"):
            return obj
        return RENAMED.get(obj, obj)
    if isinstance(obj, list):
        return [rename(v) for v in obj]
    if isinstance(obj, dict):
        return {k: rename(v) for k, v in obj.items()}
    return obj


# Int and float providers with numeric bounds nest their fields under "value" in 1.20.1 (they were inlined in 1.20.5).
# Height providers take vertical anchors (objects) for bounds and stay inline, as does weighted_list.
VALUE_WRAPPED_PROVIDERS = {"minecraft:uniform", "minecraft:biased_to_bottom", "minecraft:clamped",
                           "minecraft:clamped_normal", "minecraft:trapezoid"}
PROVIDER_BOUNDS = ("min_inclusive", "max_inclusive", "max_exclusive", "min", "max")


def wrap_providers(obj):
    """Worldgen only: {"type": "minecraft:uniform", "min_inclusive": 1, ...} -> {"type": ..., "value": {...}}."""
    if isinstance(obj, list):
        return [wrap_providers(v) for v in obj]
    if not isinstance(obj, dict):
        return obj
    obj = {k: wrap_providers(v) for k, v in obj.items()}
    if obj.get("type") in VALUE_WRAPPED_PROVIDERS and "value" not in obj:
        fields = {k: v for k, v in obj.items() if k != "type"}
        bounds = [fields[k] for k in PROVIDER_BOUNDS if k in fields]
        if bounds and all(isinstance(b, (int, float)) and not isinstance(b, bool) for b in bounds):
            return {"type": obj["type"], "value": fields}
    return obj


# ---------------------------------------------------------------------------------------------------- predicates

def holder_list(value, where: str, list_key: str) -> dict:
    """1.21 holder set ('id', '#tag' or [ids]) -> 1.20.1 {list_key: [ids]} or {"tag": tag}."""
    if isinstance(value, str):
        return {"tag": value[1:]} if value.startswith("#") else {list_key: [value]}
    if isinstance(value, list) and all(isinstance(v, str) and not v.startswith("#") for v in value):
        return {list_key: list(value)}
    fail(where, f"unsupported holder set {value!r}")


def item_pred(p: dict, where: str) -> dict:
    keys(p, {"items", "count", "durability", "predicates"}, where)
    out: dict = {}
    if "items" in p:
        out.update(holder_list(p["items"], where, "items"))
    for k in ("count", "durability"):
        if k in p:
            out[k] = p[k]
    preds = p.get("predicates", {})
    keys(preds, {"minecraft:enchantments", "minecraft:stored_enchantments"}, where + ".predicates")
    for src, dst in (("minecraft:enchantments", "enchantments"), ("minecraft:stored_enchantments", "stored_enchantments")):
        if src not in preds:
            continue
        entries = []
        for e in preds[src]:
            keys(e, {"enchantments", "levels"}, where + f".{src}")
            ench = e.get("enchantments")
            ids = [None] if ench is None else [ench] if isinstance(ench, str) else ench
            for i in ids:
                if i is not None and i.startswith("#"):
                    fail(where, f"enchantment tags do not exist in {MINECRAFT}: {i}")
                entry = {} if i is None else {"enchantment": i}
                if "levels" in e:
                    entry["levels"] = e["levels"]
                entries.append(entry)
        out[dst] = entries
    return out


def block_pred(p: dict, where: str) -> dict:
    keys(p, {"blocks", "state", "nbt"}, where)
    out: dict = {}
    if "blocks" in p:
        out.update(holder_list(p["blocks"], where, "blocks"))
    for k in ("state", "nbt"):
        if k in p:
            out[k] = p[k]
    return out


def single(value, where: str, what: str) -> str:
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
    if not isinstance(value, str) or value.startswith("#"):
        fail(where, f"{MINECRAFT} takes a single {what} id, got {value!r}")
    return value


def location_pred(p: dict, where: str) -> dict:
    keys(p, {"position", "biomes", "structures", "dimension", "smokey", "light", "block"}, where)
    out: dict = {}
    for k in ("position", "dimension", "smokey", "light"):
        if k in p:
            out[k] = p[k]
    if "biomes" in p:
        out["biome"] = single(p["biomes"], where, "biome")
    if "structures" in p:
        out["structure"] = single(p["structures"], where, "structure")
    if "block" in p:
        out["block"] = block_pred(p["block"], where + ".block")
    return out


ENTITY_FLAGS = {"is_on_fire", "is_sneaking", "is_sprinting", "is_swimming", "is_baby"}
EQUIPMENT_SLOTS = {"head", "chest", "legs", "feet", "mainhand", "offhand"}


def entity_pred(p: dict, where: str) -> dict:
    keys(p, {"type", "distance", "location", "stepping_on", "effects", "nbt", "flags", "equipment", "vehicle",
             "passenger", "targeted_entity", "team"}, where)
    out: dict = {}
    for k, v in p.items():
        if k == "type":
            out[k] = v if isinstance(v, str) else single(v, where, "entity type")
        elif k in ("location", "stepping_on"):
            out[k] = location_pred(v, f"{where}.{k}")
        elif k == "flags":
            keys(v, ENTITY_FLAGS, where + ".flags")
            out[k] = v
        elif k == "equipment":
            keys(v, EQUIPMENT_SLOTS, where + ".equipment")
            out[k] = {slot: item_pred(ip, f"{where}.equipment.{slot}") for slot, ip in v.items()}
        elif k in ("vehicle", "passenger", "targeted_entity"):
            out[k] = entity_pred(v, f"{where}.{k}")
        else:  # distance, effects, nbt, team: unchanged
            out[k] = v
    return out


def damage_source_pred(p: dict, where: str) -> dict:
    keys(p, {"tags", "source_entity", "direct_entity"}, where)
    out = dict(p)
    for k in ("source_entity", "direct_entity"):
        if k in p:
            out[k] = entity_pred(p[k], f"{where}.{k}")
    return out


def damage_pred(p: dict, where: str) -> dict:
    keys(p, {"dealt", "taken", "source_entity", "blocked", "type"}, where)
    out = dict(p)
    if "source_entity" in p:
        out["source_entity"] = entity_pred(p["source_entity"], where + ".source_entity")
    if "type" in p:
        out["type"] = damage_source_pred(p["type"], where + ".type")
    return out


# ---------------------------------------------------------------------------------------------------- loot

def number(v, where: str):
    """Number providers are unchanged; their types are checked against the 1.20.1 registry afterwards."""
    return v


def condition(c: dict, where: str) -> dict:
    t = c.get("condition")
    w = f"{where}<{t}>"
    if t == "minecraft:match_tool":
        keys(c, {"condition", "predicate"}, w)
        return {"condition": t, **({"predicate": item_pred(c["predicate"], w)} if "predicate" in c else {})}
    if t == "minecraft:entity_properties":
        keys(c, {"condition", "entity", "predicate"}, w)
        out = {"condition": t, "entity": c["entity"]}
        if "predicate" in c:
            out["predicate"] = entity_pred(c["predicate"], w)
        return out
    if t == "minecraft:location_check":
        keys(c, {"condition", "predicate", "offsetX", "offsetY", "offsetZ"}, w)
        out = {k: v for k, v in c.items() if k != "predicate"}
        if "predicate" in c:
            out["predicate"] = location_pred(c["predicate"], w)
        return out
    if t == "minecraft:random_chance":
        keys(c, {"condition", "chance"}, w)
        if not isinstance(c["chance"], (int, float)):
            fail(w, f"{MINECRAFT} random_chance takes a plain number")
        return dict(c)
    if t == "minecraft:random_chance_with_enchanted_bonus":
        keys(c, {"condition", "enchantment", "unenchanted_chance", "enchanted_chance"}, w)
        if c["enchantment"] != "minecraft:looting":
            fail(w, f"only looting bonuses exist in {MINECRAFT}")
        base = c["unenchanted_chance"]
        bonus = c["enchanted_chance"]
        if isinstance(bonus, dict) and bonus.get("type") == "minecraft:linear":
            per_level = bonus["per_level_above_first"]
            if abs(bonus["base"] - (base + per_level)) > 1e-9:
                fail(w, "linear bonus is not chance + level * multiplier")
        elif isinstance(bonus, (int, float)) and bonus == base:
            per_level = 0.0
        else:
            fail(w, f"cannot express {bonus!r} as random_chance_with_looting")
        return {"condition": "minecraft:random_chance_with_looting", "chance": base, "looting_multiplier": per_level}
    if t in ("minecraft:all_of", "minecraft:any_of"):
        keys(c, {"condition", "terms"}, w)
        return {"condition": t, "terms": [condition(x, w) for x in c["terms"]]}
    if t == "minecraft:inverted":
        keys(c, {"condition", "term"}, w)
        return {"condition": t, "term": condition(c["term"], w)}
    if t == "minecraft:block_state_property":
        keys(c, {"condition", "block", "properties"}, w)
        return dict(c)
    if t in ("minecraft:killed_by_player", "minecraft:survives_explosion"):
        keys(c, {"condition"}, w)
        return dict(c)
    if t == "minecraft:table_bonus":
        keys(c, {"condition", "enchantment", "chances"}, w)
        return dict(c)
    fail(w, "unsupported loot condition")


def conditions(cs: list, where: str) -> list:
    return [condition(c, f"{where}[{i}]") for i, c in enumerate(cs)]


def function(f: dict, where: str) -> dict:
    t = f.get("function")
    w = f"{where}<{t}>"
    out: dict
    if t == "minecraft:set_count":
        keys(f, {"function", "count", "add", "conditions"}, w)
        out = {k: v for k, v in f.items() if k != "conditions"}
    elif t == "minecraft:enchanted_count_increase":
        keys(f, {"function", "enchantment", "count", "limit", "conditions"}, w)
        if f["enchantment"] != "minecraft:looting":
            fail(w, f"only looting count bonuses exist in {MINECRAFT}")
        out = {"function": "minecraft:looting_enchant", "count": f["count"]}
        if "limit" in f:
            out["limit"] = f["limit"]
    elif t == "minecraft:apply_bonus":
        keys(f, {"function", "enchantment", "formula", "parameters", "conditions"}, w)
        out = {k: v for k, v in f.items() if k != "conditions"}
    elif t in ("minecraft:explosion_decay", "minecraft:furnace_smelt"):
        keys(f, {"function", "conditions"}, w)
        out = {"function": t}
    elif t == "minecraft:limit_count":
        keys(f, {"function", "limit", "conditions"}, w)
        out = {k: v for k, v in f.items() if k != "conditions"}
    else:
        fail(w, "unsupported loot function")
    if "conditions" in f:
        out["conditions"] = conditions(f["conditions"], w)
    return out


def functions(fs: list, where: str) -> list:
    return [function(f, f"{where}[{i}]") for i, f in enumerate(fs)]


def entry(e: dict, where: str) -> dict:
    t = e.get("type")
    w = f"{where}<{t}>"
    if t in ("minecraft:item", "minecraft:tag", "minecraft:empty"):
        keys(e, {"type", "name", "expand", "weight", "quality", "functions", "conditions"}, w)
        out = {k: v for k, v in e.items() if k not in ("functions", "conditions")}
    elif t in ("minecraft:alternatives", "minecraft:group", "minecraft:sequence"):
        keys(e, {"type", "children", "conditions"}, w)
        out = {"type": t, "children": [entry(c, f"{w}.children[{i}]") for i, c in enumerate(e["children"])]}
    elif t == "minecraft:loot_table":
        keys(e, {"type", "value", "weight", "quality", "functions", "conditions"}, w)
        if not isinstance(e["value"], str):
            fail(w, f"inline loot tables do not exist in {MINECRAFT}")
        out = {"type": t, "name": e["value"], **{k: e[k] for k in ("weight", "quality") if k in e}}
    else:
        fail(w, "unsupported loot entry")
    if "functions" in e:
        out["functions"] = functions(e["functions"], w + ".functions")
    if "conditions" in e:
        out["conditions"] = conditions(e["conditions"], w + ".conditions")
    return out


def loot_table(t: dict, where: str) -> dict:
    keys(t, {"type", "pools", "functions", "random_sequence"}, where)
    out = {k: t[k] for k in ("type", "random_sequence") if k in t}
    pools = []
    for i, pool in enumerate(t.get("pools", [])):
        w = f"{where}.pools[{i}]"
        keys(pool, {"rolls", "bonus_rolls", "entries", "conditions", "functions"}, w)
        p = {"rolls": number(pool["rolls"], w)}
        if "bonus_rolls" in pool:
            p["bonus_rolls"] = pool["bonus_rolls"]
        p["entries"] = [entry(e, f"{w}.entries[{j}]") for j, e in enumerate(pool["entries"])]
        if "conditions" in pool:
            p["conditions"] = conditions(pool["conditions"], w + ".conditions")
        if "functions" in pool:
            p["functions"] = functions(pool["functions"], w + ".functions")
        pools.append(p)
    out["pools"] = pools
    if "functions" in t:
        out["functions"] = functions(t["functions"], where + ".functions")
    return out


# ---------------------------------------------------------------------------------------------------- recipes

CRAFTING = {"minecraft:crafting_shaped", "minecraft:crafting_shapeless"}
COOKING = {"minecraft:smelting", "minecraft:smoking", "minecraft:blasting", "minecraft:campfire_cooking"}


def ingredient(i, where: str):
    if isinstance(i, list):
        return [ingredient(x, where) for x in i]
    keys(i, {"item", "tag"}, where)
    if len(i) != 1:
        fail(where, f"ingredient needs exactly one of item/tag: {i!r}")
    return dict(i)


def recipe(r: dict, where: str) -> dict:
    t = r.get("type")
    if t in CRAFTING:
        keys(r, {"type", "category", "group", "pattern", "key", "ingredients", "result", "show_notification"}, where)
        out = {k: r[k] for k in ("type", "category", "group") if k in r}
        if t == "minecraft:crafting_shaped":
            out["pattern"] = r["pattern"]
            out["key"] = {k: ingredient(v, f"{where}.key.{k}") for k, v in r["key"].items()}
        else:
            out["ingredients"] = [ingredient(v, f"{where}.ingredients") for v in r["ingredients"]]
        res = r["result"]
        keys(res, {"id", "count"}, where + ".result")
        out["result"] = {"item": res["id"], **({"count": res["count"]} if res.get("count", 1) != 1 else {})}
        if "show_notification" in r:
            out["show_notification"] = r["show_notification"]
        return out
    if t in COOKING:
        keys(r, {"type", "category", "group", "ingredient", "result", "experience", "cookingtime"}, where)
        res = r["result"]
        keys(res, {"id", "count"}, where + ".result")
        if res.get("count", 1) != 1:
            fail(where, f"cooking recipes make exactly one item in {MINECRAFT}")
        out = {k: r[k] for k in ("type", "category", "group") if k in r}
        out["ingredient"] = ingredient(r["ingredient"], where + ".ingredient")
        out["result"] = res["id"]
        for k in ("experience", "cookingtime"):
            if k in r:
                out[k] = r[k]
        return out
    if t == "minecraft:stonecutting":
        keys(r, {"type", "group", "ingredient", "result"}, where)
        res = r["result"]
        keys(res, {"id", "count"}, where + ".result")
        out = {k: r[k] for k in ("type", "group") if k in r}
        out["ingredient"] = ingredient(r["ingredient"], where + ".ingredient")
        out["result"] = res["id"]
        out["count"] = res.get("count", 1)
        return out
    fail(where, f"unsupported recipe type {t}")


# ---------------------------------------------------------------------------------------------------- advancements

TRIGGER_FIELDS = {
    "minecraft:inventory_changed": {"player", "items", "slots"},
    "minecraft:player_killed_entity": {"player", "entity"},
    "minecraft:item_used_on_block": {"player", "location"},
    "minecraft:placed_block": {"player", "location"},
    "minecraft:location": {"player"},
    "minecraft:tick": {"player"},
    "minecraft:tame_animal": {"player", "entity"},
    "minecraft:bred_animals": {"player", "parent", "partner", "child"},
    "minecraft:consume_item": {"player", "item"},
    "minecraft:entity_hurt_player": {"player", "damage"},
    "minecraft:player_hurt_entity": {"player", "damage", "entity"},
    "minecraft:effects_changed": {"player", "effects", "source"},
}


def context_pred(v, where: str):
    """1.21 entity fields are lists of loot conditions; 1.20.1 accepts the same list (or a bare entity predicate)."""
    if isinstance(v, list):
        return conditions(v, where)
    return entity_pred(v, where)


def criterion(c: dict, where: str) -> dict:
    keys(c, {"trigger", "conditions"}, where)
    t = c["trigger"]
    if t not in TRIGGER_FIELDS:
        fail(where, f"unsupported trigger {t}")
    cond = c.get("conditions", {})
    keys(cond, TRIGGER_FIELDS[t], where)
    out: dict = {}
    for k, v in cond.items():
        w = f"{where}.{k}"
        if k in ("player", "entity", "parent", "partner", "child", "source"):
            out[k] = context_pred(v, w)
        elif k == "items":
            out[k] = [item_pred(i, f"{w}[{n}]") for n, i in enumerate(v)]
        elif k == "item":
            out[k] = item_pred(v, w)
        elif k == "location":
            out[k] = conditions(v, w)
        elif k == "damage":
            out[k] = damage_pred(v, w)
        else:  # slots, effects
            out[k] = v
    return {"trigger": t, **({"conditions": out} if out else {})}


def advancement(a: dict, where: str) -> dict:
    keys(a, {"parent", "display", "criteria", "requirements", "rewards", "sends_telemetry_event"}, where)
    out: dict = {}
    if "parent" in a:
        out["parent"] = a["parent"]
    if "display" in a:
        d = dict(a["display"])
        keys(d, {"icon", "title", "description", "frame", "show_toast", "announce_to_chat", "hidden", "background"},
             where + ".display")
        icon = d["icon"]
        keys(icon, {"id", "count"}, where + ".display.icon")
        if icon.get("count", 1) != 1:
            fail(where, f"advancement icons have no count in {MINECRAFT}")
        d["icon"] = {"item": icon["id"]}
        out["display"] = d
    out["criteria"] = {name: criterion(c, f"{where}.criteria.{name}") for name, c in a["criteria"].items()}
    for k in ("requirements", "rewards", "sends_telemetry_event"):
        if k in a:
            out[k] = a[k]
    return out


# ---------------------------------------------------------------------------------------------------- other data

def biome_modifier(m: dict, where: str) -> dict:
    t = m.get("type")
    if t == "neoforge:add_features":
        keys(m, {"type", "biomes", "features", "step"}, where)
        return {"type": "forge:add_features", "biomes": m["biomes"], "features": m["features"], "step": m["step"]}
    if t == "neoforge:add_spawns":
        keys(m, {"type", "biomes", "spawners"}, where)
        spawners = m["spawners"] if isinstance(m["spawners"], list) else [m["spawners"]]
        for s in spawners:
            keys(s, {"type", "weight", "minCount", "maxCount"}, where + ".spawners")
        return {"type": "forge:add_spawns", "biomes": m["biomes"], "spawners": m["spawners"]}
    fail(where, f"unsupported biome modifier {t}")


def fabric_manifest(m: dict, where: str) -> dict:
    keys(m, {"features", "spawns"}, where)
    for f in m.get("features", []):
        keys(f, {"feature", "biomes", "step"}, where + ".features")
    for s in m.get("spawns", []):
        keys(s, {"entity", "biomes", "category", "weight", "min", "max"}, where + ".spawns")
    return m


def block_model(m: dict, where: str) -> dict:
    keys(m, {"parent", "textures", "elements", "ambientocclusion", "render_type", "display", "gui_light"}, where)
    out = copy.deepcopy(m)
    for i, el in enumerate(out.get("elements", [])):
        w = f"{where}.elements[{i}]"
        keys(el, {"from", "to", "rotation", "shade", "faces", "neoforge_data"}, w)
        if "rotation" in el and el["rotation"]["angle"] not in (-45, -22.5, 0, 22.5, 45):
            fail(w, f"element rotation {el['rotation']['angle']} is not allowed in {MINECRAFT}")
        if "neoforge_data" in el:
            data = el.pop("neoforge_data")
            keys(data, {"block_light", "sky_light", "ambient_occlusion", "color"}, w + ".neoforge_data")
            el["forge_data"] = data
        for face, f in el["faces"].items():
            keys(f, {"texture", "cullface", "uv", "rotation", "tintindex"}, f"{w}.faces.{face}")
    return out


# ---------------------------------------------------------------------------------------------------- converter

def validate(dst: Path, v: Vanilla) -> list[str]:
    """Every minecraft: id, tag, block state, model, texture and sound event referenced under dst must exist in
    the vanilla version; every #spore_and_stem: and #c: tag referenced must be generated. Returns the errors."""
    loot_types = {json.loads(p.read_text(encoding="utf-8")).get("type")
                  for p in (v.data / "loot_tables").rglob("*.json")}
    known = v.all_ids | v.triggers | APPLY_BONUS_FORMULAS | {t for t in loot_types if t}
    own_tags = set()
    for p in dst.glob("data/*/tags/**/*.json"):
        parts = p.relative_to(dst / "data").with_suffix("").parts  # ns, tags, folder.., name..
        own_tags.add(parts[0] + ":" + "/".join(parts[4 if parts[2] == "worldgen" else 3:]))
    errors: list[str] = []

    def check_state(state: dict, where: str) -> None:
        props = v.blocks.get(state["Name"])
        if props is None:
            errors.append(f"{where}: unknown block {state['Name']}")
            return
        for k, val in state.get("Properties", {}).items():
            if val not in props.get(k, []):
                errors.append(f"{where}: {state['Name']} has no state {k}={val}")

    def walk(obj, where: str, parent_key: str = "") -> None:
        if isinstance(obj, dict):
            if isinstance(obj.get("Name"), str) and obj["Name"].startswith("minecraft:"):
                check_state(obj, where)
            for k, val in obj.items():
                walk(val, where, k)
        elif isinstance(obj, list):
            for val in obj:
                walk(val, where, parent_key)
        elif isinstance(obj, str):
            tag = obj[1:] if obj.startswith("#") else obj if parent_key == "tag" else None
            if tag is not None:
                if tag.startswith("minecraft:") and tag not in v.all_tags:
                    errors.append(f"{where}: unknown vanilla tag #{tag}")
                elif tag.startswith(MOD_ID + ":") and tag not in own_tags:
                    errors.append(f"{where}: missing tag #{tag}")
                elif tag.startswith("c:") and not any(tag == t for t in own_tags):
                    errors.append(f"{where}: missing conventional tag #{tag}")
            elif obj.startswith("minecraft:") and obj not in known and not obj.startswith("minecraft:textures/"):
                errors.append(f"{where}: unknown vanilla id {obj}")

    for path in sorted(p for p in dst.rglob("*") if p.is_file()):
        rel = path.relative_to(dst).as_posix()
        if path.suffix != ".json":
            continue
        obj = json.loads(path.read_text(encoding="utf-8"))
        if rel.startswith("data/") or rel.startswith(MOD_ID + "/"):
            walk(obj, rel)
        elif "/models/" in rel:
            parent = qualify(obj.get("parent", ""))
            if parent.startswith("minecraft:") and parent not in v.models:
                errors.append(f"{rel}: unknown vanilla model {parent}")
            for tex in obj.get("textures", {}).values():
                tex = qualify(tex)
                if tex.startswith("minecraft:") and tex not in v.textures:
                    errors.append(f"{rel}: unknown vanilla texture {tex}")
            if "render_type" in obj and obj["render_type"] not in RENDER_TYPES:
                errors.append(f"{rel}: unknown render type {obj['render_type']}")
        elif "/blockstates/" in rel:
            for model in blockstate_models(obj):
                model = qualify(model)
                if model.startswith("minecraft:") and model not in v.models:
                    errors.append(f"{rel}: unknown vanilla model {model}")
        elif rel.endswith("sounds.json"):
            for event, body in obj.items():
                for snd in body.get("sounds", []):
                    if isinstance(snd, dict) and snd.get("type") == "event" and snd["name"] not in known:
                        errors.append(f"{rel}: {event} plays unknown sound event {snd['name']}")
    for name in gametest.PALETTE:
        check_state({"Name": name}, "GameTest arena")
    return errors


def qualify(ref: str) -> str:
    """Model and texture references without a namespace are minecraft's; '#var' references stay as they are."""
    return ref if not ref or ref.startswith("#") or ":" in ref else "minecraft:" + ref


def blockstate_models(bs: dict) -> list[str]:
    found = []
    for entry in list(bs.get("variants", {}).values()) + [part["apply"] for part in bs.get("multipart", [])]:
        found.extend(e["model"] for e in (entry if isinstance(entry, list) else [entry]))
    return found


class Port:
    def __init__(self, src: Path, dst: Path, vanilla: Vanilla | None):
        self.src, self.dst, self.vanilla = src, dst, vanilla
        self.written: list[Path] = []
        self.notes: dict[str, list[str]] = defaultdict(list)
        # (registry, "ns:path") -> tag json, collected first so conventional tags can be renamed and inlined
        self.tags: dict[tuple[str, str], dict] = {}

    # ---- output ------------------------------------------------------------------------------------------------
    def write_json(self, rel: str, obj) -> None:
        path = self.dst / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        self.written.append(path)

    def copy(self, src: Path, rel: str) -> None:
        path = self.dst / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, path)
        self.written.append(path)

    # ---- dispatch ----------------------------------------------------------------------------------------------
    def run(self) -> "Port":
        if self.dst.exists():
            shutil.rmtree(self.dst)
        for path in sorted(p for p in self.src.rglob("*") if p.is_file()):
            rel = path.relative_to(self.src)
            parts = rel.parts
            if parts[0] == "assets":
                self.asset(path, rel)
            elif parts[0] == "data":
                self.data(path, rel)
            elif rel.as_posix() == f"{MOD_ID}/biome_modifications.json":
                self.write_json(rel.as_posix(), fabric_manifest(self.load(path), rel.as_posix()))
            else:
                fail(rel.as_posix(), "unknown file in the generated tree")
        self.finish_tags()
        if self.vanilla is not None:
            self.validate()
        return self

    @staticmethod
    def load(path: Path):
        return json.loads(path.read_text(encoding="utf-8"))

    def asset(self, path: Path, rel: Path) -> None:
        parts = rel.parts  # assets/<ns>/<kind>/...
        if len(parts) > 3 and parts[2] == "models" and path.suffix == ".json":
            self.write_json(rel.as_posix(), block_model(self.load(path), rel.as_posix()))
        else:
            self.copy(path, rel.as_posix())

    def data(self, path: Path, rel: Path) -> None:
        ns, folder, rest = rel.parts[1], rel.parts[2], rel.parts[3:]
        where = rel.as_posix()
        if folder == "tags":
            registry, name = self.split_tag_path(rest)
            self.tags[(registry, f"{ns}:{name}")] = self.load(path)
            return
        if folder == "data_maps":
            name = f"{ns}:{Path(*rest).with_suffix('').as_posix()}"
            if name not in DROPPED_DATA_MAPS:
                fail(where, "unsupported data map")
            values = self.load(path)["values"]
            self.notes["dropped data maps"].append(f"{name} ({DROPPED_DATA_MAPS[name]}): "
                                                   + json.dumps(values, separators=(",", ":")))
            return
        sub = "/".join(rest)
        if folder in DATA_FOLDERS:
            out_rel = f"data/{ns}/{DATA_FOLDERS[folder]}/{sub}"
            if folder == "structure":
                if sub != "arena.nbt":
                    fail(where, "unknown structure (only the GameTest arena is generated)")
                self.dst.joinpath(out_rel).parent.mkdir(parents=True, exist_ok=True)
                self.dst.joinpath(out_rel).write_bytes(gametest.arena_nbt(DATA_VERSION))
                self.written.append(self.dst / out_rel)
                return
            convert = {"recipe": recipe, "loot_table": loot_table, "advancement": advancement}[folder]
            self.write_json(out_rel, rename(convert(self.load(path), where)))
        elif folder == "neoforge" and rest and rest[0] == "biome_modifier":
            self.write_json(f"data/{ns}/forge/biome_modifier/{'/'.join(rest[1:])}",
                            biome_modifier(self.load(path), where))
        elif folder == "worldgen":
            self.write_json(f"data/{ns}/worldgen/{sub}", wrap_providers(rename(self.load(path))))
        else:
            fail(where, "unknown data folder")

    @staticmethod
    def split_tag_path(rest: tuple[str, ...]) -> tuple[str, str]:
        depth = 2 if rest[0] == "worldgen" else 1
        registry = "/".join(rest[:depth])
        name = "/".join(rest[depth:])[:-len(".json")]
        return registry, name

    # ---- tags --------------------------------------------------------------------------------------------------
    def tag_target(self, registry: str, tag: str) -> list[tuple[str, str]] | None:
        """None: keep the tag as it is. []: drop it. Otherwise the 1.20.1 tags it becomes."""
        ns = tag.split(":", 1)[0]
        if ns == "c":
            if (registry, tag) not in CONVENTIONAL:
                fail(f"#{tag} ({registry})", "no 1.20.1 mapping for this conventional tag; add it to CONVENTIONAL")
            return CONVENTIONAL[(registry, tag)]
        if ns == "minecraft" and registry == "item" and (
                tag in DROPPED_VANILLA_ITEM_TAGS or tag.startswith(DROPPED_VANILLA_ITEM_TAG_PREFIXES)):
            return []
        return None

    def tag_values(self, registry: str, tag: str, seen: tuple = ()) -> list:
        if tag in seen:
            fail(f"#{tag}", "tag cycle")
        values = []
        for v in self.tags[(registry, tag)]["values"]:
            ref = v["id"] if isinstance(v, dict) else v
            if ref.startswith("#"):
                target = self.tag_target(registry, ref[1:]) if (registry, ref[1:]) in self.tags else None
                if target == []:
                    values.extend(x for x in self.tag_values(registry, ref[1:], seen + (tag,)) if x not in values)
                    self.notes["inlined tags"].append(f"{registry} {ref} (dropped) inlined into #{tag}")
                    continue
                if target:
                    ref = "#" + next(t for r, t in target if r == registry)
                    v = {**v, "id": ref} if isinstance(v, dict) else ref
            v = rename(v)
            if v not in values:
                values.append(v)
        return values

    def finish_tags(self) -> None:
        out: dict[tuple[str, str], dict] = {}
        for (registry, tag), body in sorted(self.tags.items()):
            keys(body, {"replace", "values"}, f"#{tag}")
            target = self.tag_target(registry, tag)
            values = self.tag_values(registry, tag)
            if target == []:
                self.notes["dropped tags"].append(f"{registry} #{tag}")
                continue
            for reg, name in (target or [(registry, tag)]):
                if target and name != tag:
                    self.notes["renamed conventional tags"].append(f"{registry} #{tag} -> #{name}")
                entry = out.setdefault((reg, name), {"replace": body.get("replace", False), "values": []})
                entry["values"].extend(v for v in values if v not in entry["values"])
        for (registry, tag), body in sorted(out.items()):
            ns, name = tag.split(":", 1)
            parts = registry.split("/")
            folder = "/".join([TAG_FOLDERS.get(parts[0], parts[0]), *parts[1:]])
            if parts[0] not in TAG_FOLDERS and parts[0] != "worldgen":
                fail(f"#{tag}", f"unknown tag registry {registry}")
            self.write_json(f"data/{ns}/tags/{folder}/{name}.json", body)

    # ---- validation against vanilla 1.20.1 ------------------------------------------------------------------------
    def validate(self) -> None:
        errors = validate(self.dst, self.vanilla)
        if errors:
            raise PortError(f"[{MINECRAFT}] {len(errors)} references do not exist in vanilla {MINECRAFT}:\n  "
                            + "\n  ".join(errors[:60]))

    def summary(self) -> list[str]:
        lines = []
        for title, items in self.notes.items():
            lines.append(f"{title}:")
            lines.extend(f"  {i}" for i in sorted(set(items)))
        return lines


def convert(src: Path, dst: Path, vanilla: Vanilla | None) -> Port:
    port = Port(src, dst, vanilla).run()
    notes = BUILD / f"port-{MINECRAFT}.txt"
    notes.parent.mkdir(parents=True, exist_ok=True)
    notes.write_text("\n".join(port.summary()) + "\n", encoding="utf-8")
    return port
