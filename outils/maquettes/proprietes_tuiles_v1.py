#!/usr/bin/env python3
"""Maquette « propriétés des tuiles » (grille, étape A) : python3 outils/maquettes/proprietes_tuiles_v1.py <tileset 320x80 ninja> <dossier de sortie>"""
import sys, os
from PIL import Image, ImageDraw, ImageFont
tileset, sortie = sys.argv[1], sys.argv[2]; os.makedirs(sortie, exist_ok=True)
def F(t):
    for p in ('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', '/usr/share/fonts/dejavu/DejaVuSans-Bold.ttf'):
        if os.path.exists(p): return ImageFont.truetype(p, t)
    return ImageFont.load_default()
ts = Image.open(tileset).convert('RGBA')
tuiles = [ts.crop((i*80, 0, i*80+80, 80)) for i in range(4)]
eau = Image.new('RGBA', (80, 80), '#2563A8'); d = ImageDraw.Draw(eau)
for y in (20, 44, 66): d.arc((8, y-8, 40, y+8), 200, 340, fill='#7FB5E8', width=3); d.arc((44, y-8, 76, y+8), 200, 340, fill='#7FB5E8', width=3)
route = Image.new('RGBA', (80, 80), '#8B6B43'); d = ImageDraw.Draw(route); d.rectangle((0, 22, 80, 58), fill='#B08D5A')
tuiles += [eau, route]
NOMS = ['Herbe', 'Forêt', 'Montagne', 'Sable', 'Eau', 'Route']
COUL = ['#6FBF73', '#2E7D32', '#9AA3AE', '#E0C068', '#4C9BE8', '#C9A66B']
COUT = ['1', '2', '3', '2', '—', '1']
DEF = ['0', '+1', '+2', '0', '—', '0']
BG, PANNEAU, CLAIR, NEON = '#0B141C', '#1A2733', '#DDE6EE', '#4CC9F0'
W, H = 1900, 1000
im = Image.new('RGB', (W, H), BG); g = ImageDraw.Draw(im)
def fenetre(x, y, w, h, titre):
    g.rounded_rectangle((x, y, x+w, y+h), 16, fill=PANNEAU, outline='#33485A', width=2)
    g.text((x+20, y+14), titre, fill=NEON, font=F(26))
# ---- fenêtre 1 : l'image des tuiles + terrain choisi
fenetre(20, 20, 900, 620, '1  Éditeur de tuiles : Terrains')
echelle = 1.5
for i, t in enumerate(tuiles):
    x, y = 50 + i*135, 80
    big = t.resize((120, 120), Image.NEAREST); im.paste(big, (x, y))
    g.rectangle((x, y, x+120, y+120), outline='#33485A', width=2)
    if i in (1, 2, 4):   # tuiles marquées avec le terrain choisi (Forêt)
        pass
    g.rectangle((x, y+96, x+120, y+120), fill=COUL[i]); g.text((x+8, y+98), NOMS[i], fill='#10202B', font=F(18))
g.text((50, 215), 'Touche une tuile pour lui donner le terrain choisi à droite', fill='#9FB3C4', font=F(20))
# terrains liste
g.text((50, 270), 'Terrains', fill=CLAIR, font=F(24))
for i, n in enumerate(NOMS):
    x, y = 50 + (i % 3) * 290, 310 + (i // 3) * 70
    sel = n == 'Forêt'
    g.rounded_rectangle((x, y, x+270, y+56), 12, fill='#22384A' if sel else '#16222D', outline=NEON if sel else '#33485A', width=3 if sel else 2)
    g.rounded_rectangle((x+10, y+10, x+46, y+46), 8, fill=COUL[i]); g.text((x+58, y+14), n, fill=NEON if sel else CLAIR, font=F(22))
g.rounded_rectangle((50, 460, 320, 516), 12, fill='#16222D', outline='#33485A', width=2); g.text((70, 474), '+ Nouveau terrain', fill=CLAIR, font=F(22))
g.text((50, 540), '3 tuiles utilisent « Forêt »', fill='#9FB3C4', font=F(20))
# ---- fenêtre 2 : propriétés du terrain
fenetre(940, 20, 940, 620, '2  Terrain « Forêt »')
lignes = [('Nom', 'Forêt'), ('Couleur (pour l\'aperçu)', '■ vert foncé'), ('Coût de déplacement', '2 pas'), ('Bloque le passage', 'non'),
          ('Bonus de défense', '+1'), ('Visible dans « Montrer les cases » (couleur)', 'non')]
for i, (a, b) in enumerate(lignes):
    y = 80 + i*62
    g.rounded_rectangle((970, y, 1850, y+50), 10, fill='#16222D', outline='#33485A', width=2)
    g.text((990, y+12), a, fill=CLAIR, font=F(22)); g.text((1560, y+12), b, fill=NEON, font=F(22))
g.text((970, 465), 'Mes propriétés (pour tes règles)', fill=CLAIR, font=F(24))
for i, (a, b) in enumerate([('cache', 'oui'), ('vision', '-1')]):
    y = 505 + i*52
    g.rounded_rectangle((970, y, 1850, y+44), 10, fill='#16222D', outline='#33485A', width=2); g.text((990, y+9), a + '  =  ' + b, fill=CLAIR, font=F(21))
g.text((1560, 590), '+ Ajouter', fill=NEON, font=F(21))
# ---- aperçu carte
fenetre(20, 660, 900, 320, '3  Voir les terrains sur la carte (aperçu)')
carte = ["EEEEEMMMMM", "ERRRRRRFFM", "EERSSSRFFM", "EEERHHRRRM"]
carte = ["EEHHHHMMMM", "ERRRRRRFFM", "EERHHHRFFM", "EEEEHSRRRM"]
cle = {'H': 0, 'F': 1, 'M': 2, 'S': 3, 'E': 4, 'R': 5}
for y, ligne in enumerate(carte):
    for x, ch in enumerate(ligne):
        t = tuiles[cle[ch]].resize((64, 64), Image.NEAREST); im.paste(t, (50 + x*64, 710 + y*64))
        ov = Image.new('RGBA', (64, 64), COUL[cle[ch]] + '66'); im.paste(ov, (50 + x*64, 710 + y*64), ov)
g.text((710, 740), 'Chaque terrain\na sa couleur :\nutile pour\nvérifier la carte', fill='#9FB3C4', font=F(20))
# ---- nœuds
fenetre(940, 660, 940, 320, '4  Ce que les nœuds peuvent lire')
for i, (t, d) in enumerate([('Terrain de la case (nœud vert)', '→ « Forêt »'), ('Coût et défense (nœuds verts)', '→ 2 / +1'),
                            ('Montrer les cases accessibles', 'lit le coût des terrains'), ('Chemins (Aller à…)', 'évitent les terrains qui bloquent'),
                            ('Infliger des dégâts', 'défense déduite (option)')]):
    y = 710 + i*52
    g.rounded_rectangle((970, y, 1850, y+44), 10, fill='#16222D', outline='#33485A', width=2); g.text((990, y+9), t, fill=CLAIR, font=F(20)); g.text((1500, y+9), d, fill='#9FB3C4', font=F(19))
im.save(os.path.join(sortie, 'proprietes_tuiles_v1.png')); print(im.size)
