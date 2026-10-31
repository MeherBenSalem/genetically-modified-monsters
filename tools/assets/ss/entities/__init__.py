"""Creatures: geometry, animations, textures, loot and language, one module per creature.

Each creature module (listed in CREATURES) provides:
  NAME = "sporeling"            # entity id
  CLASS = "Sporeling"           # Java prefix: client/entity/geo/<CLASS>Geometry, client/entity/anim/<CLASS>Animations
  def rig() -> Rig              # bones and cubes (UVs are packed automatically unless a cube fixes its own)
  def anims() -> list[Anim]     # named animations; the Java constant is the upper-cased name
  def textures(rig) -> dict[str, Image]   # "sporeling_glowcap" -> textures/entity/<NAME>/sporeling_glowcap.png
  def data(out) -> None         # language, loot table, tags

generate() writes the textures and data through Out, and the Java geometry/animation classes into the common source
tree of every workspace (the reference and each port in ss/ports; the generated Java uses no version-specific API),
only when their content changed, so Gradle stays incremental.
"""
from __future__ import annotations

import importlib

from ..out import Out
from ..paths import REFERENCE_WORKSPACE, java
from ..ports import PORTS
from .anim import java_animations

PACKAGE = "com.nightbeam.sporeandstem.client.entity"
# Module names under ss/entities, in creative-tab order. Add a creature by adding its module here.
CREATURES: list[str] = [
    "sporeling",
    "bloatshroom",
    "shambler",
    "sporemaw",
    "mimicap",
    "glowmoth",
    "truffler",
    "myceliarch",
    "root_spike",
]


def load(name: str):
    return importlib.import_module(f"{__name__}.{name}")


def write_java(rel: str, text: str) -> None:
    for ws in [REFERENCE_WORKSPACE, *(port.WORKSPACE for port in PORTS)]:
        path = java(ws) / "client" / "entity" / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")


def build(module) -> tuple:
    rig = module.rig()
    rig.pack()
    return rig, module.anims()


def generate(out: Out) -> None:
    from .shared import data as shared_data
    shared_data(out)
    for name in CREATURES:
        module = load(name)
        rig, anims = build(module)
        write_java(f"geo/{module.CLASS}Geometry.java", rig.java_geometry(f"{PACKAGE}.geo", f"{module.CLASS}Geometry"))
        write_java(f"anim/{module.CLASS}Animations.java",
                   java_animations(f"{PACKAGE}.anim", f"{module.CLASS}Animations", module.NAME, anims))
        for tex_name, image in module.textures(rig).items():
            out.texture(f"entity/{module.NAME}/{tex_name}", image)
        module.data(out)
