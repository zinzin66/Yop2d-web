#!/usr/bin/env python3
"""Projet de TEST des TERRAINS (grille, étape A) : tests/terrains-test.zip (moteur : commit 45192ae de claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_terrains.py <clone de zinzin66/yop2d-moteur>
Le projet contient un fichier terrains.json (la liste unique de terrains du projet) : herbe (1 pas), « forêt » = buisson (2 pas, défense +1),
« montagne » = rocher (BLOQUE), « marais » = sable (3 pas) ; le jeu de tuiles ninja est déjà marqué (ouvre l'éditeur de tuiles > « Terrains »).
Test : toucher le héros = cases accessibles (4 pas, chiffres = coût réel) ; toucher une case = le nom du terrain, son coût et sa défense
sont écrits (nœuds verts) ; les rochers (montagne) bloquent comme des murs (les tuiles ne sont PAS marquées solides)."""
import os, sys, json, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *
P = 'terrains_test/'
NJ = 'assets_ludexa/Images/Ninja/'
TILESET = NJ + 'Tuiles/tileset_ninja.png'
CASE, GX, GY = 80, 60, 140
CARTE = ["..............", "..#.#...B.....", "..#.#...B.....", "..#.....B.ss..", "....##..B.ss..",
         "....##..B.....", "..#.....B.....", "..#.#.......B.", "....#.......B.", ".............."]
BLANC, OR, VERT = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0')
carte = decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=TILESET)
carte['tuilesSolides'] = [False, False, False, False]   # plus de murs « solides » : ce sont les terrains qui bloquent
terrains = {'terrains': [
    {'id': 't1', 'nom': 'Grass', 'couleur': argb('#6FBF73'), 'cout': 1, 'bloque': False, 'defense': 0, 'proprietes': {}},
    {'id': 't2', 'nom': 'Forest', 'couleur': argb('#2E7D32'), 'cout': 2, 'bloque': False, 'defense': 1, 'proprietes': {'cache': 'oui'}},
    {'id': 't3', 'nom': 'Mountain', 'couleur': argb('#9AA3AE'), 'cout': 1, 'bloque': True, 'defense': 2, 'proprietes': {}},
    {'id': 't4', 'nom': 'Marsh', 'couleur': argb('#E0C068'), 'cout': 3, 'bloque': False, 'defense': 0, 'proprietes': {}}],
    'tuiles': {TILESET: ['t1', 't2', 't3', 't4']}}
def coin(c, l): return GX + c * CASE, GY + l * CASE
hx, hy = coin(1, 5)
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')), carte,
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True),
          objet('hero', hx, hy, NJ + 'Personnages/ninja6_bas_1.png', CASE, CASE, z=50, prefixe=P, estZoneDeClic=True)]
def etiquette(nom, y, t): return texte(nom, 1240, y, 400, 60, t, 34, BLANC, z=60, prefixe=P, cheminPolice=None, alignementTexte='DROITE')
def valeur(nom, y): return texte(nom, 1660, y - 6, 240, 70, '-', 46, VERT, z=60, prefixe=P, cheminPolice=None)
objets += [texte('info', 1240, 150, 640, 330, 'TERRAINS TEST\nTap the hero: reachable cells (4 steps),\nnumbers = real cost.\nTap any cell: its terrain.\nMountains (rocks) block.', 32, OR, z=60, prefixe=P, cheminPolice=None),
           etiquette('l1', 560, 'Terrain'), valeur('v1', 560), etiquette('l2', 650, 'Cost'), valeur('v2', 650), etiquette('l3', 740, 'Hero terrain'), valeur('v3', 740)]
L = Logique()
def vert(id, cle, cible=None):
    n = {'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': id, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': cle, 'parametres': {}}
    if cible: n['cibleNom'] = cible
    L.noeuds.append(n)
def brancher(noeud, reglage, vert_id): L.noeud(noeud)['parametres'][reglage] = '@valeur:' + vert_id
e = L.evenement('tap_hero', 'NoeudEventClicObjet', cible='hero')
L.action(e, 'show', 'montrer_cases', {'mode': 'zc_deplacement', 'pas': 4, 'couleur': '#4CC9F0', 'opacite': 40, 'contour': 'o_oui', 'chiffres': 'o_oui', 'murs': 'o_oui'}, 'hero')
e = L.evenement('tap_ground', 'NoeudEventClicObjet', cible='terrain')
L.chaine(e, [('t1', 'modifier_texte', {'valeur': ''}, 'v1'), ('t2', 'modifier_texte', {'valeur': ''}, 'v2'), ('t3', 'modifier_texte', {'valeur': ''}, 'v3')])
vert('g_terrain', 'valeur_terrain_touche'); brancher('t1', 'modifier_texte.valeur', 'g_terrain')
vert('g_cout', 'valeur_cout_terrain_touche'); brancher('t2', 'modifier_texte.valeur', 'g_cout')
vert('g_hero', 'valeur_terrain_objet', 'hero'); brancher('t3', 'modifier_texte.valeur', 'g_hero')
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test terrains', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    with open(os.path.join(p, 'terrains.json'), 'w') as f: json.dump(terrains, f)
    sortie = os.path.join(SITE_RACINE, 'tests', 'terrains-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/terrains-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
