"""Ids and English names of every block and item (mirrors registry/ModBlocks.java and ModItems.java)."""
from __future__ import annotations

WOODS = ["glowcap", "bouncecap", "inkcap"]
WOOD_NAMES = {"glowcap": "Glowcap", "bouncecap": "Bouncecap", "inkcap": "Inkcap"}

# Small fungi, in creative-tab order. (id, name, huge-growing)
FUNGI = [
    ("glowcap", "Glowcap"),
    ("bouncecap", "Bouncecap"),
    ("inkcap", "Inkcap"),
    ("morel", "Morel"),
    ("chanterelle", "Chanterelle"),
    ("deathcap", "Deathcap"),
    ("frostcap", "Frostcap"),
    ("emberstool", "Emberstool"),
    ("puffball", "Puffball"),
]
FUNGUS_IDS = [f for f, _ in FUNGI]
EDIBLE_FUNGI = ["glowcap", "bouncecap", "morel", "chanterelle", "deathcap", "frostcap", "emberstool", "puffball"]

# Cultivation Log fungi (content/CultivationFungus.java, without NONE).
CULTIVATION = ["glowcap", "bouncecap", "inkcap", "morel", "chanterelle", "frostcap", "emberstool"]

# Suffix -> English for the wood sets (id is f"{wood}_{suffix}" except the stripped ones).
WOOD_BLOCKS = [
    ("cap", "Cap"),
    ("stem", "Stem"),
    ("stripped_stem", "Stripped {} Stem"),
    ("hyphae", "Hyphae"),
    ("stripped_hyphae", "Stripped {} Hyphae"),
    ("planks", "Planks"),
    ("stairs", "Stairs"),
    ("slab", "Slab"),
    ("fence", "Fence"),
    ("fence_gate", "Fence Gate"),
    ("door", "Door"),
    ("trapdoor", "Trapdoor"),
    ("button", "Button"),
    ("pressure_plate", "Pressure Plate"),
]


def wood_id(wood: str, suffix: str) -> str:
    if suffix.startswith("stripped_"):
        return f"stripped_{wood}_{suffix[len('stripped_'):]}"
    return f"{wood}_{suffix}"


def wood_name(wood: str, suffix: str, label: str) -> str:
    w = WOOD_NAMES[wood]
    return label.format(w) if "{}" in label else f"{w} {label}"


OTHER_BLOCKS = [
    ("glowcap_gills", "Glowcap Gills"),
    ("shelf_fungus", "Shelf Fungus"),
    ("mycelial_veil", "Mycelial Veil"),
    ("mycelial_veil_plant", "Mycelial Veil Plant"),
    ("giant_puffball", "Giant Puffball"),
    ("truffle_soil", "Truffle Soil"),
    ("mycelial_soil", "Mycelial Soil"),
    ("glowcap_lantern", "Glowcap Lantern"),
    ("cultivation_log", "Cultivation Log"),
]

MATERIALS = [
    ("lumen_spores", "Lumen Spores"),
    ("mycelial_thread", "Mycelial Thread"),
    ("mycoleather", "Mycoleather"),
    ("bouncecap_gel", "Bouncecap Gel"),
    ("mycelial_core", "Mycelial Core"),
    ("truffle", "Truffle"),
    ("fruiting_heart", "Fruiting Heart"),
    ("spore_heart", "Spore Heart"),
]

FOODS = [
    ("roasted_morel", "Roasted Morel"),
    ("chanterelle_toast", "Chanterelle Toast"),
    ("glowcap_soup", "Glowcap Soup"),
    ("bouncecap_jelly", "Bouncecap Jelly"),
    ("frostcap_tea", "Frostcap Tea"),
    ("ember_skewer", "Ember Skewer"),
    ("truffle_stew", "Truffle Stew"),
    ("foragers_stew", "Forager's Stew"),
    ("antifungal_tonic", "Antifungal Tonic"),
]

GEAR = [
    ("foraging_knife", "Foraging Knife"),
    ("spore_bomb", "Spore Bomb"),
    ("mycoleather_hood", "Mycoleather Hood"),
    ("mycoleather_tunic", "Mycoleather Tunic"),
    ("mycoleather_leggings", "Mycoleather Leggings"),
    ("mycoleather_boots", "Mycoleather Boots"),
    ("bloomreaver", "Bloomreaver"),
    ("crown_of_the_bloom", "Crown of the Bloom"),
]

SPAWN_EGGS = [
    ("sporeling", "Sporeling"),
    ("truffler", "Truffler"),
    ("glowmoth", "Glowmoth"),
    ("bloatshroom", "Bloatshroom"),
    ("shambler", "Shambler"),
    ("sporemaw", "Sporemaw"),
    ("mimicap", "Mimicap"),
    ("myceliarch", "Myceliarch"),
]

HIDDEN_ITEMS = [("spore_glob", "Spore Glob")]
