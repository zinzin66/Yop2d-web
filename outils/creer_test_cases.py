#!/usr/bin/env python3
"""Projet de TEST des « cases accessibles » (grille, étape 3) : tests/cases-test.zip, à importer dans une version de test du
moteur qui contient « Montrer les cases accessibles », « Cacher les cases », « Si la case est accessible » et le nœud vert
« Pas pour aller sur la case touchée » (moteur : branche claude/discord-yop2d-config-ox8qgh, à partir du commit 833e02c).
Usage : python3 outils/creer_test_cases.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test : toucher le héros = ses cases accessibles (4 pas) en bleu, murs (briques) et monstre qui bloquent, forêt (sapins)
= 2 pas, le nombre de pas est écrit sur chaque case. Toucher une case bleue : il y va ; toucher ailleurs : « Too far! ».
Bouton « Attack range » : zone rouge de portée 2 (passe les murs) ; bouton « Hide » : tout effacer."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'cases_test/'
NJ = 'assets_ludexa/Images/Ninja/'
CASE, GX, GY = 80, 60, 140
CARTE = ["..............", "..B...s.......", "..B...s.......", "....##........", ".s..##........",
         ".s.......B....", "..B...##......", "....s.##..s...", "..B........B..", ".............."]
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')
def coin(c, l): return GX + c * CASE, GY + l * CASE
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=NJ + 'Tuiles/tileset_ninja.png'),
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True)]
for i, (c, l) in enumerate([(5, 2), (6, 2), (5, 3), (3, 6), (4, 6), (3, 7)]):   # la forêt : sapins avec le tag « foret »
    x, y = coin(c, l)
    objets.append(objet('sapin%d' % i, x, y, NJ + 'Decor/sapin.png', CASE, CASE, z=20, prefixe=P, tag='foret'))
hx, hy = coin(3, 4)
mx, my = coin(8, 3)
objets += [objet('hero', hx, hy, NJ + 'Personnages/ninja6_bas_1.png', CASE, CASE, z=50, prefixe=P, estZoneDeClic=True),
           objet('monstre', mx, my, NJ + 'Monstres/monstre9_bas_1.png', CASE, CASE, z=50, prefixe=P, tag='ennemi')]
objets += [texte('info', 1240, 150, 640, 330, 'CELLS TEST\nTap the hero: reachable cells (4 steps).\nWalls and the monster block, trees cost 2.\nTap a blue cell to go there.',
                 32, OR, z=60, prefixe=P, cheminPolice=None),
           texte('msg', 1240, 520, 640, 80, '-', 44, VERT, z=60, prefixe=P, cheminPolice=None),
           texte('cout_l', 1240, 620, 400, 60, 'Steps to touched cell', 32, BLANC, z=60, prefixe=P, cheminPolice=None, alignementTexte='DROITE'),
           texte('cout', 1670, 612, 200, 70, '-', 52, VERT, z=60, prefixe=P, cheminPolice=None)]
def bouton(nom, y, libelle, couleur):
    b = objet(nom, 1300, y, largeur=520, hauteur=110, z=60, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 22, 520, 70, libelle, 44, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_att', 740, 'Attack range', '#8A2C2C') + bouton('btn_hide', 880, 'Hide', '#555F6B')

L = Logique()
def vert(id, cle):
    L.noeuds.append({'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': id, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': cle, 'parametres': {}})
def brancher(noeud, reglage, vert_id):
    L.noeud(noeud)['parametres'][reglage] = '@valeur:' + vert_id
e = L.evenement('tap_hero', 'NoeudEventClicObjet', cible='hero')
L.chaine(e, [('show', 'montrer_cases', {'mode': 'zc_deplacement', 'pas': 4, 'couleur': '#4CC9F0', 'opacite': 40, 'contour': 'o_oui', 'chiffres': 'o_oui',
                                         'murs': 'o_oui', 'bloquants': 'ennemi', 'terrains': 'foret=2'}, 'hero'),
             ('m1', 'modifier_texte', {'valeur': 'Pick a blue cell'}, 'msg')])
e = L.evenement('tap_ground', 'NoeudEventClicObjet', cible='terrain')
t = L.chaine(e, [('cout_show', 'modifier_texte', {'valeur': ''}, 'cout'), ('ok', 'si_case_accessible', {'colonne': '=colonne(doigt.x + camera.x)', 'ligne': '=ligne(doigt.y + camera.y)'})])
vert('g_cout', 'valeur_cout_case'); brancher('cout_show', 'modifier_texte.valeur', 'g_cout')
L.chaine(VRAI(t), [('go', 'placer_case', {'colonne': 0, 'ligne': 0}, 'hero'), ('hide1', 'cacher_cases', {}), ('m2', 'modifier_texte', {'valeur': 'Moved!'}, 'msg')])
vert('g_col', 'valeur_colonne_touchee'); vert('g_row', 'valeur_ligne_touchee')
brancher('go', 'placer_case.colonne', 'g_col'); brancher('go', 'placer_case.ligne', 'g_row')
L.chaine(FAUX(t), [('m3', 'modifier_texte', {'valeur': 'Too far!'}, 'msg')])
e = L.evenement('tap_att', 'NoeudEventClicObjet', cible='btn_att')
L.chaine(e, [('att', 'montrer_cases', {'mode': 'zc_attaque', 'pas': 2, 'couleur': '#FF4040', 'opacite': 45, 'contour': 'o_oui', 'chiffres': 'o_non', 'zone': 'attaque'}, 'hero'),
             ('m4', 'modifier_texte', {'valeur': 'Attack range 2 (passes walls)'}, 'msg')])
e = L.evenement('tap_hide', 'NoeudEventClicObjet', cible='btn_hide')
L.chaine(e, [('hide2', 'cacher_cases', {}), ('m5', 'modifier_texte', {'valeur': '-'}, 'msg')])
logique = L.ranger().json()

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test cases', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'cases-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/cases-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
