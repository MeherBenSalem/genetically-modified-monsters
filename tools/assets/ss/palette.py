"""The shared palette. Blocks, items, creatures, particles and the listing art all draw from these ramps, so the mod
reads as one family. Every ramp runs darkest -> lightest and is hand hue-shifted (shadows cool, lights warm).

Identity: natural cap colours, one bioluminescent accent (GLOW teal) shared by Glowcaps, Lumen Spores, Glowmoths,
veil bulbs and the Myceliarch's gills. Spores are a warm off-white (SPORE).
"""
from __future__ import annotations

# ---- Glowcap: bioluminescent teal cap, pale blue-grey stem, cool grey-blue planks -------------------------------
GLOWCAP_CAP = ["#0b2f3a", "#124b55", "#1b7272", "#2fa6a0", "#5fd8cc", "#a8f7ec"]
GLOWCAP_RIM = ["#9ad9d0", "#c8f1ea", "#ecfffb"]
GLOW = ["#1f8f86", "#3fc7c0", "#6bf2e3", "#b8fff4", "#f0fffc"]          # emissive accent
GLOWCAP_STEM = ["#4d5a68", "#6c7c8b", "#8fa0ae", "#b3c2cc", "#d6e1e6"]
GLOWCAP_PLANKS = ["#2f3b4a", "#3f4e60", "#526477", "#6a7d90", "#8497a8"]

# ---- Bouncecap: rosy pink dome with cream spots, cream stem, rosy tan planks ------------------------------------
BOUNCECAP_CAP = ["#4c1730", "#7a2649", "#a83a63", "#d45d86", "#ef8eae", "#fbc4d4"]
BOUNCECAP_SPOT = ["#e8cdb4", "#f6e6d2", "#fff6ea"]
BOUNCECAP_STEM = ["#8d725f", "#b29680", "#d1b8a1", "#e8d6c2", "#f7ece0"]
BOUNCECAP_PLANKS = ["#6a3f43", "#87545a", "#a46e70", "#c08b87", "#d9aba3"]

# ---- Inkcap: shaggy off-white bell with an ink-black fringe, grey stem, charcoal-violet planks -------------------
INKCAP_CAP = ["#6f6a69", "#948e8b", "#b8b2ad", "#d9d4ce", "#f1eee9"]
INK = ["#07060b", "#120f19", "#1f1a2a", "#2f283d", "#463d57"]
INKCAP_STEM = ["#857f7d", "#a59f9b", "#c3bdb8", "#ddd9d4", "#f0ede9"]
INKCAP_PLANKS = ["#1c1824", "#28222f", "#352d3e", "#453b50", "#5a4f67"]

# ---- Small fungi --------------------------------------------------------------------------------------------------
MOREL = ["#3f2a17", "#634426", "#8c6539", "#b78e58", "#dcbd85", "#f2dcae"]
CHANTERELLE = ["#6e3d0e", "#9a5c14", "#c9851d", "#eaae32", "#fbd36b", "#fff0b0"]
DEATHCAP_CAP = ["#525c33", "#748048", "#99a564", "#bfc98b", "#dfe6b8", "#f3f6dc"]
DEATHCAP_WHITE = ["#b9b6a6", "#d6d3c4", "#ecebe0", "#fbfaf3"]
FROSTCAP = ["#1d4f7a", "#2f74a3", "#4f9fcb", "#8acbe9", "#c8ecfb", "#f6fdff"]
EMBER = ["#4d120d", "#8c2116", "#c9401c", "#f2732a", "#ffad48", "#ffe28a"]
PUFFBALL = ["#8f8470", "#b4a990", "#d4cab3", "#ebe4d4", "#f8f5ee", "#ffffff"]

# ---- Materials, soils and life --------------------------------------------------------------------------------------
SPORE = ["#b9ab8b", "#d6cbb0", "#e9dfc7", "#f6f0e2"]
MYCELIUM = ["#a99f91", "#c8bfb0", "#e2dbcf", "#f5f1ea", "#fffdf8"]       # threads, veils, hyphae
MYCOLEATHER = ["#4a3328", "#6a4a39", "#8c654c", "#ad8362", "#cba380"]
TRUFFLE = ["#1f1512", "#33241e", "#4b362c", "#665044", "#8a7262"]
TRUFFLE_MARBLE = ["#b9a48c", "#d8c8b3"]
LOAM = ["#1f1817", "#2b2221", "#3a2f2c", "#4b3e3a", "#5e4f4a"]             # Mycelial Soil
DIRT = ["#4b3424", "#5f4430", "#79583e", "#93704f"]
SHELF = ["#3a2418", "#6b3a1f", "#9c5427", "#c98443", "#e8b97a", "#f6e4c2"]  # turkey-tail bands
SHELF_GREY = ["#5d5550", "#857b72", "#aaa096"]
BARK = ["#271d1a", "#3a2c27", "#4f3d35", "#675045", "#806656"]             # cultivation log / Myceliarch
MYCOSIS = ["#3d5a2c", "#5c8040", "#7fb069", "#a9d38c", "#d7f0bf"]
ROOT = ["#2a1d16", "#3f2b20", "#5a3f2d", "#76563f", "#93715a"]


def hex2rgba(value: str, alpha: int = 255) -> tuple[int, int, int, int]:
    value = value.lstrip("#")
    return (int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16), alpha)


def rgba(ramp: list[str], alpha: int = 255) -> list[tuple[int, int, int, int]]:
    return [hex2rgba(c, alpha) for c in ramp]
