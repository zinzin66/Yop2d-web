#!/usr/bin/env python3
"""Projet de TEST des « lumières et ombres » : tests/lumieres-test.zip, à importer dans « Yop2D Test » (moteur : branche
claude/discord-yop2d-config-ox8qgh, commit « Lumières et ombres »).
Usage : python3 outils/creer_test_lumieres.py <clone de zinzin66/yop2d-moteur> <dossier packs (avec aventuriers/ et decors3d/)>
Ce que fait le test : un cimetière la nuit (décor 3D en 5 couches, personnages 3D haute définition). 2 lanternes du décor qui éclairent,
un voleur qui suit le doigt et porte une lanterne (objet ENFANT : la lumière le suit), un chevalier immobile. Les 2 ont une ombre douce posée avec la case « Ombre » de l'Inspecteur (aucun nœud).
Boutons : Day / Sunset (jour -> crépuscule orange -> nuit bleue en 12 s) / Night (très sombre), Lantern off / on (éteint / rallume la lumière du ninja)."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 3:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
import commun
from commun import *
PACKS = sys.argv[2]
_biblio = commun.fichier_biblio
def fichier_biblio(chemin):
    r = chemin.replace('assets_ludexa/', '', 1)
    for pack in ('decors3d', 'aventuriers'):
        if r.startswith('Images/Packs/%s/' % pack): return os.path.join(PACKS, pack, r[len('Images/Packs/%s/' % pack):])
    return _biblio(chemin)
commun.fichier_biblio = fichier_biblio

P = 'lumieres_test/'
DEC = 'assets_ludexa/Images/Packs/decors3d/Fonds/nuit_hantee/nuit_hantee_'
AV = 'assets_ludexa/Images/Packs/aventuriers/Animations/'
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')

objets = []
for i, (nom, z) in enumerate((('ciel', -100), ('01_arbres_loin', -90), ('02_arbres', -80), ('03_cimetiere', -70), ('04_avant', 80))):
    objets.append(objet('decor_' + nom, -960, 0, DEC + nom + '.webp', 3840, 1080, z=z, prefixe=P))
OMBRE = dict(ombreActive=True, ombreForce=55.0, ombreLargeur=70.0, ombreDecalageY=-6.0)   # la case « Ombre » de l'Inspecteur
hero = objet('hero', 780, 660, AV + 'voleur/repos/voleur_repos_1.png', 214, 300, z=50, prefixe=P, **OMBRE)
objets += [hero,
           objet('lanterne', 175, 160, largeur=20, hauteur=20, z=51, prefixe=P, parentId=hero['id']),   # invisible : sert de point lumineux
           objet('ami', 1250, 660, AV + 'chevalier/repos/chevalier_repos_1.png', 214, 300, z=50, prefixe=P, **OMBRE),
           objet('lampe_a', 226, 830, largeur=20, hauteur=20, z=5, prefixe=P),     # sur la lanterne du décor (à gauche)
           objet('lampe_b', 390, 735, largeur=20, hauteur=20, z=5, prefixe=P)]     # la petite lanterne plus loin
objets += [texte('info', 500, 30, 920, 140, 'LIGHTS TEST\nTouch the screen: the thief follows your finger and carries a lantern.\nNight = pitch black. Sunset goes from day to night in 12 s.',
                 30, OR, z=90, prefixe=P, cheminPolice=None, alignementTexte='CENTRE')]
def bouton(nom, x, libelle, couleur):
    b = objet(nom, x, 940, largeur=330, hauteur=110, z=90, prefixe=P, afficherFondColore=True, couleur=argb(couleur), estZoneDeClic=True)
    return [b, texte(nom + '_t', 0, 25, 330, 70, libelle, 38, BLANC, z=91, prefixe=P, parentId=b['id'], alignementTexte='CENTRE', cheminPolice=None)]
objets += bouton('btn_jour', 40, 'Day', '#B7791F') + bouton('btn_soir', 400, 'Sunset (12 s)', '#A04A1E') + bouton('btn_nuit', 760, 'Night', '#2B3A67') \
        + bouton('btn_off', 1120, 'Lantern off', '#555F6B') + bouton('btn_on', 1480, 'Lantern on', '#2E7D4F')

L = Logique()
e = L.evenement('start', 'NoeudEventStart')
L.chaine(e, [('nuit0', 'lumiere_ambiance', {'couleur': '#02040C', 'niveau': 92, 'duree': 0}),
             ('src_a', 'lumiere_source', {'couleur': '#FFC060', 'rayon': 430, 'intensite': 100, 'lueur': 100, 'vacillement': 'lv_bougie'}, 'lampe_a'),
             ('src_b', 'lumiere_source', {'couleur': '#FFC060', 'rayon': 300, 'intensite': 100, 'lueur': 80, 'vacillement': 'lv_bougie'}, 'lampe_b'),
             ('src_h', 'lumiere_source', {'couleur': '#FFD890', 'rayon': 360, 'intensite': 110, 'lueur': 100, 'vacillement': 'lv_torche'}, 'lanterne')])
e = L.evenement('finger_down', 'NoeudEventDoigtAppuye', sortie='Sortie')
L.action(e, 'follow', 'glisser_vers', {'x': '=doigt.x - hero.largeur / 2', 'y': 660, 'duree': 0.3}, 'hero')
e = L.evenement('tap_jour', 'NoeudEventClicObjet', cible='btn_jour')
L.action(e, 'jour', 'lumiere_ambiance', {'couleur': '#FFFFFF', 'niveau': 0, 'duree': 2})
e = L.evenement('tap_nuit', 'NoeudEventClicObjet', cible='btn_nuit')
L.action(e, 'nuit', 'lumiere_ambiance', {'couleur': '#02040C', 'niveau': 100, 'duree': 2})
# coucher de soleil : jour -> crépuscule orange (6 s) -> nuit bleue (6 s) ; la couleur ET l'obscurité changent en douceur
e = L.evenement('tap_soir', 'NoeudEventClicObjet', cible='btn_soir')
L.chaine(e, [('s_jour', 'lumiere_ambiance', {'couleur': '#FFFFFF', 'niveau': 0, 'duree': 0.3}),
             ('s_att0', 'attendre', {'duree': 0.4}),
             ('s_soir', 'lumiere_ambiance', {'couleur': '#8A3410', 'niveau': 40, 'duree': 6}),
             ('s_att', 'attendre', {'duree': 6}),
             ('s_nuit', 'lumiere_ambiance', {'couleur': '#02040C', 'niveau': 92, 'duree': 6})])
e = L.evenement('tap_off', 'NoeudEventClicObjet', cible='btn_off')
L.action(e, 'off', 'lumiere_eteindre', {}, 'lanterne')
e = L.evenement('tap_on', 'NoeudEventClicObjet', cible='btn_on')
L.action(e, 'on', 'lumiere_source', {'couleur': '#FFD890', 'rayon': 360, 'intensite': 110, 'lueur': 100, 'vacillement': 'lv_torche'}, 'lanterne')

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [scene('Night', objets, P)], {'Night': L.ranger().json()}, variables(P, []))
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test lumieres et ombres', 'dateCreation': '2026-10-27 12:00:00', 'dateModif': '2026-10-27 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'lumieres-test.zip')
    zipper_projet(p, sortie)
print('%d nœuds -> tests/lumieres-test.zip (%d Ko)' % (len(L.noeuds), os.path.getsize(sortie) // 1024))
