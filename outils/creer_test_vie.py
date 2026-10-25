#!/usr/bin/env python3
"""Projet de TEST « vie et dégâts » (grille, étape 4) : tests/vie-test.zip (moteur : commit f4a0273 de claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_vie.py <clone de zinzin66/yop2d-moteur>
Test : un monstre a 10 points de vie (donnés « Au démarrage »). Toucher le monstre = 3 dégâts, son texte « HP » baisse ;
à 0 il est détruit et « Defeated! » s'affiche. Bouton « Heal hero » : le héros (6 de vie sur 10) regagne 2 points, jamais plus de 10 ;
bouton « Hit hero » : 4 dégâts au héros. Bouton « Restart » : recommence."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *
P = 'vie_test/'
NJ = 'assets_ludexa/Images/Ninja/'
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          objet('hero', 300, 400, NJ + 'Personnages/ninja6_bas_1.png', 200, 200, z=50, prefixe=P, estZoneDeClic=True),
          objet('monstre', 900, 400, NJ + 'Monstres/monstre9_bas_1.png', 200, 200, z=50, prefixe=P, estZoneDeClic=True),
          texte('hp_hero', 220, 330, 360, 60, '-', 40, VERT, z=60, prefixe=P, cheminPolice=None),
          texte('hp_monstre', 820, 330, 360, 60, '-', 40, ROUGE, z=60, prefixe=P, cheminPolice=None),
          texte('msg', 300, 700, 900, 80, '-', 48, OR, z=60, prefixe=P, cheminPolice=None),
          texte('info', 1300, 120, 560, 330, 'LIFE TEST\nTap the monster: 3 damage.\nHeal hero: +2 (max 10).\nHit hero: 4 damage.', 32, OR, z=60, prefixe=P, cheminPolice=None)]
def bouton(nom, y, libelle, couleur):
    b = objet(nom, 1340, y, largeur=480, hauteur=110, z=60, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 22, 480, 70, libelle, 44, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_heal', 520, 'Heal hero', '#2E7D32') + bouton('btn_hit', 660, 'Hit hero', '#8A2C2C') + bouton('btn_restart', 800, 'Restart', '#555F6B')
L = Logique()
def aff():   # remet les deux textes de vie à jour
    return [('a_h%s', 'modifier_texte', {'valeur': '="Hero HP: " + hero.vie + " / " + hero.vie_max'}, 'hp_hero'),
            ('a_m%s', 'modifier_texte', {'valeur': '="Monster HP: " + monstre.vie'}, 'hp_monstre')]
def suite(prefixe): return [(i % prefixe,) + t[1:] for t, i in ((t, t[0]) for t in aff())]
e = L.evenement('start', 'NoeudEventStart', sortie='Suivant')
L.chaine(e, [('v1', 'definir_vie', {'vie': 10}, 'monstre'), ('v2', 'definir_vie', {'vie': 10}, 'hero'),
             ('v3', 'infliger_degats', {'degats': 4, 'detruire': 'o_non'}, 'hero')] + suite('s'))
e = L.evenement('tap_monstre', 'NoeudEventClicObjet', cible='monstre')
d = L.chaine(e, [('hit_m', 'infliger_degats', {'degats': 3, 'detruire': 'o_oui'}, 'monstre')])
L.chaine((d[0], 'port_vivant', 0), [('mm1', 'modifier_texte', {'valeur': 'Hit!'}, 'msg')] + suite('m'))
L.chaine((d[0], 'port_detruit', 1), [('mm2', 'modifier_texte', {'valeur': 'Defeated!'}, 'msg'), ('mm3', 'modifier_texte', {'valeur': 'Monster HP: 0'}, 'hp_monstre')])
e = L.evenement('tap_heal', 'NoeudEventClicObjet', cible='btn_heal')
L.chaine(e, [('heal', 'soigner', {'soin': 2}, 'hero'), ('hm', 'modifier_texte', {'valeur': 'Healed (max 10)'}, 'msg')] + suite('h'))
e = L.evenement('tap_hit', 'NoeudEventClicObjet', cible='btn_hit')
d = L.chaine(e, [('hit_h', 'infliger_degats', {'degats': 4, 'detruire': 'o_non'}, 'hero')])
L.chaine((d[0], 'port_vivant', 0), [('hh1', 'modifier_texte', {'valeur': 'Ouch!'}, 'msg')] + suite('x'))
L.chaine((d[0], 'port_detruit', 1), [('hh2', 'modifier_texte', {'valeur': 'Hero is out of health'}, 'msg')] + suite('y'))
e = L.evenement('tap_restart', 'NoeudEventClicObjet', cible='btn_restart')
L.action(e, 'rs', 'recommencer_scene')
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test vie', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'vie-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/vie-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
