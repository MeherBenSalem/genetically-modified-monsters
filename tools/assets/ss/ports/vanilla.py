"""Ground truth for a port: the vanilla client and server of the target Minecraft version.

The jars are downloaded from Mojang's version manifest into tools/assets/build/vanilla-<version>/ (git-ignored); the
client's data and assets are extracted and the server's data generator writes the registry reports. Everything is
cached, so only the first run needs the network (and a Java 17+ runtime: JAVA_HOME, the JDK 17 in /usr/lib/jvm, or
`java` on the PATH).
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import urllib.request
import zipfile
from functools import cached_property
from pathlib import Path

from ..paths import BUILD

MANIFEST = "https://piston-meta.mojang.com/mc/game/version_manifest_v2.json"


def _java() -> str:
    for home in (os.environ.get("JAVA_HOME"), "/usr/lib/jvm/java-17-openjdk-amd64", "/usr/lib/jvm/java-21-openjdk-amd64"):
        if home and (Path(home) / "bin" / "java").exists():
            return str(Path(home) / "bin" / "java")
    found = shutil.which("java")
    if not found:
        raise RuntimeError("no Java runtime found to run the vanilla data generator (set JAVA_HOME)")
    return found


class Vanilla:
    def __init__(self, version: str):
        self.version = version
        self.root = BUILD / f"vanilla-{version}"

    # ---- download / extract ------------------------------------------------------------------------------------
    def ensure(self) -> "Vanilla":
        self.root.mkdir(parents=True, exist_ok=True)
        client, server = self.root / "client.jar", self.root / "server.jar"
        if not client.exists() or not server.exists():
            manifest = json.load(urllib.request.urlopen(MANIFEST))
            entry = next(v for v in manifest["versions"] if v["id"] == self.version)
            meta = json.load(urllib.request.urlopen(entry["url"]))
            for side, path in (("client", client), ("server", server)):
                tmp = path.with_suffix(".part")
                urllib.request.urlretrieve(meta["downloads"][side]["url"], tmp)
                tmp.rename(path)
        extracted = self.root / "client"
        if not (extracted / "version.json").exists():
            with zipfile.ZipFile(client) as jar:
                for name in jar.namelist():
                    if name.startswith(("data/", "assets/")) or name == "version.json":
                        jar.extract(name, extracted)
        reports = self.root / "reports" / "reports" / "registries.json"
        if not reports.exists():
            subprocess.run([_java(), "-DbundlerMainClass=net.minecraft.data.Main", "-jar", str(server), "--reports",
                            "--output", str(self.root / "reports")], cwd=self.root, check=True,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return self

    # ---- lookups -----------------------------------------------------------------------------------------------
    @property
    def data(self) -> Path:
        return self.root / "client" / "data" / "minecraft"

    @property
    def assets(self) -> Path:
        return self.root / "client" / "assets" / "minecraft"

    @cached_property
    def version_info(self) -> dict:
        return json.loads((self.root / "client" / "version.json").read_text(encoding="utf-8"))

    @cached_property
    def registries(self) -> dict[str, set[str]]:
        """Static registries from the report, plus the datapack registries and files found in the vanilla data."""
        report = json.loads((self.root / "reports" / "reports" / "registries.json").read_text(encoding="utf-8"))
        regs = {name: set(body["entries"]) for name, body in report.items()}
        for folder in ("worldgen/biome", "worldgen/configured_feature", "worldgen/placed_feature", "damage_type",
                       "dimension_type", "trim_material", "trim_pattern", "chat_type", "loot_tables", "recipes",
                       "advancements", "structures"):
            base = self.data / folder
            regs[f"minecraft:{folder}"] = {
                "minecraft:" + p.relative_to(base).with_suffix("").as_posix()
                for p in base.rglob("*") if p.is_file()} if base.exists() else set()
        return regs

    @cached_property
    def all_ids(self) -> set[str]:
        return set().union(*self.registries.values())

    @cached_property
    def tags(self) -> dict[str, set[str]]:
        """Tag folder ('blocks', 'items', 'worldgen/biome', ...) -> tag ids without '#'."""
        out: dict[str, set[str]] = {}
        base = self.data / "tags"
        for p in base.rglob("*.json"):
            rel = p.relative_to(base).with_suffix("").as_posix().split("/")
            depth = 2 if rel[0] == "worldgen" else 1
            out.setdefault("/".join(rel[:depth]), set()).add("minecraft:" + "/".join(rel[depth:]))
        return out

    @cached_property
    def all_tags(self) -> set[str]:
        return set().union(*self.tags.values())

    @cached_property
    def blocks(self) -> dict[str, dict[str, list[str]]]:
        """Block id -> {property: [values]} from the blocks report."""
        report = json.loads((self.root / "reports" / "reports" / "blocks.json").read_text(encoding="utf-8"))
        return {bid: body.get("properties", {}) for bid, body in report.items()}

    @cached_property
    def triggers(self) -> set[str]:
        """Advancement triggers vanilla uses (1.20.x has no trigger registry report)."""
        found = set()
        for p in (self.data / "advancements").rglob("*.json"):
            for criterion in json.loads(p.read_text(encoding="utf-8")).get("criteria", {}).values():
                found.add(criterion["trigger"])
        return found

    @cached_property
    def textures(self) -> set[str]:
        base = self.assets / "textures"
        return {"minecraft:" + p.relative_to(base).with_suffix("").as_posix() for p in base.rglob("*.png")}

    @cached_property
    def models(self) -> set[str]:
        base = self.assets / "models"
        return {"minecraft:" + p.relative_to(base).with_suffix("").as_posix() for p in base.rglob("*.json")}
