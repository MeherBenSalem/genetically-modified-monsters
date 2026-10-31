import os
from pathlib import Path

TOOLS = Path(__file__).resolve().parents[1]          # tools/assets
REPO = TOOLS.parents[1]
MOD_ID = "spore_and_stem"
JAVA_PACKAGE_PATH = Path("com") / "nightbeam" / "sporeandstem"

# The reference workspace: every module generates for this Minecraft version. Other workspaces get their resources
# from a port step (ss/ports) that converts the reference tree.
REFERENCE_WORKSPACE = "1.21.1"


def workspace(name: str) -> Path:
    return REPO / name


def generated(name: str) -> Path:
    """The generated resource root of a workspace (common/src/generated/resources)."""
    return workspace(name) / "common" / "src" / "generated" / "resources"


def main_resources(name: str) -> Path:
    return workspace(name) / "common" / "src" / "main" / "resources"


def java(name: str) -> Path:
    """The common Java source root of a workspace, down to the mod's package."""
    return workspace(name) / "common" / "src" / "main" / "java" / JAVA_PACKAGE_PATH


WORKSPACE = workspace(REFERENCE_WORKSPACE)
GENERATED = generated(REFERENCE_WORKSPACE)
ASSETS = GENERATED / "assets" / MOD_ID
DATA = GENERATED / "data"
TEXTURES = ASSETS / "textures"
MODELS = ASSETS / "models"
SOUNDS = ASSETS / "sounds"
MAIN_RESOURCES = main_resources(REFERENCE_WORKSPACE)
JAVA = java(REFERENCE_WORKSPACE)
BUILD = TOOLS / "build"          # scratch output (previews, contact sheets, vanilla references) - git-ignored
# Root of an extracted vanilla client jar (the folder that contains assets/minecraft). Used only to resolve vanilla
# parent models in render3d previews and to compare scale/brightness. Never copied into the mod.
VANILLA_REF = os.environ.get("SS_VANILLA_ASSETS") or None
