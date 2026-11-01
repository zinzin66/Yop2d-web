#!/usr/bin/env python3
"""Fabrique le projet de DÉMONSTRATION « Mes nœuds » : tests/mes-noeuds-test.zip (à importer dans Yop2D).
Usage : python3 outils/creer_test_mes_noeuds.py <clone de zinzin66/yop2d-moteur>
Deux nœuds à soi (fichiers fonctions/*.json) avec des RÉGLAGES (entrées), appelés par 3 boutons, avec cadres et post-it
(en anglais, pour les testeurs Discord). Demande la version du moteur qui contient les réglages de fonction (build de test 1223 ou plus)."""
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
          texte('titre', 60, 40, 1800, 90, 'My nodes : a node of your own, with settings', 56, BLANC, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('texteScore', 60, 200, 1800, 120, 'Score: 0', 100, OR, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('aide', 160, 380, 1600, 160, 'Tap a button. The first two use the SAME node ("Give_points") with different settings. '
                'The third one waits, then speaks. Open the Blueprint to read the post-it.', 36, BLANC, z=10, prefixe=P,
                alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_10', 160, 700, 480, '#2E8B57', '+10 points')
objets += bouton('btn_50', 720, 700, 480, '#2B6CB0', '+50 points')
objets += bouton('btn_wait', 1280, 700, 480, '#8E44AD', 'Wait 3 s, then speak')

# ------------------------------------------------------------ utilitaires de notes
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

# ------------------------------------------------------------ nœud à soi n°1 : Give_points (réglages : points, message)
F1 = Logique()
e = F1.evenement('start', 'NoeudEventStart', sortie='Sortie')
F1.chaine(e, [('add', 'ajouter_variable', {'valeur': '=points'}, None, 'score'),
              ('show', 'modifier_texte', {'valeur': '="Score: " + score'}, 'texteScore'),
              ('say', 'toast', {'message': '=message'})])
for i, nid in enumerate(['start', 'add', 'show', 'say']):
    n = F1.noeud(nid); n['x'], n['y'] = float(i * 420), 0.0
f1 = F1.json()
f1['entrees'] = [{'nom': 'points', 'type': 'nombre', 'defaut': '10'}, {'nom': 'message', 'type': 'texte', 'defaut': 'Nice!'}]
n1 = []
cadre(n1, 'c_f1', 'What this node does',
      'Adds "points" to the score, updates the score text, then shows "message" at the bottom of the screen. '
      '=points and =message are the SETTINGS of this node: whoever runs it chooses their values.', BLEU, boite(F1, ['start', 'add', 'show', 'say']))
postit(n1, 'p_f1a', 'Settings (the sliders button)',
       'Tap the sliders button in the top bar to see them: points (Number, starts at 10) and message (Text, starts at "Nice!").', JAUNE, 0, 330, 440, 200)
postit(n1, 'p_f1b', 'Write =name',
       'Inside the node, write =points instead of a number. In a text field, write =message. Nothing else to learn.', VERT, 500, 330, 440, 200)
f1['notes'] = n1

# ------------------------------------------------------------ nœud à soi n°2 : Wait_then_say (réglages : seconds, words)
F2 = Logique()
e = F2.evenement('start', 'NoeudEventStart', sortie='Sortie')
F2.chaine(e, [('wait', 'attendre', {'duree': '=seconds'}), ('say', 'toast', {'message': '=words'})])
for i, nid in enumerate(['start', 'wait', 'say']):
    n = F2.noeud(nid); n['x'], n['y'] = float(i * 420), 0.0
f2 = F2.json()
f2['entrees'] = [{'nom': 'seconds', 'type': 'nombre', 'defaut': '2'}, {'nom': 'words', 'type': 'texte', 'defaut': 'Done waiting!'}]
n2 = []
cadre(n2, 'c_f2', 'Wait, then speak',
      'The wait lasts "seconds" seconds, then "words" is shown. The settings keep their value during the wait.', ORANGE, boite(F2, ['start', 'wait', 'say']))
postit(n2, 'p_f2', 'Same idea',
       'A node can wait, loop, change scenes... exactly like a normal Blueprint. Its settings are just names you can read with =name.', ROSE, 0, 330, 440, 200)
f2['notes'] = n2

# ------------------------------------------------------------ Blueprint de la scène
L = Logique()
APPEL = 'appeler_fonction'
def appel(btn, nom_noeud, fonction, reglages, y):
    e = L.evenement('ev_' + btn, 'NoeudEventClicObjet', cible=btn, sortie='Sortie')
    L.action(e, 'run_' + btn, APPEL, dict({'fonction': fonction}, **{'entree:' + k: v for k, v in reglages.items()}))
    L.noeud('ev_' + btn)['x'], L.noeud('ev_' + btn)['y'] = 0.0, float(y)
    L.noeud('run_' + btn)['x'], L.noeud('run_' + btn)['y'] = 460.0, float(y)
appel('btn_10', 'a', 'Give_points', {'points': '10', 'message': '+10!'}, 0)
appel('btn_50', 'b', 'Give_points', {'points': '50', 'message': '+50, wow!'}, 520)
appel('btn_wait', 'c', 'Wait_then_say', {'seconds': '3', 'words': 'Thanks for waiting!'}, 1040)
logique = L.json()
notes = []
cadre(notes, 'c1', 'Button +10', 'Taps on the green button run the node "Give_points" with points = 10 and message = "+10!". '
      'The lines under the node are ITS settings: tap them to change the values.', VERT, boite(L, ['ev_btn_10', 'run_btn_10']))
cadre(notes, 'c2', 'Button +50: the same node, other values', 'Same node, same file. Only the settings change: points = 50, another message.',
      BLEU, boite(L, ['ev_btn_50', 'run_btn_50']))
cadre(notes, 'c3', 'Button 3: another node of yours', 'Runs "Wait_then_say" with seconds = 3 and words = "Thanks for waiting!". '
      'This node waits, and its settings stay valid during the wait.', VIOLET, boite(L, ['ev_btn_wait', 'run_btn_wait']))
postit(notes, 'p1', 'What is a node of your own?',
       'A group of nodes saved with a name. You build it once and run it from any scene with one node. Programmers call it a function.',
       JAUNE, -520, -60, 440, 230)
postit(notes, 'p2', 'Where do I create one?',
       'Resources panel > My nodes (called "Functions" in test build 1223) > the + button. Then select it and open its Blueprint.',
       VERT, -520, 200, 440, 230)
postit(notes, 'p3', 'Where are the settings?',
       'Open the Blueprint of the node and tap the sliders button in the top bar. Add a setting with a name, a type and a starting value.',
       ORANGE, -520, 460, 440, 230)
postit(notes, 'p4', 'Try it',
       'Tap the node here, change a value (points = 100), play, tap the button. The score should go up by the new value.',
       ROSE, -520, 720, 440, 210)
logique['notes'] = notes

scene_demo = scene('Demo', objets, P)
scene_demo['variablesLocales'] = [{'id': ident(P + 'var/score'), 'nom': 'score', 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': 0}]

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene_demo], {'Demo': logique}, [], largeur=1920, hauteur=1080)
    ecrire(os.path.join(p, 'fonctions', 'Give_points.json'), f1)
    ecrire(os.path.join(p, 'fonctions', 'Wait_then_say.json'), f2)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Demo My nodes', 'dateCreation': '2026-11-01 12:00:00', 'dateModif': '2026-11-01 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'mes-noeuds-test.zip')
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                if f == 'Licence_Kenney.txt': continue
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
print('%d nœuds dans la scène, 2 nœuds à soi, %d notes -> %s (%d Ko)' % (len(L.noeuds), len(notes) + len(n1) + len(n2), sortie, os.path.getsize(sortie) // 1024))
