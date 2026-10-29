#!/usr/bin/env python3
"""Fabrique l'exemple « Tactics demo » VERSION 3 (stratégie au tour par tour sur une grille) avec les nœuds « grille » du moteur :
exemples/tactics_demo.zip + exemples/tactics_demo.png (vignette 300 x 300).
Usage : python3 outils/creer_exemple_tactique.py <clone de zinzin66/yop2d-moteur, branche claude/discord-yop2d-config-ox8qgh>
Puis : entrée dans outils/exemples/source.json (version 3), python3 outils/generer_exemples.py, python3 outils/generer_accueil.py.

Le jeu : 2 héros (Chevalier : corps à corps ; Archer : portée 3), 2 monstres, carte de 14 x 10 cases avec TERRAINS (forêt = 2 pas et +1 défense,
sable = 2 pas, montagne = infranchissable ; liste dans terrains.json). À SON TOUR le joueur touche un héros : ses cases accessibles
apparaissent en bleu (coût du terrain compté, murs et unités bloquent) ; il touche une case bleue : le héros y va (chemin) ; la zone
d'attaque apparaît en rouge : il touche un monstre dans la zone (dégâts = attaque - défense - terrain) ou « Attendre ». Chaque héros joue
une fois par tour ; quand tous ont joué (ou « Fin du tour »), les monstres avancent à côté d'un héros et l'attaquent.
Nœuds : fiche d'unité, tours, cases accessibles, terrains, chemin vers une case, s'arrêter à côté de la cible, attaquer."""
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
HEROS = {'hero1': ('Personnages/ninja6', 1, 3, (20, 6, 2, 4, 1)), 'hero2': ('Personnages/ninja4', 1, 6, (14, 4, 0, 4, 3))}
MONSTRES = {'foe1': ('Monstres/monstre3', 12, 3, (12, 5, 1, 3, 1)), 'foe2': ('Monstres/monstre8', 12, 6, (8, 4, 0, 3, 1))}
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
NOMS_UNITES = [('hero1', 'knight'), ('hero2', 'archer'), ('foe1', 'orc'), ('foe2', 'rat')]
objets += [texte('turn_text', 1240, 130, 640, 90, ' ', 56, OR, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
for i, (u, cle) in enumerate(NOMS_UNITES):
    y = 260 + i * 70
    objets += [texte('lab_' + u, 1240, y, 330, 60, ' ', 36, BLANC, z=60, prefixe=P, alignementTexte='DROITE', cheminPolice=None),
               texte('val_' + u, 1590, y - 4, 290, 70, '-', 40, VERT if u.startswith('hero') else ROUGE, z=60, prefixe=P, cheminPolice=None)]
objets += [texte('hint_text', 1240, 560, 640, 150, ' ', 30, BLANC, z=60, prefixe=P, alignementTexte='CENTRE', cheminPolice=None)]
def bouton(nom, x, w):
    b = objet(nom, x, 760, largeur=w, hauteur=120, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#2B6CB0'), estZoneDeClic=True)
    return [b, texte(nom + '_text', 0, 28, w, 70, ' ', 42, BLANC, z=61, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_wait', 1250, 290) + bouton('btn_end', 1570, 300)

# ---------------------------------------------------------------- logique
L = Logique()
ENSUITE = lambda n: (n[0], 'port_ensuite', 2)
def local(id, nom):
    return L.evenement(id, 'NoeudEventPersonnalise', {"Nom de l'événement": nom})
def appeler(depuis, id, nom, **kw):
    return L.action(depuis, id, 'appeler_evenement', {'evenement': nom}, **kw)
def dire(depuis, id, cle, cible):
    return L.action(depuis, id, 'afficher_dialogue', {'cle': cle}, cible)
def var(depuis, id, nom, valeur):
    return L.action(depuis, id, 'modifier_variable', {'valeur': valeur}, None, nom)
def cond(depuis, id, texte_):
    return L.action(depuis, id, 'condition', {'condition': texte_})
ACC = {'colonne': '=colonne(doigt.x + camera.x)', 'ligne': '=ligne(doigt.y + camera.y)'}
def montrer_deplacement(depuis, id, h):
    return L.action(depuis, id, 'montrer_cases', {'mode': 'zc_deplacement', 'pas': '=%s.mouvement' % h, 'couleur': '#4CC9F0', 'opacite': 40, 'contour': 'o_oui',
                                                  'chiffres': 'o_oui', 'murs': 'o_oui', 'bloquants': 'joueur,ennemi', 'terrains': '', 'zone': ''}, h)
def montrer_attaque(depuis, id, h):
    return L.action(depuis, id, 'montrer_cases', {'mode': 'zc_attaque', 'pas': '=%s.portee' % h, 'couleur': '#FF4040', 'opacite': 45, 'contour': 'o_oui',
                                                  'chiffres': 'o_non', 'murs': 'o_non', 'bloquants': '', 'terrains': '', 'zone': 'attaque'}, h)
def attaquer(depuis, id, qui, cible):
    t = L.action(depuis, id, 'attaquer', {'puissance': 100, 'terrain': 'o_oui', 'minimum': 'o_oui', 'detruire': 'o_oui'}, qui)
    L.noeud(id)['cibleNomB'] = cible
    return t
def vie_texte(depuis, id, u):   # « 12 / 20 » dans le texte de l'unité
    return L.action(depuis, id, 'modifier_propriete', {'propriete': 'texte', 'valeur': '=%s.vie + " / " + %s.vie_max' % (u, u)}, 'val_' + u)

# Au démarrage : fiches d'unité, compteurs, textes, puis le tour du joueur commence
e = L.evenement('start', 'NoeudEventStart')
etapes = []
for u, v in list(HEROS.items()) + list(MONSTRES.items()):
    etapes.append(('f_' + u, 'definir_fiche', dict(zip(['vie', 'attaque', 'defense', 'mouvement', 'portee'], v[3])), u))
for nom, valeur in (('etat', 0), ('sel', 0), ('joues', 0), ('heros', 2), ('monstres', 2), ('vh1', 1), ('vh2', 1), ('vf1', 1), ('vf2', 1)):
    etapes.append(('s_' + nom, 'modifier_variable', {'valeur': valeur}, None, nom))
t = L.chaine(e, etapes)
for u, cle in NOMS_UNITES:
    t = dire(t, 'sl_' + u, cle, 'lab_' + u)
    t = vie_texte(t, 'sv_' + u, u)
t = dire(t, 's_wait', 'wait', 'btn_wait_text')
t = dire(t, 's_end', 'end_turn', 'btn_end_text')
L.action(t, 's_go', 'tour_suivant', {'equipes': 'joueur,ennemi'})

# Début du tour du joueur (lancé tout seul par « Passer au tour suivant » : événement local « tour_joueur »)
e = local('tour_joueur', 'tour_joueur')
t = L.chaine(e, [('tj_etat', 'modifier_variable', {'valeur': 0}, None, 'etat'), ('tj_sel', 'modifier_variable', {'valeur': 0}, None, 'sel'),
                 ('tj_joues', 'modifier_variable', {'valeur': 0}, None, 'joues'), ('tj_c', 'cacher_cases', {'zone': ''}),
                 ('tj_a', 'modifier_taille', {'x': 1, 'y': 1}, 'hero1'), ('tj_b', 'modifier_taille', {'x': 1, 'y': 1}, 'hero2'),
                 ('tj_t', 'afficher_dialogue', {'cle': 'your_turn'}, 'turn_text'), ('tj_h', 'afficher_dialogue', {'cle': 'hint_pick'}, 'hint_text')])

# 1. Choisir un héros : ses cases accessibles apparaissent
for h, autre in (('hero1', 'hero2'), ('hero2', 'hero1')):
    n = h[-1]
    e = L.evenement('pick_' + h, 'NoeudEventClicObjet', cible=h)
    t = L.action(e, 'pk_tour_' + h, 'si_tour_de', {'equipe': 'joueur'})
    t = cond(VRAI(t), 'pk_etat_' + h, 'etat < 2')
    t = L.action(VRAI(t), 'pk_joue_' + h, 'si_a_joue', {}, h)
    L.chaine(FAUX(t), [('pk_cache_' + h, 'cacher_cases', {'zone': ''}), ('pk_sel_' + h, 'modifier_variable', {'valeur': int(n)}, None, 'sel'),
                       ('pk_etat1_' + h, 'modifier_variable', {'valeur': 1}, None, 'etat'),
                       ('pk_big_' + h, 'modifier_taille', {'x': 1.25, 'y': 1.25}, h), ('pk_small_' + h, 'modifier_taille', {'x': 1, 'y': 1}, autre),
                       ('pk_snd_' + h, 'jouer_son', {'fichier': SON + 'pop.ogg', 'volume': 60})])
    t2 = montrer_deplacement(('pk_snd_' + h, 'port_suivant', 0), 'pk_zone_' + h, h)
    dire(t2, 'pk_hint_' + h, 'hint_move', 'hint_text')

# 2. Toucher le sol : si la case est bleue, le héros choisi y va
e = L.evenement('ground', 'NoeudEventClicObjet', cible='terrain')
t = cond(e, 'g_etat', 'etat = 1')
t = cond(VRAI(t), 'g_sel', 'sel = 1')
for h, depuis in (('hero1', VRAI(t)), ('hero2', FAUX(t))):
    a = L.action(depuis, 'g_acc_' + h, 'si_case_accessible', dict(ACC, zone=''))
    s = var(VRAI(a), 'g_mv_' + h, 'etat', 4)
    go = L.action(s, 'g_go_' + h, 'chemin_vers_case', dict(ACC, vitesse=8, diagonales='false', bloquants='joueur,ennemi'), h)
    appeler(('g_go_' + h, 'port_arrive', 1), 'g_arr_' + h, 'apres_deplacement', decalage_y=170)
    dire(FAUX(a), 'g_far_' + h, 'too_far', 'hint_text')

# 3. Après le déplacement : la zone d'attaque apparaît en rouge
e = local('moved', 'apres_deplacement')
t = L.chaine(e, [('m_c', 'cacher_cases', {'zone': ''}), ('m_etat', 'modifier_variable', {'valeur': 2}, None, 'etat'), ('m_sel', 'condition', {'condition': 'sel = 1'})])
a1 = montrer_attaque(VRAI(t), 'm_a1', 'hero1')
a2 = montrer_attaque(FAUX(t), 'm_a2', 'hero2')
dire(ENSUITE(t), 'm_hint', 'hint_attack', 'hint_text')

# 4. Toucher un monstre dans la zone rouge : le héros choisi l'attaque
for f in MONSTRES:
    fn = f[-1]
    e = L.evenement('hit_' + f, 'NoeudEventClicObjet', cible=f)
    t = cond(e, 'a_etat_' + f, 'etat = 2')
    t = cond(VRAI(t), 'a_sel_' + f, 'sel = 1')
    for h, depuis in (('hero1', VRAI(t)), ('hero2', FAUX(t))):
        acc = L.action(depuis, 'a_acc_%s_%s' % (f, h), 'si_case_accessible', dict(ACC, zone='attaque'))
        hit = attaquer(VRAI(acc), 'a_hit_%s_%s' % (f, h), h, f)
        v = vie_texte(('a_hit_%s_%s' % (f, h), 'port_vivant', 0), 'a_vie_%s_%s' % (f, h), f)
        appeler(v, 'a_fin_%s_%s' % (f, h), 'fin_action')
        d = L.action(('a_hit_%s_%s' % (f, h), 'port_detruit', 1), 'a_x_%s_%s' % (f, h), 'modifier_texte', {'valeur': 'X'}, 'val_' + f, decalage_y=150)
        d = L.action(d, 'a_n_%s_%s' % (f, h), 'ajouter_variable', {'valeur': -1}, None, 'monstres')
        d = L.action(d, 'a_v_%s_%s' % (f, h), 'modifier_variable', {'valeur': 0}, None, 'vf' + fn)
        d = cond(d, 'a_w_%s_%s' % (f, h), 'monstres <= 0')
        appeler(VRAI(d), 'a_win_%s_%s' % (f, h), 'victoire')
        appeler(FAUX(d), 'a_cont_%s_%s' % (f, h), 'fin_action')
        dire(FAUX(acc), 'a_far_%s_%s' % (f, h), 'too_far', 'hint_text')

# 5. Fin de l'action d'un héros : il a joué ; quand tous ont joué, les monstres jouent
e = local('fin_action', 'fin_action')
t = cond(e, 'fa_sel', 'sel = 1')
L.action(VRAI(t), 'fa_j1', 'marquer_joue', {}, 'hero1')
L.action(FAUX(t), 'fa_j2', 'marquer_joue', {}, 'hero2', decalage_y=150)
t = L.chaine(ENSUITE(t), [('fa_cache', 'cacher_cases', {'zone': ''}), ('fa_a', 'modifier_taille', {'x': 1, 'y': 1}, 'hero1'),
                          ('fa_b', 'modifier_taille', {'x': 1, 'y': 1}, 'hero2'), ('fa_etat', 'modifier_variable', {'valeur': 0}, None, 'etat'),
                          ('fa_sel0', 'modifier_variable', {'valeur': 0}, None, 'sel'), ('fa_n', 'ajouter_variable', {'valeur': 1}, None, 'joues'),
                          ('fa_hint', 'afficher_dialogue', {'cle': 'hint_pick'}, 'hint_text'), ('fa_c', 'condition', {'condition': 'joues >= heros'})])
L.action(VRAI(t), 'fa_next', 'tour_suivant', {'equipes': 'joueur,ennemi'})

# 6. Boutons « Attendre » (le héros choisi ne fait rien de plus) et « Fin du tour »
e = L.evenement('btn_wait', 'NoeudEventClicObjet', cible='btn_wait')
t = cond(e, 'w_a', 'etat > 0')
t = cond(VRAI(t), 'w_b', 'etat < 3')
appeler(VRAI(t), 'w_go', 'fin_action')
e = L.evenement('btn_end', 'NoeudEventClicObjet', cible='btn_end')
t = L.action(e, 'e_tour', 'si_tour_de', {'equipe': 'joueur'})
t = cond(VRAI(t), 'e_etat', 'etat < 3')
L.chaine(VRAI(t), [('e_cache', 'cacher_cases', {'zone': ''}), ('e_a', 'modifier_taille', {'x': 1, 'y': 1}, 'hero1'),
                   ('e_b', 'modifier_taille', {'x': 1, 'y': 1}, 'hero2'), ('e_next', 'tour_suivant', {'equipes': 'joueur,ennemi'})])

# 7. Tour des monstres (lancé tout seul : événement local « tour_ennemi ») : chacun va à côté d'un héros vivant et l'attaque
e = local('tour_ennemi', 'tour_ennemi')
t = L.chaine(e, [('te_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('te_c', 'cacher_cases', {'zone': ''}),
                 ('te_txt', 'afficher_dialogue', {'cle': 'enemy_turn'}, 'turn_text'), ('te_hint', 'afficher_dialogue', {'cle': 'enemy_turn'}, 'hint_text'),
                 ('te_wait', 'attendre', {'duree': 0.6})])
for f in MONSTRES:
    fn = f[-1]
    t = cond(t, 'te_v_' + f, 'vf%s = 1' % fn)
    pere = VRAI(t)
    for h, autre in (('hero1', 'hero2'), ('hero2', 'hero1')):
        pn = h[-1]
        c = cond(pere, 'te_h_%s_%s' % (f, h), 'vh%s = 1' % pn)
        go = L.action(VRAI(c), 'te_go_%s_%s' % (f, h), 'chemin_vers_objet', {'vitesse': 12, 'diagonales': 'false', 'arret': 'ch_voisine', 'bloquants': 'joueur,ennemi'}, f)
        L.noeud('te_go_%s_%s' % (f, h))['cibleNomB'] = h
        appeler(('te_go_%s_%s' % (f, h), 'port_arrive', 1), 'te_arr_%s_%s' % (f, h), 'atk_%s_%s' % (f, h), decalage_y=170)
        pere = FAUX(c)   # ce héros n'est plus là : on essaie l'autre
    t = (t[0], 'port_ensuite', 2)
t = L.chaine(t, [('te_wait2', 'attendre', {'duree': 4.0}), ('te_stop1', 'chemin_arreter', {}, 'foe1'), ('te_stop2', 'chemin_arreter', {}, 'foe2')])
L.action(t, 'te_next', 'tour_suivant', {'equipes': 'joueur,ennemi'})

# 8. Un monstre attaque un héros
for f in MONSTRES:
    for h in HEROS:
        pn = h[-1]
        e = local('atk_%s_%s' % (f, h), 'atk_%s_%s' % (f, h))
        hit = attaquer(e, 'at_hit_%s_%s' % (f, h), f, h)
        v = L.chaine(('at_hit_%s_%s' % (f, h), 'port_vivant', 0), [('at_vie_%s_%s' % (f, h), 'modifier_propriete', {'propriete': 'texte', 'valeur': '=%s.vie + " / " + %s.vie_max' % (h, h)}, 'val_' + h),
                                                                     ('at_fx_%s_%s' % (f, h), 'flash_ecran', {'couleur': '#FF4040', 'intensite': 35, 'duree': 0.25})])
        d = L.action(('at_hit_%s_%s' % (f, h), 'port_detruit', 1), 'at_x_%s_%s' % (f, h), 'modifier_texte', {'valeur': 'X'}, 'val_' + h, decalage_y=150)
        d = L.action(d, 'at_n_%s_%s' % (f, h), 'ajouter_variable', {'valeur': -1}, None, 'heros')
        d = L.action(d, 'at_v_%s_%s' % (f, h), 'modifier_variable', {'valeur': 0}, None, 'vh' + pn)
        d = cond(d, 'at_w_%s_%s' % (f, h), 'heros <= 0')
        appeler(VRAI(d), 'at_lose_%s_%s' % (f, h), 'defaite')

# Fin de partie
e = local('win', 'victoire')
L.chaine(e, [('w_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('w_c', 'cacher_cases', {'zone': ''}), ('w_txt', 'afficher_dialogue', {'cle': 'victory'}, 'turn_text'),
             ('w_fx', 'effet_particules', {'modele': 'Confettis', 'quantite': 150, 'couleur': '', 'taille': 1.5}, 'turn_text'),
             ('w_snd', 'jouer_son', {'fichier': SON + 'victoire.ogg', 'volume': 80}), ('w_wait', 'attendre', {'duree': 3}),
             ('w_again', 'recommencer_scene')])
e = local('lose', 'defaite')
L.chaine(e, [('l_etat', 'modifier_variable', {'valeur': 4}, None, 'etat'), ('l_c', 'cacher_cases', {'zone': ''}), ('l_txt', 'afficher_dialogue', {'cle': 'defeat'}, 'turn_text'),
             ('l_snd', 'jouer_son', {'fichier': SON + 'game_over.ogg', 'volume': 80}), ('l_wait', 'attendre', {'duree': 3}),
             ('l_again', 'recommencer_scene')])

# Règle des formules : pas de colonne(doigt.x + camera.x) écrit à la main : on branche les nœuds verts « Colonne touchée » / « Ligne touchée »
for n in list(L.noeuds):
    cle = n.get('cleNoeud')
    if cle in ('si_case_accessible', 'chemin_vers_case'):
        for champ, vert in (('colonne', 'valeur_colonne_touchee'), ('ligne', 'valeur_ligne_touchee')):
            vid = '%s_%s' % (n['id'], 'vc' if champ == 'colonne' else 'vl')
            L.noeuds.append({'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': vid, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': vert, 'parametres': {}})
            n['parametres']['%s.%s' % (cle, champ)] = '@valeur:' + vid
scenes = [scene('Jeu', objets, P)]
VARIABLES = variables(P, [(n, 0) for n in ('etat', 'sel', 'joues', 'heros', 'monstres', 'vh1', 'vh2', 'vf1', 'vf2')])
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, scenes, {'Jeu': L.ranger().json()}, VARIABLES, ANIMS, TEXTES, pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Tactics demo', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    with open(os.path.join(p, 'terrains.json'), 'w') as f:
        json.dump(TERRAINS, f)
    sortie = os.path.join(SITE_RACINE, 'exemples')
    zipper_projet(p, os.path.join(sortie, 'tactics_demo.zip'))
    vue = [o for o in objets if o['nom'] not in ('terrain',)]
    im = dessiner(os.path.join(tmp, 'x.png'), vue, nets=True, textes={'turn_text': TEXTES['your_turn']['en'], 'btn_wait_text': 'Wait', 'btn_end_text': 'End turn',
                                                                      'lab_hero1': 'Knight', 'lab_hero2': 'Archer', 'lab_foe1': 'Orc', 'lab_foe2': 'Rat', 'hint_text': ''})
    carte_im = im.crop((GX - 20, GY - 20, GX + 14 * CASE + 20, GY + 10 * CASE + 20))
    carre = Image.new('RGB', (carte_im.width, carte_im.width), (22, 48, 31))
    carre.paste(carte_im, (0, (carte_im.width - carte_im.height) // 2))
    carre.resize((300, 300), Image.LANCZOS).save(os.path.join(sortie, 'tactics_demo.png'), optimize=True)
print('%d nœuds -> exemples/tactics_demo.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(os.path.join(sortie, 'tactics_demo.zip')) // 1024))
