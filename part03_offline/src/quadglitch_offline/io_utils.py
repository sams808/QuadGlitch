"""
io_utils.py

Fonctions liées aux fichiers d'entrée/sortie.
Ici, on charge les 4 images de départ : view_0, view_1, view_2, view_3.
"""

from pathlib import Path
from PIL import Image


EXPECTED_VIEW_NAMES = ["view_0.png", "view_1.png", "view_2.png", "view_3.png"]


def load_quad_views(input_dir: Path) -> list[Image.Image]:
    """
    Charge les 4 images fixes utilisées pour simuler les 4 caméras.

    Paramètres
    ----------
    input_dir : Path
        Dossier qui contient view_0.png, view_1.png, view_2.png et view_3.png.

    Retour
    ------
    list[Image.Image]
        Liste de 4 images PIL en mode RGB.

    Vérification
    ------------
    Si un fichier manque, la fonction stoppe le script avec une erreur claire.
    """
    views = []

    for filename in EXPECTED_VIEW_NAMES:
        path = input_dir / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Image manquante : {path}\n"
                "Place 4 images dans input/ : view_0.png, view_1.png, view_2.png, view_3.png"
            )

        image = Image.open(path).convert("RGB")
        views.append(image)

    return views


def resize_views_to_common_size(
    views: list[Image.Image],
    target_width: int | None = None,
    target_height: int | None = None,
) -> list[Image.Image]:
    """
    Met les 4 images à la même taille.

    Pourquoi ?
    ----------
    Pour faire un GIF ou une vidéo, toutes les frames doivent avoir la même taille.
    Plus tard, les 4 caméras auront aussi besoin d'un crop/alignement commun.

    Paramètres
    ----------
    views : list[Image.Image]
        Les 4 images chargées.
    target_width : int | None
        Largeur voulue. Si None, on prend la plus petite largeur parmi les images.
    target_height : int | None
        Hauteur voulue. Si None, on prend la plus petite hauteur parmi les images.

    Retour
    ------
    list[Image.Image]
        Images redimensionnées à une taille commune.
    """
    if target_width is None:
        target_width = min(img.width for img in views)
    if target_height is None:
        target_height = min(img.height for img in views)

    return [img.resize((target_width, target_height), Image.Resampling.LANCZOS) for img in views]
