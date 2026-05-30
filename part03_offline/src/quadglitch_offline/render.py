"""
render.py

Fonctions de rendu : création des frames wiggle, sauvegarde GIF, sauvegarde MP4.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from PIL import Image

from .effects import apply_effect_chain


def build_wiggle_frames(
    views: list[Image.Image],
    view_order: list[int],
    cycles: int = 4,
    effect_params: dict | None = None,
    rng=None,
) -> list[Image.Image]:
    """
    Construit une liste de frames à partir des 4 vues.

    Paramètres
    ----------
    views : list[Image.Image]
        Les 4 images de départ.
    view_order : list[int]
        Ordre de lecture des vues. Exemple : [0, 1, 2, 3, 2, 1].
    cycles : int
        Nombre de répétitions de l'ordre de lecture.
    effect_params : dict | None
        Si None, rendu clean. Sinon, applique la chaîne d'effets.
    rng : random.Random | None
        Générateur aléatoire pour les effets aléatoires.

    Retour
    ------
    list[Image.Image]
        Liste des frames prêtes à exporter.
    """
    frames = []

    for _ in range(cycles):
        for view_index in view_order:
            frame = views[view_index].copy()
            if effect_params is not None:
                frame = apply_effect_chain(frame, effect_params, rng=rng)
            frames.append(frame)

    return frames


def save_gif(frames: list[Image.Image], output_path: Path, fps: int = 8) -> None:
    """
    Sauvegarde une animation GIF.

    Paramètres
    ----------
    frames : list[Image.Image]
        Frames à écrire.
    output_path : Path
        Chemin du GIF final.
    fps : int
        Images par seconde. Plus haut = animation plus rapide.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    duration_ms = int(1000 / fps)

    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration_ms,
        loop=0,
        optimize=False,
    )


def save_mp4_with_ffmpeg(frames: list[Image.Image], output_path: Path, fps: int = 8) -> bool:
    """
    Sauvegarde une vidéo MP4 avec ffmpeg.

    Paramètres
    ----------
    frames : list[Image.Image]
        Frames à écrire.
    output_path : Path
        Chemin du MP4 final.
    fps : int
        Images par seconde.

    Retour
    ------
    bool
        True si le MP4 a été créé, False si ffmpeg n'est pas installé.
    """
    if shutil.which("ffmpeg") is None:
        print("ATTENTION : ffmpeg n'est pas installé. Le MP4 sera ignoré, mais le GIF fonctionne.")
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = output_path.parent / "_temp_frames"

    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)

    try:
        for i, frame in enumerate(frames):
            frame.save(temp_dir / f"frame_{i:04d}.png")

        command = [
            "ffmpeg",
            "-y",
            "-framerate", str(fps),
            "-i", str(temp_dir / "frame_%04d.png"),
            "-pix_fmt", "yuv420p",
            "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2",
            str(output_path),
        ]

        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
