import os
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]          # tools/assets
REPO = TOOLS.parents[1]
WORKSPACE = REPO / "1.21.1"
MOD_ID = "spore_and_stem"
GENERATED = WORKSPACE / "common" / "src" / "generated" / "resources"
ASSETS = GENERATED / "assets" / MOD_ID
DATA = GENERATED / "data"
TEXTURES = ASSETS / "textures"
MODELS = ASSETS / "models"
SOUNDS = ASSETS / "sounds"
MAIN_RESOURCES = WORKSPACE / "common" / "src" / "main" / "resources"
JAVA = WORKSPACE / "common" / "src" / "main" / "java" / "com" / "nightbeam" / "sporeandstem"
BUILD = TOOLS / "build"          # scratch output (previews, contact sheets) - git-ignored
# Root of an extracted vanilla client jar (the folder that contains assets/minecraft). Used only to resolve vanilla
# parent models in render3d previews and to compare scale/brightness. Never copied into the mod.
VANILLA_REF = os.environ.get("SS_VANILLA_ASSETS") or None
