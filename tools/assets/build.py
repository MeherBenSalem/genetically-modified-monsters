#!/usr/bin/env python3
"""Regenerates every resource of Spore & Stem into 1.21.1/common/src/generated/resources, then derives the
resource tree of every other workspace from it (ss/ports: 1.20.1/common/src/generated/resources, ...).

  python3 tools/assets/build.py               # everything
  python3 tools/assets/build.py --no-sounds   # keep the synthesised audio as it is (it takes a while)
  python3 tools/assets/build.py --no-ports    # only the reference workspace

The generated trees are wiped first, so nothing stale survives. Then run tools/assets/check.py (once per workspace,
--workspace 1.20.1 for the port). The first run of a port downloads that vanilla version into tools/assets/build/ to
check every vanilla reference against it (SS_PORT_NO_VANILLA=1 skips that check).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from ss import blocks, data, entities, gametest, items, misc, ports, sounds, worldgen  # noqa: E402
from ss.lang import base_lang  # noqa: E402
from ss.out import Out, clean  # noqa: E402
from ss.paths import GENERATED  # noqa: E402

# Order matters only for readability of the log; modules never read each other's output.
MODULES = [("misc", misc), ("blocks", blocks), ("items", items), ("data", data), ("entities", entities),
           ("worldgen", worldgen), ("gametest", gametest)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-sounds", action="store_true", help="keep the existing .ogg files")
    ap.add_argument("--no-ports", action="store_true", help="skip the other workspaces (ss/ports)")
    args = ap.parse_args()
    clean(GENERATED, keep_sounds=args.no_sounds)
    out = Out()
    base_lang(out)
    for name, module in MODULES:
        t = time.time()
        module.generate(out)
        print(f"{name:10s} {time.time() - t:6.2f}s")
    t = time.time()
    sounds.generate(out, synthesise=not args.no_sounds)
    print(f"{'sounds':10s} {time.time() - t:6.2f}s")
    out.finish()
    print(f"wrote {len(out.written)} files, {len(out.lang)} lang keys, {len(out.tags)} tags, {len(out.sounds)} sounds")
    if not args.no_ports:
        t = time.time()
        for port, result in ports.run(GENERATED):
            lossy = sum(1 for line in result.summary() if line.startswith("  "))
            print(f"port {port.MINECRAFT}: wrote {len(result.written)} files to {port.WORKSPACE}/ "
                  f"({lossy} lossy conversions, see tools/assets/build/port-{port.MINECRAFT}.txt) "
                  f"{time.time() - t:.2f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
