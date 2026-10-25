#!/usr/bin/env python3
"""Fabrique l'exemple « Tactics demo » (stratégie au tour par tour sur une grille, FAIT À LA MAIN avec les nœuds existants) :
exemples/tactics_demo.zip + exemples/tactics_demo.png (vignette 300 x 300).
Usage : python3 outils/creer_exemple_tactique.py <clone de zinzin66/yop2d-moteur>
Puis : entrée dans outils/exemples/source.json, python3 outils/generer_exemples.py, python3 outils/generer_accueil.py.

Le jeu : 2 héros, 2 monstres, une carte de 14 x 10 cases (décor en tuiles ; buissons et rochers = murs). À SON TOUR le joueur
touche un héros (il grossit), puis le sol (il y va, en contournant les murs) ou un monstre (il l'attaque). Chaque héros agit une
fois par tour (il devient gris). Quand les deux ont joué (ou si on touche « Fin du tour »), les monstres avancent vers les héros.
Un monstre qui touche un héros fait perdre une vie. Tous les monstres battus = victoire ; plus de vie = défaite.
N'utilise QUE des nœuds publiés avant la 1120 (chemins, tags, variables, conditions, événements locaux).
CE QUI MANQUE (voir « Ce qui manque » sur le site) : zone de déplacement visible, gestion des tours, limite de distance."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'tactique/'
NJ = 'assets_ludexa/Images/Ninja/'
SON = 'assets_ludexa/Sons/Yop2D/'
CASE, GX, GY = 80, 60, 140
CARTE = ["..............",
         "..B...s....B..",
         "..B...s.......",
         "....##...B....",
         ".s..##...B.s..",
         ".s.......B....",
         "..B...##......",
         "....s.##..s...",
         "..B........B..",
         ".............."]
CASES = {'hero1': (1, 3), 'hero2': (1, 6), 'foe1': (12, 3), 'foe2': (12, 6)}
IMAGES = {'hero1': 'Personnages/ninja6', 'hero2': 'Personnages/ninja4', 'foe1': 'Monstres/monstre3', 'foe2': 'Monstres/monstre8'}
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')

def coin(col, lig):
    return GX + col * CASE, GY + lig * CASE

TEXTES = {
 'your_turn': {'fr': 'À ton tour', 'en': 'Your turn', 'es': 'Tu turno', 'de': 'Du bist dran', 'it': 'Tocca a te', 'pt': 'Sua vez',
               'ru': 'Твой ход', 'zh': '轮到你了', 'ja': 'あなたの番'},
 'enemy_turn': {'fr': 'Tour des monstres', 'en': 'Monsters\' turn', 'es': 'Turno de los monstruos', 'de': 'Die Monster sind dran',
                'it': 'Turno dei mostri', 'pt': 'Vez dos monstros', 'ru': 'Ход монстров', 'zh': '怪物的回合', 'ja': 'モンスターの番'},
 'victory': {'fr': 'Victoire !', 'en': 'Victory!', 'es': '¡Victoria!', 'de': 'Sieg!', 'it': 'Vittoria!', 'pt': 'Vitória!',
             'ru': 'Победа!', 'zh': '胜利！', 'ja': '勝利！'},
 'defeat': {'fr': 'Défaite…', 'en': 'Defeat…', 'es': 'Derrota…', 'de': 'Niederlage …', 'it': 'Sconfitta…', 'pt': 'Derrota…',
            'ru': 'Поражение…', 'zh': '失败……', 'ja': '敗北…'},
 'help': {'fr': 'Touche un héros, puis le sol pour avancer\nou un monstre pour l\'attaquer.\nChaque héros joue une fois par tour.\nQuand les deux ont joué, les monstres avancent.',
          'en': 'Tap a hero, then the ground to move\nor a monster to attack it.\nEach hero plays once per turn.\nWhen both have played, the monsters move.',
          'es': 'Toca un héroe y luego el suelo para moverte\no un monstruo para atacarlo.\nCada héroe juega una vez por turno.\nCuando los dos han jugado, avanzan los monstruos.',
          'de': 'Tippe einen Helden an, dann den Boden zum Laufen\noder ein Monster zum Angreifen.\nJeder Held spielt einmal pro Runde.\nHaben beide gespielt, ziehen die Monster.',
          'it': 'Tocca un eroe, poi il terreno per muoverti\no un mostro per attaccarlo.\nOgni eroe gioca una volta per turno.\nQuando hanno giocato entrambi, avanzano i mostri.',
          'pt': 'Toque em um herói, depois no chão para andar\nou em um monstro para atacá-lo.\nCada herói joga uma vez por turno.\nQuando os dois jogaram, os monstros avançam.',
          'ru': 'Нажми на героя, затем на землю, чтобы идти,\nили на монстра, чтобы атаковать.\nКаждый герой ходит раз за ход.\nКогда сходили оба, двигаются монстры.',
          'zh': '点一个英雄，再点地面移动，\n或点怪物进行攻击。\n每个英雄每回合行动一次。\n两人都行动后，怪物前进。',
          'ja': 'ヒーローをタッチして、地面をタッチすると移動、\nモンスターをタッチすると攻撃します。\nヒーローは 1 ターンに 1 回動けます。\n2 人とも動くと、モンスターが進みます。'},
 'lives': {'fr': 'Vies', 'en': 'Lives', 'es': 'Vidas', 'de': 'Leben', 'it': 'Vite', 'pt': 'Vidas', 'ru': 'Жизни', 'zh': '生命', 'ja': 'ライフ'},
 'monsters': {'fr': 'Monstres', 'en': 'Monsters', 'es': 'Monstruos', 'de': 'Monster', 'it': 'Mostri', 'pt': 'Monstros',
              'ru': 'Монстры', 'zh': '怪物', 'ja': 'モンスター'},
 'end_turn': {'fr': 'Fin du tour', 'en': 'End turn', 'es': 'Fin del turno', 'de': 'Zug beenden', 'it': 'Fine turno', 'pt': 'Fim do turno',
              'ru': 'Конец хода', 'zh': '结束回合', 'ja': 'ターン終了'},
}

# ---------------------------------------------------------------- objets
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')),
          decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=NJ + 'Tuiles/tileset_ninja.png'),
          # le sol touchable : une zone invisible posée sur toute la carte
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True)]
ANIMS = {}
def unite(nom, vivant_tag=None):
    c, l = CASES[nom]
    x, y = coin(c, l)
    o = objet(nom, x, y, NJ + IMAGES[nom] + '_bas_1.png', CASE, CASE, z=50, prefixe=P, estPhysique=True, estStatique=False,
              graviteScale=0.0, comportement='dessus', directions='4', commandes='aucune', animationsAuto=True, vitesseComportement=6.0)
    for etat in ('walk', 'idle'):
        for d in ('bas', 'haut', 'gauche', 'droite'):
            ANIMS['%s_%s_%s' % (nom, etat, d)] = [NJ + IMAGES[nom] + '_%s_%d.png' % (d, i) for i in (range(1, 5) if etat == 'walk' else [1])]
    return o
objets += [unite(n) for n in CASES]
objets += [
    texte('turn_text', 1240, 150, 640, 90, ' ', 60, OR, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
    texte('help_text', 1240, 270, 640, 250, ' ', 30, BLANC, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None),
    texte('lives_label', 1240, 570, 330, 60, ' ', 38, BLANC, z=60, prefixe=P, alignementTexte='DROITE', cheminPolice=None),
    texte('lives_text', 1590, 560, 200, 80, '3', 60, ROUGE, z=60, prefixe=P, cheminPolice=None),
    texte('foes_label', 1240, 680, 330, 60, ' ', 38, BLANC, z=60, prefixe=P, alignementTexte='DROITE', cheminPolice=None),
    texte('foes_text', 1590, 670, 200, 80, '2', 60, VERT, z=60, prefixe=P, cheminPolice=None)]
bouton = objet('btn_end', 1300, 820, largeur=520, hauteur=120, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#2B6CB0'),
               estZoneDeClic=True)
objets += [bouton, texte('btn_end_text', 0, 28, 520, 70, ' ', 46, BLANC, z=61, prefixe=P, parentId=bouton['id'],
                         alignementTexte='CENTRE', cheminPolice=None)]

# ---------------------------------------------------------------- logique
L = Logique()
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)
def evenement_local(id, nom):
    return L.evenement(id, 'NoeudEventPersonnalise', {"Nom de l'événement": nom})
def appeler(depuis, id, nom, **kw):
    return L.action(depuis, id, 'appeler_evenement', {'evenement': nom}, **kw)
def dire(depuis, id, cle, cible):
    return L.action(depuis, id, 'afficher_dialogue', {'cle': cle}, cible)
def chemin_vers_objet(depuis, id, qui, vers, vitesse):
    t = L.action(depuis, id, 'chemin_vers_objet', {'vitesse': vitesse, 'diagonales': 'false'}, qui)
    L.noeud(id)['cibleNomB'] = vers
    return t

# Au démarrage : tout remettre à zéro, écrire les textes
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [('s_tour', 'modifier_variable', {'valeur': 1}, None, 'tour'), ('s_sel', 'modifier_variable', {'valeur': 0}, None, 'sel'),
             ('s_joues', 'modifier_variable', {'valeur': 0}, None, 'joues'), ('s_f1', 'modifier_variable', {'valeur': 0}, None, 'fini1'),
             ('s_f2', 'modifier_variable', {'valeur': 0}, None, 'fini2'), ('s_foes', 'modifier_variable', {'valeur': 2}, None, 'monstres'),
             ('s_v1', 'modifier_variable', {'valeur': 1}, None, 'vivant1'), ('s_v2', 'modifier_variable', {'valeur': 1}, None, 'vivant2'),
             ('s_vies', 'modifier_variable', {'valeur': 3}, None, 'vies')])
L.chaine(('s_vies', 'port_suivant', 0), [
    ('s_t1', 'afficher_dialogue', {'cle': 'your_turn'}, 'turn_text'), ('s_t2', 'afficher_dialogue', {'cle': 'help'}, 'help_text'),
    ('s_t3', 'afficher_dialogue', {'cle': 'lives'}, 'lives_label'), ('s_t4', 'afficher_dialogue', {'cle': 'monsters'}, 'foes_label'),
    ('s_t5', 'afficher_dialogue', {'cle': 'end_turn'}, 'btn_end_text'),
    ('s_n1', 'modifier_propriete', {'propriete': 'texte', 'valeur': '=vies'}, 'lives_text'),
    ('s_n2', 'modifier_propriete', {'propriete': 'texte', 'valeur': '=monstres'}, 'foes_text')])

# 1. Choisir un héros
for h in ('1', '2'):
    e = L.evenement('pick%s' % h, 'NoeudEventClicObjet', cible='hero%s' % h)
    t = L.chaine(e, [('pick%s_t' % h, 'condition', {'condition': 'tour = 1'})])
    t = L.chaine(VRAI(t), [('pick%s_f' % h, 'condition', {'condition': 'fini%s = 0' % h})])
    autre = '2' if h == '1' else '1'
    L.chaine(VRAI(t), [('pick%s_sel' % h, 'modifier_variable', {'valeur': int(h)}, None, 'sel'),
                       ('pick%s_big' % h, 'modifier_taille', {'x': 1.25, 'y': 1.25}, 'hero%s' % h),
                       ('pick%s_small' % h, 'modifier_taille', {'x': 1, 'y': 1}, 'hero%s' % autre),
                       ('pick%s_snd' % h, 'jouer_son', {'fichier': SON + 'pop.ogg', 'volume': 60})])

# 2. Toucher le sol : le héros choisi y va
e = L.evenement('ground', 'NoeudEventClicObjet', cible='terrain')
t = L.chaine(e, [('g_tour', 'condition', {'condition': 'tour = 1'})])
c1 = L.chaine(VRAI(t), [('g_c1', 'condition', {'condition': 'sel = 1'})])
for h, c in (('1', c1),):
    pass
def aller_au_sol(depuis, h):
    L.action(depuis, 'g_go%s' % h, 'chemin_vers_point', {'x': '=doigt.x', 'y': '=doigt.y', 'vitesse': 8, 'diagonales': 'false'}, 'hero%s' % h)
    L.chaine(('g_go%s' % h, 'port_tout_de_suite', 0), [('g_go%s_sel' % h, 'modifier_variable', {'valeur': 0}, None, 'sel'),
                                                       ('g_go%s_small' % h, 'modifier_taille', {'x': 1, 'y': 1}, 'hero%s' % h)])
    appeler(('g_go%s' % h, 'port_arrive', 1), 'g_go%s_done' % h, 'fin_hero%s' % h, decalage_y=180)
aller_au_sol(VRAI(c1), '1')
c2 = L.chaine(FAUX(c1), [('g_c2', 'condition', {'condition': 'sel = 2'})])
aller_au_sol(VRAI(c2), '2')

# 3. Toucher un monstre : le héros choisi va l'attaquer
for f, vivant in (('1', 'vivant1'), ('2', 'vivant2')):
    e = L.evenement('foe%s_tap' % f, 'NoeudEventClicObjet', cible='foe%s' % f)
    t = L.chaine(e, [('a%s_tour' % f, 'condition', {'condition': 'tour = 1'})])
    c1 = L.chaine(VRAI(t), [('a%s_c1' % f, 'condition', {'condition': 'sel = 1'})])
    for h, entree in (('1', VRAI(c1)), ('2', None)):
        if h == '2':
            c2 = L.chaine(FAUX(c1), [('a%s_c2' % f, 'condition', {'condition': 'sel = 2'})])
            entree = VRAI(c2)
        idm = 'walk%s%s' % (h, f)
        chemin_vers_objet(entree, idm, 'hero%s' % h, 'foe%s' % f, 8)
        L.chaine((idm, 'port_tout_de_suite', 0), [('%s_sel' % idm, 'modifier_variable', {'valeur': 0}, None, 'sel'),
                                                  ('%s_small' % idm, 'modifier_taille', {'x': 1, 'y': 1}, 'hero%s' % h)])
        appeler((idm, 'port_arrive', 1), '%s_hit' % idm, 'attaque%s%s' % (h, f), decalage_y=180)

# L'attaque : le monstre est détruit
for h in ('1', '2'):
    for f in ('1', '2'):
        e = evenement_local('atk%s%s' % (h, f), 'attaque%s%s' % (h, f))
        t = L.chaine(e, [('atk%s%s_fx' % (h, f), 'effet_particules', {'modele': 'Explosion', 'quantite': 30, 'couleur': '', 'taille': 1.3}, 'foe%s' % f),
                         ('atk%s%s_snd' % (h, f), 'jouer_son', {'fichier': SON + 'explosion.ogg', 'volume': 70}),
                         ('atk%s%s_del' % (h, f), 'detruire_objet', None, 'foe%s' % f),
                         ('atk%s%s_v' % (h, f), 'modifier_variable', {'valeur': 0}, None, 'vivant%s' % f),
                         ('atk%s%s_n' % (h, f), 'ajouter_variable', {'valeur': -1}, None, 'monstres'),
                         ('atk%s%s_txt' % (h, f), 'modifier_propriete', {'propriete': 'texte', 'valeur': '=monstres'}, 'foes_text'),
                         ('atk%s%s_c' % (h, f), 'condition', {'condition': 'monstres <= 0'})])
        appeler(VRAI(t), 'atk%s%s_win' % (h, f), 'victoire', decalage_y=0)
        appeler(FAUX(t), 'atk%s%s_end' % (h, f), 'fin_hero%s' % h, decalage_y=0)

# Un héros a fini son action : il devient gris ; si les deux ont joué, c'est aux monstres
for h in ('1', '2'):
    e = evenement_local('done%s' % h, 'fin_hero%s' % h)
    t = L.chaine(e, [('done%s_f' % h, 'modifier_variable', {'valeur': 1}, None, 'fini%s' % h),
                     ('done%s_g' % h, 'filtre_couleur', {'filtre': 'Noir et Blanc'}, 'hero%s' % h),
                     ('done%s_j' % h, 'ajouter_variable', {'valeur': 1}, None, 'joues'),
                     ('done%s_c' % h, 'condition', {'condition': 'joues >= 2'})])
    appeler(VRAI(t), 'done%s_go' % h, 'tour_monstres')

# Bouton « Fin du tour »
e = L.evenement('end_tap', 'NoeudEventClicObjet', cible='btn_end')
t = L.chaine(e, [('end_c', 'condition', {'condition': 'tour = 1'})])
appeler(VRAI(t), 'end_go', 'tour_monstres')

# Le tour des monstres : chacun va vers « son » héros pendant un moment, puis on s'arrête
e = evenement_local('foes', 'tour_monstres')
t = L.chaine(e, [('f_tour', 'modifier_variable', {'valeur': 2}, None, 'tour'),
                 ('f_txt', 'afficher_dialogue', {'cle': 'enemy_turn'}, 'turn_text'),
                 ('f_wait0', 'attendre', {'duree': 0.8}),
                 ('f_c1', 'condition', {'condition': 'vivant1 = 1'})])
chemin_vers_objet(VRAI(t), 'f_go1', 'foe1', 'hero1', 4)
appeler(('f_go1', 'port_arrive', 1), 'f_hit1', 'monstre_touche', decalage_y=180)
t = L.chaine(ENSUITE(t), [('f_c2', 'condition', {'condition': 'vivant2 = 1'})])
chemin_vers_objet(VRAI(t), 'f_go2', 'foe2', 'hero2', 4)
appeler(('f_go2', 'port_arrive', 1), 'f_hit2', 'monstre_touche', decalage_y=180)
t = L.chaine(ENSUITE(t), [('f_wait', 'attendre', {'duree': 1.6}), ('f_s1', 'condition', {'condition': 'vivant1 = 1'})])
L.action(VRAI(t), 'f_stop1', 'chemin_arreter', None, 'foe1')
t = L.chaine(ENSUITE(t), [('f_s2', 'condition', {'condition': 'vivant2 = 1'})])
L.action(VRAI(t), 'f_stop2', 'chemin_arreter', None, 'foe2')
appeler(ENSUITE(t), 'f_new', 'nouveau_tour')

# Un monstre touche un héros : une vie en moins
e = evenement_local('hit', 'monstre_touche')
t = L.chaine(e, [('h_v', 'ajouter_variable', {'valeur': -1}, None, 'vies'),
                 ('h_txt', 'modifier_propriete', {'propriete': 'texte', 'valeur': '=vies'}, 'lives_text'),
                 ('h_flash', 'flash_ecran', {'couleur': '#FF4040', 'intensite': 45, 'duree': 0.3}),
                 ('h_shake', 'tremblement_camera', {'intensite': 10, 'duree': 400}),
                 ('h_c', 'condition', {'condition': 'vies <= 0'})])
appeler(VRAI(t), 'h_lose', 'defaite')

# Nouveau tour : les héros redeviennent actifs
e = evenement_local('newturn', 'nouveau_tour')
L.chaine(e, [('n_tour', 'modifier_variable', {'valeur': 1}, None, 'tour'), ('n_sel', 'modifier_variable', {'valeur': 0}, None, 'sel'),
             ('n_joues', 'modifier_variable', {'valeur': 0}, None, 'joues'), ('n_f1', 'modifier_variable', {'valeur': 0}, None, 'fini1'),
             ('n_f2', 'modifier_variable', {'valeur': 0}, None, 'fini2'),
             ('n_g1', 'filtre_couleur', {'filtre': 'Aucun'}, 'hero1'), ('n_g2', 'filtre_couleur', {'filtre': 'Aucun'}, 'hero2'),
             ('n_txt', 'afficher_dialogue', {'cle': 'your_turn'}, 'turn_text')])

# Fin de partie
e = evenement_local('win', 'victoire')
L.chaine(e, [('w_tour', 'modifier_variable', {'valeur': 3}, None, 'tour'), ('w_txt', 'afficher_dialogue', {'cle': 'victory'}, 'turn_text'),
             ('w_fx', 'effet_particules', {'modele': 'Confettis', 'quantite': 150, 'couleur': '', 'taille': 1.5}, 'turn_text'),
             ('w_snd', 'jouer_son', {'fichier': SON + 'victoire.ogg', 'volume': 80}), ('w_wait', 'attendre', {'duree': 3}),
             ('w_again', 'recommencer_scene')])
e = evenement_local('lose', 'defaite')
L.chaine(e, [('l_tour', 'modifier_variable', {'valeur': 3}, None, 'tour'), ('l_txt', 'afficher_dialogue', {'cle': 'defeat'}, 'turn_text'),
             ('l_snd', 'jouer_son', {'fichier': SON + 'game_over.ogg', 'volume': 80}), ('l_wait', 'attendre', {'duree': 3}),
             ('l_again', 'recommencer_scene')])

scenes = [scene('Jeu', objets, P)]
VARIABLES = variables(P, [(n, 0) for n in ('tour', 'sel', 'joues', 'fini1', 'fini2', 'monstres', 'vivant1', 'vivant2', 'vies')])

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, scenes, {'Jeu': L.ranger().json()}, VARIABLES, ANIMS, TEXTES, pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Tactics demo', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'exemples')
    zipper_projet(p, os.path.join(sortie, 'tactics_demo.zip'))
    vue = [o for o in objets if o['nom'] not in ('terrain',)]
    im = dessiner(os.path.join(tmp, 'x.png'), vue, nets=True, textes={'turn_text': TEXTES['your_turn']['en'], 'lives_label': 'Lives', 'foes_label': 'Monsters', 'help_text': '', 'btn_end_text': 'End turn'})
    carte = im.crop((GX - 20, GY - 20, GX + 14 * CASE + 20, GY + 10 * CASE + 20))
    carre = Image.new('RGB', (carte.width, carte.width), (22, 48, 31))   # vignette carrée : la carte au centre
    carre.paste(carte, (0, (carte.width - carte.height) // 2))
    carre.resize((300, 300), Image.LANCZOS).save(os.path.join(sortie, 'tactics_demo.png'), optimize=True)
print('%d nœuds -> exemples/tactics_demo.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(os.path.join(sortie, 'tactics_demo.zip')) // 1024))
