"""Block loot tables, recipes, tags, data maps and advancements (1.21.1 formats)."""
from __future__ import annotations

from .data_content import CULTIVATION, EDIBLE_FUNGI, FUNGUS_IDS, WOODS
from .out import Out, rid
from .paths import MOD_ID

KNIFE = f"#{MOD_ID}:foraging_tools"


def i(name: str) -> str:
    return rid(name)


# ------------------------------------------------------------------------------------------------- loot helpers

SURVIVES = {"condition": "minecraft:survives_explosion"}
SILK = {"condition": "minecraft:match_tool", "predicate": {"predicates": {"minecraft:enchantments": [
    {"enchantments": "minecraft:silk_touch", "levels": {"min": 1}}]}}}
SHEARS = {"condition": "minecraft:match_tool", "predicate": {"items": "minecraft:shears"}}
WITH_KNIFE = {"condition": "minecraft:match_tool", "predicate": {"items": KNIFE}}
SILK_OR_SHEARS = {"condition": "minecraft:any_of", "terms": [SILK, SHEARS]}


def table(*pools, kind="minecraft:block", random_sequence=None) -> dict:
    t = {"type": kind, "pools": list(pools)}
    if random_sequence:
        t["random_sequence"] = random_sequence
    return t


def pool(entries, conditions=None, rolls=1.0, functions=None) -> dict:
    p = {"rolls": rolls, "bonus_rolls": 0.0, "entries": entries}
    if conditions:
        p["conditions"] = conditions
    if functions:
        p["functions"] = functions
    return p


def item(name: str, functions=None, conditions=None, weight=None) -> dict:
    e = {"type": "minecraft:item", "name": i(name)}
    if functions:
        e["functions"] = functions
    if conditions:
        e["conditions"] = conditions
    if weight:
        e["weight"] = weight
    return e


def count(n, conditions=None, add=False) -> dict:
    f = {"function": "minecraft:set_count", "count": n, "add": add}
    if conditions:
        f["conditions"] = conditions
    return f


def uniform(lo, hi) -> dict:
    return {"type": "minecraft:uniform", "min": lo, "max": hi}


def fortune() -> dict:
    return {"function": "minecraft:apply_bonus", "enchantment": "minecraft:fortune", "formula": "minecraft:uniform_bonus_count",
            "parameters": {"bonusMultiplier": 1}}


def decay() -> dict:
    return {"function": "minecraft:explosion_decay"}


def state_is(block: str, **props) -> dict:
    return {"condition": "minecraft:block_state_property", "block": i(block),
            "properties": {k: str(v).lower() for k, v in props.items()}}


def self_drop(block: str) -> dict:
    return table(pool([item(block)], [SURVIVES]), random_sequence=f"{MOD_ID}:blocks/{block}")


def block_loot(out: Out, name: str, t: dict) -> None:
    t.setdefault("random_sequence", f"{MOD_ID}:blocks/{name}")
    out.loot_table("blocks", name, t)


# ------------------------------------------------------------------------------------------------- loot tables

def loot(out: Out) -> None:
    for f in FUNGUS_IDS:
        # a fungus drops itself; cut with a Foraging Knife it drops two
        block_loot(out, f, table(pool([item(f, functions=[count(2.0, [WITH_KNIFE])])], [SURVIVES])))
        block_loot(out, f"potted_{f}", table(pool([item("minecraft:flower_pot")], [SURVIVES]),
                                             pool([item(f)], [SURVIVES])))

    extras = {"glowcap": "lumen_spores", "bouncecap": "bouncecap_gel", "inkcap": "minecraft:ink_sac"}
    for w in WOODS:
        cap = f"{w}_cap"
        # Caps drop themselves (they are Mycoleather's raw material) and sometimes their spores, gel or ink, more
        # often when cut with a knife; now and then a small fungus to start a new one.
        block_loot(out, cap, table(
            pool([item(cap)], [SURVIVES]),
            pool([item(extras[w], functions=[count(uniform(1, 2)), decay()])],
                 [{"condition": "minecraft:any_of", "terms": [
                     {"condition": "minecraft:all_of", "terms": [WITH_KNIFE, {"condition": "minecraft:random_chance",
                                                                              "chance": 0.5}]},
                     {"condition": "minecraft:random_chance", "chance": 0.2}]}]),
            pool([item(w)], [{"condition": "minecraft:random_chance", "chance": 0.05}, SURVIVES])))
        for suffix in ("stem", "hyphae", "planks", "stairs", "fence", "fence_gate", "trapdoor", "button",
                       "pressure_plate"):
            block_loot(out, f"{w}_{suffix}", self_drop(f"{w}_{suffix}"))
        for suffix in ("stem", "hyphae"):
            block_loot(out, f"stripped_{w}_{suffix}", self_drop(f"stripped_{w}_{suffix}"))
        slab = f"{w}_slab"
        block_loot(out, slab, table(pool([item(slab, functions=[count(2.0, [state_is(slab, type="double")]), decay()])])))
        door = f"{w}_door"
        block_loot(out, door, table(pool([item(door)], [state_is(door, half="lower"), SURVIVES])))

    block_loot(out, "glowcap_gills", table(
        pool([{"type": "minecraft:alternatives", "children": [
            item("glowcap_gills", conditions=[SILK_OR_SHEARS]),
            item("lumen_spores", functions=[count(uniform(1, 2)), fortune(), decay()])]}])))
    shelves = [count(float(n), [state_is("shelf_fungus", shelves=n)]) for n in (2, 3)]
    block_loot(out, "shelf_fungus", table(pool([item("shelf_fungus", functions=shelves + [decay()])])))
    for veil in ("mycelial_veil", "mycelial_veil_plant"):
        block_loot(out, veil, table(
            pool([{"type": "minecraft:alternatives", "children": [
                item("mycelial_veil", conditions=[SILK_OR_SHEARS]),
                item("mycelial_thread", conditions=[WITH_KNIFE], functions=[count(uniform(1, 2))]),
                item("mycelial_thread", conditions=[{"condition": "minecraft:random_chance", "chance": 0.33}])]}]),
            pool([item("lumen_spores")], [state_is(veil, bulb=True)])))
    block_loot(out, "giant_puffball", table(pool([{"type": "minecraft:alternatives", "children": [
        item("giant_puffball", conditions=[SILK]),
        item("puffball", functions=[count(uniform(2, 4)), decay()])]}])))
    block_loot(out, "truffle_soil", table(
        pool([{"type": "minecraft:alternatives", "children": [
            item("truffle_soil", conditions=[SILK]),
            item("truffle", functions=[count(uniform(1, 2)), fortune(), decay()])]}]),
        pool([item("minecraft:dirt")], [{"condition": "minecraft:inverted", "term": SILK}, SURVIVES])))
    for name in ("mycelial_soil", "glowcap_lantern"):
        block_loot(out, name, self_drop(name))
    log = "cultivation_log"
    ripe = [pool([item(f, functions=[count(2.0)])], [state_is(log, fungus=f, stage=3), SURVIVES]) for f in CULTIVATION]
    block_loot(out, log, table(pool([item(log)], [SURVIVES]), *ripe))


# ------------------------------------------------------------------------------------------------- recipes

def ing(x: str) -> dict:
    return {"tag": x[1:]} if x.startswith("#") else {"item": i(x)}


def shaped(out: Out, name: str, pattern: list[str], key: dict, result: str, n: int = 1, category: str = "misc",
           group: str | None = None) -> None:
    r = {"type": "minecraft:crafting_shaped", "category": category, "pattern": pattern,
         "key": {k: ing(v) for k, v in key.items()}, "result": {"id": i(result), "count": n}}
    if group:
        r["group"] = group
    out.recipe(name, r)


def shapeless(out: Out, name: str, ingredients: list[str], result: str, n: int = 1, category: str = "misc",
              group: str | None = None) -> None:
    r = {"type": "minecraft:crafting_shapeless", "category": category, "ingredients": [ing(x) for x in ingredients],
         "result": {"id": i(result), "count": n}}
    if group:
        r["group"] = group
    out.recipe(name, r)


def cooking(out: Out, name: str, kind: str, ingredient: str, result: str, xp: float, time: int) -> None:
    out.recipe(name, {"type": f"minecraft:{kind}", "category": "food", "ingredient": ing(ingredient),
                      "result": {"id": i(result)}, "experience": xp, "cookingtime": time})


def recipes(out: Out) -> None:
    for w in WOODS:
        p = f"{w}_planks"
        shapeless(out, p, [f"#{MOD_ID}:{w}_stems"], p, 4, "building", "planks")
        shaped(out, f"{w}_hyphae", ["##", "##"], {"#": f"{w}_stem"}, f"{w}_hyphae", 3, "building", "bark")
        shaped(out, f"stripped_{w}_hyphae", ["##", "##"], {"#": f"stripped_{w}_stem"}, f"stripped_{w}_hyphae", 3,
               "building", "bark")
        shaped(out, f"{w}_stairs", ["#  ", "## ", "###"], {"#": p}, f"{w}_stairs", 4, "building", "wooden_stairs")
        shaped(out, f"{w}_slab", ["###"], {"#": p}, f"{w}_slab", 6, "building", "wooden_slab")
        shaped(out, f"{w}_fence", ["W#W", "W#W"], {"W": p, "#": "minecraft:stick"}, f"{w}_fence", 3, "misc",
               "wooden_fence")
        shaped(out, f"{w}_fence_gate", ["#W#", "#W#"], {"W": p, "#": "minecraft:stick"}, f"{w}_fence_gate", 1,
               "redstone", "wooden_fence_gate")
        shaped(out, f"{w}_door", ["##", "##", "##"], {"#": p}, f"{w}_door", 3, "redstone", "wooden_door")
        shaped(out, f"{w}_trapdoor", ["###", "###"], {"#": p}, f"{w}_trapdoor", 2, "redstone", "wooden_trapdoor")
        shapeless(out, f"{w}_button", [p], f"{w}_button", 1, "redstone", "wooden_button")
        shaped(out, f"{w}_pressure_plate", ["##"], {"#": p}, f"{w}_pressure_plate", 1, "redstone",
               "wooden_pressure_plate")

    caps = f"#{MOD_ID}:caps"
    shapeless(out, "mycoleather", [caps, caps, caps, "mycelial_thread"], "mycoleather", 2)
    shapeless(out, "string_from_mycelial_thread", ["mycelial_thread", "mycelial_thread"], "minecraft:string")
    shapeless(out, "black_dye_from_inkcap", ["inkcap"], "minecraft:black_dye", 1, "misc", "black_dye")
    shapeless(out, "mycelial_soil", ["minecraft:dirt", "minecraft:bone_meal", f"#{MOD_ID}:fungi", f"#{MOD_ID}:fungi"],
              "mycelial_soil", 2, "building")
    shaped(out, "giant_puffball", ["###", "###", "###"], {"#": "puffball"}, "giant_puffball", 1, "building")
    shaped(out, "glowcap_lantern", [" T ", "SLS", " S "], {"T": "mycelial_thread", "S": f"#{MOD_ID}:glowcap_stems",
                                                            "L": "lumen_spores"}, "glowcap_lantern", 1, "building")
    shaped(out, "cultivation_log", ["LLL", "TST"], {"L": "#minecraft:logs_that_burn", "T": "mycelial_thread",
                                                     "S": "mycelial_soil"}, "cultivation_log", 2, "building")
    shaped(out, "fruiting_heart", ["LTL", "MCM", "LTL"], {"L": "lumen_spores", "T": "truffle", "M": "mycoleather",
                                                           "C": "mycelial_core"}, "fruiting_heart")

    # food
    cooking(out, "roasted_morel", "smelting", "morel", "roasted_morel", 0.35, 200)
    cooking(out, "roasted_morel_from_smoking", "smoking", "morel", "roasted_morel", 0.35, 100)
    cooking(out, "roasted_morel_from_campfire_cooking", "campfire_cooking", "morel", "roasted_morel", 0.35, 600)
    shapeless(out, "chanterelle_toast", ["minecraft:bread", "chanterelle", "chanterelle"], "chanterelle_toast", 1, "misc")
    shapeless(out, "glowcap_soup", ["minecraft:bowl", "glowcap", "glowcap", "lumen_spores"], "glowcap_soup")
    shapeless(out, "bouncecap_jelly", ["minecraft:glass_bottle", "bouncecap_gel", "minecraft:sugar"], "bouncecap_jelly")
    shapeless(out, "frostcap_tea", ["minecraft:glass_bottle", "frostcap", "frostcap", "minecraft:sugar"], "frostcap_tea")
    shapeless(out, "ember_skewer", ["minecraft:stick", "emberstool", "roasted_morel"], "ember_skewer")
    shapeless(out, "truffle_stew", ["minecraft:bowl", "truffle", "morel", "chanterelle", "minecraft:baked_potato"],
              "truffle_stew")
    edible = f"#{MOD_ID}:edible_fungi"
    shapeless(out, "foragers_stew", ["minecraft:bowl", edible, edible, edible], "foragers_stew")
    shapeless(out, "antifungal_tonic", ["minecraft:glass_bottle", "frostcap", "chanterelle", "minecraft:honey_bottle"],
              "antifungal_tonic")

    # gear
    shaped(out, "foraging_knife", ["  I", " T ", "S  "], {"I": "minecraft:iron_ingot", "T": "mycelial_thread",
                                                          "S": "minecraft:stick"}, "foraging_knife", 1, "equipment")
    shapeless(out, "spore_bomb", ["puffball", "deathcap", "mycelial_thread"], "spore_bomb", 2, "equipment")
    m = "mycoleather"
    shaped(out, "mycoleather_hood", ["###", "# #"], {"#": m}, "mycoleather_hood", 1, "equipment")
    shaped(out, "mycoleather_tunic", ["# #", "###", "###"], {"#": m}, "mycoleather_tunic", 1, "equipment")
    shaped(out, "mycoleather_leggings", ["###", "# #", "# #"], {"#": m}, "mycoleather_leggings", 1, "equipment")
    shaped(out, "mycoleather_boots", ["# #", "# #"], {"#": m}, "mycoleather_boots", 1, "equipment")
    shapeless(out, "bloomreaver", ["spore_heart", "minecraft:diamond_sword", "lumen_spores", "lumen_spores",
                                   "mycoleather", "mycoleather"], "bloomreaver", 1, "equipment")
    shapeless(out, "crown_of_the_bloom", ["spore_heart", "minecraft:golden_helmet", "glowcap_cap", "glowcap_cap"],
              "crown_of_the_bloom", 1, "equipment")


# ------------------------------------------------------------------------------------------------- tags

def tags(out: Out) -> None:
    small = [i(f) for f in FUNGUS_IDS]
    potted = [i(f"potted_{f}") for f in FUNGUS_IDS]
    caps = [i(f"{w}_cap") for w in WOODS]
    for w in WOODS:
        stems = [i(f"{w}_stem"), i(f"stripped_{w}_stem"), i(f"{w}_hyphae"), i(f"stripped_{w}_hyphae")]
        for reg in ("block", "item"):
            out.tag(reg, f"{w}_stems", stems)
            out.tag(reg, "minecraft:logs", f"#{MOD_ID}:{w}_stems")
            out.tag(reg, "minecraft:planks", i(f"{w}_planks"))
            out.tag(reg, "minecraft:wooden_stairs", i(f"{w}_stairs"))
            out.tag(reg, "minecraft:wooden_slabs", i(f"{w}_slab"))
            out.tag(reg, "minecraft:wooden_fences", i(f"{w}_fence"))
            out.tag(reg, "minecraft:fence_gates", i(f"{w}_fence_gate"))
            out.tag(reg, "minecraft:wooden_doors", i(f"{w}_door"))
            out.tag(reg, "minecraft:wooden_trapdoors", i(f"{w}_trapdoor"))
            out.tag(reg, "minecraft:wooden_buttons", i(f"{w}_button"))
            out.tag(reg, "minecraft:wooden_pressure_plates", i(f"{w}_pressure_plate"))
        out.tag("block", "minecraft:mineable/axe", stems + [i(f"{w}_{s}") for s in (
            "planks", "stairs", "slab", "fence", "fence_gate", "door", "trapdoor", "button", "pressure_plate", "cap")])
    out.tag("item", "c:stripped_logs", [i(f"stripped_{w}_stem") for w in WOODS])
    out.tag("block", "c:stripped_logs", [i(f"stripped_{w}_stem") for w in WOODS])
    out.tag("item", "c:stripped_woods", [i(f"stripped_{w}_hyphae") for w in WOODS])
    out.tag("block", "c:stripped_woods", [i(f"stripped_{w}_hyphae") for w in WOODS])

    for reg in ("block", "item"):
        out.tag(reg, "fungi", small + ["minecraft:red_mushroom", "minecraft:brown_mushroom"])
        out.tag(reg, "caps", caps)
    out.tag("item", "edible_fungi", [i(f) for f in EDIBLE_FUNGI if f != "deathcap"]
            + ["minecraft:red_mushroom", "minecraft:brown_mushroom"])
    out.tag("item", "foraging_tools", i("foraging_knife"))
    out.tag("block", "fungus_soil", ["#minecraft:dirt", "minecraft:moss_block", "minecraft:mycelium", "#minecraft:nylium",
                                     "minecraft:mud", "minecraft:muddy_mangrove_roots", i("mycelial_soil"),
                                     i("truffle_soil")])
    out.tag("block", "shelf_fungus_hosts", "#minecraft:logs")
    out.tag("block", "myceliarch_summon_blocks", ["minecraft:mycelium", i("mycelial_soil"), "minecraft:podzol",
                                                  "minecraft:moss_block"])
    out.tag("block", "mineable/knife", small + caps + [i("glowcap_gills"), i("shelf_fungus"), i("mycelial_veil"),
                                                       i("mycelial_veil_plant"), i("giant_puffball"),
                                                       "minecraft:red_mushroom_block", "minecraft:brown_mushroom_block",
                                                       "minecraft:mushroom_stem", "minecraft:red_mushroom",
                                                       "minecraft:brown_mushroom", "#minecraft:cave_vines"])
    out.tag("block", "minecraft:mineable/axe", [i("shelf_fungus"), i("cultivation_log"), i("glowcap_lantern")])
    out.tag("block", "minecraft:mineable/hoe", [i("glowcap_gills"), i("giant_puffball"), i("mycelial_veil"),
                                                i("mycelial_veil_plant")] + caps)
    out.tag("block", "minecraft:mineable/shovel", [i("truffle_soil"), i("mycelial_soil")])
    out.tag("block", "minecraft:mushroom_grow_block", i("mycelial_soil"))
    out.tag("block", "minecraft:dirt", [i("mycelial_soil"), i("truffle_soil")])
    out.tag("block", "minecraft:climbable", [i("mycelial_veil"), i("mycelial_veil_plant")])
    out.tag("block", "minecraft:enderman_holdable", small + [i("giant_puffball")])
    out.tag("block", "minecraft:flower_pots", potted)
    out.tag("block", "minecraft:sword_efficient", small + [i("mycelial_veil"), i("mycelial_veil_plant"),
                                                           i("glowcap_gills")])
    out.tag("block", "minecraft:inside_step_sound_blocks", small)

    out.tag("item", "c:mushrooms", small)
    out.tag("item", "c:leathers", i("mycoleather"))
    out.tag("item", "c:slime_balls", i("bouncecap_gel"))
    out.tag("item", "c:strings", i("mycelial_thread"))
    out.tag("item", "c:foods/soup", [i("glowcap_soup"), i("truffle_stew"), i("foragers_stew")])
    out.tag("item", "c:foods/food_poisoning", i("deathcap"))
    out.tag("item", "c:foods/edible_when_placed", [i(f) for f in EDIBLE_FUNGI])
    out.tag("item", "c:drinks", [i("bouncecap_jelly"), i("frostcap_tea"), i("antifungal_tonic")])
    out.tag("item", "c:foods", ["#c:foods/soup", i("roasted_morel"), i("chanterelle_toast"), i("ember_skewer"),
                                i("truffle"), i("bouncecap_jelly"), i("frostcap_tea"), i("antifungal_tonic")]
            + [i(f) for f in EDIBLE_FUNGI])
    armor = {"head": ["mycoleather_hood", "crown_of_the_bloom"], "chest": ["mycoleather_tunic"],
             "leg": ["mycoleather_leggings"], "foot": ["mycoleather_boots"]}
    for slot, items in armor.items():
        out.tag("item", f"minecraft:{slot}_armor", [i(x) for x in items])
    out.tag("item", "minecraft:trimmable_armor", [i("mycoleather_hood"), i("mycoleather_tunic"),
                                                  i("mycoleather_leggings"), i("mycoleather_boots")])
    out.tag("item", "minecraft:swords", i("bloomreaver"))
    for t in ("minecraft:enchantable/mining", "minecraft:enchantable/mining_loot", "minecraft:enchantable/durability"):
        out.tag("item", t, i("foraging_knife"))
    # Tag names, shown by recipe viewers and asked for by Fabric's convention tags.
    names = {"fungi": "Fungi", "edible_fungi": "Edible Fungi", "caps": "Mushroom Caps",
             "glowcap_stems": "Glowcap Stems", "bouncecap_stems": "Bouncecap Stems", "inkcap_stems": "Inkcap Stems",
             "foraging_tools": "Foraging Tools"}
    for path, name in names.items():
        out.tr(f"tag.item.{MOD_ID}.{path}", name)


def data_maps(out: Out) -> None:
    """Mirrors registry/ModCompostables.java (Fabric registers those in code)."""
    chances = {f: 0.65 for f in FUNGUS_IDS}
    chances.update({f"{w}_cap": 0.85 for w in WOODS})
    chances.update({"glowcap_gills": 0.65, "shelf_fungus": 0.65, "mycelial_veil": 0.5, "giant_puffball": 0.85,
                    "truffle": 0.65, "lumen_spores": 0.3})
    for name, chance in chances.items():
        out.data_map("neoforge:item/compostables", i(name), {"chance": chance})


# ------------------------------------------------------------------------------------------------- advancements

ADVANCEMENTS = [
    # id, parent, icon, frame, title, description, criteria
    ("root", None, "glowcap", "task", "Spore & Stem", "Find one of the strange new fungi",
     {"fungus": ("inventory_changed", {"items": [{"items": f"#{MOD_ID}:fungi"}]})}),
    ("glowcap", "root", "glowcap", "task", "Lights Out, Caps On", "Pick a Glowcap, the mushroom that glows",
     {"glowcap": ("inventory_changed", {"items": [{"items": i("glowcap")}]})}),
    ("all_fungi", "glowcap", "morel", "challenge", "Mycophile", "Collect every kind of small fungus",
     {f: ("inventory_changed", {"items": [{"items": i(f)}]}) for f in FUNGUS_IDS}),
    ("bounce", "root", "bouncecap", "task", "Bounce House", "Stand on the cap of a Huge Bouncecap",
     {"bounce": ("location", {"player": [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {
         "stepping_on": {"block": {"blocks": i("bouncecap_cap")}}}}]})}),
    ("cultivate", "root", "cultivation_log", "task", "Patience of a Log", "Inoculate a Cultivation Log with a fungus",
     {"inoculate": ("item_used_on_block", {"location": [
         {"condition": "minecraft:location_check", "predicate": {"block": {"blocks": i("cultivation_log")}}},
         {"condition": "minecraft:match_tool", "predicate": {"items": f"#{MOD_ID}:fungi"}}]})}),
    ("mycoleather", "root", "mycoleather", "task", "Grown, Not Tanned", "Make Mycoleather from mushroom caps",
     {"mycoleather": ("inventory_changed", {"items": [{"items": i("mycoleather")}]})}),
    ("full_mycoleather", "mycoleather", "mycoleather_hood", "goal", "Mycologist",
     "Wear a full set of Mycoleather and breathe easy among the spores",
     {"wear": ("tick", {"player": [{"condition": "minecraft:entity_properties", "entity": "this", "predicate": {
         "equipment": {"head": {"items": i("mycoleather_hood")}, "chest": {"items": i("mycoleather_tunic")},
                       "legs": {"items": i("mycoleather_leggings")}, "feet": {"items": i("mycoleather_boots")}}}}]})}),
    ("truffle", "root", "truffle", "task", "Truffle Shuffle", "Dig up a Truffle",
     {"truffle": ("inventory_changed", {"items": [{"items": i("truffle")}]})}),
    ("tame_sporeling", "truffle", "sporeling_spawn_egg", "task", "A Friend in Spores", "Tame a Sporeling with Truffles",
     {"tame": ("tame_animal", {"entity": [{"condition": "minecraft:entity_properties", "entity": "this",
                                           "predicate": {"type": i("sporeling")}}]})}),
    ("bloatshroom", "root", "puffball", "task", "Pop Goes the Puffball", "Kill a Bloatshroom",
     {"kill": ("player_killed_entity", {"entity": [{"condition": "minecraft:entity_properties", "entity": "this",
                                                    "predicate": {"type": i("bloatshroom")}}]})}),
    ("mimicap", "bloatshroom", "mimicap_spawn_egg", "task", "That Mushroom Has Teeth", "Get bitten by a Mimicap",
     {"bitten": ("entity_hurt_player", {"damage": {"source_entity": {"type": i("mimicap")}}})}),
    ("tonic", "root", "antifungal_tonic", "task", "Clean Bill of Health", "Drink an Antifungal Tonic",
     {"drink": ("consume_item", {"item": {"items": i("antifungal_tonic")}})}),
    ("summon", "root", "fruiting_heart", "goal", "The Fruiting Body", "Call up the Myceliarch with a Fruiting Heart",
     {"summon": ("item_used_on_block", {"location": [
         {"condition": "minecraft:location_check", "predicate": {"block": {"blocks": f"#{MOD_ID}:myceliarch_summon_blocks"}}},
         {"condition": "minecraft:match_tool", "predicate": {"items": i("fruiting_heart")}}]})}),
    ("kill_myceliarch", "summon", "spore_heart", "challenge", "Uprooted", "Defeat the Myceliarch",
     {"kill": ("player_killed_entity", {"entity": [{"condition": "minecraft:entity_properties", "entity": "this",
                                                    "predicate": {"type": i("myceliarch")}}]})}),
    ("bloomreaver", "kill_myceliarch", "bloomreaver", "goal", "Reap What You Sow", "Forge the Bloomreaver",
     {"bloomreaver": ("inventory_changed", {"items": [{"items": i("bloomreaver")}]})}),
]


def advancements(out: Out) -> None:
    for aid, parent, icon, frame, title, desc, criteria in ADVANCEMENTS:
        display = {"icon": {"id": i(icon)}, "title": {"translate": f"advancements.{MOD_ID}.{aid}.title"},
                   "description": {"translate": f"advancements.{MOD_ID}.{aid}.description"}, "frame": frame,
                   "show_toast": aid != "root", "announce_to_chat": aid != "root", "hidden": False}
        if aid == "root":
            display["background"] = f"{MOD_ID}:textures/block/mycelial_soil_top.png"
        adv = {"display": display,
               "criteria": {name: {"trigger": f"minecraft:{trig}", "conditions": cond}
                            for name, (trig, cond) in criteria.items()},
               "requirements": [[name] for name in criteria]}
        if parent:
            adv["parent"] = f"{MOD_ID}:{parent}"
        if frame == "challenge":
            adv["rewards"] = {"experience": 100}
        out.advancement(aid, adv)
        out.tr(f"advancements.{MOD_ID}.{aid}.title", title)
        out.tr(f"advancements.{MOD_ID}.{aid}.description", desc)


def generate(out: Out) -> None:
    loot(out)
    recipes(out)
    tags(out)
    data_maps(out)
    advancements(out)
