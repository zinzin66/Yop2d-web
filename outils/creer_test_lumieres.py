#!/usr/bin/env python3
"""Projet de TEST des « lumières et ombres » : tests/lumieres-test.zip, à importer dans « Yop2D Test » (moteur : branche
claude/discord-yop2d-config-ox8qgh, commit « Lumières et ombres »).
Usage : python3 outils/creer_test_lumieres.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test : un carrefour la nuit. 2 torches fixes (l'une vacille fort, l'autre comme une bougie), un ninja qui suit le doigt
et qui porte une lanterne (objet ENFANT du ninja : la lumière le suit), un monstre immobile. Le ninja et le monstre ont une ombre douce.
Boutons : Day / Sunset (jour -> crépuscule orange -> nuit bleue en 12 s) / Night (très sombre), Lantern off / on (éteint / rallume la lumière du ninja)."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'lumieres_test/'
NJ = 'assets_ludexa/Images/Ninja/'
BLANC, OR, VERT = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0')

objets = [objet('fond', 0, 0, NJ + 'Fonds/ninja_carrefour.png', 1920, 1080, z=-100, prefixe=P)]
# 2 torches fixes : un poteau + une flamme (la lumière est accrochée à la flamme)
for nom, x in (('a', 330), ('b', 1530)):
    objets.append(objet('poteau_' + nom, x, 360, largeur=24, hauteur=130, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#5B3A22')))
    objets.append(objet('flamme_' + nom, x - 8, 318, largeur=40, hauteur=54, z=6, prefixe=P, afficherFondColore=True, couleur=argb('#FFB347')))
hero = objet('hero', 800, 560, NJ + 'Personnages/ninja6_bas_1.png', 170, 170, z=50, prefixe=P)
objets += [hero,
           objet('lanterne', 120, 70, largeur=26, hauteur=46, z=51, prefixe=P, parentId=hero['id'], afficherFondColore=True, couleur=argb('#FFE08A')),
           objet('monstre', 1160, 600, NJ + 'Monstres/monstre9_bas_1.png', 150, 150, z=50, prefixe=P)]
objets += [texte('info', 560, 40, 800, 140, 'LIGHTS TEST\nTouch the screen: the ninja follows your finger and carries a lantern.\nTorches flicker. Shadows are under the ninja and the monster.',
                 30, OR, z=60, prefixe=P, cheminPolice=None, alignementTexte='CENTRE')]
def bouton(nom, x, libelle, couleur):
    b = objet(nom, x, 900, largeur=330, hauteur=110, z=60, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 25, 330, 70, libelle, 38, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_jour', 40, 'Day', '#B7791F') + bouton('btn_soir', 400, 'Sunset (12 s)', '#A04A1E') + bouton('btn_nuit', 760, 'Night', '#2B3A67') \
        + bouton('btn_off', 1120, 'Lantern off', '#555F6B') + bouton('btn_on', 1480, 'Lantern on', '#2E7D4F')

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [('nuit0', 'lumiere_ambiance', {'couleur': '#0A1030', 'niveau': 85, 'duree': 0}),
             ('src_a', 'lumiere_source', {'couleur': '#FFB050', 'rayon': 520, 'intensite': 100, 'lueur': 100, 'vacillement': 'lv_torche'}, 'flamme_a'),
             ('src_b', 'lumiere_source', {'couleur': '#FFC070', 'rayon': 420, 'intensite': 100, 'lueur': 100, 'vacillement': 'lv_bougie'}, 'flamme_b'),
             ('src_h', 'lumiere_source', {'couleur': '#FFD890', 'rayon': 330, 'intensite': 100, 'lueur': 100, 'vacillement': 'lv_torche'}, 'lanterne'),
             ('om_h', 'ombre_objet', {'ombre': 'o_oui', 'force': 50, 'largeur': 80}, 'hero'),
             ('om_m', 'ombre_objet', {'ombre': 'o_oui', 'force': 50, 'largeur': 80}, 'monstre')])
e = L.evenement('finger_down', 'NoeudEventDoigtAppuye', sortie='Sortie')
L.action(e, 'follow', 'glisser_vers', {'x': '=doigt.x - hero.largeur / 2', 'y': '=doigt.y - hero.hauteur', 'duree': 0.3}, 'hero')
e = L.evenement('tap_jour', 'NoeudEventClicObjet', cible='btn_jour')
L.action(e, 'jour', 'lumiere_ambiance', {'couleur': '#FFFFFF', 'niveau': 0, 'duree': 2})
e = L.evenement('tap_nuit', 'NoeudEventClicObjet', cible='btn_nuit')
L.action(e, 'nuit', 'lumiere_ambiance', {'couleur': '#050A20', 'niveau': 90, 'duree': 2})
# coucher de soleil : jour -> crépuscule orange (6 s) -> nuit bleue (6 s) ; la couleur ET l'obscurité changent en douceur
e = L.evenement('tap_soir', 'NoeudEventClicObjet', cible='btn_soir')
L.chaine(e, [('s_jour', 'lumiere_ambiance', {'couleur': '#FFFFFF', 'niveau': 0, 'duree': 0.3}),
             ('s_att0', 'attendre', {'duree': 0.4}),
             ('s_soir', 'lumiere_ambiance', {'couleur': '#8A3410', 'niveau': 40, 'duree': 6}),
             ('s_att', 'attendre', {'duree': 6}),
             ('s_nuit', 'lumiere_ambiance', {'couleur': '#050A20', 'niveau': 90, 'duree': 6})])
e = L.evenement('tap_off', 'NoeudEventClicObjet', cible='btn_off')
L.action(e, 'off', 'lumiere_eteindre', {}, 'lanterne')
e = L.evenement('tap_on', 'NoeudEventClicObjet', cible='btn_on')
L.action(e, 'on', 'lumiere_source', {'couleur': '#FFD890', 'rayon': 330, 'intensite': 100, 'lueur': 100, 'vacillement': 'lv_torche'}, 'lanterne')

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Night', objets, P)], {'Night': L.ranger().json()}, variables(P, []))
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test lumieres et ombres', 'dateCreation': '2026-10-27 12:00:00', 'dateModif': '2026-10-27 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'lumieres-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/lumieres-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
