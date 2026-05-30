"""
effects.py

Premiers effets glitch du projet QuadGlitch.
Chaque effet prend une image PIL en entrée et renvoie une nouvelle image PIL.
On ne modifie pas l'image originale en place : c'est plus sûr et plus facile à comprendre.
"""

from __future__ import annotations

import random
import numpy as np
from PIL import Image, ImageEnhance


def _shift_channel(channel: np.ndarray, dx: int, dy: int) -> np.ndarray:
    """
    Décale un canal couleur sans faire de wrap-around.

    Paramètres
    ----------
    channel : np.ndarray
        Image 2D correspondant à un canal couleur, par exemple R, G ou B.
    dx : int
        Décalage horizontal en pixels. Positif = vers la droite.
    dy : int
        Décalage vertical en pixels. Positif = vers le bas.

    Retour
    ------
    np.ndarray
        Canal décalé. Les zones qui apparaissent sont remplies avec 0.
    """
    height, width = channel.shape
    shifted = np.zeros_like(channel)

    # Zone source : partie de l'image originale qu'on peut copier.
    src_x0 = max(0, -dx)
    src_x1 = min(width, width - dx)
    src_y0 = max(0, -dy)
    src_y1 = min(height, height - dy)

    # Zone destination : là où cette partie sera collée.
    dst_x0 = max(0, dx)
    dst_x1 = min(width, width + dx)
    dst_y0 = max(0, dy)
    dst_y1 = min(height, height + dy)

    shifted[dst_y0:dst_y1, dst_x0:dst_x1] = channel[src_y0:src_y1, src_x0:src_x1]
    return shifted


def rgb_shift(image: Image.Image, red_dx: int = 6, blue_dx: int = -6, red_dy: int = 0, blue_dy: int = 0) -> Image.Image:
    """
    Sépare légèrement les canaux rouge et bleu.

    Effet visuel
    ------------
    Donne un effet de décalage chromatique / écran cassé / aberration numérique.

    Paramètres
    ----------
    image : Image.Image
        Image RGB à traiter.
    red_dx, red_dy : int
        Décalage du canal rouge.
    blue_dx, blue_dy : int
        Décalage du canal bleu.
    """
    arr = np.array(image.convert("RGB"))

    red = _shift_channel(arr[:, :, 0], red_dx, red_dy)
    green = arr[:, :, 1]
    blue = _shift_channel(arr[:, :, 2], blue_dx, blue_dy)

    out = np.stack([red, green, blue], axis=2)
    return Image.fromarray(out.astype(np.uint8), mode="RGB")


def slice_tear(image: Image.Image, slice_height: int = 24, max_offset: int = 45, probability: float = 0.45, rng: random.Random | None = None) -> Image.Image:
    """
    Décale des bandes horizontales de l'image.

    Effet visuel
    ------------
    Simule des déchirures numériques, comme si certaines lignes arrivaient trop tôt/trop tard.

    Paramètres
    ----------
    slice_height : int
        Hauteur approximative d'une bande horizontale en pixels.
    max_offset : int
        Décalage horizontal maximum en pixels.
    probability : float
        Probabilité qu'une bande soit déplacée. 0 = aucune bande, 1 = toutes les bandes.
    rng : random.Random | None
        Générateur aléatoire contrôlé par un seed, pour reproduire les résultats.
    """
    rng = rng or random.Random()
    arr = np.array(image.convert("RGB"))
    height, width, _ = arr.shape
    out = arr.copy()

    for y in range(0, height, slice_height):
        y2 = min(y + slice_height, height)
        if rng.random() < probability:
            dx = rng.randint(-max_offset, max_offset)
            out[y:y2, :, :] = np.roll(arr[y:y2, :, :], shift=dx, axis=1)

    return Image.fromarray(out.astype(np.uint8), mode="RGB")


def scanlines(image: Image.Image, spacing: int = 3, darkness: float = 0.35) -> Image.Image:
    """
    Assombrit régulièrement des lignes horizontales.

    Effet visuel
    ------------
    Donne une texture d'écran CRT/VHS/monitor.

    Paramètres
    ----------
    spacing : int
        Une ligne sur combien est affectée. 3 = une ligne sombre toutes les 3 lignes.
    darkness : float
        Force de l'assombrissement. 0 = aucun effet, 1 = lignes noires.
    """
    arr = np.array(image.convert("RGB")).astype(np.float32)
    darkness = max(0.0, min(1.0, darkness))

    arr[::spacing, :, :] *= (1.0 - darkness)

    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), mode="RGB")


def macroblock_glitch(image: Image.Image, block_size: int = 32, probability: float = 0.08, max_offset: int = 100, rng: random.Random | None = None) -> Image.Image:
    """
    Déplace des blocs carrés de l'image.

    Effet visuel
    ------------
    Imite une compression vidéo cassée : gros blocs mal placés, texture numérique sale.

    Paramètres
    ----------
    block_size : int
        Taille des blocs carrés en pixels.
    probability : float
        Probabilité de déplacer chaque bloc.
    max_offset : int
        Distance maximum de déplacement du bloc source.
    rng : random.Random | None
        Générateur aléatoire contrôlé par un seed.
    """
    rng = rng or random.Random()
    arr = np.array(image.convert("RGB"))
    height, width, _ = arr.shape
    out = arr.copy()

    for y in range(0, height - block_size, block_size):
        for x in range(0, width - block_size, block_size):
            if rng.random() < probability:
                sx = min(max(x + rng.randint(-max_offset, max_offset), 0), width - block_size)
                sy = min(max(y + rng.randint(-max_offset, max_offset), 0), height - block_size)
                out[y:y + block_size, x:x + block_size] = arr[sy:sy + block_size, sx:sx + block_size]

    return Image.fromarray(out.astype(np.uint8), mode="RGB")


def palette_shift(image: Image.Image, hue_shift: int = 24, saturation: float = 1.35, contrast: float = 1.15) -> Image.Image:
    """
    Change la couleur globale de l'image.

    Effet visuel
    ------------
    Produit un rendu plus artificiel : couleurs qui dérivent, saturation étrange, contraste modifié.

    Paramètres
    ----------
    hue_shift : int
        Décalage de teinte sur 0-255. Petit = subtil, grand = très coloré.
    saturation : float
        Multiplicateur de saturation. 1 = inchangé, >1 = plus saturé, <1 = moins saturé.
    contrast : float
        Multiplicateur de contraste. 1 = inchangé.
    """
    img = image.convert("RGB")

    # PIL permet de convertir en HSV : Hue, Saturation, Value.
    hsv = np.array(img.convert("HSV"))
    hsv[:, :, 0] = (hsv[:, :, 0].astype(np.int16) + hue_shift) % 256
    img = Image.fromarray(hsv.astype(np.uint8), mode="HSV").convert("RGB")

    img = ImageEnhance.Color(img).enhance(saturation)
    img = ImageEnhance.Contrast(img).enhance(contrast)
    return img


def apply_effect_chain(image: Image.Image, params: dict, rng: random.Random | None = None) -> Image.Image:
    """
    Applique plusieurs effets dans un ordre fixe.

    Pourquoi un ordre fixe ?
    ------------------------
    Pour que le rendu soit reproductible. Si on change l'ordre des effets, le résultat change.

    Paramètres
    ----------
    image : Image.Image
        Image de départ.
    params : dict
        Dictionnaire contenant les paramètres de chaque effet.
    rng : random.Random | None
        Générateur aléatoire utilisé par les effets aléatoires.
    """
    rng = rng or random.Random()
    out = image.copy()

    if params["effects"]["rgb_shift"]["enabled"]:
        p = params["effects"]["rgb_shift"]
        out = rgb_shift(out, red_dx=p["red_dx"], blue_dx=p["blue_dx"], red_dy=p["red_dy"], blue_dy=p["blue_dy"])

    if params["effects"]["slice_tear"]["enabled"]:
        p = params["effects"]["slice_tear"]
        out = slice_tear(out, slice_height=p["slice_height"], max_offset=p["max_offset"], probability=p["probability"], rng=rng)

    if params["effects"]["macroblock_glitch"]["enabled"]:
        p = params["effects"]["macroblock_glitch"]
        out = macroblock_glitch(out, block_size=p["block_size"], probability=p["probability"], max_offset=p["max_offset"], rng=rng)

    if params["effects"]["palette_shift"]["enabled"]:
        p = params["effects"]["palette_shift"]
        out = palette_shift(out, hue_shift=p["hue_shift"], saturation=p["saturation"], contrast=p["contrast"])

    if params["effects"]["scanlines"]["enabled"]:
        p = params["effects"]["scanlines"]
        out = scanlines(out, spacing=p["spacing"], darkness=p["darkness"])

    return out


def scramble_view_order(default_order: list[int], enabled: bool, rng: random.Random | None = None) -> list[int]:
    """
    Change l'ordre de lecture des vues.

    Exemple
    -------
    Ordre clean : [0, 1, 2, 3, 2, 1]
    Ordre glitch possible : [2, 0, 3, 1, 3, 0]

    Paramètres
    ----------
    default_order : list[int]
        Ordre normal du wiggle.
    enabled : bool
        Si False, on garde l'ordre normal.
    rng : random.Random | None
        Générateur aléatoire contrôlé par un seed.
    """
    if not enabled:
        return default_order

    rng = rng or random.Random()
    new_order = default_order.copy()
    rng.shuffle(new_order)
    return new_order
