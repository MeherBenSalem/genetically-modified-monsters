"""The GameTest arena: data/spore_and_stem/structure/arena.nbt, 13×18×13 of air on a stone floor."""
from __future__ import annotations

import gzip
import struct

from .out import Out

SIZE = (13, 18, 13)


def _nbt(tag_type: int, name: str | None, value) -> bytes:
    def payload(t, v):
        if t == 3:
            return struct.pack(">i", v)
        if t == 8:
            raw = v.encode("utf-8")
            return struct.pack(">H", len(raw)) + raw
        if t == 9:
            elem_type, items = v
            return struct.pack(">bi", elem_type if items else 0, len(items)) + b"".join(payload(elem_type, i) for i in items)
        if t == 10:
            return b"".join(_nbt(ct, cn, cv) for cn, (ct, cv) in v.items()) + b"\x00"
        raise ValueError(t)

    head = struct.pack(">b", tag_type)
    if name is not None:
        raw = name.encode("utf-8")
        head += struct.pack(">H", len(raw)) + raw
    return head + payload(tag_type, value)


def generate(out: Out) -> None:
    sx, sy, sz = SIZE
    blocks = [{"pos": (9, (3, [x, 0, z])), "state": (3, 1)} for x in range(sx) for z in range(sz)]
    root = {
        "DataVersion": (3, 3955),
        "size": (9, (3, [sx, sy, sz])),
        "palette": (9, (10, [{"Name": (8, "minecraft:air")}, {"Name": (8, "minecraft:stone")}])),
        "blocks": (9, (10, blocks)),
        "entities": (9, (10, [])),
    }
    out.bytes(out.data_path("structure/arena.nbt"), gzip.compress(_nbt(10, "", root), mtime=0))
