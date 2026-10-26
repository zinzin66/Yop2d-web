#!/usr/bin/env python3
"""Projet de TEST de « Choisir une cible », des statistiques personnalisées et du calcul de dégâts libre :
tests/cibles-test.zip, à importer dans une version de test du moteur qui les contient (branche claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_cibles.py <clone de zinzin66/yop2d-moteur>
Le monstre (au milieu) a une portée de 3 cases et la statistique perso « munitions = 3 ». Trois héros (tag « heros ») sont à
des distances différentes : h1 (2 cases, vie 10, armure 0), h2 (3 cases, vie 4, armure 5), h3 (6 cases : HORS portée, vie 20).
Boutons : « Closest in range » (h1 saute), « Weakest in range » (h2 saute : vie 4), « Highest armor » (stat perso : h2),
« Attack the closest » (dégâts = attaquant.attaque * 2 - cible.armure : h1 perd 6 vie), « Anyone, no limit » (h3 est
atteint seulement avec portée 0 = sans limite : le plus proche reste h1 ; essaie « Weakest, no limit » : h2).
Le texte du haut montre la vie des trois héros et les munitions du monstre."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'cibles_test/'
CASE = 80
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')
X0, Y0 = 80, 160
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F'))]
for c in range(12):
    for l in range(8):
        objets.append(objet('case_%d_%d' % (c, l), X0 + c * CASE, Y0 + l * CASE, largeur=CASE - 2, hauteur=CASE - 2, z=-50, prefixe=P,
                            afficherFondColore=True, couleur=argb('#1F4D2E' if (c + l) % 2 == 0 else '#245A35')))
def unite(nom, c, l, couleur, tag):
    return objet(nom, X0 + c * CASE + 8, Y0 + l * CASE + 8, largeur=CASE - 18, hauteur=CASE - 18, z=50, prefixe=P, afficherFondColore=True, couleur=argb(couleur), tag=tag)
objets += [unite('monstre', 4, 3, '#E0524A', 'monstres'), unite('h1', 4, 5, '#7FB4FF', 'heros'), unite('h2', 7, 3, '#7FE3FF', 'heros'),
           unite('h3', 10, 7, '#C79BFF', 'heros')]
for nom in ('monstre', 'h1', 'h2', 'h3'):
    o = next(x for x in objets if x['nom'] == nom)
    objets.append(texte('n_' + nom, o['x'] - 20, o['y'] + 56, 100, 30, nom, 22, BLANC, z=60, prefixe=P, cheminPolice=None, alignementTexte='CENTRE'))
objets.append(texte('info', 40, 20, 1840, 100, '-', 34, OR, z=60, prefixe=P, cheminPolice=None))
objets.append(texte('msg', 40, 840, 1000, 80, 'Tap a button on the right', 34, BLANC, z=60, prefixe=P, cheminPolice=None))

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [('f_m', 'definir_fiche', {'vie': 12, 'attaque': 4, 'defense': 1, 'mouvement': 3, 'portee': 3, 'autres': 'munitions = 3'}, 'monstre'),
             ('f_1', 'definir_fiche', {'vie': 10, 'attaque': 3, 'defense': 1, 'mouvement': 4, 'portee': 1, 'autres': 'armure = 0'}, 'h1'),
             ('f_2', 'definir_fiche', {'vie': 4, 'attaque': 3, 'defense': 1, 'mouvement': 4, 'portee': 1, 'autres': 'armure = 5'}, 'h2'),
             ('f_3', 'definir_fiche', {'vie': 20, 'attaque': 3, 'defense': 1, 'mouvement': 4, 'portee': 1, 'autres': 'armure = 1'}, 'h3')])
e = L.evenement('frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'show', 'modifier_propriete', {'propriete': 'texte', 'valeur': '="h1 vie " + h1.vie + "   h2 vie " + h2.vie + "   h3 vie " + h3.vie + "   monstre munitions " + monstre.munitions'}, 'info')

BOUTONS = [('Closest in range', {'regle': 'cb_proche', 'portee': '=monstre.portee'}, False),
           ('Weakest in range (least health)', {'regle': 'cb_moins_vie', 'portee': '=monstre.portee'}, False),
           ('Highest armor in range (custom stat)', {'regle': 'cb_stat_haute', 'stat': 'armure', 'portee': '=monstre.portee'}, False),
           ('Weakest, no range limit', {'regle': 'cb_moins_vie', 'portee': 0}, False),
           ('Closest, range 1 (nobody)', {'regle': 'cb_proche', 'portee': 1}, False),
           ('Attack the closest: damage = attacker.attaque x 2 - target.armure', {'regle': 'cb_proche', 'portee': '=monstre.portee'}, True)]
for i, (nom, reglages, attaque) in enumerate(BOUTONS):
    bx, by = 1100, 160 + i * 100
    objets.append(objet('b%d' % i, bx, by, largeur=760, hauteur=84, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#2B3A55')))
    objets.append(texte('t%d' % i, bx + 16, by + 14, 730, 60, nom, 26, BLANC, z=6, prefixe=P, cheminPolice=None))
    e = L.evenement('tap%d' % i, 'NoeudEventClicObjet', cible='b%d' % i)
    r = {'tag': 'heros'}; r.update(reglages)
    c = L.action(e, 'ch%d' % i, 'choisir_cible', r, 'monstre')
    if attaque:
        a = L.action((c[0], 'port_trouvee', 0), 'att%d' % i, 'attaquer', {'puissance': 100, 'terrain': 'o_non', 'minimum': 'o_oui', 'detruire': 'o_oui',
                                                                        'formule_degats': 'attaquant.attaque * 2 - cible.armure'}, 'monstre')
        L.noeud('att%d' % i)['cibleNomB'] = '__OBJET_IMPLIQUE__'
        L.action(a, 'okm%d' % i, 'modifier_propriete', {'propriete': 'texte', 'valeur': 'Attacked!'}, 'msg')
    else:
        s = L.action((c[0], 'port_trouvee', 0), 'sa%d' % i, 'sautiller', {'duree': 500, 'intensite': 20, 'infini': 'false'}, '__OBJET_IMPLIQUE__')
        L.action(s, 'ok%d' % i, 'modifier_propriete', {'propriete': 'texte', 'valeur': 'Target found'}, 'msg')
    L.action((c[0], 'port_aucune', 1), 'no%d' % i, 'modifier_propriete', {'propriete': 'texte', 'valeur': 'No target'}, 'msg', decalage_y=200)
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Test', objets, P)], {'Test': logique}, [])
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test cibles', 'dateCreation': '2026-10-26 12:00:00', 'dateModif': '2026-10-26 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'cibles-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/cibles-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
