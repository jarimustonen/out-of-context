#!/usr/bin/env python3
# Square 1080x1080 Lu.ma event cover, matching the OG image: off-white field,
# dark type, and the braille "context window" as big red favicon TILES with
# off-white square dots. The grid spans the full content width (margin to
# margin); the text sits compactly above it.
#
# Output: luma-cover.svg + luma-cover.png (this dir). Not shipped by the site —
# upload luma-cover.png as the Lu.ma event cover. Needs rsvg-convert + Archivo
# Black (see AGENTS.md).

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(HERE, "luma-cover.svg")
PNG_PATH = os.path.join(HERE, "luma-cover.png")

BG = "#f3f2f2"; INK = "#201e1d"; RED = "#ec3013"; OFF = "#f3f2f2"
FF = "Archivo Black, Archivo, sans-serif"
W = H = 1080
LX = 96                       # content margin (shared by text + grid)
DOTS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}
LET = {'O': {1, 3, 5}, 'U': {1, 3, 6}, 'T': {2, 3, 4, 5}, 'F': {1, 2, 4},
       'C': {1, 4}, 'N': {1, 3, 4, 5}, 'E': {1, 5}, 'X': {1, 3, 4, 6}}
BROWS = ["OUT", "OF", "CONTEXT"]

p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
p.append(f'<rect width="{W}" height="{H}" fill="{BG}"/>')
p.append(f'<rect x="1" y="1" width="{W-2}" height="{H-2}" fill="none" stroke="{INK}" stroke-width="2"/>')
p.append(f'<text x="{LX}" y="112" font-family="{FF}" font-size="42" letter-spacing="2" fill="{INK}">OUT OF CONTEXT</text>')
p.append(f'<text x="{LX-4}" y="248" font-family="{FF}" font-size="104" letter-spacing="-2" fill="{INK}">Demoilta #1</text>')
p.append(f'<text x="{LX}" y="324" font-family="{FF}" font-size="32" letter-spacing="0.5" fill="{RED}">KE 16.9.2026 &#183; KLO 18:00</text>')
p.append(f'<text x="{LX}" y="366" font-family="{FF}" font-size="28" letter-spacing="0.5" fill="{INK}" opacity="0.72">VILHONKATU 4 B 18 &#183; ILMAINEN</text>')

# braille as big red favicon tiles, full content width
cols, rows = 7, 5
gap = 8
sq = (W - 2 * LX - (cols - 1) * gap) // cols          # fill margin-to-margin
gw = cols * sq + (cols - 1) * gap
gx0 = LX
gy0 = 418
d = sq * 0.22
xs = [sq * 0.34, sq * 0.66]
ys = [sq * 0.24, sq * 0.5, sq * 0.76]
for r in range(rows):
    word = BROWS[r - 1] if 1 <= r <= 3 else ""
    for c in range(cols):
        x = gx0 + c * (sq + gap)
        y = gy0 + r * (sq + gap)
        p.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="{RED}"/>')
        if c < len(word):
            on = LET[word[c]]
            for dn, (cc, rr) in DOTS.items():
                if dn in on:
                    p.append(f'<rect x="{x+xs[cc]-d/2:.1f}" y="{y+ys[rr]-d/2:.1f}" width="{d:.1f}" height="{d:.1f}" fill="{OFF}"/>')

p.append('</svg>')

with open(SVG_PATH, "w") as f:
    f.write("".join(p))
print(f"wrote {SVG_PATH}")
subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), SVG_PATH, "-o", PNG_PATH], check=True)
print(f"wrote {PNG_PATH}")
