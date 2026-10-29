#!/usr/bin/env python3
"""Projet de TEST des PORTÉES LIBRES (« Montrer les cases accessibles » : formes, portée minimale, saut, positions libres) :
tests/portees-test.zip, à importer dans une version de test du moteur qui les contient (branche claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_portees.py <clone de zinzin66/yop2d-moteur>
Le héros est au milieu d'une grille de 12 x 10 cases ; 10 boutons à droite montrent chacun une zone différente :
losange (comme avant), carré, croix, diagonales, 8 directions, anneau (portée minimale 2), cavalier, mes positions,
saut du cavalier (4 pierres bloquent la case d'arrivée), et losange SANS la case du héros."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'portees_test/'
CASE = 80
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F'))]
for c in range(12):
    for l in range(10):
        objets.append(objet('case_%d_%d' % (c, l), c * CASE + 80, l * CASE + 160, largeur=CASE - 2, hauteur=CASE - 2, z=-50, prefixe=P,
                            afficherFondColore=True, couleur=argb('#1F4D2E' if (c + l) % 2 == 0 else '#245A35')))
HX, HY = 5, 5
objets.append(objet('hero', HX * CASE + 80 + 8, HY * CASE + 160 + 8, largeur=CASE - 18, hauteur=CASE - 18, z=50, prefixe=P, afficherFondColore=True, couleur=argb('#FFD166')))
for i, (c, l) in enumerate([(7, 4), (4, 7), (3, 4), (6, 6)]):   # les pierres du test « saut »
    objets.append(objet('pierre%d' % i, c * CASE + 80 + 8, l * CASE + 160 + 8, largeur=CASE - 18, hauteur=CASE - 18, z=40, prefixe=P,
                        afficherFondColore=True, couleur=argb('#8A8F98'), tag='mur'))
objets.append(texte('info', 40, 30, 1000, 100, 'Pick a shape on the right: the cells around the hero show its range.', 36, OR, z=60, prefixe=P, cheminPolice=None))

FORMES = [('Diamond', {'mode': 'zc_attaque', 'forme': 'fm_losange', 'pas': 3}),
          ('Square', {'mode': 'zc_attaque', 'forme': 'fm_carre', 'pas': 2}),
          ('Cross', {'mode': 'zc_attaque', 'forme': 'fm_croix', 'pas': 4}),
          ('Diagonals', {'mode': 'zc_attaque', 'forme': 'fm_diagonales', 'pas': 3}),
          ('8 directions', {'mode': 'zc_attaque', 'forme': 'fm_huit', 'pas': 3}),
          ('Ring (min 2)', {'mode': 'zc_attaque', 'forme': 'fm_losange', 'pas': 4, 'portee_min': 2}),
          ('Knight', {'mode': 'zc_attaque', 'forme': 'fm_cavalier'}),
          ('My positions', {'mode': 'zc_attaque', 'forme': 'fm_perso', 'positions': '2,0 ; -2,0 ; 0,3 ; 1,-1'}),
          ('Knight jump (stones block)', {'mode': 'zc_saut', 'forme': 'fm_cavalier', 'bloquants': 'mur'}),
          ('Diamond without hero cell', {'mode': 'zc_attaque', 'forme': 'fm_losange', 'pas': 3, 'sans_depart': 'o_oui'})]
L = Logique()
for i, (nom, reglages) in enumerate(FORMES):
    bx, by = 1100, 160 + i * 90
    objets.append(objet('b%d' % i, bx, by, largeur=720, hauteur=76, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#2B3A55')))
    objets.append(texte('t%d' % i, bx + 20, by + 12, 680, 52, nom, 34, BLANC, z=6, prefixe=P, cheminPolice=None))
    e = L.evenement('tap%d' % i, 'NoeudEventClicObjet', cible='b%d' % i)
    r = {'couleur': '#FF8A5C' if reglages['mode'] == 'zc_attaque' else '#7FE3FF', 'opacite': 45, 'contour': 'o_oui', 'chiffres': 'o_non', 'murs': 'o_oui'}
    r.update(reglages)
    L.chaine(e, [('cache%d' % i, 'cacher_cases', {}), ('montre%d' % i, 'montrer_cases', r, 'hero')])
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Test', objets, P)], {'Test': logique}, [])
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test portees', 'dateCreation': '2026-10-26 12:00:00', 'dateModif': '2026-10-26 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'portees-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/portees-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
