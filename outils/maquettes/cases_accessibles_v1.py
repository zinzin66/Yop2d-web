#!/usr/bin/env python3
"""Maquette « cases accessibles » (grille, étape 3) : python3 outils/maquettes/cases_accessibles_v1.py <dossier de sortie>"""
import sys, os
from collections import deque
from PIL import Image, ImageDraw, ImageFont
sortie = sys.argv[1]; os.makedirs(sortie, exist_ok=True)
def police(t):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, t)
    return ImageFont.load_default()
C, L, S = 9, 7, 64
MURS = {(3,1),(3,2),(3,3),(5,4),(5,5),(6,4),(1,5)}
FORET = {(2,4),(3,4),(4,4),(2,5),(3,5)}
HERO, AMI, ENNEMI = (2,3), (1,2), (6,2)
def portee(depart, pm, cout=False):
    d = {depart: 0}; q = deque([depart])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            n = (x+dx, y+dy)
            if not (0 <= n[0] < C and 0 <= n[1] < L) or n in MURS or n == ENNEMI or n == AMI: continue
            c = d[(x,y)] + (2 if cout and n in FORET else 1)
            if c <= pm and c < d.get(n, 99): d[n] = c; q.append(n)
    return d
def plateau(titre, mode):
    im = Image.new('RGB', (C*S+40, L*S+110), '#111C26'); g = ImageDraw.Draw(im)
    g.text((20, 14), titre, fill='#4CC9F0', font=police(22))
    ox, oy = 20, 56
    acc = portee(HERO, 4, cout=(mode == 'cout'))
    for y in range(L):
        for x in range(C):
            r = (ox+x*S, oy+y*S, ox+x*S+S-2, oy+y*S+S-2)
            col = '#1E3B2A'
            if (x,y) in FORET: col = '#14532D'
            if (x,y) in MURS: col = '#5B6470'
            g.rectangle(r, fill=col)
            if (x,y) in acc and (x,y) != HERO and mode != 'attaque':
                g.rectangle(r, fill='#1F6FA8', outline='#4CC9F0', width=3)
                if mode == 'cout': g.text((r[0]+22, r[1]+18), str(acc[(x,y)]), fill='white', font=police(22))
            if mode == 'attaque':
                dist = abs(x-HERO[0]) + abs(y-HERO[1])
                if 1 <= dist <= 2 and (x,y) not in MURS:
                    g.rectangle(r, fill='#8A2C2C', outline='#FF7B7B', width=3)
            if (x,y) in FORET: g.text((r[0]+4, r[1]+2), '🌲'[0] if False else '', fill='white')
    def pion(c, col, t):
        x, y = c; g.ellipse((ox+x*S+10, oy+y*S+10, ox+x*S+S-12, oy+y*S+S-12), fill=col, outline='white', width=3)
        g.text((ox+x*S+24, oy+y*S+20), t, fill='white', font=police(22))
    pion(HERO, '#2E7D32', 'H'); pion(AMI, '#2E7D32', 'A'); pion(ENNEMI, '#B02A2A', 'M')
    return im, g
a, ga = plateau('1  Cases où je peux aller (4 pas)', 'depl')
b, gb = plateau('2  Idem avec forêt = coûte 2 pas', 'cout')
c, gc = plateau('3  Cases où je peux attaquer (portée 2)', 'attaque')
for im, g, t in ((a, ga, 'Murs et amis bloquent. Le monstre aussi.'), (b, gb, 'Les chiffres = pas utilisés pour arriver.'), (c, gc, 'Même idée, mais sans tenir compte des murs.')):
    g.text((20, im.height-40), t, fill='#C9D3DC', font=police(18))
W = a.width
# noeuds
n = Image.new('RGB', (W*3, 290), '#0B141C'); g = ImageDraw.Draw(n)
def boite(x, titre, lignes, coul='#2B6CB0'):
    g.rounded_rectangle((x, 30, x+470, 262), 14, fill='#1A2733', outline=coul, width=3)
    g.rectangle((x, 30, x+470, 70), fill=coul); g.text((x+14, 38), titre, fill='white', font=police(22))
    for i, l in enumerate(lignes): g.text((x+16, 84+i*34), l, fill='#DDE6EE', font=police(19))
boite(20, 'Montrer les cases accessibles', ['Qui : hero', 'Pas de déplacement : 4', 'Couleur : bleu', 'Les murs bloquent : oui', 'Les unités bloquent : oui'])
boite(W+20, 'Si la case est accessible', ['Case touchée : colonne / ligne', '→ Vrai : Aller à la case', '→ Faux : message « trop loin »'], '#7C4DFF')
boite(W*2+20, 'Cacher les cases', ['(après le déplacement', 'ou quand on change d\'unité)'], '#555F6B')
out = Image.new('RGB', (W*3, a.height+290), '#0B141C')
out.paste(a, (0, 0)); out.paste(b, (W, 0)); out.paste(c, (2*W, 0)); out.paste(n, (0, a.height))
out.save(os.path.join(sortie, 'cases_accessibles_v1.png')); print(out.size)
