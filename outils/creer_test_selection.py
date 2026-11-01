#!/usr/bin/env python3
"""Projet de TEST « sélection d'objet + chemin dans la zone » : tests/selection-test.zip (à importer dans une version de test du
moteur qui contient « Sélectionner l'objet » et le réglage « Rester dans la zone montrée » : build 1225 ou plus).
Usage : python3 outils/creer_test_selection.py <clone de zinzin66/yop2d-moteur>
3 carrés (tag « unite »). Toucher un carré = il est sélectionné (plus gros) et ses cases accessibles (3 pas) apparaissent ; toucher
une case bleue = SEUL ce carré y va, en restant dans la zone ; retoucher le carré sélectionné = on le désélectionne. Un seul événement
« Au clic sur # unite » sert pour les trois carrés (l'objet touché = l'objet impliqué) et les nœuds visent « L'objet sélectionné »."""
import os, sys, tempfile, zipfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'selection_test/'
BLANC, OR, VERT = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0')
IMPLIQUE, SELECTIONNE, TAG = '__OBJET_IMPLIQUE__', '__OBJET_SELECTIONNE__', 'tag:unite'
CASE = 80   # sans décor en tuiles, la grille = cases de 80 px depuis (0, 0)

objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#10151F')),
          objet('terrain', 0, 0, largeur=1200, hauteur=880, z=1, prefixe=P, afficherFondColore=True, couleur=argb('#1D2B3A'), estZoneDeClic=True)]
for nom, c, l, couleur in [('unite1', 2, 2, '#E74C3C'), ('unite2', 7, 4, '#3498DB'), ('unite3', 4, 8, '#2ECC71')]:
    objets.append(objet(nom, c * CASE + 5, l * CASE + 5, largeur=70, hauteur=70, z=50, prefixe=P, tag='unite',
                        afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True))
objets.append(texte('info', 1240, 40, 640, 700,
                    'SELECTION + ZONE TEST\n\n1. Tap a square: it is selected (bigger) and the cells it can reach (3 steps) appear.\n\n'
                    '2. Tap a blue cell: ONLY that square walks there, always inside the blue zone.\n\n'
                    '3. Tap the selected square again: it is deselected.\n\nOne single event "On click on # unite" serves the 3 squares.',
                    32, OR, z=60, prefixe=P, cheminPolice=None))

L = Logique()
ACC = {}   # colonne / ligne vides = la case touchée (aucune formule)
ZONE = {'mode': 'zc_deplacement', 'pas': 3, 'couleur': '#4CC9F0', 'opacite': 40, 'contour': 'o_oui', 'chiffres': 'o_oui',
        'murs': 'o_oui', 'bloquants': '', 'terrains': '', 'zone': ''}

# 1. Toucher un carré : le sélectionner (ou le désélectionner si c'est déjà lui)
e = L.evenement('ev_unite', 'NoeudEventClicObjet', cible=TAG)
t = L.action(e, 'u_est', 'si_est_selectionne', {}, IMPLIQUE)
L.chaine(VRAI(t), [('u_desel', 'deselectionner_objet', {}), ('u_cache', 'cacher_cases', {'zone': ''}),
                   ('u_reset', 'modifier_taille', {'x': 1, 'y': 1}, TAG)])
L.chaine(FAUX(t), [('u_cache2', 'cacher_cases', {'zone': ''}), ('u_reset2', 'modifier_taille', {'x': 1, 'y': 1}, TAG),
                   ('u_sel', 'selectionner_objet', {}, IMPLIQUE), ('u_big', 'modifier_taille', {'x': 1.25, 'y': 1.25}, SELECTIONNE),
                   ('u_zone', 'montrer_cases', ZONE, SELECTIONNE)])

# 2. Toucher le terrain : si un carré est sélectionné et que la case est bleue, SEUL celui-là y va (dans la zone)
e = L.evenement('ev_sol', 'NoeudEventClicObjet', cible='terrain')
t = L.action(e, 'g_sel', 'si_objet_selectionne', {})
a = L.action(VRAI(t), 'g_acc', 'si_case_accessible', dict(ACC, zone=''))
L.action(VRAI(a), 'g_go', 'chemin_vers_case', dict(ACC, vitesse=8, diagonales='false', bloquants='', limite_zone='o_oui', nom_zone_limite=''), SELECTIONNE)
L.chaine(('g_go', 'port_arrive', 1), [('g_cache', 'cacher_cases', {'zone': ''}), ('g_reset', 'modifier_taille', {'x': 1, 'y': 1}, TAG),
                                      ('g_desel', 'deselectionner_objet', {})])

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    sc = scene('Test', objets, P)
    ecrire_projet(p, [sc], {'Test': L.json()}, [], largeur=1920, hauteur=1080)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test selection', 'dateCreation': '2026-11-01 12:00:00', 'dateModif': '2026-11-01 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'selection-test.zip')
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                if f == 'Licence_Kenney.txt': continue
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
print('%d nœuds -> %s (%d Ko)' % (len(L.noeuds), sortie, os.path.getsize(sortie) // 1024))
