#!/usr/bin/env python3
"""Projet de TEST du KIT TACTIQUE : tests/kit-test-simple.zip, à importer dans une version de test du moteur qui contient le kit
(branche claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_kit.py <clone de zinzin66/yop2d-moteur>
Grille de 12 x 8 cases de 80 px. Un lancier (equipe « joueur », tags « lance »), un cavalier lourd et un archer
(equipe « ennemi »). Le fichier donnees.txt du projet décrit les unités, les états Poison et Lent, la règle
« lance > cavalerie = 150 » et une colline (hauteur 2). Les boutons à droite testent chaque nœud ; la ligne du haut
affiche les statistiques. Le lancier porte un dessin avec des parties ROSES : « Couleur d'équipe » les passe en bleu."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
import commun
from commun import *
from PIL import Image, ImageDraw

commun.taille_image = lambda chemin: (64, 64)
P = 'kit_test/'
CASE = 80
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')
X0, Y0 = 80, 160

DONNEES = """# Données du jeu de test (Yop2D)
unite Lancier: vie=12, attaque=5, defense=1, mouvement=4, portee=1, vision=3, tags=lance
unite Cavalier: vie=14, attaque=6, defense=2, mouvement=5, portee=1, tags=cavalerie lourd
unite Archer: vie=8, attaque=4, defense=0, mouvement=3, portee=3, tags=archer
etat Poison: duree=2, degats=2
etat Lent: duree=2, stat=mouvement, delta=-2
regle: lance > cavalerie = 150
hauteur 1,2 = 2
hauteur 2,2 = 2
"""

objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P, afficherFondColore=True, couleur=argb('#16301F'))]
for c in range(12):
    for l in range(8):
        objets.append(objet('case_%d_%d' % (c, l), X0 + c * CASE, Y0 + l * CASE, largeur=CASE - 2, hauteur=CASE - 2, z=-50, prefixe=P,
                            afficherFondColore=True, couleur=argb('#1F4D2E' if (c + l) % 2 == 0 else '#245A35')))
def unite(nom, c, l, couleur, tag, image=None):
    return objet(nom, X0 + c * CASE + 8, Y0 + l * CASE + 8, image=image, largeur=CASE - 18, hauteur=CASE - 18, z=50, prefixe=P,
                 afficherFondColore=image is None, couleur=argb(couleur), tag=tag)
objets += [unite('lancier', 1, 4, '#7FB4FF', 'joueur', 'assets_ludexa/Images/soldat.png'), unite('cavalier', 5, 4, '#E0524A', 'ennemi'),
           unite('archer', 8, 6, '#C79BFF', 'ennemi')]
for nom in ('lancier', 'cavalier', 'archer'):
    o = next(x for x in objets if x['nom'] == nom)
    objets.append(texte('n_' + nom, o['x'] - 20, o['y'] + 56, 100, 30, nom, 22, BLANC, z=60, prefixe=P, cheminPolice=None, alignementTexte='CENTRE'))
objets.append(texte('info', 40, 20, 1840, 120, '-', 30, OR, z=60, prefixe=P, cheminPolice=None))
objets.append(texte('msg', 40, 840, 1000, 80, 'Touche un bouton a droite. Pour recommencer : arrete le jeu puis relance.', 34, BLANC, z=60, prefixe=P, cheminPolice=None))

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
prec = e
for i, (nid, cle, regl, cible) in enumerate([('d1', 'appliquer_donnees', {'nom': 'Lancier'}, 'lancier'), ('d2', 'appliquer_donnees', {'nom': 'Cavalier'}, 'cavalier'),
             ('d3', 'appliquer_donnees', {'nom': 'Archer'}, 'archer'),
             ('s1', 'modifier_stat', {'stat': 'niveau', 'operation': 'st_o_fixer', 'valeur': 1}, 'lancier'),
             ('s2', 'modifier_stat', {'stat': 'xp', 'operation': 'st_o_fixer', 'valeur': 0}, 'lancier'),
             ('s3', 'modifier_stat', {'stat': 'etat_poison', 'operation': 'st_o_fixer', 'valeur': 0}, 'cavalier')]):
    prec = L.action(prec, nid, cle, regl, cible)
    if cle == 'appliquer_donnees':
        prec = (nid, 'port_trouve', 0)
e = L.evenement('frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'show', 'modifier_propriete', {'propriete': 'texte', 'valeur': '="Vie du lancier (bleu) : " + lancier.vie + "      Vie du cavalier (rouge) : " + cavalier.vie'}, 'info')

def msg(txt):
    return {'propriete': 'texte', 'valeur': txt}
def bouton(i, nom):
    bx, by = 1100, 220 + i * 150
    objets.append(objet('b%d' % i, bx, by, largeur=780, hauteur=110, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#2B3A55'), tag='btn%d' % i))
    objets.append(texte('t%d' % i, bx + 16, by + 28, 750, 60, nom, 30, BLANC, z=6, prefixe=P, cheminPolice=None, tag='btn%d' % i))
    return L.evenement('tap%d' % i, 'NoeudEventClicObjet', cible='tag:btn%d' % i)
BLANC_TXT = 'Touche un bouton a droite. Pour recommencer : arrete le jeu (carre) puis relance (triangle).'
# 1. attaque avec règle de tags, perforation et riposte
e = bouton(0, '1. Le lancier attaque le cavalier')
n = L.action(e, 'a0', 'attaquer', {'puissance': 100, 'terrain': 'o_non', 'minimum': 'o_oui', 'detruire': 'o_oui', 'perforation': 30, 'riposte': 100}, 'lancier')
L.noeud('a0')['cibleNomB'] = 'cavalier'
L.action((n[0], 'port_vivant', 0), 'm0', 'modifier_propriete', msg('Le cavalier a perdu de la vie. Il a rendu un coup : le lancier aussi.'), 'msg')
# 2. poison : donné puis deux "tour suivant" (le poison tombe au début du tour des ennemis)
e = bouton(1, '2. Poison sur le cavalier')
n = L.action(e, 'p1', 'donner_etat', {'etat': 'Poison'}, 'cavalier')
n = L.action(n, 'p2', 'tour_suivant', {'equipes': 'joueur,ennemi'})
n = L.action(n, 'p3', 'tour_suivant', {'equipes': 'joueur,ennemi'})
L.action(n, 'm1', 'modifier_propriete', msg('Poison : le cavalier perd 2 de vie a chaque tour des ennemis.'), 'msg')
# 3. l'IA joue
e = bouton(2, '3. Le cavalier joue tout seul (IA)')
n = L.action(e, 'i2', 'ia_jouer', {'ennemis': 'joueur', 'style': 'ia_agressif', 'vitesse': 10}, 'cavalier')
s2 = L.action((n[0], 'port_arrive', 0), 'si2', 'si_stat', {'stat': 'cible_ia', 'comparaison': 'st_c_ge', 'valeur': 1}, 'cavalier')
at = L.action((s2[0], 'port_vrai', 0), 'at2', 'attaquer', {'puissance': 100, 'terrain': 'o_non', 'minimum': 'o_oui', 'detruire': 'o_oui', 'riposte': 100}, 'cavalier')
L.noeud('at2')['cibleNomB'] = '__OBJET_IMPLIQUE__'
L.action((at[0], 'port_vivant', 0), 'm2', 'modifier_propriete', msg('Le cavalier est venu tout seul et a attaque le lancier.'), 'msg')
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Test', objets, P)], {'Test': logique}, [])
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test kit tactique simple', 'dateCreation': '2026-10-29 12:00:00', 'dateModif': '2026-10-29 12:00:00'})
    os.makedirs(os.path.join(p, 'assets_ludexa', 'Textes'), exist_ok=True)
    lib = os.path.join(tmp, 'lib'); os.makedirs(os.path.join(lib, 'assets_ludexa', 'Images'), exist_ok=True)
    ancien = commun.fichier_biblio
    commun.fichier_biblio = lambda c: os.path.join(lib, c) if c == 'assets_ludexa/Images/soldat.png' else ancien(c)
    with open(os.path.join(p, 'assets_ludexa', 'Textes', 'donnees.txt'), 'w', encoding='utf-8') as f:
        f.write(DONNEES)
    # un petit soldat dessiné : corps gris, manteau et plumet ROSES (#FF00FF, avec ombres) à remplacer par la couleur d'équipe
    im = Image.new('RGBA', (64, 64), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    dr.ellipse((22, 4, 42, 24), fill=(205, 200, 190, 255))                       # tête
    dr.polygon([(32, 0), (26, 10), (38, 10)], fill=(255, 0, 255, 255))           # plumet rose
    dr.rectangle((20, 24, 44, 52), fill=(255, 0, 255, 255)); dr.rectangle((20, 40, 44, 52), fill=(170, 0, 170, 255))   # manteau rose + ombre
    dr.rectangle((24, 52, 30, 62), fill=(120, 120, 130, 255)); dr.rectangle((34, 52, 40, 62), fill=(120, 120, 130, 255))   # jambes
    dr.rectangle((48, 8, 51, 58), fill=(150, 110, 60, 255)); dr.polygon([(49, 0), (45, 10), (54, 10)], fill=(200, 200, 210, 255))   # lance
    im.save(os.path.join(lib, 'assets_ludexa', 'Images', 'soldat.png'))
    sortie = os.path.join(SITE_RACINE, 'tests', 'kit-test-simple.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/kit-test-simple.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
