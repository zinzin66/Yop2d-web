#!/usr/bin/env python3
"""Fabrique le TUTORIEL « Missile tutorial » (le mécanisme des missiles guidés de Space 1, version courte, avec cadres et post-it
dans le Blueprint) : exemples/missile_tutorial.zip + exemples/missile_tutorial.png.
Les images viennent de l'exemple Space 1 (dessinées par l'utilisateur) : exemples/space_1-1.zip.
Usage : python3 outils/creer_tutoriel_missile.py <clone de zinzin66/yop2d-moteur>"""
import os, sys, json, tempfile, zipfile
SITE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'missile/'
IM = 'assets_ludexa/Images/'
SON = 'assets_ludexa/Sons/Yop2D/'
SRC = {'foe': 'ennemi1.png', 'player': 'ResizedImage_2026-10-13_17-01-42_7707.png', 'missile': 'missile.png',
       'e1': 'explosion_1.png', 'e2': 'explosion_2.png', 'e3': 'explosion_3.png', 'e4': 'explosion_4.png'}
NOIR, BLANC = argb('#111111'), argb('#FFFFFF')

def img(nom, fichier, x, y, l, h, **r):
    o = objet(nom, x, y, largeur=l, hauteur=h, prefixe=P, **r)
    o['cheminImage'] = IM + fichier
    return o

objets = [objet('background', 0, 0, largeur=1080, hauteur=1920, z=-100, prefixe=P, afficherFondColore=True, couleur=BLANC),
          img('foe', SRC['foe'], 470, 190, 140, 142, z=5, tag='ennemi'),
          img('player', SRC['player'], 465, 1450, 150, 174, z=5, tag='joueur'),
          img('missile_modele', SRC['missile'], -700, 500, 104, 37, z=6, tag='missile'),
          texte('title', 40, 40, 1000, 90, ' ', 64, NOIR, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('lives_label', 40, 1750, 400, 60, ' ', 40, NOIR, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('lives_text', 440, 1735, 200, 90, '3', 76, NOIR, z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
          texte('hint', 40, 1830, 1000, 60, ' ', 32, argb('#555555'), z=10, prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
ANIMS = {'explosion': [IM + SRC[k] for k in ('e1', 'e2', 'e3', 'e4')]}

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [
    ('s_title', 'afficher_dialogue', {'cle': 'title'}, 'title'),
    ('s_label', 'afficher_dialogue', {'cle': 'lives'}, 'lives_label'),
    ('s_hint', 'afficher_dialogue', {'cle': 'hint'}, 'hint'),
    ('s_vies', 'modifier_variable', {'valeur': 3}, None, 'vies'),
    ('s_clock', 'repeter', {'delai': 2.5, 'repetitions': 0, 'nom': 'salve'})])
t = L.action(('s_clock', 'port_a_chaque_fois', 1), 'm_left', 'missile_guide',
             {'modele': 'missile_modele', 'angle': 200, 'vitesse': 9, 'virage': 2.2, 'attente': 0.35, 'duree_vie': 3.2}, 'foe')
t = L.action(t, 'm_right', 'missile_guide', {'modele': 'missile_modele', 'angle': 340, 'vitesse': 9, 'virage': 2.2, 'attente': 0.35, 'duree_vie': 3.2}, 'foe')
L.action(t, 'm_snd', 'jouer_son', {'fichier': SON + 'laser.ogg', 'volume': 60})

e = L.evenement('finger', 'NoeudEventDoigtAppuye', sortie='Sortie')
L.action(e, 'f_move', 'glisser_vers', {'x': '=doigt.x - 75', 'y': '=doigt.y - 200', 'duree': 0.15}, 'player')

e = L.evenement('hit', 'NoeudEventCollisionTag', {'Tag': 'missile'}, 'player', sortie='Sortie')
t = L.chaine(e, [
    ('h_gone', 'detruire_objet', {}, '__OBJET_IMPLIQUE__'),
    ('h_vie', 'ajouter_variable', {'valeur': -1}, None, 'vies'),
    ('h_txt', 'modifier_propriete', {'propriete': 'texte', 'valeur': '=vies'}, 'lives_text'),
    ('h_clone', 'generer_clone', {}, 'player'),
    ('h_anim', 'jouer_animation', {'animation': 'explosion', 'vitesse': 12, 'boucle': 'false'}, '__OBJET_IMPLIQUE__'),
    ('h_after', 'detruire_apres', {'delai': 0.34}, '__OBJET_IMPLIQUE__'),
    ('h_fx', 'effet_particules', {'modele': 'Etincelles', 'quantite': 14, 'couleur': '#FFB000', 'taille': 0.9}, 'player'),
    ('h_shake', 'tremblement_camera', {'intensite': 7, 'duree': 200}),
    ('h_snd', 'jouer_son', {'fichier': SON + 'explosion.ogg', 'volume': 60}),
    ('h_dead', 'condition', {'condition': 'vies <= 0'})])
L.chaine(VRAI(t), [('h_wait', 'attendre', {'duree': 0.5}), ('h_again', 'recommencer_scene', {})])

# ---------------------------------------------------------------- rangement + cadres
L.ranger(ecart_y=60, ecart_evenements=240)
MARGE, ENTETE = 30, 46
JAUNE, BLEU, VERT, ROSE, ORANGE = [c - (1 << 32) for c in (0xFFFFE082, 0xFF81D4FA, 0xFFA5D6A7, 0xFFF8BBD0, 0xFFFFCC80)]
notes = []
def boite(ids):
    ns = [L.noeud(i) for i in ids]
    return (min(n['x'] for n in ns), min(n['y'] for n in ns), max(n['x'] + taille_noeud(n)[0] for n in ns), max(n['y'] + taille_noeud(n)[1] for n in ns))
def cadre(id, titre, texte, couleur, ids):
    x1, y1, x2, y2 = boite(ids)
    notes.append({'id': id, 'type': 'cadre', 'x': x1 - MARGE, 'y': y1 - MARGE - ENTETE, 'l': x2 - x1 + 2 * MARGE, 'h': y2 - y1 + 2 * MARGE + ENTETE,
                  'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})
def postit(id, titre, texte, couleur, x, y, l=380, h=230):
    notes.append({'id': id, 'type': 'postit', 'x': x, 'y': y, 'l': l, 'h': h, 'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})
G1 = ['start', 's_title', 's_label', 's_hint', 's_vies', 's_clock', 'm_left', 'm_right', 'm_snd']
G2 = ['finger', 'f_move']
G3 = ['hit', 'h_gone', 'h_vie', 'h_txt', 'h_clone', 'h_anim', 'h_after', 'h_fx', 'h_shake', 'h_snd', 'h_dead', 'h_wait', 'h_again']
cadre('c1', 'Step 1 - The enemy fires missiles', '"Repeat" runs the nodes after it every 2.5 seconds. "Launch a guided missile" copies the model object "missile_modele" '
      'and sends it from the enemy. Two missiles per salvo: one starts to the left (angle 200), one to the right (angle 340), then both curve towards your ship.', BLEU, G1)
cadre('c2', 'Step 2 - Move your ship', 'While your finger is down, "Slide to" brings the ship under your finger. Move to dodge the missiles.', VERT, G2)
cadre('c3', 'Step 3 - A missile hits you', 'The event "If an object touches a tag" fires when the ship touches any object with the tag "missile". '
      '"The involved object" is that missile: it is destroyed. One life less, then an explosion: "Create a copy" copies the ship, "Play the animation" '
      'plays the explosion on the copy and "Destroy after a delay" removes it. No life left: the scene restarts.', ORANGE, G3)
xp = boite(G1)[0] - 470
postit('n_model', 'The model', 'The object "missile_modele" waits outside the screen with the tag "missile". Its picture must point to the RIGHT: the node turns it.', JAUNE, xp, boite(G1)[1] - MARGE - ENTETE, h=210)
postit('n_set', 'The settings', 'Speed: pixels per step. Turn: degrees per step (bigger = sharper curve). Wait before aiming: 0.35 s of straight flight. Life time: after 3.2 s the missile explodes by itself.', ROSE, xp, boite(G1)[1] + 230, h=290)
postit('n_tag', 'Tags', 'One tag, many missiles: the collision event works for every missile created during the game.', VERT, xp, boite(G3)[1] - MARGE - ENTETE, h=190)

def T(fr, en, es, de, it, pt, ru, zh, ja): return dict(zip(LANGUES, [fr, en, es, de, it, pt, ru, zh, ja]))
TEXTES = {
    'title': T('Missiles guidés', 'Guided missiles', 'Misiles guiados', 'Lenkraketen', 'Missili guidati', 'Mísseis guiados', 'Управляемые ракеты', '制导导弹', '誘導ミサイル'),
    'lives': T('Vies', 'Lives', 'Vidas', 'Leben', 'Vite', 'Vidas', 'Жизни', '生命', 'ライフ'),
    'hint': T('Touche l\'écran pour déplacer ton vaisseau et esquiver.', 'Touch the screen to move your ship and dodge.',
              'Toca la pantalla para mover tu nave y esquivar.', 'Tippe auf den Bildschirm, um dein Schiff zu bewegen und auszuweichen.',
              'Tocca lo schermo per muovere la nave e schivare.', 'Toque na tela para mover sua nave e desviar.',
              'Касайся экрана, чтобы двигать корабль и уворачиваться.', '触摸屏幕移动飞船并躲避。', '画面をタッチして機体を動かし、よけよう。')}

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    logique = L.json(); logique['notes'] = notes
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, variables(P, [('vies', 3)]), ANIMS, TEXTES)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Missile tutorial', 'dateCreation': '2026-10-30 12:00:00', 'dateModif': '2026-10-30 12:00:00'})
    # images de l'utilisateur, prises dans l'exemple Space 1
    with zipfile.ZipFile(os.path.join(SITE, 'exemples', 'space_1-1.zip')) as z:
        for f in SRC.values():
            z.extract('assets_ludexa/Images/' + f, p)
    sortie = os.path.join(SITE, 'exemples')
    zp = os.path.join(sortie, 'missile_tutorial.zip')
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for r, _, fs in os.walk(p):
            for f in sorted(fs):
                z.write(os.path.join(r, f), os.path.relpath(os.path.join(r, f), p))
        for c in chemins_utilises(p):
            if not os.path.exists(os.path.join(p, c)):
                if not os.path.exists(fichier_biblio(c)): sys.exit('Fichier introuvable : ' + c)
                z.write(fichier_biblio(c), c)
    # vignette : le vaisseau, l'ennemi et deux missiles qui courbent
    from PIL import Image, ImageDraw
    d = os.path.join(p, 'assets_ludexa', 'Images')
    vue = Image.new('RGB', (600, 600), (255, 255, 255)); dr = ImageDraw.Draw(vue)
    def coller(f, centre, taille, angle=0):
        im = Image.open(os.path.join(d, f)).convert('RGBA').resize(taille, Image.LANCZOS).rotate(angle, expand=True)
        vue.paste(im, (centre[0] - im.width // 2, centre[1] - im.height // 2), im)
    for pts in ([(300, 130), (150, 220), (140, 340), (230, 450)], [(300, 130), (450, 220), (460, 340), (370, 450)]):
        dr.line(pts, fill=(160, 160, 160), width=5, joint='curve')
    coller(SRC['foe'], (300, 110), (150, 152)); coller(SRC['player'], (300, 500), (130, 150))
    coller(SRC['missile'], (146, 300), (104, 37), 80); coller(SRC['missile'], (454, 300), (104, 37), 100)
    vue.resize((300, 300), Image.LANCZOS).save(os.path.join(sortie, 'missile_tutorial.png'), optimize=True)
print('%d nœuds, %d notes -> exemples/missile_tutorial.zip (%d Ko)' % (len(L.noeuds), len(notes), os.path.getsize(zp) // 1024))
