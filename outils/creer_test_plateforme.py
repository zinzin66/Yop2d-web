#!/usr/bin/env python3
"""Fabrique le projet du TUTORIEL « Ton premier jeu de plateforme » : tests/plateforme-tuto-test.zip (à importer dans Yop2D).
Usage : python3 outils/creer_test_plateforme.py <clone de zinzin66/yop2d-moteur>
Un héros (homme des cavernes), un sol, un fond, 3 perles à ramasser, une tortue qui fait des allers-retours sur un bloc en
hauteur, et un score. Images : pack « Préhistoire » de la bibliothèque du moteur (Superpowers, CC0), copiées dans le zip.
RÈGLE : aucune formule de programmeur (seulement =score et des comparaisons simples)."""
import os, sys, tempfile, zipfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'tuto_plateforme/'
PH = 'assets_ludexa/Images/Prehistorique/'
BTN = 'assets_ludexa/Images/Yop2D/Interface/bouton_saut.png'
SOL = 1080 - 192                 # le dessus du sol
BLANC = argb('#FFFFFF')
TB = 210

def ph_objet(nom, x, y, image, k, z=50, **r):
    l, h = taille_image(PH + image)
    return objet(nom, x, y, PH + image, l * k, h * k, z=z, prefixe=P, **r)

# ------------------------------------------------------------------ la scène
objets = [
    objet('fond', 0, 0, PH + 'Fonds/prehisto_jungle.png', 1920, 1080, z=-100, prefixe=P),
    objet('sol', 0, SOL, PH + 'Sols/sol_herbe_640.png', 1920, 192, z=10, prefixe=P,
          comportement='sol', estPhysique=True, estStatique=True),
    # le bloc en hauteur (dessus à 150 px au-dessus du sol : le héros saute environ 200 px)
    objet('bloc', 1100, SOL - 150, PH + 'Sols/plateforme_herbe_160.png', 480, 144, z=10, prefixe=P,
          comportement='sol', estPhysique=True, estStatique=True),
    # les 3 perles (tag « piece »)
    ph_objet('piece1', 640, SOL - 110, 'Objets/perle_or.png', 4, tag='piece'),
    ph_objet('piece2', 930, SOL - 330, 'Objets/perle_or.png', 4, tag='piece'),
    ph_objet('piece3', 1290, SOL - 150 - 100, 'Objets/perle_or.png', 4, tag='piece'),
    # la tortue : va-et-vient toute seule sur le bloc (comportement « Patrouille »), tag « ennemi »
    objet('tortue', 1180, SOL - 150 - 114, PH + 'Monstres/tortue_marche_1.png', 180, 114, z=60, prefixe=P,
          comportement='patrouille', vitesseComportement=4.0, animationsAuto=True, estPhysique=True,
          estStatique=False, rebond=0.0, tag='ennemi'),
    # le héros : comportement « Personnage de plateforme », commandé par le joystick et le bouton de saut
    objet('player', 160, SOL - 186, PH + 'Personnages/caverman_repos_1.png', 198, 186, z=100, prefixe=P,
          comportement='plateforme', commandes='joystick', boutonSaut='btn_jump', vitesseComportement=6.0,
          sautComportement=18.0, animationsAuto=True, estPhysique=True, estStatique=False, rebond=0.0),
    objet('joystick', 40, 1080 - 290 - 30, largeur=290, hauteur=290, z=60, prefixe=P, type='joystick',
          couleur=argb('#0E141E', 150)),
    objet('btn_jump', 1920 - TB - 40, 1080 - TB - 30, BTN, TB, TB, z=60, prefixe=P),
    # le score : un petit panneau sombre + le texte
    objet('panneau_score', 40, 40, largeur=440, hauteur=110, z=40, prefixe=P, afficherFondColore=True,
          couleur=argb('#0E141E', 190)),
    texte('texteScore', 60, 55, 400, 80, 'Pièces : 0', 56, BLANC, prefixe=P, cheminPolice=None),
]

# ------------------------------------------------------------------ les nœuds
L = Logique()
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)

# 1. Le héros touche une perle : elle disparaît, le score monte, le texte change
e = L.evenement('touche_piece', 'NoeudEventCollisionTag', {'Tag': 'piece'}, 'player', sortie='Sortie')
t = L.chaine(e, [('piece_detruire', 'detruire_objet', {}, '__OBJET_IMPLIQUE__'),
                 ('piece_score', 'ajouter_variable', {'valeur': 1}, None, 'score'),
                 ('piece_texte', 'modifier_texte', {'valeur': '="Pièces : " + score'}, 'texteScore'),
                 ('piece_toutes', 'condition', {'condition': '=score >= 3'})])
L.chaine(VRAI(t), [('victoire_message', 'toast', {'message': 'Bravo ! Tu as les 3 perles !'}),
                   ('victoire_attente', 'attendre', {'duree': 3}),
                   ('victoire_recommencer', 'recommencer_scene')])

# 2. Le héros touche la tortue : petit message, puis on recommence
e = L.evenement('touche_ennemi', 'NoeudEventCollisionTag', {'Tag': 'ennemi'}, 'player', sortie='Sortie')
L.chaine(e, [('ennemi_flash', 'flash_ecran', {}),
             ('ennemi_message', 'toast', {'message': 'Aïe ! La tortue t\'a touché.'}),
             ('ennemi_attente', 'attendre', {'duree': 1}),
             ('ennemi_recommencer', 'recommencer_scene')])

# 3. Le héros reste dans l'écran
e = L.evenement('chaque_image', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'garder', 'garder_dans_ecran', {'marge': 0}, 'player')

scene_jeu = scene('Jeu', objets, P)
scene_jeu['variablesLocales'] = [{'id': ident(P + 'var/score'), 'nom': 'score', 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': 0}]

# ------------------------------------------------------------------ rangement + cadres + post-it (notes du Blueprint)
ECART_X, ECART_Y, MARGE, ENTETE = 90, 70, 30, 46
JAUNE, BLEU, VERT, ROSE, ORANGE, VIOLET = [c - (1 << 32) for c in (0xFFFFE082, 0xFF81D4FA, 0xFFA5D6A7, 0xFFF8BBD0, 0xFFFFCC80, 0xFFCE93D8)]

def poser(ids, x, y):
    bas = y
    for i in ids:
        n = L.noeud(i)
        n['x'], n['y'] = float(x), float(y)
        l, h = taille_noeud(n)
        x += l + ECART_X
        bas = max(bas, y + h)
    return bas

def section(ids, x, y):
    bas = poser(ids, x, y)
    droite = max(L.noeud(i)['x'] + taille_noeud(L.noeud(i))[0] for i in ids)
    return (x, y, droite, bas)

notes = []
def cadre(id, titre, texte, couleur, boite):
    x1, y1, x2, y2 = boite
    notes.append({'id': id, 'type': 'cadre', 'x': x1 - MARGE, 'y': y1 - MARGE - ENTETE, 'l': x2 - x1 + 2 * MARGE,
                  'h': y2 - y1 + 2 * MARGE + ENTETE, 'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})

def postit(id, titre, texte, couleur, x, y, l=380, h=200):
    notes.append({'id': id, 'type': 'postit', 'x': x, 'y': y, 'l': l, 'h': h, 'titre': titre, 'texte': texte,
                  'couleur': couleur, 'replie': False})

ESPACE = 2 * MARGE + ENTETE + 80
# 1. perle
b1 = section(['touche_piece', 'piece_detruire', 'piece_score', 'piece_texte', 'piece_toutes'], 0, 0)
b1v = section(['victoire_message', 'victoire_attente', 'victoire_recommencer'], L.noeud('piece_toutes')['x'], b1[3] + ECART_Y)
b1 = (b1[0], b1[1], max(b1[2], b1v[2]), b1v[3])
# 2. ennemi
b2 = section(['touche_ennemi', 'ennemi_flash', 'ennemi_message', 'ennemi_attente', 'ennemi_recommencer'], 0, b1[3] + ESPACE)
# 3. rester dans l'écran
b3 = section(['chaque_image', 'garder'], 0, b2[3] + ESPACE)

cadre('cadre_pieces', 'Step 5 - Collect the pearls',
      'Each pearl has the tag "piece". When the hero touches an object with this tag, the pearl is destroyed (the touched '
      'object is the "involved object"), the score goes up by 1 and the text shows it. At 3 the player wins.', VERT, b1)
cadre('cadre_ennemi', 'Step 7 - The turtle',
      'The turtle has the tag "ennemi". If the hero touches it: screen flash, a message, a short wait, then the scene restarts '
      '(the score goes back to 0).', ROSE, b2)
cadre('cadre_ecran', 'Step 8 - Stay inside the screen',
      'Every frame, the hero is kept inside the screen so he cannot walk out of the level.', BLEU, b3)
xp = -470
postit('note_variable', 'The score',
       '"score" is a scene variable. It goes back to 0 when the scene restarts. The text shows it with ="Pièces : " + score.',
       JAUNE, xp, b1[1] - MARGE - ENTETE, h=230)
postit('note_tag', 'Tags',
       'A tag is a family name. One setup works for the 3 pearls because they all have the tag "piece".',
       VERT, xp, b1[1] - MARGE - ENTETE + 250, h=200)
postit('note_patrouille', 'No node for the walk',
       'The turtle walks back and forth by itself: it has the behavior "Patrol". Nothing to build.',
       ORANGE, xp, b2[1] - MARGE - ENTETE, h=200)

# ------------------------------------------------------------------ écriture du projet + images
animations = {
    'idle': [PH + 'Personnages/caverman_repos_%d.png' % i for i in range(1, 7)],
    'walk': [PH + 'Personnages/caverman_marche_%d.png' % i for i in range(1, 7)],
    'tortue_marche': [PH + 'Monstres/tortue_marche_%d.png' % i for i in range(1, 7)],
    'tortue_repos': [PH + 'Monstres/tortue_repos_%d.png' % i for i in range(1, 5)],
}
fichiers = {c for liste in animations.values() for c in liste}
fichiers |= {PH + 'Fonds/prehisto_jungle.png', PH + 'Sols/sol_herbe_640.png', PH + 'Sols/plateforme_herbe_160.png',
             PH + 'Objets/perle_or.png', BTN, PH + 'Licence_CC0.txt', PH + 'Credits.txt'}

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    logique = L.json()
    logique['notes'] = notes
    ecrire_projet(p, [scene_jeu], {'Jeu': logique}, [], animations=animations, largeur=1920, hauteur=1080, pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Tuto plateforme', 'dateCreation': '2026-11-02 12:00:00',
                                          'dateModif': '2026-11-02 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'plateforme-tuto-test.zip')
    with zipfile.ZipFile(sortie, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                if os.path.join(r, f).endswith('Licence_Kenney.txt'): continue
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
        manquants = []
        for c in sorted(fichiers):
            src = fichier_biblio(c)
            if os.path.exists(src): z.write(src, c)
            else: manquants.append(c)
print('%d nœuds, %d notes -> %s (%d Ko)' % (len(L.noeuds), len(notes), sortie, os.path.getsize(sortie) // 1024))
if manquants: print('IMAGES MANQUANTES :', manquants)
