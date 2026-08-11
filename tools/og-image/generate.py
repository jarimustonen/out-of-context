#!/usr/bin/env python3
# Generate the Out of Context Open Graph image (1200x630).
#
# Brand: modernist red grid — accent #ec3013 on warm off-white #f3f2f2,
# Archivo Black display type (the heavy static cut of the site's Archivo 800).
# Left: big wordmark + "Demoja, ei kalvoja." + a large two-line date/location.
# Right: the braille "context window" grid as favicon TILES — each cell a red
# square with off-white square dots, no orange background panel, as large as
# fits (matches favicon.svg + the site's hero grid).
#
# Output:  og.svg (source) + ../../static/og-image.png (shipped asset).
# Rerun whenever the date / location / tagline changes, then commit the PNG.
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
FF = "Archivo Black, Archivo, sans-serif"

parts = []
parts.append(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">')
parts.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')

# thin dark frame like the site's 2px content borders
parts.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{INK}" stroke-width="2"/>')

# ---- left text column ----
LX = 72
parts.append(f'<text x="{LX}" y="132" font-family="{FF}" font-size="56" letter-spacing="1" fill="{INK}">OUT OF CONTEXT</text>')
parts.append(f'<text x="{LX-4}" y="322" font-family="{FF}" font-size="100" letter-spacing="-3" fill="{INK}">Demoja,</text>')
parts.append(f'<text x="{LX-4}" y="422" font-family="{FF}" font-size="100" letter-spacing="-3" fill="{INK}">ei kalvoja.</text>')
parts.append(f'<text x="{LX}" y="512" font-family="{FF}" font-size="34" letter-spacing="0.5" fill="{RED}">KE 16.9.2026 &#183; KLO 18:00</text>')
parts.append(f'<text x="{LX}" y="558" font-family="{FF}" font-size="30" letter-spacing="0.5" fill="{INK}" opacity="0.72">VILHONKATU 4 B 18 &#183; ILMAINEN</text>')

# ---- right: braille "OUT OF CONTEXT" as big favicon tiles (no orange panel) ----
DOTS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}
LET = {'O': {1, 3, 5}, 'U': {1, 3, 6}, 'T': {2, 3, 4, 5}, 'F': {1, 2, 4},
       'C': {1, 4}, 'N': {1, 3, 4, 5}, 'E': {1, 5}, 'X': {1, 3, 4, 6}}
BROWS = ["OUT", "OF", "CONTEXT"]
bcols, brows = 7, 5
bsq, bgap = 60, 8
gw = bcols * bsq + (bcols - 1) * bgap
gh = brows * bsq + (brows - 1) * bgap
bx0 = W - LX - gw                     # right edge aligned to the left text's margin
by0 = (H - gh) // 2
d = bsq * 0.22
xs = [bsq * 0.34, bsq * 0.66]
ys = [bsq * 0.24, bsq * 0.5, bsq * 0.76]

for r in range(brows):
    word = BROWS[r - 1] if 1 <= r <= 3 else ""
    for c in range(bcols):
        x = bx0 + c * (bsq + bgap)
        y = by0 + r * (bsq + bgap)
        parts.append(f'<rect x="{x}" y="{y}" width="{bsq}" height="{bsq}" fill="{RED}"/>')
        if c < len(word):
            on = LET[word[c]]
            for dn, (cc, rr) in DOTS.items():
                if dn in on:
                    parts.append(f'<rect x="{x + xs[cc] - d/2:.1f}" y="{y + ys[rr] - d/2:.1f}" width="{d:.1f}" height="{d:.1f}" fill="{OFF}"/>')

parts.append('</svg>')

with open(SVG_PATH, "w") as f:
    f.write("\n".join(parts))
print(f"wrote {SVG_PATH}")

subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), SVG_PATH, "-o", PNG_PATH], check=True)
print(f"wrote {os.path.normpath(PNG_PATH)}")
