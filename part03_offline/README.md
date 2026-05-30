# QuadGlitch — Partie 3 — moteur wiggle/glitch offline

Objectif : valider le moteur créatif avec 4 images fixes, sans caméra, sans Pico, sans interface graphique.

## Installation rapide

```bash
cd ~/QuadGlitch/part03_offline
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
sudo apt install -y ffmpeg
```

## Images attendues

Place 4 images dans `input/` avec ces noms :

```text
input/view_0.png
input/view_1.png
input/view_2.png
input/view_3.png
```

Tu peux aussi générer des images de test :

```bash
python make_test_images.py
```

## Lancer le rendu

```bash
python run_offline.py
```

Le script écrit les fichiers dans `output/` :

```text
clean_wiggle.gif
clean_wiggle.mp4
glitch_wiggle.gif
glitch_wiggle.mp4
glitch_preview.png
manifest.json
```

## Principe

Le script charge 4 vues, les remet à la même taille, crée une séquence wiggle propre, puis crée une séquence glitchée avec :

- RGB shift
- slice tear
- scanlines
- macroblock glitch
- palette shift
- view order scramble

Le manifest JSON sauvegarde les paramètres utilisés, le seed, les fichiers d'entrée et les fichiers de sortie.
