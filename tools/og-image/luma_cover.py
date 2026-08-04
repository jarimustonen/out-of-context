#!/usr/bin/env python3
# Square 1080x1080 Lu.ma cover: full red, off-white type + braille grid.
RED="#ec3013"; OFF="#f3f2f2"
FF="Archivo Black, Archivo, sans-serif"
W=H=1080
DOTS={1:(0,0),2:(0,1),3:(0,2),4:(1,0),5:(1,1),6:(1,2)}
LET={'O':{1,3,5},'U':{1,3,6},'T':{2,3,4,5},'F':{1,2,4},'C':{1,4},'N':{1,3,4,5},'E':{1,5},'X':{1,3,4,6}}
BROWS=["OUT","OF","CONTEXT"]
p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
p.append(f'<rect width="{W}" height="{H}" fill="{RED}"/>')
LX=96
p.append(f'<text x="{LX}" y="150" font-family="{FF}" font-size="32" letter-spacing="5" fill="{OFF}">OUT OF CONTEXT</text>')
p.append(f'<text x="{LX-4}" y="330" font-family="{FF}" font-size="118" letter-spacing="-3" fill="{OFF}">Demoja,</text>')
p.append(f'<text x="{LX-4}" y="450" font-family="{FF}" font-size="118" letter-spacing="-3" fill="{OFF}">ei kalvoja.</text>')
p.append(f'<text x="{LX}" y="540" font-family="{FF}" font-size="26" letter-spacing="1.5" fill="{OFF}" opacity="0.9">HELSINKI &#183; KE 16.9.2026 &#183; KLO 18:00 &#183; ILMAINEN</text>')
# braille grid, off-white on red
cols,rows=7,5
sq,gap=62,10
gw=cols*sq+(cols-1)*gap
gx0=(W-gw)//2
gy0=600
dr=sq*0.085
def bar(y):
    for c in range(cols):
        p.append(f'<rect x="{gx0+c*(sq+gap)}" y="{y}" width="{sq}" height="{sq}" fill="{OFF}"/>')
bar(gy0)
for ri,word in enumerate(BROWS):
    y=gy0+(ri+1)*(sq+gap)
    for c in range(cols):
        x=gx0+c*(sq+gap)
        p.append(f'<rect x="{x}" y="{y}" width="{sq}" height="{sq}" fill="none" stroke="{OFF}" stroke-opacity="0.55" stroke-width="2.5"/>')
        if c<len(word):
            on=LET[word[c]]
            xs=[x+sq*0.34,x+sq*0.66]; ys=[y+sq*0.24,y+sq*0.5,y+sq*0.76]
            for d,(cc,rr) in DOTS.items():
                if d in on:
                    p.append(f'<circle cx="{xs[cc]:.1f}" cy="{ys[rr]:.1f}" r="{dr:.1f}" fill="{OFF}"/>')
bar(gy0+4*(sq+gap))
p.append(f'<text x="{W//2}" y="1010" font-family="{FF}" font-size="28" letter-spacing="1" fill="{OFF}" text-anchor="middle" opacity="0.92">out-of-context.dev</text>')
p.append('</svg>')
open("/private/tmp/claude-501/-Users-jari-Sources-out-of-context/f5b865af-bd3e-415f-bd42-1b4e2bf2fb2d/scratchpad/luma_cover.svg","w").write("".join(p))
print("ok")
