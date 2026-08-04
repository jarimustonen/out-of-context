#!/usr/bin/env python3
# Square 1080x1080 Lu.ma event cover: full red, off-white type + braille grid.
# Braille dots are favicon-style hard squares (matching the site + OG image).
#
# Output: luma-cover.svg + luma-cover.png (both in this dir). Not shipped by the
# site — upload luma-cover.png as the Lu.ma event cover. Rerun when date/tagline
# changes. Needs rsvg-convert + Archivo Black (see AGENTS.md).

import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SVG_PATH = os.path.join(HERE, "luma-cover.svg")
PNG_PATH = os.path.join(HERE, "luma-cover.png")

RED = "#ec3013"; OFF = "#f3f2f2"
FF = "Archivo Black, Archivo, sans-serif"
W = H = 1080
DOTS = {1: (0, 0), 2: (0, 1), 3: (0, 2), 4: (1, 0), 5: (1, 1), 6: (1, 2)}
LET = {'O': {1, 3, 5}, 'U': {1, 3, 6}, 'T': {2, 3, 4, 5}, 'F': {1, 2, 4},
       'C': {1, 4}, 'N': {1, 3, 4, 5}, 'E': {1, 5}, 'X': {1, 3, 4, 6}}
BROWS = ["OUT", "OF", "CONTEXT"]

p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
p.append(f'<rect width="{W}" height="{H}" fill="{RED}"/>')
LX = 96
p.append(f'<text x="{LX}" y="150" font-family="{FF}" font-size="32" letter-spacing="5" fill="{OFF}">OUT OF CONTEXT</text>')
p.append(f'<text x="{LX-4}" y="330" font-family="{FF}" font-size="118" letter-spacing="-3" fill="{OFF}">Demoja,</text>')
p.append(f'<text x="{LX-4}" y="450" font-family="{FF}" font-size="118" letter-spacing="-3" fill="{OFF}">ei kalvoja.</text>')
p.append(f'<text x="{LX}" y="540" font-family="{FF}" font-size="26" letter-spacing="1.5" fill="{OFF}" opacity="0.9">HELSINKI &#183; KE 16.9.2026 &#183; KLO 18:00 &#183; ILMAINEN</text>')

# braille grid, off-white square-dots on red
cols, rows = 7, 5
sq, gap = 62, 10
gw = cols * sq + (cols - 1) * gap
gx0 = (W - gw) // 2
gy0 = 600
d = sq * 0.22


def bar(y):
    for c in range(cols):
        p.append(f'<rect x="{gx0+c*(sq+gap)}" y="{y}" width="{sq}" height="{sq}" fill="{OFF}"/>')


bar(gy0)
for ri, word in enumerate(BROWS):
    y = gy0 + (ri + 1) * (sq + gap)
    for c in range(cols):
        x = gx0 + c * (sq + gap)
        p.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="none" stroke="{OFF}" stroke-opacity="0.55" stroke-width="2.5"/>')
        if c < len(word):
            on = LET[word[c]]
            xs = [x + sq * 0.34, x + sq * 0.66]
            ys = [y + sq * 0.24, y + sq * 0.5, y + sq * 0.76]
            for dn, (cc, rr) in DOTS.items():
                if dn in on:
                    p.append(f'<rect x="{xs[cc]-d/2:.1f}" y="{ys[rr]-d/2:.1f}" width="{d:.1f}" height="{d:.1f}" fill="{OFF}"/>')
bar(gy0 + 4 * (sq + gap))
p.append(f'<text x="{W//2}" y="1010" font-family="{FF}" font-size="28" letter-spacing="1" fill="{OFF}" text-anchor="middle" opacity="0.92">out-of-context.dev</text>')
p.append('</svg>')

with open(SVG_PATH, "w") as f:
    f.write("".join(p))
print(f"wrote {SVG_PATH}")
subprocess.run(["rsvg-convert", "-w", str(W), "-h", str(H), SVG_PATH, "-o", PNG_PATH], check=True)
print(f"wrote {PNG_PATH}")
