"""Block textures, block models, blockstates and block language entries."""
from __future__ import annotations

from . import art_fungi, art_models, art_other, art_wood
from .data_content import FUNGI, OTHER_BLOCKS, WOOD_BLOCKS, WOOD_NAMES, WOODS, wood_id, wood_name
from .out import Out
from .paths import MOD_ID

ROT = (0, 90, 180, 270)


def m(name: str) -> str:
    return f"{MOD_ID}:block/{name}"


def variant(model: str, x: int = 0, y: int = 0, uvlock: bool = False) -> dict:
    v = {"model": model}
    if x:
        v["x"] = x
    if y:
        v["y"] = y
    if uvlock:
        v["uvlock"] = True
    return v


def generate(out: Out) -> None:
    fungi(out)
    for wood in WOODS:
        wood_set(out, wood)
    art_other.generate(out)


# ---------------------------------------------------------------------------------------------------- fungi

def fungi(out: Out) -> None:
    materials = art_fungi.all_materials()
    for name, label in FUNGI:
        for key, sprite in materials[name].items():
            if key in art_models.FUNGUS_TEXTURES[name]:
                out.texture(f"block/fungus/{name}_{key}", sprite.image())
        out.block_model(name, art_models.fungus_model(name))
        out.blockstate(name, {"variants": {"": [variant(m(name), y=r) for r in ROT]}})
        out.block_model(f"potted_{name}", art_models.potted_model(name))
        out.blockstate(f"potted_{name}", {"variants": {"": variant(m(f"potted_{name}"))}})
        out.tr(f"block.{MOD_ID}.{name}", label)
        out.tr(f"block.{MOD_ID}.potted_{name}", f"Potted {label}")


# ---------------------------------------------------------------------------------------------------- wood sets

FACING_Y = {"east": 0, "south": 90, "west": 180, "north": 270}       # stairs and doors
GATE_Y = {"south": 0, "west": 90, "north": 180, "east": 270}
TRAP_Y = {"north": 0, "east": 90, "south": 180, "west": 270}
BUTTON_Y = {"north": 0, "east": 90, "south": 180, "west": 270}
BUTTON_CEILING_Y = {"north": 180, "east": 270, "south": 0, "west": 90}


def wood_set(out: Out, w: str) -> None:
    # Textures
    out.texture(f"block/{w}_planks", art_wood.planks(w).image())
    out.texture(f"block/{w}_stem", art_wood.stem_side(w).image())
    out.texture(f"block/{w}_stem_top", art_wood.stem_top(w).image())
    out.texture(f"block/stripped_{w}_stem", art_wood.stem_side(w, True).image())
    out.texture(f"block/stripped_{w}_stem_top", art_wood.stem_top(w, True).image())
    out.texture(f"block/{w}_cap", art_wood.cap_outside(w).image())
    out.texture(f"block/{w}_cap_inside", art_wood.cap_inside(w).image())
    top, bottom = art_wood.door(w)
    out.texture(f"block/{w}_door_top", top.image())
    out.texture(f"block/{w}_door_bottom", bottom.image())
    out.texture(f"block/{w}_trapdoor", art_wood.trapdoor(w).image())
    planks = m(f"{w}_planks")

    # Cap: six faces, each either skin or gills (like vanilla huge mushroom blocks).
    for model, tex in ((f"{w}_cap", f"{w}_cap"), (f"{w}_cap_inside", f"{w}_cap_inside")):
        if w == "glowcap":
            # Glowcap caps glow: the same single face as vanilla's template, full-bright on NeoForge.
            out.block_model(model, {"parent": "minecraft:block/block", "textures": {"texture": m(tex), "particle": m(tex)},
                                    "elements": [{"from": [0, 0, 0], "to": [16, 16, 0],
                                                  "neoforge_data": dict(art_models.FULL_BRIGHT),
                                                  "faces": {"north": {"texture": "#texture", "cullface": "north"}}}]})
        else:
            out.block_model(model, {"parent": "minecraft:block/template_single_face", "textures": {"texture": m(tex)}})
    out.block_model(f"{w}_cap_inventory", {"parent": "minecraft:block/cube_all", "textures": {"all": m(f"{w}_cap")}})
    parts = []
    for face, rot in (("north", {}), ("east", {"y": 90}), ("south", {"y": 180}), ("west", {"y": 270}),
                      ("up", {"x": 270}), ("down", {"x": 90})):
        for state, model in (("true", f"{w}_cap"), ("false", f"{w}_cap_inside")):
            apply = {"model": m(model)}
            if rot:
                apply.update(rot)
                apply["uvlock"] = True
            parts.append({"when": {face: state}, "apply": apply})
    out.blockstate(f"{w}_cap", {"multipart": parts})

    # Stems and hyphae.
    for name, side, end in ((f"{w}_stem", f"{w}_stem", f"{w}_stem_top"),
                            (f"stripped_{w}_stem", f"stripped_{w}_stem", f"stripped_{w}_stem_top"),
                            (f"{w}_hyphae", f"{w}_stem", f"{w}_stem"),
                            (f"stripped_{w}_hyphae", f"stripped_{w}_stem", f"stripped_{w}_stem")):
        out.block_model(name, {"parent": "minecraft:block/cube_column", "textures": {"end": m(end), "side": m(side)}})
        out.blockstate(name, {"variants": {"axis=x": variant(m(name), x=90, y=90), "axis=y": variant(m(name)),
                                           "axis=z": variant(m(name), x=90)}})

    out.block_model(f"{w}_planks", {"parent": "minecraft:block/cube_all", "textures": {"all": planks}})
    out.blockstate(f"{w}_planks", {"variants": {"": variant(m(f"{w}_planks"))}})

    # Stairs
    tex3 = {"bottom": planks, "top": planks, "side": planks}
    out.block_model(f"{w}_stairs", {"parent": "minecraft:block/stairs", "textures": tex3})
    out.block_model(f"{w}_stairs_inner", {"parent": "minecraft:block/inner_stairs", "textures": tex3})
    out.block_model(f"{w}_stairs_outer", {"parent": "minecraft:block/outer_stairs", "textures": tex3})
    variants = {}
    for facing, base in FACING_Y.items():
        for half in ("bottom", "top"):
            for shape in ("straight", "inner_left", "inner_right", "outer_left", "outer_right"):
                model = {"straight": f"{w}_stairs"}.get(shape, f"{w}_stairs_inner" if shape.startswith("inner")
                                                        else f"{w}_stairs_outer")
                y = base
                if half == "bottom" and shape in ("inner_left", "outer_left"):
                    y -= 90
                if half == "top" and shape in ("inner_right", "outer_right"):
                    y += 90
                x = 180 if half == "top" else 0
                y %= 360
                variants[f"facing={facing},half={half},shape={shape}"] = variant(m(model), x=x, y=y, uvlock=bool(x or y))
    out.blockstate(f"{w}_stairs", {"variants": variants})

    # Slab
    out.block_model(f"{w}_slab", {"parent": "minecraft:block/slab", "textures": tex3})
    out.block_model(f"{w}_slab_top", {"parent": "minecraft:block/slab_top", "textures": tex3})
    out.blockstate(f"{w}_slab", {"variants": {"type=bottom": variant(m(f"{w}_slab")),
                                              "type=double": variant(planks),
                                              "type=top": variant(m(f"{w}_slab_top"))}})

    # Fence
    for suffix, parent in (("fence_post", "fence_post"), ("fence_side", "fence_side"), ("fence_inventory", "fence_inventory")):
        out.block_model(f"{w}_{suffix}", {"parent": f"minecraft:block/{parent}", "textures": {"texture": planks}})
    fence = [{"apply": {"model": m(f"{w}_fence_post")}}]
    for face, y in (("north", 0), ("east", 90), ("south", 180), ("west", 270)):
        apply = {"model": m(f"{w}_fence_side"), "uvlock": True}
        if y:
            apply["y"] = y
        fence.append({"when": {face: "true"}, "apply": apply})
    out.blockstate(f"{w}_fence", {"multipart": fence})

    # Fence gate
    for suffix, parent in (("fence_gate", "template_fence_gate"), ("fence_gate_open", "template_fence_gate_open"),
                           ("fence_gate_wall", "template_fence_gate_wall"),
                           ("fence_gate_wall_open", "template_fence_gate_wall_open")):
        out.block_model(f"{w}_{suffix}", {"parent": f"minecraft:block/{parent}", "textures": {"texture": planks}})
    variants = {}
    for facing, y in GATE_Y.items():
        for in_wall in ("false", "true"):
            for open_ in ("false", "true"):
                model = f"{w}_fence_gate" + ("_wall" if in_wall == "true" else "") + ("_open" if open_ == "true" else "")
                variants[f"facing={facing},in_wall={in_wall},open={open_}"] = variant(m(model), y=y, uvlock=True)
    out.blockstate(f"{w}_fence_gate", {"variants": variants})

    # Door
    for part in ("bottom_left", "bottom_left_open", "bottom_right", "bottom_right_open", "top_left", "top_left_open",
                 "top_right", "top_right_open"):
        out.block_model(f"{w}_door_{part}", {"parent": f"minecraft:block/door_{part}", "render_type": "minecraft:cutout",
                                             "textures": {"bottom": m(f"{w}_door_bottom"), "top": m(f"{w}_door_top")}})
    variants = {}
    for facing, base in FACING_Y.items():
        for half in ("lower", "upper"):
            for hinge in ("left", "right"):
                for open_ in ("false", "true"):
                    part = ("bottom" if half == "lower" else "top") + f"_{hinge}" + ("_open" if open_ == "true" else "")
                    y = base
                    if open_ == "true":
                        y += 90 if hinge == "left" else 270
                    variants[f"facing={facing},half={half},hinge={hinge},open={open_}"] = variant(m(f"{w}_door_{part}"), y=y % 360)
    out.blockstate(f"{w}_door", {"variants": variants})

    # Trapdoor
    for part in ("bottom", "top", "open"):
        out.block_model(f"{w}_trapdoor_{part}", {"parent": f"minecraft:block/template_trapdoor_{part}",
                                                 "render_type": "minecraft:cutout",
                                                 "textures": {"texture": m(f"{w}_trapdoor")}})
    variants = {}
    for facing, y in TRAP_Y.items():
        for half in ("bottom", "top"):
            for open_ in ("false", "true"):
                if open_ == "true":
                    variants[f"facing={facing},half={half},open=true"] = variant(m(f"{w}_trapdoor_open"), y=y)
                else:
                    variants[f"facing={facing},half={half},open=false"] = variant(m(f"{w}_trapdoor_{half}"))
    out.blockstate(f"{w}_trapdoor", {"variants": variants})

    # Button
    for suffix, parent in (("button", "button"), ("button_pressed", "button_pressed"), ("button_inventory", "button_inventory")):
        out.block_model(f"{w}_{suffix}", {"parent": f"minecraft:block/{parent}", "textures": {"texture": planks}})
    variants = {}
    for face in ("floor", "wall", "ceiling"):
        for facing in ("north", "east", "south", "west"):
            for powered in ("false", "true"):
                model = f"{w}_button_pressed" if powered == "true" else f"{w}_button"
                x = {"floor": 0, "wall": 90, "ceiling": 180}[face]
                y = BUTTON_CEILING_Y[facing] if face == "ceiling" else BUTTON_Y[facing]
                variants[f"face={face},facing={facing},powered={powered}"] = variant(m(model), x=x, y=y, uvlock=face == "wall")
    out.blockstate(f"{w}_button", {"variants": variants})

    # Pressure plate
    out.block_model(f"{w}_pressure_plate", {"parent": "minecraft:block/pressure_plate_up", "textures": {"texture": planks}})
    out.block_model(f"{w}_pressure_plate_down", {"parent": "minecraft:block/pressure_plate_down", "textures": {"texture": planks}})
    out.blockstate(f"{w}_pressure_plate", {"variants": {"powered=false": variant(m(f"{w}_pressure_plate")),
                                                        "powered=true": variant(m(f"{w}_pressure_plate_down"))}})

    for suffix, label in WOOD_BLOCKS:
        out.tr(f"block.{MOD_ID}.{wood_id(w, suffix)}", wood_name(w, suffix, label))


def item_parent(block_id: str) -> str:
    """The block model a block item should use (for items.py)."""
    for w in WOODS:
        if block_id == f"{w}_fence":
            return m(f"{w}_fence_inventory")
        if block_id == f"{w}_button":
            return m(f"{w}_button_inventory")
        if block_id == f"{w}_trapdoor":
            return m(f"{w}_trapdoor_bottom")
        if block_id == f"{w}_cap":
            return m(f"{w}_cap_inventory")
    return art_other.ITEM_PARENTS.get(block_id, m(block_id))


__all__ = ["generate", "item_parent", "OTHER_BLOCKS", "WOOD_NAMES"]
