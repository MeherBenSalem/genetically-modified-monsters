"""Creature rigs: one Python source per creature for its geometry, UV layout, texture and animations.

Coordinates follow Minecraft model space exactly (the Java code is generated from them):
- units are pixels (16 = one block), **+y points down**, the creature faces **-z** (its front is the north face),
  its right side is -x.
- the generated model has a "root" part at offset (0, 24, 0): y = 0 under root is the ground, so anything standing
  on the ground has negative y.
- a Bone's ``pivot`` is relative to its parent's pivot; a Cube's ``origin`` is relative to its bone's pivot.
- rotations are in degrees and compose like ModelPart (Z·Y·X, X applied first).

Box UV regions (texOffs u, v; size w, h, d), each as seen from outside the box:
  top (u+d, v, w×d)  bottom (u+d+w, v, w×d)  right (u, v+d, d×h)  front (u+d, v+d, w×h)
  left (u+d+w, v+d, d×h)  back (u+2d+w, v+d, w×h)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import radians

FACES = ("top", "bottom", "right", "front", "left", "back")


@dataclass
class Cube:
    name: str
    origin: tuple[float, float, float]
    size: tuple[int, int, int]
    mat: str = "base"
    inflate: float = 0.0
    mirror: bool = False
    uv: tuple[int, int] | None = None   # assigned by Rig.pack() unless fixed here
    data: dict = field(default_factory=dict)  # free-form hints for painters (e.g. {"face": "eyes"})

    @property
    def footprint(self) -> tuple[int, int]:
        w, h, d = self.size
        return 2 * (d + w), d + h

    def regions(self) -> dict[str, tuple[int, int, int, int]]:
        """Face -> (x0, y0, width, height) in the texture."""
        u, v = self.uv
        w, h, d = self.size
        return {
            "top": (u + d, v, w, d),
            "bottom": (u + d + w, v, w, d),
            "right": (u, v + d, d, h),
            "front": (u + d, v + d, w, h),
            "left": (u + d + w, v + d, d, h),
            "back": (u + 2 * d + w, v + d, w, h),
        }


@dataclass
class Bone:
    name: str
    pivot: tuple[float, float, float] = (0.0, 0.0, 0.0)
    rot: tuple[float, float, float] = (0.0, 0.0, 0.0)
    cubes: list[Cube] = field(default_factory=list)
    children: list["Bone"] = field(default_factory=list)

    def box(self, name: str, origin, size, mat: str = "base", inflate: float = 0.0, mirror: bool = False,
            uv=None, **data) -> "Bone":
        self.cubes.append(Cube(name, tuple(map(float, origin)), tuple(map(int, size)), mat, inflate, mirror,
                               tuple(uv) if uv else None, dict(data)))
        return self

    def child(self, name: str, pivot=(0, 0, 0), rot=(0, 0, 0)) -> "Bone":
        bone = Bone(name, tuple(map(float, pivot)), tuple(map(float, rot)))
        self.children.append(bone)
        return bone

    def walk(self, parent: "Bone | None" = None):
        yield self, parent
        for c in self.children:
            yield from c.walk(self)


class Rig:
    def __init__(self, name: str, tex: tuple[int, int] = (64, 64)):
        self.name = name
        self.tex = tex
        self.root = Bone("root", (0.0, 24.0, 0.0))

    def bones(self):
        return [b for b, _ in self.root.walk()]

    def bone(self, name: str) -> Bone:
        for b in self.bones():
            if b.name == name:
                return b
        raise KeyError(name)

    def cubes(self):
        for b in self.bones():
            for c in b.cubes:
                yield b, c

    def validate(self) -> None:
        names = [b.name for b in self.bones()]
        dupes = {n for n in names if names.count(n) > 1}
        if dupes:
            raise ValueError(f"{self.name}: duplicate bone names {sorted(dupes)}")

    def pack(self, padding: int = 0) -> None:
        """Shelf-packs every cube without a fixed uv into the texture, tallest first. Raises when it doesn't fit."""
        self.validate()
        tw, th = self.tex
        used: list[tuple[int, int, int, int]] = []
        for _, c in self.cubes():
            if c.uv is not None:
                fw, fh = c.footprint
                used.append((c.uv[0], c.uv[1], fw, fh))
        free = [c for _, c in self.cubes() if c.uv is None]
        free.sort(key=lambda c: (-c.footprint[1], -c.footprint[0]))

        def clash(x, y, w, h):
            return any(x < ux + uw + padding and ux < x + w + padding and y < uy + uh + padding and uy < y + h + padding
                       for ux, uy, uw, uh in used)

        for c in free:
            fw, fh = c.footprint
            placed = False
            for y in range(0, th - fh + 1):
                for x in range(0, tw - fw + 1):
                    if not clash(x, y, fw, fh):
                        c.uv = (x, y)
                        used.append((x, y, fw, fh))
                        placed = True
                        break
                if placed:
                    break
            if not placed:
                raise ValueError(f"{self.name}: cube {c.name} ({fw}x{fh}) does not fit in {tw}x{th}")

    # ---- Java ------------------------------------------------------------------------------------------------
    def java_geometry(self, package: str, class_name: str) -> str:
        self.validate()
        lines = [
            "// GENERATED by tools/assets/ss/entities from the creature's rig. Do not edit; run tools/assets/build.py.",
            f"package {package};",
            "",
            "import net.minecraft.client.model.geom.PartPose;",
            "import net.minecraft.client.model.geom.builders.CubeDeformation;",
            "import net.minecraft.client.model.geom.builders.CubeListBuilder;",
            "import net.minecraft.client.model.geom.builders.LayerDefinition;",
            "import net.minecraft.client.model.geom.builders.MeshDefinition;",
            "import net.minecraft.client.model.geom.builders.PartDefinition;",
            "",
            f"/** Geometry of the {self.name.replace('_', ' ')}: bones, cubes and UVs. */",
            f"public final class {class_name} {{",
            f"    public static final int TEXTURE_WIDTH = {self.tex[0]};",
            f"    public static final int TEXTURE_HEIGHT = {self.tex[1]};",
            "",
            f"    private {class_name}() {{",
            "    }",
            "",
            "    public static LayerDefinition createBodyLayer() {",
            "        MeshDefinition mesh = new MeshDefinition();",
            "        PartDefinition parts = mesh.getRoot();",
        ]
        var = {}

        def f(x: float) -> str:
            s = f"{x:.4f}".rstrip("0")
            s = s + "0" if s.endswith(".") else s
            return ("0.0" if s == "-0.0" else s) + "F"

        def emit(bone: Bone, parent_var: str):
            v = "p_" + bone.name
            var[bone.name] = v
            builder = "CubeListBuilder.create()"
            for c in bone.cubes:
                if c.uv is None:
                    raise ValueError(f"{self.name}: cube {c.name} has no uv (call pack())")
                builder += f"\n                .texOffs({c.uv[0]}, {c.uv[1]})"
                if c.mirror:
                    builder += ".mirror()"
                ox, oy, oz = c.origin
                w, h, d = c.size
                builder += (f".addBox({f(ox)}, {f(oy)}, {f(oz)}, {f(w)}, {f(h)}, {f(d)}, "
                            f"new CubeDeformation({f(c.inflate)}))")
                if c.mirror:
                    builder += ".mirror(false)"
            px, py, pz = bone.pivot
            rx, ry, rz = (radians(a) for a in bone.rot)
            pose = (f"PartPose.offsetAndRotation({f(px)}, {f(py)}, {f(pz)}, {f(rx)}, {f(ry)}, {f(rz)})"
                    if any(bone.rot) else f"PartPose.offset({f(px)}, {f(py)}, {f(pz)})")
            lines.append(f"        PartDefinition {v} = {parent_var}.addOrReplaceChild(\"{bone.name}\", {builder},")
            lines.append(f"                {pose});")
            for c in bone.children:
                emit(c, v)

        emit(self.root, "parts")
        lines += [
            f"        return LayerDefinition.create(mesh, TEXTURE_WIDTH, TEXTURE_HEIGHT);",
            "    }",
            "}",
            "",
        ]
        return "\n".join(lines)
