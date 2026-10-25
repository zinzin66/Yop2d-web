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
    objet('mur_gauche', -300, -400, largeur=300, hauteur=2800, z=1, prefixe=P, type='zone'),
    objet('mur_droit', 1080, -400, largeur=300, hauteur=2800, z=1, prefixe=P, type='zone'),
    objet('mur_haut', -300, -300, largeur=1680, hauteur=300, z=1, prefixe=P, type='zone'),
    objet('mur_bas', -300, 1920, largeur=1680, hauteur=300, z=1, prefixe=P, type='zone'),
    image('raquette', 436, 1700, 'paddleBlu.png', 208, 48, comportement='glisse', estDeplacable=True),
    image('balle', 518, 1000, 'ballBlue.png', 44, 44),
    texte('texteScore', 40, 70, 480, 70, 'Score : 0', 48, BLANC, prefixe=P, cheminPolice=None),
    texte('texteVies', 600, 70, 440, 70, 'Vies : 3', 48, OR, prefixe=P, cheminPolice=None),
]

L = Logique()
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)
# La raquette : le joueur la glisse au doigt ; chaque image on la remet à sa hauteur et on la garde dans l'écran
e = L.evenement('paddle_frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.chaine(e, [('lock_y', 'modifier_propriete', {'propriete': 'y', 'valeur': 1700}, 'raquette'),
             ('keep_in', 'garder_dans_ecran', {'marge': 0}, 'raquette')])
# La balle part, puis avance à chaque image
e = L.evenement('start', 'NoeudEventStart', sortie='Sortie')
L.chaine(e, [('start_vx', 'modifier_variable', {'valeur': 6}, None, 'vx'),
             ('start_vy', 'modifier_variable', {'valeur': -9}, None, 'vy')])
e = L.evenement('frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'push', 'pousser', {'x': '=vx', 'y': '=vy'}, 'balle')
# Les murs invisibles : la balle repart de l'autre côté (des nombres tout simples, rien à calculer)
for ev, mur, var, val, nom in [('wall_left', 'mur_gauche', 'vx', 6, 'left_do'), ('wall_right', 'mur_droit', 'vx', -6, 'right_do'),
                               ('wall_top', 'mur_haut', 'vy', 9, 'top_do')]:
    e = L.evenement(ev, 'NoeudEventCollisionAB', cible='balle', sortie='Collision')
    L.noeud(ev)['cibleNomB'] = mur
    L.action(e, nom, 'modifier_variable', {'valeur': val}, None, var)
# La raquette : la balle remonte, avec une direction un peu au hasard
e = L.evenement('hit_paddle', 'NoeudEventCollisionAB', cible='balle', sortie='Collision')
L.noeud('hit_paddle')['cibleNomB'] = 'raquette'
L.chaine(e, [('paddle_vy', 'modifier_variable', {'valeur': -9}, None, 'vy'),
             ('paddle_vx', 'modifier_variable', {'valeur': '=random(-6, 6)'}, None, 'vx')])
# Les briques : on casse, la balle repart de l'autre sens, score, victoire
e = L.evenement('hit_brick', 'NoeudEventCollisionTag', {'Tag': 'brique'}, 'balle', sortie='Sortie')
t = L.chaine(e, [('brick_destroy', 'detruire_objet', {}, '__OBJET_IMPLIQUE__'),
                 ('brick_dir', 'condition', {'condition': '=vy < 0'})])
L.action(VRAI(t), 'dir_down', 'modifier_variable', {'valeur': 9}, None, 'vy')
L.action(FAUX(t), 'dir_up', 'modifier_variable', {'valeur': -9}, None, 'vy')
t = L.chaine(ENSUITE(t), [('brick_score', 'ajouter_variable', {'valeur': 10}, None, 'score'),
                          ('brick_count', 'ajouter_variable', {'valeur': -1}, None, 'briques'),
                          ('brick_text', 'modifier_texte', {'valeur': '="Score : " + score'}, 'texteScore'),
                          ('all_gone', 'condition', {'condition': '=briques <= 0'})])
L.chaine(VRAI(t), [('win_vx', 'modifier_variable', {'valeur': 0}, None, 'vx'),
                   ('win_vy', 'modifier_variable', {'valeur': 0}, None, 'vy'),
                   ('win_toast', 'toast', {'message': 'Gagné !'}), ('win_wait', 'attendre', {'duree': 2}),
                   ('win_restart', 'recommencer_scene')])
# Le bas de l'écran : une vie en moins
e = L.evenement('hit_bottom', 'NoeudEventCollisionAB', cible='balle', sortie='Collision')
L.noeud('hit_bottom')['cibleNomB'] = 'mur_bas'
t = L.chaine(e, [('lose_life', 'ajouter_variable', {'valeur': -1}, None, 'vies'),
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

scene_jeu = scene('Jeu', objets, P)
scene_jeu['variablesLocales'] = [
    {'id': ident(P + 'var/' + n), 'nom': n, 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': v}
    for n, v in [('score', 0), ('vies', 3), ('briques', 24), ('vx', 0), ('vy', 0)]]

# ---------------------------------------------------------------- rangement + cadres + post-it (notes du Blueprint)
ECART_X, ECART_Y, MARGE, ENTETE = 90, 70, 30, 46
JAUNE, BLEU, VERT, ROSE, ORANGE, VIOLET = [c - (1 << 32) for c in (0xFFFFE082, 0xFF81D4FA, 0xFFA5D6A7, 0xFFF8BBD0, 0xFFFFCC80, 0xFFCE93D8)]

def poser(ids, x, y):
    """Pose des nœuds en ligne, de gauche à droite ; renvoie le bas de la ligne."""
    bas = y
    for i in ids:
        n = L.noeud(i)
        n['x'], n['y'] = float(x), float(y)
        l, h = taille_noeud(n)
        x += l + ECART_X
        bas = max(bas, y + h)
    return bas

def colonne(i):
    return L.noeud(i)['x']

def section(lignes, x, y):
    """lignes : liste de lignes ; une ligne = liste d'ids, ou (id sous lequel aligner, [ids]) pour une ligne alignée sous un nœud.
    Renvoie (x1, y1, x2, y2) = la boîte qui entoure toute la section."""
    haut, y0 = y, y
    droite = x
    for ligne in lignes:
        if isinstance(ligne, tuple):
            ids = ligne[1]
            xl = colonne(ligne[0])
        else:
            ids, xl = ligne, x
        bas = poser(ids, xl, y0)
        y0 = bas + ECART_Y
        for i in ids:
            n = L.noeud(i)
            droite = max(droite, n['x'] + taille_noeud(n)[0])
    return (x, haut, droite, y0 - ECART_Y)

notes = []
def cadre(id, titre, texte, couleur, boite):
    x1, y1, x2, y2 = boite
    notes.append({'id': id, 'type': 'cadre', 'x': x1 - MARGE, 'y': y1 - MARGE - ENTETE, 'l': x2 - x1 + 2 * MARGE,
                  'h': y2 - y1 + 2 * MARGE + ENTETE, 'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})
    return notes[-1]

def postit(id, titre, texte, couleur, x, y, l=380, h=190):
    notes.append({'id': id, 'type': 'postit', 'x': x, 'y': y, 'l': l, 'h': h, 'titre': titre, 'texte': texte,
                  'couleur': couleur, 'replie': False})

HAUT = 0
ESPACE = 2 * MARGE + ENTETE + 80
# 1. la raquette
b1 = section([['paddle_frame', 'lock_y', 'keep_in']], 0, HAUT)
# 2. la balle part et avance
b2 = section([['start', 'start_vx', 'start_vy'], ['frame', 'push']], 0, b1[3] + ESPACE)
# 3. les murs
b3 = section([['wall_left', 'left_do'], ['wall_right', 'right_do'], ['wall_top', 'top_do']], 0, b2[3] + ESPACE)
# 4. la raquette renvoie la balle
b4 = section([['hit_paddle', 'paddle_vy', 'paddle_vx']], 0, b3[3] + ESPACE)
# 5. les briques et la victoire
b5 = section([['hit_brick', 'brick_destroy', 'brick_dir', 'brick_score', 'brick_count', 'brick_text', 'all_gone'],
              ('brick_dir', ['dir_down']), ('brick_dir', ['dir_up']),
              ('all_gone', ['win_vx', 'win_vy', 'win_toast', 'win_wait', 'win_restart'])], 0, b4[3] + ESPACE)
# 6. le bas de l'écran : les vies
b6 = section([['hit_bottom', 'lose_life', 'show_lives', 'no_lives'],
              ('lose_life', ['lost_ball', 'lost_vx', 'lost_vy', 'lost_toast', 'lost_wait', 'lost_restart']),
              ('lose_life', ['relaunch', 'relaunch_vy', 'relaunch_vx'])], 0, b5[3] + ESPACE)

cadre('cadre_raquette', 'Step 2 - The paddle follows your finger',
      'The paddle has the behavior "Slid with the finger": the player drags it. Every frame, it is put back at the same '
      'height (Set a property: y = 1700) and kept inside the screen (Keep in screen).', BLEU, b1)
cadre('cadre_depart', 'Step 3 - The ball starts and moves',
      'When the game starts, the ball speed is set: vx = 6 (to the right) and vy = -9 (negative = up). Then, every '
      'frame, the ball is pushed by vx and vy.', VERT, b2)
cadre('cadre_murs', 'Step 4 - The walls send the ball back',
      'The three invisible walls (zones around the screen) change the ball direction with plain numbers: left wall: '
      'vx = 6, right wall: vx = -6, top wall: vy = 9. Nothing to calculate.', ORANGE, b3)
cadre('cadre_raquette_rebond', 'Step 5 - The ball bounces on the paddle',
      'The ball goes back up (vy = -9) and leaves in a random direction (vx = a random number between -6 and 6), so '
      'the game is never the same.', VIOLET, b4)
cadre('cadre_briques', 'Steps 6 and 7 - Break the bricks and win',
      'Each brick has the tag "brique", so one setup works for every brick. The touched brick is the "involved object": '
      'it is destroyed. If the ball was going up (vy < 0) it goes down, otherwise it goes up. Then the score goes up and '
      'the brick counter goes down. At 0 bricks the ball stops and the player wins.', JAUNE, b5)
cadre('cadre_vies', 'Step 8 - Lives and game over',
      'When the ball touches the wall under the screen, one life is lost. No life left: the ball is put back in the '
      'middle and stopped, then "Perdu !" and the scene restarts. Otherwise the ball is relaunched.', ROSE, b6)

xp = -470   # colonne des post-it, à gauche des cadres
postit('note_variables', 'Variables',
       'score, vies (lives), briques (bricks left), vx and vy (ball speed) are scene variables. They go back to their '
       'starting value when the scene restarts.', JAUNE, xp, b1[1] - MARGE - ENTETE, h=210)
postit('note_negatif', 'Negative = up',
       'In Yop2D, Y grows toward the bottom of the screen. vy = -9 sends the ball up.', VERT, xp, b2[1] - MARGE - ENTETE)
postit('note_murs', 'Invisible walls',
       'The walls are "Zone" objects placed around the screen. They are invisible during the game but the ball can touch '
       'them.', ORANGE, xp, b3[1] - MARGE - ENTETE, h=210)
postit('note_ensuite', 'Output "Then"',
       'A Condition has 3 outputs: True, False and Then. "Then" always runs after, whatever the answer.',
       VIOLET, xp, b5[1] - MARGE - ENTETE, h=210)
postit('note_arreter', 'Stop the ball!',
       'Before the 2 second wait, the ball is put back and stopped. Otherwise it keeps touching the bottom wall and loses '
       'a life on every frame.', ROSE, xp, b6[1] - MARGE - ENTETE, h=210)

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    logique = L.json()
    logique['notes'] = notes
    ecrire_projet(p, [scene_jeu], {'Jeu': logique}, [], largeur=1080, hauteur=1920)
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
print('%d nœuds, %d notes -> %s (%d Ko)' % (len(L.noeuds), len(notes), sortie, os.path.getsize(sortie) // 1024))
