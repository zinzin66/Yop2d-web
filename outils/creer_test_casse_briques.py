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
# 1. la raquette
b1 = section([['finger', 'move_paddle']], 0, HAUT)
# 2. la balle part
b2 = section([['start', 'start_vx', 'start_vy']], 0, b1[3] + 2 * MARGE + ENTETE + 80)
# 3. la balle avance et rebondit sur les bords
b3 = section([['frame', 'push', 'left', 'right', 'top'], ('left', ['left_do']), ('right', ['right_do']), ('top', ['top_do'])],
             0, b2[3] + 2 * MARGE + ENTETE + 80)
# 4. les vies (à droite de la section 3, sur la même hauteur)
x_vies = b3[2] + 2 * MARGE + 120
b4 = section([['bottom', 'lose_life', 'show_lives', 'no_lives'],
              ('lose_life', ['lost_ball', 'lost_vx', 'lost_vy', 'lost_toast', 'lost_wait', 'lost_restart']),
              ('lose_life', ['relaunch', 'relaunch_vy', 'relaunch_vx'])], x_vies, b3[1])
# 5. rebond sur la raquette
y5 = max(b3[3], b4[3]) + 2 * MARGE + ENTETE + 80
b5 = section([['hit_paddle', 'paddle_vy', 'paddle_vx']], 0, y5)
# 6. briques et victoire
b6 = section([['hit_brick', 'brick_destroy', 'brick_vy', 'brick_score', 'brick_count', 'brick_text', 'all_gone'],
              ('all_gone', ['win_vx', 'win_vy', 'win_toast', 'win_wait', 'win_restart'])],
             0, b5[3] + 2 * MARGE + ENTETE + 80)

cadre('cadre_raquette', 'Step 2 - The paddle follows your finger',
      'While a finger is on the screen, the paddle is moved to the finger X position. doigt.x - 104 centers the paddle '
      '(104 = half its width). clamp(..., 0, 872) keeps it on screen (872 = 1080 - 208).', BLEU, b1)
cadre('cadre_depart', 'Step 3 - The ball starts',
      'When the game starts, the ball speed is set: vx = 6 (to the right) and vy = -9 (negative = up).', VERT, b2)
cadre('cadre_bords', 'Steps 3 and 4 - The ball moves and bounces off the edges',
      'Every frame, the ball is pushed by (vx, vy). Then three Condition nodes, chained with their "Then" output, test the '
      'left edge, the right edge and the top. abs(vx) is always positive and -abs(vx) always negative, so the ball can '
      'never get stuck in an edge.', ORANGE, b3)
cadre('cadre_vies', 'Step 8 - Lives and game over',
      'If the ball goes below the screen, one life is lost and the text is updated. No life left: the ball is put back in '
      'the middle and stopped, then "Game over" and the scene restarts. Otherwise the ball is relaunched.', ROSE, b4)
cadre('cadre_raquette_rebond', 'Step 5 - The ball bounces on the paddle',
      'vy = -abs(vy) sends the ball back up. The vx formula uses the place where the ball touches the paddle: in the '
      'middle it goes straight, on the sides it goes sideways. The player can aim.', VIOLET, b5)
cadre('cadre_briques', 'Steps 6 and 7 - Break the bricks and win',
      'Each brick has the tag "brique", so this one setup works for every brick. The touched brick is the "involved '
      'object": it is destroyed, the ball bounces (vy = -vy), the score goes up and the brick counter goes down. '
      'At 0 bricks the ball stops and the player wins.', JAUNE, b6)

xp = -470   # colonne des post-it, à gauche des cadres
postit('note_variables', 'Variables',
       'score, vies (lives), briques (bricks left), vx and vy (ball speed) are scene variables. They go back to their '
       'starting value when the scene restarts.', JAUNE, xp, b1[1] - MARGE - ENTETE, h=210)
postit('note_negatif', 'Negative = up',
       'In Yop2D, Y grows toward the bottom of the screen. vy = -9 sends the ball up.', VERT, xp, b2[1] - MARGE - ENTETE)
postit('note_ensuite', 'Output "Then"',
       'A Condition has 3 outputs: True, False and Then. "Then" always runs after, so we use it to chain the tests.',
       ORANGE, xp, b3[1] - MARGE - ENTETE, h=210)
postit('note_arreter', 'Stop the ball!',
       'Before the 2 second wait, the ball is put back and stopped. Otherwise it keeps falling and loses a life on every '
       'frame (the counter reached -178!).', ROSE, x_vies, b4[3] + 2 * MARGE + 30, h=210)
postit('note_tag', 'Tag = one setup for all',
       'Add 100 more bricks: as long as they have the tag "brique", nothing else to do. Do not forget to update the '
       'variable "briques".', JAUNE, xp, b6[1] - MARGE - ENTETE, h=210)

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
