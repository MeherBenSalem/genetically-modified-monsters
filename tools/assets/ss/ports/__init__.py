"""Ports: other Minecraft versions' resource trees, derived from the reference (1.21.1) tree after every build.

A port is a module with
  WORKSPACE = "1.20.1"        # the workspace folder at the repository root
  MINECRAFT = "1.20.1"        # the vanilla version its references are validated against
  convert(src, dst, vanilla)  # writes the converted tree to dst (wiping it first); returns an object with
                              #   .written (paths) and .summary() (lossy conversions, one line each)

To add a version, write ss/ports/v<version>.py (start from the closest existing port) and list it in PORTS. The
entity geometry/animation Java is written into every port's workspace as well (ss/entities).
"""
from __future__ import annotations

import os
from pathlib import Path

from ..paths import generated
from . import v1_20_1
from .vanilla import Vanilla

PORTS = [v1_20_1]


def run(src: Path) -> list[tuple[object, object]]:
    """Converts src for every port. SS_PORT_NO_VANILLA=1 skips the vanilla download and reference checks."""
    results = []
    for port in PORTS:
        vanilla = None if os.environ.get("SS_PORT_NO_VANILLA") else Vanilla(port.MINECRAFT).ensure()
        results.append((port, port.convert(src, generated(port.WORKSPACE), vanilla)))
    return results
