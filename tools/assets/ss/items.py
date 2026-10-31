"""Item textures, item models and item language entries."""
from __future__ import annotations

from . import art_items, art_wood
from .blocks import item_parent
from .data_content import (FOODS, FUNGI, GEAR, HIDDEN_ITEMS, MATERIALS, OTHER_BLOCKS, SPAWN_EGGS, WOOD_BLOCKS, WOODS,
                           wood_id)
from .out import Out
from .paths import MOD_ID

HANDHELD = {"foraging_knife", "bloomreaver", "ember_skewer"}
# Block items drawn flat (like vanilla doors, vines and lanterns): block id -> texture
FLAT_BLOCK_ITEMS = {"glowcap_gills": "block/glowcap_gills_tip", "shelf_fungus": "item/shelf_fungus",
                    "mycelial_veil": "item/mycelial_veil", "glowcap_lantern": "item/glowcap_lantern"}

DESCRIPTIONS = {
    "fruiting_heart": "Use on Mycelium, Mycelial Soil, Podzol or Moss to call up the Myceliarch",
    "mycoleather_armor": "Full set: Spore Ward",
    "crown_of_the_bloom": "Night Vision and Spore Ward while worn",
    "bloomreaver": "Hits infect. Use: Spore Burst",
}


def generated(texture: str, handheld: bool = False) -> dict:
    return {"parent": "minecraft:item/handheld" if handheld else "minecraft:item/generated",
            "textures": {"layer0": f"{MOD_ID}:{texture}"}}


def generate(out: Out) -> None:
    sprites = art_items.all_items()
    for name, sprite in sprites.items():
        if name in FLAT_BLOCK_ITEMS and not FLAT_BLOCK_ITEMS[name].startswith("item/"):
            continue
        out.texture(f"item/{name}", sprite.image())

    # Small fungi: flat icons for the hand and inventory, 3D when placed.
    for name, _ in FUNGI:
        out.item_model(name, generated(f"item/{name}"))

    for group in (MATERIALS, FOODS, GEAR, HIDDEN_ITEMS):
        for name, label in group:
            out.item_model(name, generated(f"item/{name}", name in HANDHELD))
            out.tr(f"item.{MOD_ID}.{name}", label)

    for w in WOODS:
        out.texture(f"item/{w}_door", art_wood.door_item(w).image())
        for suffix, _ in WOOD_BLOCKS:
            bid = wood_id(w, suffix)
            if suffix == "door":
                out.item_model(bid, generated(f"item/{w}_door"))
            else:
                out.item_model(bid, {"parent": item_parent(bid)})

    for bid, _ in OTHER_BLOCKS:
        if bid == "mycelial_veil_plant":
            continue
        if bid in FLAT_BLOCK_ITEMS:
            out.item_model(bid, generated(FLAT_BLOCK_ITEMS[bid]))
        else:
            out.item_model(bid, {"parent": item_parent(bid)})

    for mob, label in SPAWN_EGGS:
        out.item_model(f"{mob}_spawn_egg", {"parent": "minecraft:item/template_spawn_egg"})
        out.tr(f"item.{MOD_ID}.{mob}_spawn_egg", f"{label} Spawn Egg")

    for key, text in DESCRIPTIONS.items():
        out.tr(f"item.{MOD_ID}.{key}.desc", text)
