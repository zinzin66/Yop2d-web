#!/usr/bin/env python3
"""Fabrique le projet de TEST du guide « casse-briques » : tests/casse-briques-test.zip (à importer dans Yop2D).
Usage : python3 outils/creer_test_casse_briques.py <clone de zinzin66/yop2d-moteur>
Il suit EXACTEMENT les étapes de guides/source/casse-briques (mêmes nœuds, mêmes formules).
Images : Puzzle Pack de Kenney (CC0), copiées dans tests/casse-briques/images/."""
import os, sys, tempfile, zipfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

IMG = os.path.join(SITE_RACINE, 'tests', 'casse-briques', 'images')
DOSSIER_IMAGES = 'assets_ludexa/Images/casse_briques/'
P = 'casse_briques/'
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')

def image(nom, x, y, fichier, l, h, z=5, **r):
    o = objet(nom, x, y, largeur=l, hauteur=h, z=z, prefixe=P, **r)
    o['cheminImage'] = DOSSIER_IMAGES + fichier
    return o

objets = [objet('fond', 0, 0, largeur=1080, hauteur=1920, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#14142B'))]
couleurs = ['red', 'yellow', 'green']
for ligne, c in enumerate(couleurs):
    for col in range(8):
        objets.append(image('brique%d_%d' % (ligne + 1, col + 1), 28 + 128 * col, 300 + 64 * ligne,
                            'element_%s_rectangle_glossy.png' % c, 128, 64, tag='brique'))
objets += [
    image('raquette', 436, 1700, 'paddleBlu.png', 208, 48),
    image('balle', 518, 1000, 'ballBlue.png', 44, 44),
    texte('texteScore', 40, 70, 480, 70, 'Score : 0', 48, BLANC, prefixe=P, cheminPolice=None),
    texte('texteVies', 600, 70, 440, 70, 'Vies : 3', 48, OR, prefixe=P, cheminPolice=None),
]

L = Logique()
# Étape 3 : la balle part
e = L.evenement('start', 'NoeudEventStart', sortie='Sortie')
L.chaine(e, [('start_vx', 'modifier_variable', {'valeur': 6}, None, 'vx'),
             ('start_vy', 'modifier_variable', {'valeur': -9}, None, 'vy')])
# Étape 2 : la raquette suit le doigt
e = L.evenement('finger', 'NoeudEventDoigtAppuye', sortie='Sortie')
L.action(e, 'move_paddle', 'deplacer', {'x': '=clamp(doigt.x - 104, 0, 872)', 'y': 1700}, 'raquette')
# Étapes 3, 4 et 8 : la balle avance, rebondit sur les bords, tombe
e = L.evenement('frame', 'NoeudEventChaqueImage', sortie='Sortie')
t = L.action(e, 'push', 'pousser', {'x': '=vx', 'y': '=vy'}, 'balle')
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)
c1 = L.action(t, 'left', 'condition', {'condition': '=balle.x <= 0'})
L.action(VRAI(c1), 'left_do', 'modifier_variable', {'valeur': '=abs(vx)'}, None, 'vx')
c2 = L.action(ENSUITE(c1), 'right', 'condition', {'condition': '=balle.x >= 1036'})
L.action(VRAI(c2), 'right_do', 'modifier_variable', {'valeur': '=-abs(vx)'}, None, 'vx')
c3 = L.action(ENSUITE(c2), 'top', 'condition', {'condition': '=balle.y <= 0'})
L.action(VRAI(c3), 'top_do', 'modifier_variable', {'valeur': '=abs(vy)'}, None, 'vy')
c4 = L.action(ENSUITE(c3), 'bottom', 'condition', {'condition': '=balle.y >= 1920'})
t = L.chaine(VRAI(c4), [('lose_life', 'ajouter_variable', {'valeur': -1}, None, 'vies'),
                        ('show_lives', 'modifier_texte', {'valeur': '="Vies : " + vies'}, 'texteVies'),
                        ('no_lives', 'condition', {'condition': '=vies <= 0'})])
L.chaine(VRAI(t), [('lost_ball', 'deplacer', {'x': 518, 'y': 1000}, 'balle'),
                   ('lost_vx', 'modifier_variable', {'valeur': 0}, None, 'vx'),
                   ('lost_vy', 'modifier_variable', {'valeur': 0}, None, 'vy'),
                   ('lost_toast', 'toast', {'message': 'Perdu !'}), ('lost_wait', 'attendre', {'duree': 2}),
                   ('lost_restart', 'recommencer_scene')])
L.chaine(FAUX(t), [('relaunch', 'deplacer', {'x': 518, 'y': 1000}, 'balle'),
                   ('relaunch_vy', 'modifier_variable', {'valeur': -9}, None, 'vy'),
                   ('relaunch_vx', 'modifier_variable', {'valeur': 6}, None, 'vx')])
# Étape 5 : rebond sur la raquette
e = L.evenement('hit_paddle', 'NoeudEventCollisionAB', cible='balle', sortie='Collision')
L.noeud('hit_paddle')['cibleNomB'] = 'raquette'
L.chaine(e, [('paddle_vy', 'modifier_variable', {'valeur': '=-abs(vy)'}, None, 'vy'),
             ('paddle_vx', 'modifier_variable', {'valeur': '=(balle.x + 22 - raquette.x - 104) / 13'}, None, 'vx')])
# Étapes 6 et 7 : casser les briques, gagner
e = L.evenement('hit_brick', 'NoeudEventCollisionTag', {'Tag': 'brique'}, 'balle', sortie='Sortie')
t = L.chaine(e, [('brick_destroy', 'detruire_objet', {}, '__OBJET_IMPLIQUE__'),
                 ('brick_vy', 'modifier_variable', {'valeur': '=-vy'}, None, 'vy'),
                 ('brick_score', 'ajouter_variable', {'valeur': 10}, None, 'score'),
                 ('brick_count', 'ajouter_variable', {'valeur': -1}, None, 'briques'),
                 ('brick_text', 'modifier_texte', {'valeur': '="Score : " + score'}, 'texteScore'),
                 ('all_gone', 'condition', {'condition': '=briques <= 0'})])
L.chaine(VRAI(t), [('win_vx', 'modifier_variable', {'valeur': 0}, None, 'vx'),
                   ('win_vy', 'modifier_variable', {'valeur': 0}, None, 'vy'),
                   ('win_toast', 'toast', {'message': 'Gagné !'}), ('win_wait', 'attendre', {'duree': 2}),
                   ('win_restart', 'recommencer_scene')])

scene_jeu = scene('Jeu', objets, P)
scene_jeu['variablesLocales'] = [
    {'id': ident(P + 'var/' + n), 'nom': n, 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': v}
    for n, v in [('score', 0), ('vies', 3), ('briques', 24), ('vx', 0), ('vy', 0)]]

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene_jeu], {'Jeu': L.ranger().json()}, [], largeur=1080, hauteur=1920)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test casse-briques', 'dateCreation': '2026-10-25 12:00:00',
                                          'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'casse-briques-test.zip')
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                if os.path.join(r, f).endswith('Licence_Kenney.txt'): continue
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
        for f in sorted(os.listdir(IMG)):
            z.write(os.path.join(IMG, f), DOSSIER_IMAGES + f)
print('%d nœuds -> %s (%d Ko)' % (len(L.noeuds), sortie, os.path.getsize(sortie) // 1024))
