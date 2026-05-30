"""
run_offline.py

Point d'entrée principal pour la partie 3 du projet QuadGlitch.
Ce script :
1. charge 4 images fixes ;
2. crée un clean wiggle ;
3. crée un glitch wiggle ;
4. sauvegarde GIF + MP4 ;
5. sauvegarde un manifest JSON.

Lance-le depuis le dossier part03_offline :
python run_offline.py
"""

from pathlib import Path
import random

from src.quadglitch_offline.io_utils import EXPECTED_VIEW_NAMES, load_quad_views, resize_views_to_common_size
from src.quadglitch_offline.effects import scramble_view_order
from src.quadglitch_offline.render import build_wiggle_frames, save_gif, save_mp4_with_ffmpeg
from src.quadglitch_offline.manifest import save_manifest


# ============================================================
# PARAMÈTRES PRINCIPAUX
# ============================================================
# Pour commencer, on met les paramètres ici, en haut du fichier.
# Plus tard, on pourra les déplacer dans un preset JSON ou une interface.

PARAMS = {
    "software_version": "0.1.0",
    "seed": 123456,

    # Taille de travail. 960x540 est léger pour le Pi et suffisant pour tester.
    # Mets None si tu veux garder la plus petite taille commune des images.
    "target_width": 960,
    "target_height": 540,

    # Ordre de wiggle normal : gauche -> droite -> gauche.
    # Avec 4 vues, [0,1,2,3,2,1] donne un mouvement aller-retour fluide.
    "clean_view_order": [0, 1, 2, 3, 2, 1],

    # Nombre de répétitions de la séquence.
    "cycles": 5,

    # Vitesse de l'animation.
    "fps": 8,

    "effects": {
        "view_order_scramble": {
            "enabled": True,
        },
        "rgb_shift": {
            "enabled": True,
            "red_dx": 8,
            "red_dy": 0,
            "blue_dx": -8,
            "blue_dy": 0,
        },
        "slice_tear": {
            "enabled": True,
            "slice_height": 18,
            "max_offset": 140,
            "probability": 0.75,
        },
        "scanlines": {
            "enabled": True,
            "spacing": 3,
            "darkness": 0.28,
        },
        "macroblock_glitch": {
            "enabled": True,
            "block_size": 32,
            "probability": 0.075,
            "max_offset": 110,
        },
        "palette_shift": {
            "enabled": True,
            "hue_shift": 18,
            "saturation": 1.35,
            "contrast": 1.12,
        },
    },
}


# ============================================================
# DOSSIERS DU PROJET
# ============================================================
ROOT_DIR = Path(__file__).resolve().parent
INPUT_DIR = ROOT_DIR / "input"
OUTPUT_DIR = ROOT_DIR / "output"


def main() -> None:
    """
    Fonction principale du script.
    On garde la logique dans une fonction main() pour que le code soit plus propre.
    """
    rng = random.Random(PARAMS["seed"])

    print("=== QuadGlitch — Partie 3 — moteur offline ===")
    print(f"Dossier d'entrée : {INPUT_DIR}")
    print(f"Dossier de sortie : {OUTPUT_DIR}")

    # 1. Charger les 4 images.
    views = load_quad_views(INPUT_DIR)

    # 2. Mettre les images à une taille commune.
    views = resize_views_to_common_size(
        views,
        target_width=PARAMS["target_width"],
        target_height=PARAMS["target_height"],
    )

    # 3. Construire le wiggle propre.
    clean_order = PARAMS["clean_view_order"]
    clean_frames = build_wiggle_frames(
        views=views,
        view_order=clean_order,
        cycles=PARAMS["cycles"],
        effect_params=None,
        rng=rng,
    )

    # 4. Construire le wiggle glitché.
    glitch_order = scramble_view_order(
        default_order=clean_order,
        enabled=PARAMS["effects"]["view_order_scramble"]["enabled"],
        rng=rng,
    )

    glitch_frames = build_wiggle_frames(
        views=views,
        view_order=glitch_order,
        cycles=PARAMS["cycles"],
        effect_params=PARAMS,
        rng=rng,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # 5. Sauvegarder GIF.
    clean_gif = OUTPUT_DIR / "clean_wiggle.gif"
    glitch_gif = OUTPUT_DIR / "glitch_wiggle.gif"
    save_gif(clean_frames, clean_gif, fps=PARAMS["fps"])
    save_gif(glitch_frames, glitch_gif, fps=PARAMS["fps"])

    # 6. Sauvegarder MP4 si ffmpeg est disponible.
    clean_mp4 = OUTPUT_DIR / "clean_wiggle.mp4"
    glitch_mp4 = OUTPUT_DIR / "glitch_wiggle.mp4"
    clean_mp4_ok = save_mp4_with_ffmpeg(clean_frames, clean_mp4, fps=PARAMS["fps"])
    glitch_mp4_ok = save_mp4_with_ffmpeg(glitch_frames, glitch_mp4, fps=PARAMS["fps"])

    # 7. Sauvegarder une image fixe de preview.
    preview_path = OUTPUT_DIR / "glitch_preview.png"
    glitch_frames[0].save(preview_path)

    # 8. Sauvegarder le manifest JSON.
    output_files = [
        str(clean_gif),
        str(glitch_gif),
        str(preview_path),
    ]
    if clean_mp4_ok:
        output_files.append(str(clean_mp4))
    if glitch_mp4_ok:
        output_files.append(str(glitch_mp4))

    manifest_params = dict(PARAMS)
    manifest_params["actual_glitch_view_order"] = glitch_order

    save_manifest(
        output_path=OUTPUT_DIR / "manifest.json",
        params=manifest_params,
        input_files=[str(INPUT_DIR / name) for name in EXPECTED_VIEW_NAMES],
        output_files=output_files,
    )

    print("\nRendu terminé.")
    print(f"- Clean GIF   : {clean_gif}")
    print(f"- Glitch GIF  : {glitch_gif}")
    print(f"- Preview PNG : {preview_path}")
    print(f"- Manifest    : {OUTPUT_DIR / 'manifest.json'}")
    if clean_mp4_ok and glitch_mp4_ok:
        print(f"- Clean MP4   : {clean_mp4}")
        print(f"- Glitch MP4  : {glitch_mp4}")
    else:
        print("MP4 non créé car ffmpeg n'est pas disponible. Installe-le avec : sudo apt install -y ffmpeg")


if __name__ == "__main__":
    main()
