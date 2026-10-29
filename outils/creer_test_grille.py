#!/usr/bin/env python3
"""Projet de TEST des nœuds « grille » (étape 1) : tests/grille-test.zip, à importer dans une version de test du moteur
qui contient « Colonne touchée », « Ligne touchée », « Colonne / Ligne d'un objet », « Placer sur une case » et
« Centrer sur sa case » (moteur : branche claude/discord-yop2d-config-ox8qgh, à partir du commit a225730).
Usage : python3 outils/creer_test_grille.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test : toucher le sol envoie le héros 1 au CENTRE de la case touchée (nœuds verts « touchée » branchés sur
« Placer sur une case ») et écrit la colonne et la ligne touchées ; toucher le héros 2 (posé exprès de travers dans sa case)
le recentre (« Centrer sur sa case ») ; les colonne / ligne du héros 1 s'écrivent à chaque image (nœuds verts « d'un objet »)."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'grille_test/'
NJ = 'assets_ludexa/Images/Ninja/'
CASE, GX, GY = 80, 60, 140
CARTE = ["..............", "..B...s....B..", "..B...s.......", "....##...B....", ".s..##...B.s..",
         ".s.......B....", "..B...##......", "....s.##..s...", "..B........B..", ".............."]
BLANC, OR, VERT = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0')

def coin(c, l): return GX + c * CASE, GY + l * CASE
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=NJ + 'Tuiles/tileset_ninja.png'),
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True)]
x1, y1 = coin(1, 3)
x2, y2 = coin(1, 6)
objets += [objet('hero', x1, y1, NJ + 'Personnages/ninja6_bas_1.png', CASE, CASE, z=50, prefixe=P),
           objet('hero2', x2 + 23, y2 + 17, NJ + 'Personnages/ninja4_bas_1.png', CASE, CASE, z=50, prefixe=P)]   # posé de travers exprès
def etiquette(nom, y, texte_, couleur=BLANC):
    return texte(nom, 1240, y, 400, 60, texte_, 36, couleur, z=60, prefixe=P, alignementTexte='DROITE', cheminPolice=None)
def valeur(nom, y):
    return texte(nom, 1670, y - 6, 200, 70, '-', 52, VERT, z=60, prefixe=P, cheminPolice=None)
objets += [texte('info', 1240, 150, 640, 330, 'GRID TEST\nTap the ground: the hero goes to the CENTER of the touched cell.\nTap the 2nd hero (placed off-center on purpose): it re-centers itself.',
                 32, OR, z=60, prefixe=P, cheminPolice=None),
           etiquette('l1', 560, 'Column touched'), valeur('v1', 560), etiquette('l2', 650, 'Row touched'), valeur('v2', 650),
           etiquette('l3', 780, 'Hero column'), valeur('v3', 780), etiquette('l4', 870, 'Hero row'), valeur('v4', 870)]

L = Logique()
def vert(id, cle, parametres=None, cible=None):
    n = {'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': id, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': cle,
         'parametres': {cle + '.' + k: str(v) for k, v in (parametres or {}).items()}}
    if cible: n['cibleNom'] = cible
    L.noeuds.append(n)
def brancher(noeud, reglage, vert_id):
    L.noeud(noeud)['parametres'][reglage] = '@valeur:' + vert_id

e = L.evenement('tap_ground', 'NoeudEventClicObjet', cible='terrain')
L.chaine(e, [('place', 'placer_case', {'colonne': 0, 'ligne': 0}, 'hero'),
             ('show_col', 'modifier_texte', {'valeur': ''}, 'v1'), ('show_row', 'modifier_texte', {'valeur': ''}, 'v2')])
for vid, cle, noeud, champ in (('g_col_a', 'valeur_colonne_touchee', 'place', 'placer_case.colonne'), ('g_row_a', 'valeur_ligne_touchee', 'place', 'placer_case.ligne'),
                               ('g_col_b', 'valeur_colonne_touchee', 'show_col', 'modifier_texte.valeur'), ('g_row_b', 'valeur_ligne_touchee', 'show_row', 'modifier_texte.valeur')):
    vert(vid, cle); brancher(noeud, champ, vid)
e = L.evenement('tap_hero2', 'NoeudEventClicObjet', cible='hero2')
L.action(e, 'recenter', 'centrer_case', None, 'hero2')
e = L.evenement('every_frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.chaine(e, [('hero_col', 'modifier_texte', {'valeur': ''}, 'v3'), ('hero_row', 'modifier_texte', {'valeur': ''}, 'v4')])
vert('g_hc', 'valeur_colonne_objet', cible='hero'); brancher('hero_col', 'modifier_texte.valeur', 'g_hc')
vert('g_hr', 'valeur_ligne_objet', cible='hero'); brancher('hero_row', 'modifier_texte.valeur', 'g_hr')
logique = L.ranger().json()

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test grille', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'grille-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/grille-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
