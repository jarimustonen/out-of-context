#!/usr/bin/env python3
# Generate the Out of Context Open Graph image (1200x630).
#
# Brand: modernist red grid — accent #ec3013 on warm off-white #f3f2f2,
# Archivo Black display type (the heavy static cut of the site's Archivo 800).
#
# Output:  og.svg (source) + ../../static/og-image.png (shipped asset).
# Rerun this whenever the date / seat count / tagline on the image changes,
# then commit static/og-image.png.
#
# Requires: rsvg-convert (librsvg) and the Archivo Black TTF discoverable by
# fontconfig. On a machine without it:
#   curl -sSL -o /tmp/ArchivoBlack.ttf \
#     https://github.com/google/fonts/raw/main/ofl/archivoblack/ArchivoBlack-Regular.ttf
# and point fontconfig at it (see AGENTS.md).

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(HERE, "og.svg")
PNG_PATH = os.path.join(HERE, "..", "..", "static", "og-image.png")

BG = "#f3f2f2"
INK = "#201e1d"
RED = "#ec3013"
OFF = "#f3f2f2"

W, H = 1200, 630
PANEL_X = 744          # red panel starts here
FF = "Archivo Black, Archivo, sans-serif"

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

# thin dark frame like the site's 2px content borders
parts.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{INK}" stroke-width="2"/>')

# right red panel
parts.append(f'<rect x="{PANEL_X}" y="0" width="{W-PANEL_X}" height="{H}" fill="{RED}"/>')

# ---- left text column ----
LX = 72
parts.append(f'<text x="{LX}" y="86" font-family="{FF}" font-size="26" letter-spacing="4" fill="{INK}">OUT OF CONTEXT</text>')
parts.append(f'<text x="{LX}" y="250" font-family="{FF}" font-size="21" letter-spacing="1.5" fill="{RED}">HELSINKI &#183; KE 16.9.2026 &#183; 18:00 &#183; ILMAINEN</text>')
parts.append(f'<text x="{LX-4}" y="360" font-family="{FF}" font-size="104" letter-spacing="-3" fill="{INK}">Demoja,</text>')
parts.append(f'<text x="{LX-4}" y="464" font-family="{FF}" font-size="104" letter-spacing="-3" fill="{INK}">ei kalvoja.</text>')
parts.append(f'<text x="{LX}" y="566" font-family="{FF}" font-size="22" letter-spacing="0.5" fill="{INK}" opacity="0.55">out-of-context.dev</text>')

# ---- right panel: context-window grid spelling "OUT OF CONTEXT" in braille ----
# Each square is one braille letter; red frame rows top and bottom. Off-white on
# the red panel — the inverse of the site's red-on-off-white hero grid.
parts.append(f'<text x="800" y="150" font-family="{FF}" font-size="17" letter-spacing="2.5" fill="{OFF}">CONTEXT WINDOW</text>')
DOTS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}
LET = {'O': {1, 3, 5}, 'U': {1, 3, 6}, 'T': {2, 3, 4, 5}, 'F': {1, 2, 4},
       'C': {1, 4}, 'N': {1, 3, 4, 5}, 'E': {1, 5}, 'X': {1, 3, 4, 6}}
BROWS = ["OUT", "OF", "CONTEXT"]
bcols = 7
bsq, bgap = 40, 10
bx0, by0 = 800, 182
dr = bsq * 0.085


def _bar(y):
    return "".join(
        f'<rect x="{bx0 + c * (bsq + bgap)}" y="{y}" width="{bsq}" height="{bsq}" fill="{OFF}"/>'
        for c in range(bcols))


parts.append(_bar(by0))
for ri, word in enumerate(BROWS):
    y = by0 + (ri + 1) * (bsq + bgap)
    for c in range(bcols):
        x = bx0 + c * (bsq + bgap)
        parts.append(f'<rect x="{x}" y="{y}" width="{bsq}" height="{bsq}" fill="none" stroke="{OFF}" stroke-opacity="0.55" stroke-width="2"/>')
        if c < len(word):
            on = LET[word[c]]
            xs = [x + bsq * 0.34, x + bsq * 0.66]
            ys = [y + bsq * 0.24, y + bsq * 0.5, y + bsq * 0.76]
            for d, (cc, rr) in DOTS.items():
                if d in on:
                    parts.append(f'<circle cx="{xs[cc]:.1f}" cy="{ys[rr]:.1f}" r="{dr:.1f}" fill="{OFF}"/>')
parts.append(_bar(by0 + 4 * (bsq + bgap)))
by_bottom = by0 + 5 * (bsq + bgap)
parts.append(f'<text x="800" y="{by_bottom + 20}" font-family="{FF}" font-size="20" fill="{OFF}">11 / 30 paikkaa</text>')

parts.append('</svg>')

with open(SVG_PATH, "w") as f:
    f.write("\n".join(parts))
print(f"wrote {SVG_PATH}")

subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), SVG_PATH, "-o", PNG_PATH], check=True)
print(f"wrote {os.path.normpath(PNG_PATH)}")
