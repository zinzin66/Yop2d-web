#!/usr/bin/env python3
"""Fabrique le TUTORIEL « Tactics tutorial » (version courte de Tactics demo : 1 héros, 1 monstre, avec cadres et post-it dans le Blueprint) :
exemples/tactics_tutorial.zip + exemples/tactics_tutorial.png.
Usage : python3 outils/creer_tutoriel_tactique.py <clone de zinzin66/yop2d-moteur, branche claude/discord-yop2d-config-ox8qgh>"""
import os, sys, json, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'tactique/'
NJ = 'assets_ludexa/Images/Ninja/'
SON = 'assets_ludexa/Sons/Yop2D/'
TILESET = NJ + 'Tuiles/tileset_ninja.png'
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
# nom : (image, colonne, ligne, fiche = (vie, attaque, défense, mouvement, portée))
HEROS = {'hero1': ('Personnages/ninja6', 1, 3, (20, 6, 2, 4, 1))}
MONSTRES = {'foe1': ('Monstres/monstre3', 12, 3, (12, 5, 1, 3, 1))}
IMAGES = {n: v[0] for n, v in list(HEROS.items()) + list(MONSTRES.items())}
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')

def coin(col, lig):
    return GX + col * CASE, GY + lig * CASE

def tous(en, fr, es, pt, de, it, ru, zh, ja):
    return dict(zip(['en', 'fr', 'es', 'pt', 'de', 'it', 'ru', 'zh', 'ja'], [en, fr, es, pt, de, it, ru, zh, ja]))
TEXTES = {
 'your_turn': {'fr': 'À ton tour', 'en': 'Your turn', 'es': 'Tu turno', 'de': 'Du bist dran', 'it': 'Tocca a te', 'pt': 'Sua vez',
               'ru': 'Твой ход', 'zh': '轮到你了', 'ja': 'あなたの番'},
 'enemy_turn': {'fr': 'Tour des monstres', 'en': 'Monsters\' turn', 'es': 'Turno de los monstruos', 'de': 'Die Monster sind dran',
                'it': 'Turno dei mostri', 'pt': 'Vez dos monstros', 'ru': 'Ход монстров', 'zh': '怪物的回合', 'ja': 'モンスターの番'},
 'victory': {'fr': 'Victoire !', 'en': 'Victory!', 'es': '¡Victoria!', 'de': 'Sieg!', 'it': 'Vittoria!', 'pt': 'Vitória!',
             'ru': 'Победа!', 'zh': '胜利！', 'ja': '勝利！'},
 'defeat': {'fr': 'Défaite…', 'en': 'Defeat…', 'es': 'Derrota…', 'de': 'Niederlage …', 'it': 'Sconfitta…', 'pt': 'Derrota…',
            'ru': 'Поражение…', 'zh': '失败……', 'ja': '敗北…'},
 'end_turn': {'fr': 'Fin du tour', 'en': 'End turn', 'es': 'Fin del turno', 'de': 'Zug beenden', 'it': 'Fine turno', 'pt': 'Fim do turno',
              'ru': 'Конец хода', 'zh': '结束回合', 'ja': 'ターン終了'},
 'wait': tous('Wait', 'Attendre', 'Esperar', 'Esperar', 'Warten', 'Aspetta', 'Ждать', '待机', 'まつ'),
 'too_far': tous('Too far!', 'Trop loin !', '¡Demasiado lejos!', 'Muito longe!', 'Zu weit!', 'Troppo lontano!', 'Слишком далеко!', '太远了！', '遠すぎる！'),
 'hint_pick': tous('Touch one of your heroes.', 'Touche un de tes héros.', 'Toca uno de tus héroes.', 'Toque em um dos seus heróis.', 'Tippe einen deiner Helden an.',
                   'Tocca uno dei tuoi eroi.', 'Нажми на одного из героев.', '点你的一个英雄。', 'ヒーローをタッチ。'),
 'hint_move': tous('Touch a blue cell to move there.', 'Touche une case bleue pour y aller.', 'Toca una casilla azul para ir.', 'Toque em uma casa azul para ir.',
                   'Tippe ein blaues Feld, um dorthin zu gehen.', 'Tocca una casella blu per andarci.', 'Нажми на синюю клетку, чтобы пойти.', '点蓝色格子前往。', '青いマスをタッチして移動。'),
 'hint_attack': tous('Touch a monster in the red zone, or Wait.', 'Touche un monstre dans la zone rouge, ou Attendre.', 'Toca un monstruo en la zona roja, o Esperar.',
                     'Toque em um monstro na zona vermelha, ou Esperar.', 'Tippe ein Monster in der roten Zone an, oder Warten.', 'Tocca un mostro nella zona rossa, o Aspetta.',
                     'Нажми на монстра в красной зоне или «Ждать».', '点红色区域内的怪物，或待机。', '赤い範囲のモンスターをタッチ、または「まつ」。'),
 'knight': tous('Knight', 'Chevalier', 'Caballero', 'Cavaleiro', 'Ritter', 'Cavaliere', 'Рыцарь', '骑士', '騎士'),
 'archer': tous('Archer', 'Archer', 'Arquero', 'Arqueiro', 'Bogenschütze', 'Arciere', 'Лучник', '弓箭手', '弓兵'),
 'orc': tous('Orc', 'Orc', 'Orco', 'Orc', 'Ork', 'Orco', 'Орк', '兽人', 'オーク'),
 'rat': tous('Rat', 'Rat', 'Rata', 'Rato', 'Ratte', 'Ratto', 'Крыса', '老鼠', 'ネズミ'),
}

# ---------------------------------------------------------------- objets
carte = decor_tuiles('carte', GX, GY, CARTE, prefixe=P, taille=CASE, tileset=TILESET)
carte['tuilesSolides'] = [False, False, False, False]   # ce sont les TERRAINS (terrains.json) qui bloquent
TERRAINS = {'terrains': [
    {'id': 't1', 'nom': 'Grass', 'couleur': argb('#6FBF73'), 'cout': 1, 'bloque': False, 'defense': 0, 'proprietes': {}},
    {'id': 't2', 'nom': 'Forest', 'couleur': argb('#2E7D32'), 'cout': 2, 'bloque': False, 'defense': 1, 'proprietes': {}},
    {'id': 't3', 'nom': 'Mountain', 'couleur': argb('#9AA3AE'), 'cout': 1, 'bloque': True, 'defense': 2, 'proprietes': {}},
    {'id': 't4', 'nom': 'Sand', 'couleur': argb('#E0C068'), 'cout': 2, 'bloque': False, 'defense': 0, 'proprietes': {}}],
    'tuiles': {TILESET: ['t1', 't2', 't3', 't4']}}
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F')), carte,
          objet('terrain', GX, GY, largeur=14 * CASE, hauteur=10 * CASE, z=1, prefixe=P, type='zone', estZoneDeClic=True)]
ANIMS = {}
def unite(nom, tag, col, lig, clic):
    x, y = coin(col, lig)
    o = objet(nom, x, y, NJ + IMAGES[nom] + '_bas_1.png', CASE, CASE, z=50, prefixe=P, tag=tag, estZoneDeClic=clic, estPhysique=True, estStatique=False,
              graviteScale=0.0, comportement='dessus', directions='4', commandes='aucune', animationsAuto=True, vitesseComportement=6.0)
    for etat in ('walk', 'idle'):
        for d in ('bas', 'haut', 'gauche', 'droite'):
            ANIMS['%s_%s_%s' % (nom, etat, d)] = [NJ + IMAGES[nom] + '_%s_%d.png' % (d, i) for i in (range(1, 5) if etat == 'walk' else [1])]
    return o
objets += [unite(n, 'joueur', v[1], v[2], True) for n, v in HEROS.items()] + [unite(n, 'ennemi', v[1], v[2], True) for n, v in MONSTRES.items()]
NOMS_UNITES = [('hero1', 'knight'), ('foe1', 'orc')]
objets += [texte('turn_text', 1240, 130, 640, 90, ' ', 56, OR, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
for i, (u, cle) in enumerate(NOMS_UNITES):
    y = 260 + i * 70
    objets += [texte('lab_' + u, 1240, y, 330, 60, ' ', 36, BLANC, z=60, prefixe=P, alignementTexte='DROITE', cheminPolice=None),
               texte('val_' + u, 1590, y - 4, 290, 70, '-', 40, VERT if u.startswith('hero') else ROUGE, z=60, prefixe=P, cheminPolice=None)]
objets += [texte('hint_text', 1240, 560, 640, 150, ' ', 30, BLANC, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
def bouton(nom, x, w):
    b = objet(nom, x, 760, largeur=w, hauteur=120, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#2B6CB0'), estZoneDeClic=True)
    return [b, texte(nom + '_text', 0, 28, w, 70, ' ', 42, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_wait', 1250, 290)

# ---------------------------------------------------------------- logique
L = Logique()
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)
def local(id, nom):
    return L.evenement(id, 'NoeudEventPersonnalise', {"Nom de l'événement": nom})
def appeler(depuis, id, nom, **kw):
    return L.action(depuis, id, 'appeler_evenement', {'evenement': nom}, **kw)
def dire(depuis, id, cle, cible):
    return L.action(depuis, id, 'afficher_dialogue', {'cle': cle}, cible)
def cond(depuis, id, texte_):
    return L.action(depuis, id, 'condition', {'condition': texte_})
def vie_texte(depuis, id, u):   # « 12 / 20 » dans le texte de l'unité
    return L.action(depuis, id, 'modifier_propriete', {'propriete': 'texte', 'valeur': '=%s.vie + " / " + %s.vie_max' % (u, u)}, 'val_' + u)
def var(depuis, id, nom, valeur):
    return L.action(depuis, id, 'modifier_variable', {'valeur': valeur}, None, nom)
ACC = {'colonne': '', 'ligne': ''}   # remplacés par les nœuds verts « Colonne touchée » / « Ligne touchée » plus bas
H, F = 'hero1', 'foe1'

# 1. Au démarrage
e = L.evenement('start', 'NoeudEventStart')
t = L.action(e, 'f_hero1', 'definir_fiche', dict(zip(['vie', 'attaque', 'defense', 'mouvement', 'portee'], HEROS[H][3])), H)
t = L.action(t, 'f_foe1', 'definir_fiche', dict(zip(['vie', 'attaque', 'defense', 'mouvement', 'portee'], MONSTRES[F][3])), F)
t = var(t, 's_etat', 'etat', 0)
t = dire(t, 'sl_hero1', 'knight', 'lab_hero1')
t = vie_texte(t, 'sv_hero1', H)
t = dire(t, 'sl_foe1', 'orc', 'lab_foe1')
t = vie_texte(t, 'sv_foe1', F)
t = dire(t, 's_wait', 'wait', 'btn_wait_text')
L.action(t, 's_go', 'tour_suivant', {'equipes': 'joueur,ennemi'})

# 2. Début du tour du joueur
e = local('tour_joueur', 'tour_joueur')
L.chaine(e, [('tj_etat', 'modifier_variable', {'valeur': 0}, None, 'etat'), ('tj_c', 'cacher_cases', {'zone': ''}),
             ('tj_a', 'modifier_taille', {'x': 1, 'y': 1}, H), ('tj_t', 'afficher_dialogue', {'cle': 'your_turn'}, 'turn_text'),
             ('tj_h', 'afficher_dialogue', {'cle': 'hint_pick'}, 'hint_text')])

# 3. Toucher le héros : cases bleues
e = L.evenement('pick_hero1', 'NoeudEventClicObjet', cible=H)
t = L.action(e, 'pk_tour', 'si_tour_de', {'equipe': 'joueur'})
t = cond(VRAI(t), 'pk_etat', 'etat < 2')
L.chaine(VRAI(t), [('pk_cache', 'cacher_cases', {'zone': ''}), ('pk_etat1', 'modifier_variable', {'valeur': 1}, None, 'etat'),
                   ('pk_big', 'modifier_taille', {'x': 1.25, 'y': 1.25}, H), ('pk_snd', 'jouer_son', {'fichier': SON + 'pop.ogg', 'volume': 60}),
                   ('pk_zone', 'montrer_cases', {'mode': 'zc_deplacement', 'pas': '=hero1.mouvement', 'couleur': '#4CC9F0', 'opacite': 40, 'contour': 'o_oui',
                                                  'chiffres': 'o_oui', 'murs': 'o_oui', 'bloquants': 'joueur,ennemi', 'terrains': '', 'zone': ''}, H),
                   ('pk_hint', 'afficher_dialogue', {'cle': 'hint_move'}, 'hint_text')])

# 4. Toucher le sol : si la case est bleue, le héros y va
e = L.evenement('ground', 'NoeudEventClicObjet', cible='terrain')
t = cond(e, 'g_etat', 'etat = 1')
a = L.action(VRAI(t), 'g_acc', 'si_case_accessible', dict(ACC, zone=''))
s = var(VRAI(a), 'g_mv', 'etat', 4)
L.action(s, 'g_go', 'chemin_vers_case', dict(ACC, vitesse=8, diagonales='false', bloquants='joueur,ennemi'), H)
appeler(('g_go', 'port_arrive', 1), 'g_arr', 'apres_deplacement')
dire(FAUX(a), 'g_far', 'too_far', 'hint_text')

# 5. Après le déplacement : zone d'attaque rouge
e = local('moved', 'apres_deplacement')
L.chaine(e, [('m_c', 'cacher_cases', {'zone': ''}), ('m_etat', 'modifier_variable', {'valeur': 2}, None, 'etat'),
             ('m_zone', 'montrer_cases', {'mode': 'zc_attaque', 'pas': '=hero1.portee', 'couleur': '#FF4040', 'opacite': 45, 'contour': 'o_oui',
                                          'chiffres': 'o_non', 'murs': 'o_non', 'bloquants': '', 'terrains': '', 'zone': 'attaque'}, H),
             ('m_hint', 'afficher_dialogue', {'cle': 'hint_attack'}, 'hint_text')])

# 6. Toucher le monstre dans la zone rouge : attaque
e = L.evenement('hit_foe1', 'NoeudEventClicObjet', cible=F)
t = cond(e, 'a_etat', 'etat = 2')
acc = L.action(VRAI(t), 'a_acc', 'si_case_accessible', dict(ACC, zone='attaque'))
L.action(VRAI(acc), 'a_hit', 'attaquer', {'puissance': 100, 'terrain': 'o_oui', 'minimum': 'o_oui', 'detruire': 'o_oui'}, H)
L.noeud('a_hit')['cibleNomB'] = F
v = vie_texte(('a_hit', 'port_vivant', 0), 'a_vie', F)
appeler(v, 'a_fin', 'fin_action')
L.action(('a_hit', 'port_detruit', 1), 'a_x', 'modifier_texte', {'valeur': 'X'}, 'val_' + F)
appeler(('a_x', 'port_suivant', 0), 'a_win', 'victoire')
dire(FAUX(acc), 'a_far', 'too_far', 'hint_text')

# 7. Fin de l'action du héros (et bouton « Attendre »)
e = local('fin_action', 'fin_action')
L.chaine(e, [('fa_j', 'marquer_joue', {}, H), ('fa_cache', 'cacher_cases', {'zone': ''}), ('fa_a', 'modifier_taille', {'x': 1, 'y': 1}, H),
             ('fa_etat', 'modifier_variable', {'valeur': 3}, None, 'etat'), ('fa_next', 'tour_suivant', {'equipes': 'joueur,ennemi'})])
e = L.evenement('btn_wait', 'NoeudEventClicObjet', cible='btn_wait')
t = cond(e, 'w_a', 'etat > 0')
t = cond(VRAI(t), 'w_b', 'etat < 3')
appeler(VRAI(t), 'w_go', 'fin_action')

# 8. Tour du monstre
e = local('tour_ennemi', 'tour_ennemi')
t = L.chaine(e, [('te_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('te_c', 'cacher_cases', {'zone': ''}),
                 ('te_txt', 'afficher_dialogue', {'cle': 'enemy_turn'}, 'turn_text'), ('te_hint', 'afficher_dialogue', {'cle': 'enemy_turn'}, 'hint_text'),
                 ('te_wait', 'attendre', {'duree': 0.6})])
L.action(t, 'te_go', 'chemin_vers_objet', {'vitesse': 12, 'diagonales': 'false', 'arret': 'ch_voisine', 'bloquants': 'joueur,ennemi'}, F)
L.noeud('te_go')['cibleNomB'] = H
appeler(('te_go', 'port_arrive', 1), 'te_arr', 'atk_foe1')
t = L.chaine(('te_go', 'port_tout_de_suite', 0), [('te_wait2', 'attendre', {'duree': 4.0}), ('te_stop', 'chemin_arreter', {}, F)])
L.action(t, 'te_next', 'tour_suivant', {'equipes': 'joueur,ennemi'})

# 9. Le monstre attaque
e = local('atk_foe1', 'atk_foe1')
L.action(e, 'at_hit', 'attaquer', {'puissance': 100, 'terrain': 'o_oui', 'minimum': 'o_oui', 'detruire': 'o_oui'}, F)
L.noeud('at_hit')['cibleNomB'] = H
L.chaine(('at_hit', 'port_vivant', 0), [('at_vie', 'modifier_propriete', {'propriete': 'texte', 'valeur': '=hero1.vie + " / " + hero1.vie_max'}, 'val_' + H),
                                         ('at_fx', 'flash_ecran', {'couleur': '#FF4040', 'intensite': 35, 'duree': 0.25})])
d = L.action(('at_hit', 'port_detruit', 1), 'at_x', 'modifier_texte', {'valeur': 'X'}, 'val_' + H)
appeler(d, 'at_lose', 'defaite')

# 10. Victoire et défaite
e = local('win', 'victoire')
L.chaine(e, [('w_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('w_c', 'cacher_cases', {'zone': ''}), ('w_txt', 'afficher_dialogue', {'cle': 'victory'}, 'turn_text'),
             ('w_fx', 'effet_particules', {'modele': 'Confettis', 'quantite': 150, 'couleur': '', 'taille': 1.5}, 'turn_text'),
             ('w_snd', 'jouer_son', {'fichier': SON + 'victoire.ogg', 'volume': 80}), ('w_wait', 'attendre', {'duree': 3}),
             ('w_again', 'recommencer_scene')])
e = local('lose', 'defaite')
L.chaine(e, [('l_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('l_c', 'cacher_cases', {'zone': ''}), ('l_txt', 'afficher_dialogue', {'cle': 'defeat'}, 'turn_text'),
             ('l_snd', 'jouer_son', {'fichier': SON + 'game_over.ogg', 'volume': 80}), ('l_wait', 'attendre', {'duree': 3}),
             ('l_again', 'recommencer_scene')])

# Nœuds verts « Colonne touchée » / « Ligne touchée » (pas de formule à écrire)
for n in list(L.noeuds):
    cle = n.get('cleNoeud')
    if cle in ('si_case_accessible', 'chemin_vers_case'):
        for champ, vert in (('colonne', 'valeur_colonne_touchee'), ('ligne', 'valeur_ligne_touchee')):
            vid = '%s_%s' % (n['id'], 'vc' if champ == 'colonne' else 'vl')
            L.noeuds.append({'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': vid, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': vert, 'parametres': {}})
            n['parametres']['%s.%s' % (cle, champ)] = '@valeur:' + vid

# ---------------------------------------------------------------- rangement, cadres et post-it
ECART_X, ECART_Y, MARGE, ENTETE = 90, 70, 30, 46
JAUNE, BLEU, VERT, ROSE, ORANGE, VIOLET = [c - (1 << 32) for c in (0xFFFFE082, 0xFF81D4FA, 0xFFA5D6A7, 0xFFF8BBD0, 0xFFFFCC80, 0xFFCE93D8)]
def poser(ids, x, y):
    bas = y
    for i in ids:
        n = L.noeud(i); n['x'], n['y'] = float(x), float(y)
        l, h = taille_noeud(n); x += l + ECART_X; bas = max(bas, y + h)
    return bas
def section(lignes, x, y):
    haut, y0, droite = y, y, x
    for ligne in lignes:
        ids, xl = (ligne[1], L.noeud(ligne[0])['x']) if isinstance(ligne, tuple) else (ligne, x)
        bas = poser(ids, xl, y0); y0 = bas + ECART_Y
        for i in ids:
            n = L.noeud(i); droite = max(droite, n['x'] + taille_noeud(n)[0])
    return (x, haut, droite, y0 - ECART_Y)
notes = []
def cadre(id, titre, texte, couleur, boite):
    x1, y1, x2, y2 = boite
    notes.append({'id': id, 'type': 'cadre', 'x': x1 - MARGE, 'y': y1 - MARGE - ENTETE, 'l': x2 - x1 + 2 * MARGE, 'h': y2 - y1 + 2 * MARGE + ENTETE,
                  'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})
def postit(id, titre, texte, couleur, x, y, l=380, h=210):
    notes.append({'id': id, 'type': 'postit', 'x': x, 'y': y, 'l': l, 'h': h, 'titre': titre, 'texte': texte, 'couleur': couleur, 'replie': False})

ESPACE = 2 * MARGE + ENTETE + 80
b = {}
y = 0
def bloc(nom, lignes):
    global y
    b[nom] = section(lignes, 0, y); y = b[nom][3] + ESPACE
bloc(1, [['start', 'f_hero1', 'f_foe1', 's_etat', 'sl_hero1', 'sv_hero1', 'sl_foe1', 'sv_foe1', 's_wait', 's_go']])
bloc(2, [['tour_joueur', 'tj_etat', 'tj_c', 'tj_a', 'tj_t', 'tj_h']])
bloc(3, [['pick_hero1', 'pk_tour', 'pk_etat', 'pk_cache', 'pk_etat1', 'pk_big', 'pk_snd', 'pk_zone', 'pk_hint']])
bloc(4, [['ground', 'g_etat', 'g_acc', 'g_mv', 'g_go', 'g_arr'], ('g_acc', ['g_far', 'g_acc_vc', 'g_acc_vl']), ('g_go', ['g_go_vc', 'g_go_vl'])])
bloc(5, [['moved', 'm_c', 'm_etat', 'm_zone', 'm_hint']])
bloc(6, [['hit_foe1', 'a_etat', 'a_acc', 'a_hit', 'a_vie', 'a_fin'], ('a_hit', ['a_x', 'a_win']), ('a_acc', ['a_far', 'a_acc_vc', 'a_acc_vl'])])
bloc(7, [['fin_action', 'fa_j', 'fa_cache', 'fa_a', 'fa_etat', 'fa_next'], ['btn_wait', 'w_a', 'w_b', 'w_go']])
bloc(8, [['tour_ennemi', 'te_etat', 'te_c', 'te_txt', 'te_hint', 'te_wait', 'te_go', 'te_wait2', 'te_stop', 'te_next'], ('te_go', ['te_arr'])])
bloc(9, [['atk_foe1', 'at_hit', 'at_vie', 'at_fx'], ('at_hit', ['at_x', 'at_lose'])])
bloc(10, [['win', 'w_etat', 'w_c', 'w_txt', 'w_fx', 'w_snd', 'w_wait', 'w_again'], ['lose', 'l_etat', 'l_c', 'l_txt', 'l_snd', 'l_wait', 'l_again']])

cadre('c1', 'Step 1 - At the start: unit sheets', 'When the game starts, "Give a unit sheet" gives each unit its life, attack, defense, movement and range. They become '
      'object variables you can read anywhere (for example hero1.movement). Then the texts are written and "Go to the next turn" starts the first team (joueur).', BLEU, b[1])
cadre('c2', 'Step 2 - The player\'s turn', 'Each team is a tag. "Go to the next turn" fires a local event named "tour_" + the team: here "tour_joueur". '
      'The variable "etat" says where we are: 0 = choose a hero, 1 = hero chosen, 2 = hero moved, 3 = done, 4 = monsters playing.', VERT, b[2])
cadre('c3', 'Step 3 - Touch the hero: blue cells', '"If it is the turn of" checks the team. "Show reachable cells" paints the cells the hero can reach with its movement '
      '(hero1.movement = 4 steps). Walls, mountains and other units block; forest and sand cost 2 steps. The numbers are the steps needed.', ORANGE, b[3])
cadre('c4', 'Step 4 - Touch a blue cell: the hero walks', '"If the cell is reachable" checks the touched cell. The two green nodes give its column and row '
      '(no formula to type). If yes, "Go to the cell (path)" walks the hero to the middle of the cell. When he arrives, the event "apres_deplacement" starts.', VIOLET, b[4])
cadre('c5', 'Step 5 - The red zone', 'Same node, other mode: "Attack" shows the cells within the hero\'s range (hero1.range) in red. '
      'It uses a zone name ("attaque") so the blue and red zones can exist together.', ROSE, b[5])
cadre('c6', 'Step 6 - Touch the monster: attack', 'If the touched cell is in the red zone, "Attack" computes the damage: attack - defense - terrain defense '
      '(the monster in a forest is harder to hit). Still alive: update the life text. No life left: the monster is destroyed and the player wins.', JAUNE, b[6])
cadre('c7', 'Step 7 - End of the hero\'s action', '"Mark as having played" remembers that the hero played this turn, then the turn passes to the monsters. '
      'The "Wait" button does the same without attacking.', BLEU, b[7])
cadre('c8', 'Step 8 - The monster\'s turn', 'The local event "tour_ennemi" starts by itself. "Go to an object (path)" walks the monster next to the hero (setting '
      '"Stop: next to the target"). The path is stopped after 4 seconds, then the turn goes back to the player.', VERT, b[8])
cadre('c9', 'Step 9 - The monster attacks', 'When he arrives, the monster attacks the hero with the same "Attack" node. If the hero has no life left, the game is lost.', ORANGE, b[9])
cadre('c10', 'Step 10 - Victory and defeat', 'Two local events: confetti and a sound for the victory, a sound for the defeat, then the scene restarts.', VIOLET, b[10])

xp = -470
postit('n_tags', 'Tags = teams', 'Heroes have the tag "joueur", monsters the tag "ennemi". The turn nodes and the blocking settings use these tags.', JAUNE, xp, b[2][1] - MARGE - ENTETE, h=190)
postit('n_green', 'Green nodes', 'A green node gives a value to a setting, no formula to type. Here "Touched column" and "Touched row".', VERT, xp, b[4][1] - MARGE - ENTETE)
postit('n_terrain', 'Terrains', 'Forest, sand and mountains come from the list of terrains of the project (tile editor > Terrains). Cost, blocking and defense are set there.',
       ORANGE, xp, b[3][1] - MARGE - ENTETE, h=230)
postit('n_event', 'Local events', 'A local event is a mini-script you start with "Call event". It avoids copying the same nodes twice.', ROSE, xp, b[7][1] - MARGE - ENTETE)

scenes = [scene('Jeu', objets, P)]
VARIABLES = variables(P, [('etat', 0)])
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    logique = L.json()
    logique['notes'] = notes
    ecrire_projet(p, scenes, {'Jeu': logique}, VARIABLES, ANIMS, TEXTES, pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Tactics tutorial', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    with open(os.path.join(p, 'terrains.json'), 'w') as f:
        json.dump(TERRAINS, f)
    sortie = os.path.join(SITE_RACINE, 'exemples')
    zipper_projet(p, os.path.join(sortie, 'tactics_tutorial.zip'))
    vue = [o for o in objets if o['nom'] not in ('terrain',)]
    im = dessiner(os.path.join(tmp, 'x.png'), vue, nets=True, textes={'turn_text': TEXTES['your_turn']['en'], 'btn_wait_text': 'Wait',
                                                                      'lab_hero1': 'Knight', 'lab_foe1': 'Orc', 'hint_text': ''})
    carte_im = im.crop((GX - 20, GY - 20, GX + 14 * CASE + 20, GY + 10 * CASE + 20))
    carre = Image.new('RGB', (carte_im.width, carte_im.width), (22, 48, 31))
    carre.paste(carte_im, (0, (carte_im.width - carte_im.height) // 2))
    carre.resize((300, 300), Image.LANCZOS).save(os.path.join(sortie, 'tactics_tutorial.png'), optimize=True)
print('%d nœuds, %d notes -> exemples/tactics_tutorial.zip (%d Ko)' % (len(L.noeuds), len(notes), os.path.getsize(os.path.join(sortie, 'tactics_tutorial.zip')) // 1024))
