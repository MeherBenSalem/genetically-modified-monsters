"""Entity data shared by every creature: the fungal and Mycosis-riser tags, and the projectile names."""
from __future__ import annotations

from ..out import Out

# Fungal creatures shrug off Mycosis and spore clouds (docs/DESIGN.md §4).
FUNGAL = ["sporeling", "bloatshroom", "shambler", "sporemaw", "mimicap", "glowmoth", "truffler", "myceliarch"]
# Those that rise as Shamblers when they die infected (docs/DESIGN.md §3).
RISERS = ["minecraft:zombie", "minecraft:husk", "minecraft:drowned", "minecraft:villager", "minecraft:pillager",
          "minecraft:vindicator", "minecraft:witch", "minecraft:player"]


def data(out: Out) -> None:
    out.tag("entity_type", "fungal", [f"spore_and_stem:{e}" for e in FUNGAL])
    out.tag("entity_type", "mycosis_risers", RISERS)
    out.tr("entity.spore_and_stem.spore_glob", "Spore Glob")
    out.tr("entity.spore_and_stem.spore_bomb", "Spore Bomb")
