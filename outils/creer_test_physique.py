#!/usr/bin/env python3
"""Projet de TEST de la « physique réaliste » : tests/physique-test.zip, à importer dans « Yop2D Test » (moteur : branche
claude/discord-yop2d-config-ox8qgh, commit « Physique réaliste »).
Usage : python3 outils/creer_test_physique.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test (aucune image : des formes de couleur) :
- un PENDULE (boule au bout d'une tige, accrochée à un point fixe) ;
- une CHAÎNE de 6 maillons (charnières) avec une boule lourde au bout ;
- un PONT de 8 planches (charnières) entre deux quais fixes ; des balles et un ballon tombent dessus ;
- une VOITURE (2 roues avec suspension, moteur réglé par les boutons Gas / Stop) ;
- une TOUR de 4 caisses en bois qu'une pierre fait tomber ;
- le sol et les murs sont de l'ANCIEN comportement « Sol / mur » : ils servent de murs aux objets physiques ;
- le DOIGT saisit et tire n'importe quel objet (nœud « Saisir avec le doigt ») ;
- boutons : Gas, Stop, Boom (explosion), Cut bridge (coupe la planche 4), Reset."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
import commun
from commun import *

P = 'physique_test/'
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')
MATIERES = {   # même valeurs que PhysiqueReelle.matiere()
    'bois': (0.7, 0.2, 0.6, '#C58A4A'), 'pierre': (2.5, 0.05, 0.8, '#7A7F87'), 'metal': (4.0, 0.1, 0.4, '#9AA5B1'),
    'caoutchouc': (1.0, 0.85, 0.9, '#E4572E'), 'ballon': (0.4, 0.75, 0.5, '#F6C945'), 'glace': (0.9, 0.05, 0.02, '#8FD3F4')}

def phys(nom, x, y, l, h, matiere, forme='boite', mode='dynamique', z=10, couleur=None, **kw):
    dens, reb, fro, col = MATIERES.get(matiere, (1.0, 0.3, 0.5, '#B0B8C4'))
    return objet(nom, x, y, largeur=l, hauteur=h, z=z, prefixe=P, type='rond' if forme == 'cercle' else 'carre',
                 afficherFondColore=True, couleur=argb(couleur or col), comportement='physique', phType=mode, phForme=forme,
                 phDensite=dens, phRebond=reb, phFrottement=fro, estPhysique=(mode != 'dynamique'), estStatique=True, **kw)

def sol(nom, x, y, l, h):
    return objet(nom, x, y, largeur=l, hauteur=h, z=5, prefixe=P, afficherFondColore=True, couleur=argb('#3B4A5A'),
                 comportement='sol', estPhysique=True, estStatique=True)

objets = [sol('sol', -60, 1000, 2040, 100), sol('mur_g', -60, -300, 60, 1400), sol('mur_d', 1920, -300, 60, 1400)]
# pendule
objets += [phys('pivot', 150, 60, 30, 30, None, mode='fixe', couleur='#FFFFFF'),
           phys('pendule', 365, 25, 100, 100, 'metal', 'cercle')]
# chaîne
objets.append(phys('pivot2', 505, 60, 30, 30, None, mode='fixe', couleur='#FFFFFF'))
for k in range(6):
    objets.append(phys('maillon_%d' % (k + 1), 508, 75 + 60 * k, 24, 60, 'metal', couleur='#C8D0DA'))
objets.append(phys('boule_lourde', 475, 435, 90, 90, 'metal', 'cercle', couleur='#5A6674'))
# pont
objets += [phys('quai_g', 700, 500, 60, 500, None, mode='fixe', couleur='#6B5B45'), phys('quai_d', 1400, 500, 60, 500, None, mode='fixe', couleur='#6B5B45')]
for k in range(8):
    objets.append(phys('planche_%d' % (k + 1), 760 + 80 * k, 500, 80, 24, 'bois'))
objets += [phys('balle_1', 1000, 40, 70, 70, 'caoutchouc', 'cercle'), phys('ballon', 1150, 150, 80, 80, 'ballon', 'cercle')]
# voiture
objets += [phys('caisse_auto', 120, 875, 240, 60, 'metal', couleur='#2E7D4F'),
           phys('roue_av', 115, 910, 90, 90, 'caoutchouc', 'cercle', couleur='#222B33'),
           phys('roue_ar', 275, 910, 90, 90, 'caoutchouc', 'cercle', couleur='#222B33')]
# tour de caisses et pierre
for k in range(4):
    objets.append(phys('caisse_%d' % (k + 1), 1560, 910 - 90 * k, 90, 90, 'bois', tag='caisse'))
objets.append(phys('pierre', 1580, 100, 110, 110, 'pierre', 'cercle', tag='caisse'))
objets.append(phys('glace', 1700, 930, 140, 60, 'glace'))

objets += [texte('info', 360, 130, 1200, 100, 'PHYSICS TEST\nTouch and drag any object. Gas / Stop drive the car, Boom blows things away, Cut bridge cuts a plank.',
                 30, OR, z=90, prefixe=P, cheminPolice=None, alignementTexte='CENTRE')]
def bouton(nom, x, libelle, couleur):
    b = objet(nom, x, 20, largeur=300, hauteur=90, z=90, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 18, 300, 60, libelle, 36, BLANC, z=91, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_gaz', 40, 'Gas', '#2E7D4F') + bouton('btn_stop', 360, 'Stop', '#555F6B') + bouton('btn_boom', 680, 'Boom', '#A04A1E') \
        + bouton('btn_coupe', 1000, 'Cut bridge', '#7A3E8F') + bouton('btn_reset', 1320, 'Reset', '#B7791F')

L = Logique()
def lier(e, id, a, b, type, nom='', **champs):
    p = {'type': type, 'nom': nom}
    p.update(champs)
    suite = L.action(e, id, 'physique_lier', p, a)
    if b: L.noeud(id)['cibleNomB'] = b
    return suite

# 1) monde + pendule
e = L.evenement('start', 'NoeudEventStart')
s = L.action(e, 'monde', 'physique_monde', {'gravite_y': 100, 'gravite_x': 0})
lier(s, 'l_pendule', 'pendule', 'pivot', 'ph_l_tige', 'pendule')
# 2) chaîne
e = L.evenement('start2', 'NoeudEventStart')
prec, s = 'pivot2', e
for k in range(6):
    s = lier(s, 'l_maillon_%d' % (k + 1), 'maillon_%d' % (k + 1), prec, 'ph_l_charniere', 'maillon_%d' % (k + 1), ancre='ph_a_haut')
    prec = 'maillon_%d' % (k + 1)
lier(s, 'l_boule', 'boule_lourde', prec, 'ph_l_charniere', 'boule', ancre='ph_a_haut')
# 3) pont
e = L.evenement('start3', 'NoeudEventStart')
prec, s = 'quai_g', e
for k in range(8):
    s = lier(s, 'l_planche_%d' % (k + 1), 'planche_%d' % (k + 1), prec, 'ph_l_charniere', 'pont_%d' % (k + 1), ancre='ph_a_gauche')
    prec = 'planche_%d' % (k + 1)
lier(s, 'l_quai_d', 'planche_8', 'quai_d', 'ph_l_charniere', 'pont_fin', ancre='ph_a_droite')
# 4) voiture : A = la caisse, B = la roue ; le point de la roue = coin de la caisse décalé de 40 / 20 pixels
e = L.evenement('start4', 'NoeudEventStart')
s = lier(e, 'l_roue_av', 'caisse_auto', 'roue_av', 'ph_l_roue', 'roue_av', ancre='ph_a_bas_gauche', decalage_x=40, decalage_y=20, raideur=5)
lier(s, 'l_roue_ar', 'caisse_auto', 'roue_ar', 'ph_l_roue', 'roue_ar', ancre='ph_a_bas_droite', decalage_x=-40, decalage_y=20, raideur=5)

# doigt : saisir pendant qu'on touche, lâcher au relâchement
e = L.evenement('finger_down', 'NoeudEventDoigtAppuye', sortie='Sortie')
L.action(e, 'saisir', 'physique_doigt', {'mode': 'ph_d_saisir'})
e = L.evenement('finger_up', 'NoeudEventFinClic')
L.action(e, 'lacher', 'physique_doigt', {'mode': 'ph_d_lacher'})

e = L.evenement('tap_gaz', 'NoeudEventClicObjet', cible='btn_gaz')
L.action(e, 'gaz', 'physique_regler_liaison', {'nom': 'roue_ar', 'moteur': 720, 'force_moteur': 30})
e = L.evenement('tap_stop', 'NoeudEventClicObjet', cible='btn_stop')
L.action(e, 'stop', 'physique_regler_liaison', {'nom': 'roue_ar', 'moteur': 0})
e = L.evenement('tap_boom', 'NoeudEventClicObjet', cible='btn_boom')
L.action(e, 'boom', 'physique_explosion', {'x': 1100, 'y': 900, 'rayon': 600, 'force': 1500})
e = L.evenement('tap_coupe', 'NoeudEventClicObjet', cible='btn_coupe')
L.action(e, 'coupe', 'physique_couper', {'nom': 'pont_4'})
e = L.evenement('tap_reset', 'NoeudEventClicObjet', cible='btn_reset')
L.action(e, 'reset', 'recommencer_scene', {})

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Physics', objets, P)], {'Physics': L.ranger().json()}, variables(P, []))
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test physique realiste', 'dateCreation': '2026-10-27 12:00:00', 'dateModif': '2026-10-27 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'physique-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/physique-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
