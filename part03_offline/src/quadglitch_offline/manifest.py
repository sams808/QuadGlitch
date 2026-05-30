"""
manifest.py

Sauvegarde un fichier JSON qui documente exactement le rendu généré.
C'est important pour pouvoir retrouver les paramètres d'un glitch réussi.
"""

from __future__ import annotations

import json
import platform
from datetime import datetime
from pathlib import Path


def save_manifest(
    output_path: Path,
    params: dict,
    input_files: list[str],
    output_files: list[str],
) -> None:
    """
    Écrit le manifest JSON.

    Paramètres
    ----------
    output_path : Path
        Chemin du fichier manifest.json.
    params : dict
        Tous les paramètres utilisés pour le rendu.
    input_files : list[str]
        Liste des images d'entrée.
    output_files : list[str]
        Liste des fichiers générés.
    """
    manifest = {
        "project": "QuadGlitch",
        "part": "part03_offline_wiggle_glitch_engine",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "python_version": platform.python_version(),
        "input_files": input_files,
        "output_files": output_files,
        "parameters": params,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
