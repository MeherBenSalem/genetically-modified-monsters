"""Collects every generated file. Modules write through one Out so that shared files (language, tags, sounds.json,
data maps) are merged across modules and written once at the end, in a stable order."""
from __future__ import annotations

import json
import shutil
from collections import defaultdict
from pathlib import Path

from PIL import Image

from .paths import GENERATED, MOD_ID


def rid(path: str, ns: str = MOD_ID) -> str:
    """'glowcap' -> 'spore_and_stem:glowcap'; ids that already carry a namespace are kept."""
    return path if ":" in path else f"{ns}:{path}"


class Out:
    def __init__(self, root: Path = GENERATED):
        self.root = root
        self.written: set[Path] = set()
        self.lang: dict[str, str] = {}
        # (registry folder, namespace, name) -> {"replace": bool, "values": [..]}
        self.tags: dict[tuple[str, str, str], dict] = {}
        self.sounds: dict[str, dict] = {}
        self.data_maps: dict[tuple[str, str], dict] = defaultdict(dict)  # (ns:path) -> values

    # ---- paths --------------------------------------------------------------------------------------------------
    def asset_path(self, rel: str, ns: str = MOD_ID) -> Path:
        return self.root / "assets" / ns / rel

    def data_path(self, rel: str, ns: str = MOD_ID) -> Path:
        return self.root / "data" / ns / rel

    # ---- writers ------------------------------------------------------------------------------------------------
    def _track(self, path: Path) -> Path:
        if path in self.written:
            raise ValueError(f"{path} written twice")
        self.written.add(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    def json(self, path: Path, obj) -> None:
        self._track(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def png(self, path: Path, img: Image.Image) -> None:
        img.save(self._track(path), optimize=True)

    def bytes(self, path: Path, data: bytes) -> None:
        self._track(path).write_bytes(data)

    def asset_json(self, rel: str, obj, ns: str = MOD_ID) -> None:
        self.json(self.asset_path(rel, ns), obj)

    def data_json(self, rel: str, obj, ns: str = MOD_ID) -> None:
        self.json(self.data_path(rel, ns), obj)

    def texture(self, rel: str, img: Image.Image) -> None:
        """rel like 'block/glowcap_planks' (no extension)."""
        self.png(self.asset_path(f"textures/{rel}.png"), img)

    def texture_meta(self, rel: str, meta: dict) -> None:
        self.json(self.asset_path(f"textures/{rel}.png.mcmeta"), meta)

    def block_model(self, name: str, obj) -> None:
        self.asset_json(f"models/block/{name}.json", obj)

    def item_model(self, name: str, obj) -> None:
        self.asset_json(f"models/item/{name}.json", obj)

    def blockstate(self, name: str, obj) -> None:
        self.asset_json(f"blockstates/{name}.json", obj)

    def loot_table(self, kind: str, name: str, obj) -> None:
        """kind: 'blocks' or 'entities'."""
        self.data_json(f"loot_table/{kind}/{name}.json", obj)

    def recipe(self, name: str, obj) -> None:
        self.data_json(f"recipe/{name}.json", obj)

    def advancement(self, name: str, obj) -> None:
        self.data_json(f"advancement/{name}.json", obj)

    # ---- merged files -------------------------------------------------------------------------------------------
    def tr(self, key: str, value: str) -> None:
        if key in self.lang and self.lang[key] != value:
            raise ValueError(f"lang key {key} defined twice: {self.lang[key]!r} / {value!r}")
        self.lang[key] = value

    def tag(self, registry: str, name: str, values, replace: bool = False) -> None:
        """registry: 'block', 'item', 'entity_type', 'worldgen/biome', ... name: 'minecraft:logs' or 'fungi'."""
        ns, _, path = rid(name).partition(":")
        entry = self.tags.setdefault((registry, ns, path), {"replace": replace, "values": []})
        for value in ([values] if isinstance(values, (str, dict)) else values):
            if value not in entry["values"]:
                entry["values"].append(value)

    def sound(self, event: str, sounds: list, subtitle: str | None = None) -> None:
        """event like 'entity.sporeling.ambient'. sounds: names ('spore_and_stem:x') or dicts."""
        if event in self.sounds:
            raise ValueError(f"sound event {event} defined twice")
        entry = {"sounds": sounds}
        if subtitle:
            entry["subtitle"] = f"subtitles.{MOD_ID}.{event}"
            self.tr(entry["subtitle"], subtitle)
        self.sounds[event] = entry

    def data_map(self, name: str, key: str, value) -> None:
        """name like 'neoforge:item/compostables'."""
        self.data_maps[name][key] = value

    def finish(self) -> None:
        for (registry, ns, path), entry in sorted(self.tags.items()):
            self.json(self.root / "data" / ns / "tags" / registry / f"{path}.json",
                      {"replace": entry["replace"], "values": entry["values"]})
        if self.lang:
            self.asset_json("lang/en_us.json", dict(sorted(self.lang.items())))
        if self.sounds:
            self.asset_json("sounds.json", dict(sorted(self.sounds.items())))
        for name, values in sorted(self.data_maps.items()):
            ns, _, path = name.partition(":")
            self.json(self.root / "data" / ns / "data_maps" / f"{path}.json", {"values": dict(sorted(values.items()))})


def clean(root: Path = GENERATED, keep_sounds: bool = False) -> None:
    """Removes the generated tree (optionally keeping synthesised audio, which is slow to rebuild)."""
    if not root.exists():
        return
    sounds = root / "assets" / MOD_ID / "sounds"
    keep = None
    if keep_sounds and sounds.exists():
        keep = root.parent / "_sounds_keep"
        if keep.exists():
            shutil.rmtree(keep)
        shutil.move(str(sounds), str(keep))
    shutil.rmtree(root)
    if keep is not None:
        sounds.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(keep), str(sounds))
