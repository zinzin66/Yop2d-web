#!/usr/bin/env python3
"""Projet de TEST du PION DE PLATEAU (grille, étape B) : tests/pion-test.zip (moteur : à partir du commit 922eeea qui ajoute
« Déplacer le pion d'une case » et « Aller à la case (chemin) »).
Usage : python3 outils/creer_test_pion.py <clone de zinzin66/yop2d-moteur>
Test : 4 boutons ▲ ▼ ◀ ▶ = le pion avance d'UNE case, toujours bien centré ; contre un mur, le monstre (tag ennemi) ou le bord de
la carte : « Blocked! ». Toucher une case du sol : le pion y va en contournant les murs et le monstre."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *
P = 'pion_test/'
NJ = 'assets_ludexa/Images/Ninja/'
CASE, GX, GY = 80, 60, 140
CARTE = ["..............", "..B...s.......", "..B...s.......", "....##........", ".s..##........",
         ".s.......B....", "..B...##......", "....s.##..s...", "..B........B..", ".............."]
BLANC, OR, VERT = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0')
def coin(c, l): return GX + c * CASE, GY + l * CASE
hx, hy = coin(1, 3)
mx, my = coin(6, 4)
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=NJ + 'Tuiles/tileset_ninja.png'),
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True),
          objet('pion', hx, hy, NJ + 'Personnages/ninja6_bas_1.png', CASE, CASE, z=50, prefixe=P),
          objet('monstre', mx, my, NJ + 'Monstres/monstre9_bas_1.png', CASE, CASE, z=50, prefixe=P, tag='ennemi'),
          texte('info', 1240, 150, 640, 300, 'PIECE TEST\nArrows: one cell at a time.\nWalls, the monster and the edge block.\nTap the ground: walks there.', 32, OR, z=60, prefixe=P, cheminPolice=None),
          texte('msg', 1240, 470, 640, 80, '-', 48, VERT, z=60, prefixe=P, cheminPolice=None)]
def bouton(nom, x, y, symbole):
    b = objet(nom, x, y, largeur=130, hauteur=130, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#2B6CB0'), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 30, 130, 80, symbole, 56, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('b_haut', 1500, 600, '^') + bouton('b_bas', 1500, 880, 'v') + bouton('b_gauche', 1360, 740, '<') + bouton('b_droite', 1640, 740, '>')
L = Logique()
for nom, d in (('haut', 'pd_haut'), ('bas', 'pd_bas'), ('gauche', 'pd_gauche'), ('droite', 'pd_droite')):
    e = L.evenement('tap_' + nom, 'NoeudEventClicObjet', cible='b_' + nom)
    n = L.action(e, 'pas_' + nom, 'pion_une_case', {'direction': d, 'vitesse': 8, 'bloquants': 'ennemi'}, 'pion')
    L.chaine(('pas_' + nom, 'port_arrive', 0), [('ok_' + nom, 'modifier_texte', {'valeur': 'OK'}, 'msg')])
    L.chaine(('pas_' + nom, 'port_bloque', 1), [('no_' + nom, 'modifier_texte', {'valeur': 'Blocked!'}, 'msg')])
e = L.evenement('tap_ground', 'NoeudEventClicObjet', cible='terrain')
L.action(e, 'go', 'chemin_vers_case', {'colonne': '=colonne(doigt.x + camera.x)', 'ligne': '=ligne(doigt.y + camera.y)', 'vitesse': 8, 'diagonales': 'false', 'bloquants': 'ennemi'}, 'pion')
L.chaine(('go', 'port_arrive', 1), [('go_ok', 'modifier_texte', {'valeur': 'Arrived'}, 'msg')])
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test pion', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'pion-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/pion-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
