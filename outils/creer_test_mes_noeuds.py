#!/usr/bin/env python3
"""Fabrique le projet de DÉMONSTRATION « Mes nœuds » : tests/mes-noeuds-test.zip (à importer dans Yop2D).
Usage : python3 outils/creer_test_mes_noeuds.py <clone de zinzin66/yop2d-moteur>
Trois nœuds à soi (fichiers fonctions/*.json) avec des RÉGLAGES (entrées) : un qui agit sur l'objet touché et en lance un autre, avec cadres et post-it
(en anglais, pour les testeurs Discord). Demande la version du moteur qui contient les réglages de fonction (build de test 1224 ou plus)."""
import os, sys, tempfile, zipfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'mes_noeuds/'
BLANC, OR, VERT_T = argb('#FFFFFF'), argb('#FFD166'), argb('#7BD88F')
JAUNE, BLEU, VERT, ROSE, ORANGE, VIOLET = [c - (1 << 32) for c in (0xFFFFE082, 0xFF81D4FA, 0xFFA5D6A7, 0xFFF8BBD0, 0xFFFFCC80, 0xFFCE93D8)]
MARGE, ENTETE = 30, 46

def bouton(nom, x, y, w, couleur, libelle):
    b = objet(nom, x, y, largeur=w, hauteur=120, z=10, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_text', 0, 28, w, 70, libelle, 42, BLANC, z=11, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]

objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#14142B')),
          texte('titre', 60, 30, 1800, 90, 'My nodes : build your own blocks, with settings', 56, BLANC, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('texteScore', 60, 130, 1800, 110, 'Score: 0', 90, OR, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('aide', 120, 880, 1680, 150, 'Tap a cube: the SAME node ("Pop_and_score") makes it bounce and gives points, with its own settings '
                '(small cubes: height 15, bonus 1 - big cube: height 40, bonus 10). Open the Blueprint to read the post-it.', 32, BLANC, z=10,
                prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
for i, (couleur, x) in enumerate([('#E74C3C', 260), ('#3498DB', 560), ('#2ECC71', 860)]):
    objets.append(objet('cube_%d' % (i + 1), x, 420, largeur=200, hauteur=200, z=10, prefixe=P, afficherFondColore=True,
                        couleur=argb(couleur), estZoneDeClic=True, tag='cube'))
objets.append(objet('cube_big', 1260, 340, largeur=340, hauteur=340, z=10, prefixe=P, afficherFondColore=True,
                    couleur=argb('#F1C40F'), estZoneDeClic=True, tag='big'))
objets += bouton('btn_double', 360, 730, 560, '#2B6CB0', 'Double my score')
objets += bouton('btn_wait', 1000, 730, 560, '#8E44AD', 'Wait 3 s, then speak')

def boite(L, ids):
    x1 = y1 = 10 ** 9; x2 = y2 = -10 ** 9
    for i in ids:
        n = L.noeud(i); l, h = taille_noeud(n)
        x1, y1, x2, y2 = min(x1, n['x']), min(y1, n['y']), max(x2, n['x'] + l), max(y2, n['y'] + h)
    return x1, y1, x2, y2

def cadre(notes, id, titre, texte, couleur, b):
    x1, y1, x2, y2 = b
    notes.append({'id': id, 'type': 'cadre', 'x': x1 - MARGE, 'y': y1 - MARGE - ENTETE, 'l': x2 - x1 + 2 * MARGE,
                  'h': y2 - y1 + 2 * MARGE + ENTETE, 'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})

def postit(notes, id, titre, texte, couleur, x, y, l=400, h=220):
    notes.append({'id': id, 'type': 'postit', 'x': x, 'y': y, 'l': l, 'h': h, 'titre': titre, 'texte': texte,
                  'couleur': couleur, 'replie': False})

def aligner(F, ids, pas=430, y=0.0):
    for i, nid in enumerate(ids):
        n = F.noeud(nid); n['x'], n['y'] = float(i * pas), y

# ------------------------------------------------------------ nœud n°1 : Give_points (points, message)
F1 = Logique()
e = F1.evenement('start', 'NoeudEventStart', sortie='Sortie')
F1.chaine(e, [('add', 'ajouter_variable', {'valeur': '=points'}, None, 'score'),
              ('show', 'modifier_texte', {'valeur': '="Score: " + score'}, 'texteScore'),
              ('say', 'toast', {'message': '=message'})])
aligner(F1, ['start', 'add', 'show', 'say'])
f1 = F1.json()
f1['entrees'] = [{'nom': 'points', 'type': 'nombre', 'defaut': '10'}, {'nom': 'message', 'type': 'texte', 'defaut': 'Nice!'}]
n1 = []
cadre(n1, 'c_f1', 'What this node does',
      'Adds "points" to the score, updates the score text, then shows "message" at the bottom of the screen. '
      '=points and =message are the SETTINGS of this node: whoever runs it chooses their values.', BLEU, boite(F1, ['start', 'add', 'show', 'say']))
postit(n1, 'p_f1a', 'Settings of this node',
       'Tap the "My node settings" button (sliders icon, top bar) to see them: points (Number, starts at 10) and message (Text, starts at "Nice!").', JAUNE, 0, 330, 460, 210)
postit(n1, 'p_f1b', 'Write =name',
       'Inside the node, write =points instead of a number. In a text field, write =message. Nothing else to learn.', VERT, 520, 330, 460, 210)
f1['notes'] = n1

# ------------------------------------------------------------ nœud n°2 : Pop_and_score (height, bonus) : agit sur l'objet touché + lance le nœud n°1
F2 = Logique()
e = F2.evenement('start', 'NoeudEventStart', sortie='Sortie')
F2.chaine(e, [('jump', 'sautiller', {'intensite': '=height', 'duree': '400'}, '__OBJET_IMPLIQUE__'),
              ('give', 'appeler_fonction', {'fonction': 'Give_points', 'entree:points': '=bonus', 'entree:message': 'Pop!'})])
aligner(F2, ['start', 'jump', 'give'])
f2 = F2.json()
f2['entrees'] = [{'nom': 'height', 'type': 'nombre', 'defaut': '20'}, {'nom': 'bonus', 'type': 'nombre', 'defaut': '1'}]
n2 = []
cadre(n2, 'c_f2', 'Bounce the touched cube, then give points',
      'The node acts on "the involved object": the cube that was tapped. It bounces by "height", then runs ANOTHER node of yours '
      '(Give_points) giving it your setting "bonus".', ORANGE, boite(F2, ['start', 'jump', 'give']))
postit(n2, 'p_f2a', 'The touched object',
       'In the target choice, pick "The involved object". The same node then works for any cube that runs it.', ROSE, 0, 330, 460, 200)
postit(n2, 'p_f2b', 'A node can run another node',
       'Here the setting "bonus" of this node is passed to the setting "points" of Give_points: write =bonus in that line.', VIOLET, 520, 330, 460, 200)
f2['notes'] = n2

# ------------------------------------------------------------ nœud n°3 : Wait_then_say (seconds, words)
F3 = Logique()
e = F3.evenement('start', 'NoeudEventStart', sortie='Sortie')
F3.chaine(e, [('wait', 'attendre', {'duree': '=seconds'}), ('say', 'toast', {'message': '=words'})])
aligner(F3, ['start', 'wait', 'say'])
f3 = F3.json()
f3['entrees'] = [{'nom': 'seconds', 'type': 'nombre', 'defaut': '2'}, {'nom': 'words', 'type': 'texte', 'defaut': 'Done waiting!'}]
n3 = []
cadre(n3, 'c_f3', 'Wait, then speak',
      'The wait lasts "seconds" seconds, then "words" is shown. The settings keep their value during the wait.', VERT, boite(F3, ['start', 'wait', 'say']))
f3['notes'] = n3

# ------------------------------------------------------------ Blueprint de la scène
L = Logique()
APPEL = 'appeler_fonction'
def appel(ev, cible, fonction, reglages, y):
    e = L.evenement('ev_' + ev, 'NoeudEventClicObjet', cible=cible, sortie='Sortie')
    L.action(e, 'run_' + ev, APPEL, dict({'fonction': fonction}, **{'entree:' + k: v for k, v in reglages.items()}))
    L.noeud('ev_' + ev)['x'], L.noeud('ev_' + ev)['y'] = 0.0, float(y)
    L.noeud('run_' + ev)['x'], L.noeud('run_' + ev)['y'] = 460.0, float(y)
appel('cube', 'tag:cube', 'Pop_and_score', {'height': '15', 'bonus': '1'}, 0)
appel('big', 'tag:big', 'Pop_and_score', {'height': '40', 'bonus': '10'}, 520)
appel('double', 'btn_double', 'Give_points', {'points': '=score', 'message': 'Doubled!'}, 1040)
appel('wait', 'btn_wait', 'Wait_then_say', {'seconds': '3', 'words': 'Thanks for waiting!'}, 1560)
logique = L.json()
notes = []
cadre(notes, 'c1', 'The 3 small cubes (tag "cube")', 'ONE event for all the small cubes ("Click on # cube"). It runs your node Pop_and_score with '
      'height = 15 and bonus = 1. The lines under the node are ITS settings: tap them to change the values.', VERT, boite(L, ['ev_cube', 'run_cube']))
cadre(notes, 'c2', 'The big cube (tag "big"): same node, other values', 'Same node, same file. Only the settings change: height = 40, bonus = 10.',
      BLEU, boite(L, ['ev_big', 'run_big']))
cadre(notes, 'c3', 'Double my score: a setting can be a calculation', 'The setting "points" of Give_points receives =score, so the score is doubled. '
      'A setting can be a number, a text, or a small calculation.', ORANGE, boite(L, ['ev_double', 'run_double']))
cadre(notes, 'c4', 'Another node: it waits', 'Runs "Wait_then_say" with seconds = 3. The node waits, and its settings stay valid during the wait.',
      VIOLET, boite(L, ['ev_wait', 'run_wait']))
postit(notes, 'p1', 'What is a node of your own?',
       'A group of nodes saved with a name. You build it once and run it from any scene with one node. Programmers call it a function.',
       JAUNE, -520, -60, 440, 230)
postit(notes, 'p2', 'Where do I create one?',
       'Resources panel > My nodes > the + button. Then select it and open its Blueprint. You can also switch from this screen: top button "Switch Blueprint" > My nodes.',
       VERT, -520, 200, 440, 250)
postit(notes, 'p3', 'Where are the settings?',
       'Open the Blueprint of the node and tap the "My node settings" button (sliders icon, top bar). Add a setting with a name, a type and a starting value.',
       ORANGE, -520, 480, 440, 240)
postit(notes, 'p4', 'Try it',
       'Tap a cube: it bounces and the score goes up. Change height or bonus here, play again. Then open Pop_and_score to see how it works.',
       ROSE, -520, 750, 440, 230)
logique['notes'] = notes

scene_demo = scene('Demo', objets, P)
scene_demo['variablesLocales'] = [{'id': ident(P + 'var/score'), 'nom': 'score', 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': 0}]
n_notes = len(notes) + len(n1) + len(n2) + len(n3)

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene_demo], {'Demo': logique}, [], largeur=1920, hauteur=1080)
    ecrire(os.path.join(p, 'fonctions', 'Give_points.json'), f1)
    ecrire(os.path.join(p, 'fonctions', 'Pop_and_score.json'), f2)
    ecrire(os.path.join(p, 'fonctions', 'Wait_then_say.json'), f3)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Demo My nodes 2', 'dateCreation': '2026-11-01 12:00:00', 'dateModif': '2026-11-01 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'mes-noeuds-test.zip')
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                if f == 'Licence_Kenney.txt': continue
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
print('%d nœuds dans la scène, 2 nœuds à soi, %d notes -> %s (%d Ko)' % (len(L.noeuds), n_notes, sortie, os.path.getsize(sortie) // 1024))
