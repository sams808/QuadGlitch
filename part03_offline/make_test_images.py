"""
make_test_images.py

Crée 4 images de test si tu n'as pas encore de photos.
Les images ont des couleurs et textes différents pour vérifier facilement l'ordre du wiggle.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

INPUT_DIR = Path("input")
INPUT_DIR.mkdir(exist_ok=True)

colors = [
    (220, 60, 60),
    (60, 180, 80),
    (70, 100, 220),
    (220, 180, 60),
]

for i, color in enumerate(colors):
    img = Image.new("RGB", (960, 540), color)
    draw = ImageDraw.Draw(img)

    # Motifs simples pour voir le décalage et les glitches.
    for x in range(0, 960, 80):
        draw.line((x + i * 10, 0, x + i * 10, 540), fill=(255, 255, 255), width=2)
    for y in range(0, 540, 60):
        draw.line((0, y + i * 6, 960, y + i * 6), fill=(0, 0, 0), width=2)

    text = f"QuadGlitch view_{i}"
    draw.rectangle((70, 205, 890, 335), fill=(0, 0, 0))
    draw.text((110, 245), text, fill=(255, 255, 255))

    img.save(INPUT_DIR / f"view_{i}.png")

print("Images de test créées dans input/view_0.png à input/view_3.png")
