#!/usr/bin/env python3
"""Projet de TEST du KIT TACTIQUE : tests/kit-test.zip, à importer dans une version de test du moteur qui contient le kit
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
objets.append(texte('msg', 40, 840, 1000, 80, 'Tap a button on the right', 34, BLANC, z=60, prefixe=P, cheminPolice=None))

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [('d1', 'appliquer_donnees', {'nom': 'Lancier'}, 'lancier'), ('d2', 'appliquer_donnees', {'nom': 'Cavalier'}, 'cavalier'),
             ('d3', 'appliquer_donnees', {'nom': 'Archer'}, 'archer'),
             ('s1', 'modifier_stat', {'stat': 'niveau', 'operation': 'st_o_fixer', 'valeur': 1}, 'lancier'),
             ('s2', 'modifier_stat', {'stat': 'xp', 'operation': 'st_o_fixer', 'valeur': 0}, 'lancier'),
             ('s3', 'modifier_stat', {'stat': 'etat_poison', 'operation': 'st_o_fixer', 'valeur': 0}, 'cavalier')])
e = L.evenement('frame', 'NoeudEventChaqueImage', sortie='Sortie')
L.action(e, 'show', 'modifier_propriete', {'propriete': 'texte', 'valeur': '="lancier vie " + lancier.vie + " niv " + lancier.niveau + " xp " + lancier.xp + "   cavalier vie " + cavalier.vie + " poison " + cavalier.etat_poison + " mv " + cavalier.mouvement + "   archer vie " + archer.vie + "   tour " + numero_tour()'}, 'info')

def msg(txt):
    return {'propriete': 'texte', 'valeur': txt}
BOUTONS = [
    ('1. Attack: spear vs heavy cavalry (rule 150%, pierce 30%, counter 100%)', 'attaquer', {'puissance': 100, 'terrain': 'o_non', 'minimum': 'o_oui', 'detruire': 'o_oui', 'perforation': 30, 'riposte': 100}, 'lancier', 'cavalier'),
    ('2. Poison the cavalry (2 turns, 2 damage)', 'donner_etat', {'etat': 'Poison'}, 'cavalier', None),
    ('3. Slow the cavalry (movement -2 for 2 turns)', 'donner_etat', {'etat': 'Lent'}, 'cavalier', None),
    ('4. Next turn (joueur, ennemi): poison hurts at the start of the enemy turn', 'tour_suivant', {'equipes': 'joueur,ennemi'}, None, None),
    ('5. Fireball on the cavalry: radius 3, strength 5, falloff 20%', 'effet_zone', {'effet': 'ez_degats', 'valeur': 5, 'rayon': 3, 'tags': 'ennemi', 'baisse': 20}, 'cavalier', None),
    ('6. Spear gains 120 XP (level up: vie +2, attaque +1)', 'gagner_xp', {'quantite': 120, 'palier': 100, 'gains': 'vie=2, attaque=1'}, 'lancier', None),
    ('7. Team colour: pink -> blue on the spearman', 'couleur_equipe', {'couleur': '#2F6BFF', 'repere': '#FF00FF', 'tolerance': 30}, 'lancier', None),
    ('8. Fog of war (spear sees 3 tiles; enemies hidden)', 'brouillard_maj', {'equipe': 'joueur', 'ennemis': 'ennemi', 'vision': 3}, None, None),
    ('9. Remove the fog', 'brouillard_enlever', {}, None, None),
    ('10. Enemy AI plays (aggressive): moves, then attacks if cible_ia = 1', 'ia_jouer', {'ennemis': 'joueur', 'style': 'ia_agressif', 'vitesse': 10}, 'cavalier', None),
    ('11. Remember position, then move the spear 3 tiles right', 'memoriser_position', {}, 'lancier', None),
    ('12. Cancel the move (spear goes back)', 'annuler_deplacement', {}, 'lancier', None),
]
for i, (nom, cle, reglages, a, b) in enumerate(BOUTONS):
    bx, by = 1100, 160 + i * 66
    objets.append(objet('b%d' % i, bx, by, largeur=780, hauteur=60, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#2B3A55')))
    objets.append(texte('t%d' % i, bx + 12, by + 14, 760, 40, nom, 21, BLANC, z=6, prefixe=P, cheminPolice=None))
    e = L.evenement('tap%d' % i, 'NoeudEventClicObjet', cible='b%d' % i)
    n = L.action(e, 'a%d' % i, cle, reglages, a)
    if b:
        L.noeud('a%d' % i)['cibleNomB'] = b
    if cle == 'ia_jouer':
        # à l'arrivée : si cible_ia = 1, le cavalier attaque la cible choisie (objet impliqué)
        s = L.action((n[0], 'port_arrive', 0), 'si%d' % i, 'si_stat', {'stat': 'cible_ia', 'comparaison': 'st_c_ge', 'valeur': 1}, 'cavalier')
        at = L.action((s[0], 'port_vrai', 0), 'at%d' % i, 'attaquer', {'puissance': 100, 'terrain': 'o_non', 'minimum': 'o_oui', 'detruire': 'o_oui', 'riposte': 100}, 'cavalier')
        L.noeud('at%d' % i)['cibleNomB'] = '__OBJET_IMPLIQUE__'
        L.action(at, 'm%d' % i, 'modifier_propriete', msg('AI attacked'), 'msg')
    elif cle == 'memoriser_position':
        p = L.action(n, 'pl%d' % i, 'placer_case', {'colonne': 4, 'ligne': 4}, 'lancier')
        L.action(p, 'm%d' % i, 'modifier_propriete', msg('Moved: now cancel it'), 'msg')
    elif cle == 'annuler_deplacement':
        L.action((n[0], 'port_fait', 0), 'm%d' % i, 'modifier_propriete', msg('Move cancelled'), 'msg')
    else:
        L.action(n, 'm%d' % i, 'modifier_propriete', msg('Done: ' + nom.split(':')[0].split('(')[0]), 'msg')
logique = L.ranger().json()
with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Test', objets, P)], {'Test': logique}, [])
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test kit tactique', 'dateCreation': '2026-10-29 12:00:00', 'dateModif': '2026-10-29 12:00:00'})
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
    sortie = os.path.join(SITE_RACINE, 'tests', 'kit-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/kit-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
