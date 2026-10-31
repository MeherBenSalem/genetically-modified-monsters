"""World generation data: configured and placed features, the biome tags that decide where they go, NeoForge biome
modifiers, and spore_and_stem/biome_modifications.json (the same table, read by FabricWorldgen on Fabric).

Every placed feature gets its own biome tag, #spore_and_stem:has_feature/<name>, and every spawn entry its own
#spore_and_stem:spawns/<name>, so datapacks can move anything without touching code. Densities follow
docs/DESIGN.md section 5: the Mushroom Fields are the showcase, everywhere else fungi are discoveries.
"""
from __future__ import annotations

from .out import Out
from .paths import MOD_ID

VEGETAL = "vegetal_decoration"
ORES = "underground_ores"


def ns(path: str) -> str:
    return path if ":" in path else f"{MOD_ID}:{path}"


def mc(path: str) -> str:
    return path if ":" in path else f"minecraft:{path}"


def state(block: str, **props) -> dict:
    s = {"Name": ns(block) if ":" not in block else block}
    if props:
        s["Properties"] = {k: str(v).lower() for k, v in props.items()}
    return s


def uniform(lo: int, hi: int) -> dict:
    return {"type": "minecraft:uniform", "min_inclusive": lo, "max_inclusive": hi}


# ---------------------------------------------------------------------------------------------- configured features

def huge(kind: str, height, radius, any_ground: bool = False) -> dict:
    config = {"height": height, "radius": radius}
    if any_ground:
        config["any_ground"] = True
    return {"type": ns(kind), "config": config}


def air_or(*blocks: str) -> dict:
    return {"type": "minecraft:matching_blocks", "blocks": [mc("air"), *blocks] if blocks else mc("air")}


def patch(block: str, tries: int, xz: int, y: int, *, replace: tuple[str, ...] = (), extra: list | None = None) -> dict:
    """A random patch of a small fungus: only into air (or the listed blocks) and only where it would survive."""
    predicates = [air_or(*replace), {"type": "minecraft:would_survive", "state": state(block)}]
    predicates += extra or []
    return {
        "type": "minecraft:random_patch",
        "config": {
            "tries": tries, "xz_spread": xz, "y_spread": y,
            "feature": {
                "feature": {"type": "minecraft:simple_block",
                            "config": {"to_place": {"type": "minecraft:simple_state_provider", "state": state(block)}}},
                "placement": [{"type": "minecraft:block_predicate_filter",
                               "predicate": {"type": "minecraft:all_of", "predicates": predicates}}],
            },
        },
    }


def _lava_at(offsets) -> dict:
    return {"type": "minecraft:any_of", "predicates": [
        {"type": "minecraft:matching_fluids", "offset": list(o), "fluids": [mc("lava"), mc("flowing_lava")]} for o in offsets]}


def near_lava() -> list:
    """Lava three blocks away (light 12): close enough to feel its warmth, dark enough for the fungus to survive.
    Fungi on bare stone need light below 13, so nothing is placed where lava is any closer."""
    ring3 = [(3, 0, 0), (-3, 0, 0), (0, 0, 3), (0, 0, -3), (2, 0, 1), (-2, 0, 1), (2, 0, -1), (-2, 0, -1),
             (1, 0, 2), (-1, 0, 2), (1, 0, -2), (-1, 0, -2), (2, -1, 0), (-2, -1, 0), (0, -1, 2), (0, -1, -2)]
    close = [(dx, dy, dz) for dx in range(-2, 3) for dz in range(-2, 3) for dy in (0, -1)
             if 0 < abs(dx) + abs(dz) + abs(dy) <= 2]
    return [_lava_at(ring3), {"type": "minecraft:not", "predicate": _lava_at(close)}]


CONFIGURED: dict[str, dict] = {
    # Bone meal grows small Glowcaps, Bouncecaps and Inkcaps through these three (ModConfiguredFeatures).
    "huge_glowcap": huge("huge_glowcap", uniform(6, 10), uniform(3, 4)),
    "huge_bouncecap": huge("huge_bouncecap", uniform(3, 5), uniform(3, 4)),
    "huge_inkcap": huge("huge_inkcap", uniform(7, 12), 2),
    # Variants for worldgen.
    "huge_inkcap_tall": huge("huge_inkcap", uniform(9, 13), {"type": "minecraft:weighted_list", "distribution": [
        {"weight": 3, "data": 2}, {"weight": 1, "data": 3}]}),
    "cave_huge_glowcap": huge("huge_glowcap", uniform(4, 7), uniform(2, 3), any_ground=True),
    "patch_glowcap": patch("glowcap", 28, 6, 2),
    "patch_glowcap_cave": patch("glowcap", 20, 4, 2),
    "patch_bouncecap": patch("bouncecap", 24, 5, 2),
    "patch_inkcap": patch("inkcap", 24, 5, 2),
    "patch_morel": patch("morel", 16, 5, 2),
    "patch_chanterelle": patch("chanterelle", 20, 5, 2),
    "patch_deathcap": patch("deathcap", 16, 5, 2),
    "patch_frostcap": patch("frostcap", 20, 5, 2, replace=(mc("snow"),)),
    "patch_emberstool": patch("emberstool", 16, 4, 2),
    "patch_emberstool_lava": patch("emberstool", 32, 5, 2, extra=near_lava()),
    "patch_emberstool_nether": patch("emberstool", 24, 6, 3),
    "patch_puffball": patch("puffball", 20, 5, 2),
    "patch_giant_puffball": {
        "type": "minecraft:random_patch",
        "config": {
            "tries": 8, "xz_spread": 4, "y_spread": 1,
            "feature": {
                "feature": {"type": "minecraft:simple_block", "config": {
                    "to_place": {"type": "minecraft:simple_state_provider", "state": state("giant_puffball")}}},
                "placement": [{"type": "minecraft:block_predicate_filter", "predicate": {"type": "minecraft:all_of", "predicates": [
                    air_or(),
                    {"type": "minecraft:matching_blocks", "offset": [0, -1, 0], "blocks": [mc("grass_block"), mc("dirt"), mc("podzol")]},
                ]}}],
            },
        },
    },
    "shelf_fungus": {"type": ns("shelf_fungus"), "config": {"count": uniform(8, 14)}},
    "mycelial_veil": {"type": ns("mycelial_veil"), "config": {"count": uniform(3, 6)}},
    "fairy_ring": {"type": ns("fairy_ring"), "config": {
        "fungus": {"type": "minecraft:weighted_state_provider", "entries": [
            {"weight": 4, "data": state("puffball")},
            {"weight": 3, "data": state("bouncecap")},
            {"weight": 2, "data": state("chanterelle")},
            {"weight": 1, "data": state("morel")},
        ]},
        "radius": uniform(3, 5),
        "center_chance": 0.2,
    }},
    "ore_truffle_soil": {"type": "minecraft:ore", "config": {
        "size": 8, "discard_chance_on_air_exposure": 0.3,
        "targets": [{"target": {"predicate_type": "minecraft:block_match", "block": mc("dirt")}, "state": state("truffle_soil")}],
    }},
}

# ---------------------------------------------------------------------------------------------- placement modifiers


def rarity(chance: int) -> dict:
    return {"type": "minecraft:rarity_filter", "chance": chance}


def count(n) -> dict:
    return {"type": "minecraft:count", "count": n}


IN_SQUARE = {"type": "minecraft:in_square"}
BIOME = {"type": "minecraft:biome"}


def heightmap(kind: str = "MOTION_BLOCKING_NO_LEAVES") -> dict:
    return {"type": "minecraft:heightmap", "heightmap": kind}


DRY = {"type": "minecraft:surface_water_depth_filter", "max_water_depth": 0}


def height(lo: dict, hi: dict) -> dict:
    return {"type": "minecraft:height_range", "height": {"type": "minecraft:uniform", "min_inclusive": lo, "max_inclusive": hi}}


def absolute(y: int) -> dict:
    return {"absolute": y}


def above_bottom(y: int) -> dict:
    return {"above_bottom": y}


FLOOR_SCAN = {"type": "minecraft:environment_scan", "direction_of_search": "down", "max_steps": 16,
              "allowed_search_condition": {"type": "minecraft:matching_blocks", "blocks": mc("air")},
              "target_condition": {"type": "minecraft:solid"}}
CEILING_SCAN = {"type": "minecraft:environment_scan", "direction_of_search": "up", "max_steps": 12,
                "allowed_search_condition": {"type": "minecraft:matching_blocks", "blocks": mc("air")},
                "target_condition": {"type": "minecraft:has_sturdy_face", "direction": "down"}}


def offset_y(y) -> dict:
    return {"type": "minecraft:random_offset", "xz_spread": 0, "y_spread": y}


def underground(depth: int) -> dict:
    """Keeps a placement at least `depth` blocks under the surface (never on the surface of a cave opening)."""
    return {"type": "minecraft:surface_relative_threshold_filter", "heightmap": "OCEAN_FLOOR_WG", "max_inclusive": -depth}


def surface(*mods) -> list:
    return [*mods, IN_SQUARE, heightmap(), DRY, BIOME]


def cave_floor(n, lo: dict, hi: dict, depth: int = 8) -> list:
    return [count(n), IN_SQUARE, height(lo, hi), FLOOR_SCAN, offset_y(1), underground(depth), BIOME]


# ---------------------------------------------------------------------------------------------- biomes

OVERWORLD = ["#minecraft:is_overworld"]
LAND = ["#spore_and_stem:overworld_land"]
OLD_GROWTH_TAIGA = [mc("old_growth_pine_taiga"), mc("old_growth_spruce_taiga")]
BIRCH = [mc("birch_forest"), mc("old_growth_birch_forest")]

# name: (configured feature, placement, biomes, step)
PLACED: dict[str, tuple[str, list, list[str], str]] = {
    # The showcase: Mushroom Fields become a forest of giants.
    "huge_glowcap_grove": ("huge_glowcap", surface(count(1)), [mc("mushroom_fields")], VEGETAL),
    "huge_bouncecap_grove": ("huge_bouncecap", surface(rarity(2)), [mc("mushroom_fields")], VEGETAL),
    "huge_inkcap_grove": ("huge_inkcap_tall", surface(rarity(2)), [mc("mushroom_fields")], VEGETAL),
    # Elsewhere, landmarks.
    "huge_bouncecap": ("huge_bouncecap", surface(rarity(5)), [mc("flower_forest")], VEGETAL),
    "huge_bouncecap_rare": ("huge_bouncecap", surface(rarity(24)), [mc("meadow")], VEGETAL),
    "huge_inkcap": ("huge_inkcap", surface(rarity(4)), [mc("dark_forest")], VEGETAL),
    "huge_inkcap_sparse": ("huge_inkcap", surface(rarity(8)), [mc("swamp")], VEGETAL),
    # Glowing groves underground.
    # Environment scans only succeed when the random start is in cave air, so these counts are attempts, not
    # results (vanilla does the same for glow lichen and cave vines). Lush caves need more: their own moss, clay
    # and vines take most of the floor and ceiling first.
    "cave_huge_glowcap": ("cave_huge_glowcap", cave_floor(4, above_bottom(8), absolute(40), 10), OVERWORLD, VEGETAL),
    "lush_huge_glowcap": ("cave_huge_glowcap", cave_floor(12, above_bottom(8), absolute(40), 10), [mc("lush_caves")], VEGETAL),
    "cave_glowcap_patch": ("patch_glowcap_cave", cave_floor(6, above_bottom(4), absolute(50)), OVERWORLD, VEGETAL),
    "lush_glowcap_patch": ("patch_glowcap_cave", cave_floor(14, above_bottom(4), absolute(50)), [mc("lush_caves")], VEGETAL),
    "mycelial_veils": ("mycelial_veil", [count(8), IN_SQUARE, height(above_bottom(8), absolute(60)), CEILING_SCAN,
                                         offset_y(-1), underground(10), BIOME], OVERWORLD, VEGETAL),
    "emberstool_cave": ("patch_emberstool", cave_floor(2, above_bottom(4), absolute(0)), OVERWORLD, VEGETAL),
    "emberstool_lava": ("patch_emberstool_lava", cave_floor(5, above_bottom(4), absolute(0)), OVERWORLD, VEGETAL),
    "emberstool_nether": ("patch_emberstool_nether", [rarity(2), {"type": "minecraft:count_on_every_layer", "count": 1}, BIOME],
                          [mc("crimson_forest"), mc("basalt_deltas")], VEGETAL),
    # Small fungi on the surface.
    "patch_glowcap": ("patch_glowcap", surface(rarity(3)), [mc("mushroom_fields"), mc("dark_forest")], VEGETAL),
    "patch_bouncecap": ("patch_bouncecap", surface(rarity(4)),
                        [mc("flower_forest"), mc("meadow"), *BIRCH, mc("cherry_grove"), mc("mushroom_fields")], VEGETAL),
    "patch_inkcap": ("patch_inkcap", surface(rarity(4)),
                     [mc("swamp"), mc("mangrove_swamp"), mc("dark_forest"), *OLD_GROWTH_TAIGA], VEGETAL),
    "patch_morel": ("patch_morel", surface(rarity(6)), [mc("forest"), *BIRCH, mc("flower_forest")], VEGETAL),
    "patch_chanterelle": ("patch_chanterelle", surface(rarity(5)), [mc("taiga"), *OLD_GROWTH_TAIGA, *BIRCH], VEGETAL),
    "patch_deathcap": ("patch_deathcap", surface(rarity(4)), [mc("dark_forest")], VEGETAL),
    "patch_frostcap": ("patch_frostcap", surface(rarity(5)),
                       [mc("snowy_taiga"), mc("snowy_plains"), mc("grove"), mc("snowy_slopes"), mc("ice_spikes")], VEGETAL),
    "patch_puffball": ("patch_puffball", surface(rarity(6)),
                       [mc("plains"), mc("sunflower_plains"), mc("meadow"), mc("savanna"), mc("savanna_plateau")], VEGETAL),
    "patch_giant_puffball": ("patch_giant_puffball", surface(rarity(28)),
                             [mc("plains"), mc("sunflower_plains"), mc("meadow"), mc("savanna")], VEGETAL),
    "shelf_fungus": ("shelf_fungus", surface(count(2)),
                     [mc("dark_forest"), *OLD_GROWTH_TAIGA, mc("old_growth_birch_forest"), mc("swamp"),
                      mc("mangrove_swamp"), mc("forest")], VEGETAL),
    "fairy_ring": ("fairy_ring", surface(rarity(48)),
                   [mc("plains"), mc("sunflower_plains"), mc("meadow"), mc("forest"), mc("flower_forest"), *BIRCH], VEGETAL),
    # Truffles in the dirt under forests.
    "ore_truffle_soil": ("ore_truffle_soil", [count(3), IN_SQUARE, heightmap("OCEAN_FLOOR_WG"), offset_y(uniform(-6, -2)), BIOME],
                         [mc("forest"), mc("flower_forest"), *BIRCH, mc("dark_forest"), mc("taiga"), *OLD_GROWTH_TAIGA], ORES),
}

# Overworld land: every vanilla overworld biome except the oceans, the Mushroom Fields (no monsters there, as in
# vanilla) and the Deep Dark.
OVERWORLD_LAND = [
    "#minecraft:is_forest", "#minecraft:is_taiga", "#minecraft:is_mountain", "#minecraft:is_hill",
    "#minecraft:is_savanna", "#minecraft:is_badlands", "#minecraft:is_jungle", "#minecraft:is_beach", "#minecraft:is_river",
    mc("plains"), mc("sunflower_plains"), mc("snowy_plains"), mc("ice_spikes"), mc("desert"), mc("swamp"),
    mc("mangrove_swamp"), mc("stony_shore"), mc("dripstone_caves"), mc("lush_caves"),
]

# name: (entity, category, weight, min, max, biomes). Weights from docs/DESIGN.md section 5. The *_rare entries put
# a few of the cave dwellers into every overworld land biome, so they turn up in caves anywhere.
SPAWNS: dict[str, tuple[str, str, int, int, int, list[str]]] = {
    "sporeling": ("sporeling", "creature", 10, 2, 4,
                  [mc("mushroom_fields"), mc("dark_forest"), mc("flower_forest"), mc("meadow"), mc("swamp"), mc("taiga"),
                   *OLD_GROWTH_TAIGA, mc("lush_caves")]),
    "truffler": ("truffler", "creature", 6, 1, 3,
                 [mc("dark_forest"), *OLD_GROWTH_TAIGA, mc("forest"), mc("mushroom_fields")]),
    "glowmoth": ("glowmoth", "ambient", 8, 1, 3, OVERWORLD),
    "bloatshroom": ("bloatshroom", "monster", 25, 1, 2, LAND),
    "shambler": ("shambler", "monster", 20, 1, 3,
                 [mc("dark_forest"), mc("swamp"), mc("mangrove_swamp"), mc("lush_caves"), mc("dripstone_caves")]),
    "shambler_rare": ("shambler", "monster", 5, 1, 2, LAND),
    "sporemaw": ("sporemaw", "monster", 10, 1, 1, [mc("dark_forest"), mc("swamp"), mc("lush_caves")]),
    "sporemaw_rare": ("sporemaw", "monster", 3, 1, 1, LAND),
    "mimicap": ("mimicap", "monster", 8, 1, 1,
                [mc("forest"), mc("dark_forest"), *BIRCH, mc("taiga"), *OLD_GROWTH_TAIGA]),
    "mimicap_rare": ("mimicap", "monster", 2, 1, 1, LAND),
}


def generate(out: Out) -> None:
    for name, feature in CONFIGURED.items():
        out.data_json(f"worldgen/configured_feature/{name}.json", feature)

    out.tag("worldgen/biome", "overworld_land", OVERWORLD_LAND)

    manifest = {"features": [], "spawns": []}
    for name, (configured, placement, biomes, step) in PLACED.items():
        if configured not in CONFIGURED:
            raise ValueError(f"placed feature {name} uses unknown configured feature {configured}")
        out.data_json(f"worldgen/placed_feature/{name}.json", {"feature": ns(configured), "placement": placement})
        tag = f"has_feature/{name}"
        out.tag("worldgen/biome", tag, biomes)
        out.data_json(f"neoforge/biome_modifier/add_{name}.json", {
            "type": "neoforge:add_features", "biomes": f"#{ns(tag)}", "features": ns(name), "step": step})
        manifest["features"].append({"feature": ns(name), "biomes": ns(tag), "step": step})

    for name, (entity, category, weight, lo, hi, biomes) in SPAWNS.items():
        tag = f"spawns/{name}"
        out.tag("worldgen/biome", tag, biomes)
        out.data_json(f"neoforge/biome_modifier/spawn_{name}.json", {
            "type": "neoforge:add_spawns", "biomes": f"#{ns(tag)}",
            "spawners": {"type": ns(entity), "weight": weight, "minCount": lo, "maxCount": hi}})
        manifest["spawns"].append({"entity": ns(entity), "biomes": ns(tag), "category": category,
                                   "weight": weight, "min": lo, "max": hi})

    # Read by FabricWorldgen from the mod jar (not a datapack path, so vanilla and NeoForge ignore it).
    out.json(out.root / MOD_ID / "biome_modifications.json", manifest)
