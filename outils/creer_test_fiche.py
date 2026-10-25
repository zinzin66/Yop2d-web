#!/usr/bin/env python3
"""Projet de TEST de la FICHE D'UNITÉ et de « Attaquer » (grille, étape C) : tests/fiche-test.zip.
Usage : python3 outils/creer_test_fiche.py <clone de zinzin66/yop2d-moteur>
Test : un héros (vie 20, attaque 5, défense 1) et deux monstres : Orc (vie 12, attaque 4, défense 2) et Rat (vie 6, attaque 2, défense 0).
Toucher un monstre = le héros l'attaque : dégâts = attaque - défense (Orc : 3, Rat : 5, jamais moins de 1) ; à 0 il est détruit.
Bouton « Orc hits hero » : l'orc attaque le héros (4 - 1 = 3). Les textes montrent la vie de chacun (=orc.vie…)."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *
P = 'fiche_test/'
NJ = 'assets_ludexa/Images/Ninja/'
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          objet('hero', 250, 450, NJ + 'Personnages/ninja6_bas_1.png', 200, 200, z=50, prefixe=P),
          objet('orc', 750, 300, NJ + 'Monstres/monstre9_bas_1.png', 200, 200, z=50, prefixe=P, estZoneDeClic=True),
          objet('rat', 750, 620, NJ + 'Monstres/monstre3_bas_1.png', 200, 200, z=50, prefixe=P, estZoneDeClic=True),
          texte('hp_hero', 150, 380, 400, 60, '-', 36, VERT, z=60, prefixe=P, cheminPolice=None),
          texte('hp_orc', 650, 230, 400, 60, '-', 36, ROUGE, z=60, prefixe=P, cheminPolice=None),
          texte('hp_rat', 650, 550, 400, 60, '-', 36, ROUGE, z=60, prefixe=P, cheminPolice=None),
          texte('msg', 150, 880, 1000, 80, '-', 44, OR, z=60, prefixe=P, cheminPolice=None),
          texte('info', 1300, 120, 560, 360, 'UNIT SHEET TEST\nTap a monster: the hero attacks.\ndamage = attack - defense (min 1)\nOrc: HP 12 def 2 / Rat: HP 6 def 0', 30, OR, z=60, prefixe=P, cheminPolice=None)]
b = objet('btn_orc', 1340, 560, largeur=500, hauteur=110, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#8A2C2C'), estZoneDeClic=True)
b2 = objet('btn_restart', 1340, 700, largeur=500, hauteur=110, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#555F6B'), estZoneDeClic=True)
objets += [b, texte('btn_orc_t', 0, 22, 500, 70, 'Orc hits hero', 42, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None),
           b2, texte('btn_restart_t', 0, 22, 500, 70, 'Restart', 42, BLANC, z=61, prefixe=P, parentId=b2['id'], alignementTexte='CENTRE', cheminPolice=None)]
L = Logique()
def aff(prefixe):
    return [(prefixe + 'a', 'modifier_texte', {'valeur': '="Hero HP: " + hero.vie + " / " + hero.vie_max'}, 'hp_hero'),
            (prefixe + 'b', 'modifier_texte', {'valeur': '="Orc HP: " + orc.vie'}, 'hp_orc'),
            (prefixe + 'c', 'modifier_texte', {'valeur': '="Rat HP: " + rat.vie'}, 'hp_rat')]
e = L.evenement('start', 'NoeudEventStart', sortie='Suivant')
L.chaine(e, [('f1', 'definir_fiche', {'vie': 20, 'attaque': 5, 'defense': 1, 'mouvement': 4, 'portee': 1}, 'hero'),
             ('f2', 'definir_fiche', {'vie': 12, 'attaque': 4, 'defense': 2, 'mouvement': 3, 'portee': 1}, 'orc'),
             ('f3', 'definir_fiche', {'vie': 6, 'attaque': 2, 'defense': 0, 'mouvement': 5, 'portee': 1}, 'rat')] + aff('s'))
for nom, hp in (('orc', 'hp_orc'), ('rat', 'hp_rat')):
    e = L.evenement('tap_' + nom, 'NoeudEventClicObjet', cible=nom)
    a = L.action(e, 'hit_' + nom, 'attaquer', {'puissance': 100, 'terrain': 'o_oui', 'minimum': 'o_oui', 'detruire': 'o_oui'}, 'hero')
    L.noeud('hit_' + nom)['cibleNomB'] = nom
    L.chaine(('hit_' + nom, 'port_vivant', 0), [('v_' + nom, 'modifier_texte', {'valeur': 'Hit the ' + nom + '!'}, 'msg')] + aff('v' + nom))
    L.chaine(('hit_' + nom, 'port_detruit', 1), [('d_' + nom, 'modifier_texte', {'valeur': nom + ' defeated!'}, 'msg'), ('dh_' + nom, 'modifier_texte', {'valeur': nom + ' HP: 0'}, hp)])
e = L.evenement('tap_btn_orc', 'NoeudEventClicObjet', cible='btn_orc')
L.action(e, 'orc_hit', 'attaquer', {'puissance': 100, 'terrain': 'o_oui', 'minimum': 'o_oui', 'detruire': 'o_non'}, 'orc')
L.noeud('orc_hit')['cibleNomB'] = 'hero'
L.chaine(('orc_hit', 'port_vivant', 0), [('oh1', 'modifier_texte', {'valeur': 'The orc hits the hero!'}, 'msg')] + aff('oh'))
L.chaine(('orc_hit', 'port_detruit', 1), [('oh2', 'modifier_texte', {'valeur': 'Hero is out of health'}, 'msg')] + aff('ok'))
e = L.evenement('tap_restart', 'NoeudEventClicObjet', cible='btn_restart')
L.action(e, 'rs', 'recommencer_scene')
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test fiche unite', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'fiche-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/fiche-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
