"""Language entries that belong to no single module (creative tab, effects, tooltips)."""
from __future__ import annotations

from .out import Out
from .paths import MOD_ID


def base_lang(out: Out) -> None:
    out.tr(f"itemGroup.{MOD_ID}", "Spore & Stem")
    out.tr(f"effect.{MOD_ID}.mycosis", "Mycosis")
    out.tr(f"effect.{MOD_ID}.spore_ward", "Spore Ward")
    out.tr(f"effect.{MOD_ID}.rooted", "Rooted")
