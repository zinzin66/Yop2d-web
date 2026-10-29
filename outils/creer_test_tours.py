#!/usr/bin/env python3
"""Projet de TEST des nœuds « tours » (grille, étape 2) : tests/tours-test.zip, à importer dans une version de test du moteur
qui contient « Passer au tour suivant », « Si c'est le tour de… », « Marquer comme ayant joué », « Si l'unité a déjà joué »
et le nœud vert « Numéro du tour » (moteur : branche claude/discord-yop2d-config-ox8qgh, à partir du commit 817d85c).
Usage : python3 outils/creer_test_tours.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test : 2 héros (tag joueur) et 2 monstres (tag ennemi). Au démarrage le tour du JOUEUR commence. Toucher un héros
= il joue (une seule fois par tour ; 2e fois : « déjà joué »). Bouton « Fin du tour » = tour des monstres (1,5 s) puis retour
au joueur, le numéro du tour augmente. Toucher pendant le tour des monstres : « pas ton tour »."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'tours_test/'
NJ = 'assets_ludexa/Images/Ninja/'
BLANC, OR, VERT, ROUGE = argb('#FFFFFF'), argb('#FFD166'), argb('#7BE0A0'), argb('#FF7B7B')
objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F'))]
unites = [('hero1', 'ninja6', 300, 300, 'joueur'), ('hero2', 'ninja4', 300, 600, 'joueur'),
          ('foe1', 'monstre9', 900, 300, 'ennemi'), ('foe2', 'monstre9', 900, 600, 'ennemi')]
for nom, img, x, y, tag in unites:
    objets.append(objet(nom, x, y, NJ + ('Personnages/' if 'ninja' in img else 'Monstres/') + img + '_bas_1.png', 160, 160, z=50,
                        prefixe=P, tag=tag, estZoneDeClic=True))
objets += [texte('info', 1240, 60, 640, 300, 'TURNS TEST\nTap a hero: it plays (once per turn).\nTap "End turn": the monsters play, then it is your turn again.',
                 32, OR, z=60, prefixe=P, cheminPolice=None),
           texte('etat', 1240, 380, 640, 80, '-', 56, VERT, z=60, prefixe=P, cheminPolice=None),
           texte('numero', 1240, 480, 640, 70, '-', 44, BLANC, z=60, prefixe=P, cheminPolice=None),
           texte('msg', 1240, 580, 640, 140, '-', 40, BLANC, z=60, prefixe=P, cheminPolice=None)]
bouton = objet('btn_end', 1300, 820, largeur=520, hauteur=120, z=60, prefixe=P, afficherFondColore=True, couleur=argb('#2B6CB0'), estZoneDeClic=True)
objets += [bouton, texte('btn_end_text', 0, 28, 520, 70, 'End turn', 46, BLANC, z=61, prefixe=P, parentId=bouton['id'],
                         alignementTexte='CENTRE', cheminPolice=None)]

L = Logique()
def vert(id, cle, parametres=None, cible=None):
    n = {'classeType': 'com.ludexa.moteur.NoeudGenerique', 'id': id, 'portsEntree': [], 'x': 0.0, 'y': 0.0, 'cleNoeud': cle,
         'parametres': {cle + '.' + k: str(v) for k, v in (parametres or {}).items()}}
    if cible: n['cibleNom'] = cible
    L.noeuds.append(n)
def brancher(noeud, reglage, vert_id):
    L.noeud(noeud)['parametres'][reglage] = '@valeur:' + vert_id
def dire(id, texte_):
    return (id, 'modifier_texte', {'valeur': texte_}, 'msg')

e = L.evenement('start', 'NoeudEventStart', sortie='Suivant')
L.action(e, 'go', 'tour_suivant', {'equipes': 'joueur,ennemi'})
e = L.evenement('tour_joueur', 'NoeudEventPersonnalise', {"Nom de l'événement": 'tour_joueur'})
L.chaine(e, [('t_j1', 'modifier_texte', {'valeur': 'YOUR TURN'}, 'etat'), dire('t_j2', 'Your heroes can play.')])
e = L.evenement('tour_ennemi', 'NoeudEventPersonnalise', {"Nom de l'événement": 'tour_ennemi'})
L.chaine(e, [('t_e1', 'modifier_texte', {'valeur': 'MONSTERS TURN'}, 'etat'), dire('t_e2', 'The monsters play...'),
             ('t_e3', 'attendre', {'duree': 1.5}), ('t_e4', 'tour_suivant', {'equipes': 'joueur,ennemi'})])
for h in ('hero1', 'hero2'):
    e = L.evenement('clic_' + h, 'NoeudEventClicObjet', cible=h)
    t = L.chaine(e, [('c_%s_t' % h, 'si_tour_de', {'equipe': 'joueur'})])
    L.chaine((t[0], 'port_faux', 1), [dire('c_%s_non' % h, 'Not your turn!')])
    j = L.chaine(VRAI(t), [('c_%s_j' % h, 'si_a_joue', {}, h)])
    L.chaine((j[0], 'port_vrai', 0), [dire('c_%s_deja' % h, h + ' already played this turn!')])
    L.chaine((j[0], 'port_faux', 1), [('c_%s_m' % h, 'marquer_joue', {}, h), dire('c_%s_ok' % h, h + ' plays!')])
e = L.evenement('clic_fin', 'NoeudEventClicObjet', cible='btn_end')
L.chaine(e, [('f_t', 'si_tour_de', {'equipe': 'joueur'})])
L.action(VRAI(('f_t', '', 0)), 'f_go', 'tour_suivant', {'equipes': 'joueur,ennemi'})
e = L.evenement('every_frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'num', 'modifier_texte', {'valeur': ''}, 'numero')
vert('g_num', 'valeur_numero_tour'); brancher('num', 'modifier_texte.valeur', 'g_num')
logique = L.ranger().json()

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Jeu', objets, P)], {'Jeu': logique}, [], pixels_nets=True)
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test tours', 'dateCreation': '2026-10-25 12:00:00', 'dateModif': '2026-10-25 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'tours-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/tours-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
