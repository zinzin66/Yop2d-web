#!/usr/bin/env python3
"""Projet de TEST de la « Logique globale » : tests/global-test.zip, à importer dans une version de test du moteur qui
contient la logique globale (moteur : branche claude/discord-yop2d-config-ox8qgh).
Usage : python3 outils/creer_test_global.py <clone de zinzin66/yop2d-moteur>
Ce que fait le test : 2 scènes (Carte 1, Carte 2) qui ont chacune un texte « info » et un bouton ; AUCUN nœud dans les scènes
sauf pour changer de scène. Tout le reste est dans la logique globale (fichier logique/global.json) :
  - Au démarrage (une seule fois) : la variable « visites » passe à 0 ;
  - À chaque nouvelle scène : « visites » + 1 et le texte « info » (de la scène qui vient de s'ouvrir) l'affiche ;
  - un clic sur un bouton « suivant » ou « retour » fait changer de scène (nœud visant l'objet par son tag, présent dans les 2 scènes).
Résultat attendu : le compteur monte à chaque changement de scène (1, 2, 3…) sans qu'il soit écrit dans les scènes."""
import os, sys, tempfile
SITE_RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if len(sys.argv) != 2:
    sys.exit(__doc__)
sys.path.insert(0, os.path.join(sys.argv[1], 'outils', 'modeles'))
from commun import *

P = 'global_test/'
BLANC, OR = argb('#FFFFFF'), argb('#FFD166')

def scene_de(nom, couleur, texte_titre, cible):
    objets = [objet('fond', 0, 0, largeur=1920, hauteur=1080, z=-100, prefixe=P + nom, afficherFondColore=True, couleur=argb(couleur)),
              texte('titre', 160, 120, 1600, 120, texte_titre, 64, OR, z=5, prefixe=P + nom, cheminPolice=None, alignementTexte='CENTRE'),
              texte('info', 160, 380, 1600, 160, '?', 56, BLANC, z=5, prefixe=P + nom, cheminPolice=None, alignementTexte='CENTRE'),
              objet('bouton', 660, 700, largeur=600, hauteur=160, z=5, prefixe=P + nom, afficherFondColore=True, couleur=argb('#4CC9F0'), tag='bouton'),
              texte('bouton_texte', 660, 740, 600, 80, 'Next scene', 48, argb('#0C162E'), z=6, prefixe=P + nom, cheminPolice=None, alignementTexte='CENTRE')]
    return objets

A = scene('Carte 1', scene_de('a', '#16301F', 'Map 1 (this scene has no node for the counter)', 'Carte 2'), P)
B = scene('Carte 2', scene_de('b', '#2A1B3D', 'Map 2 (same: the counter is in the GLOBAL logic)', 'Carte 1'), P)

# logique de chaque scène : seulement le changement de scène (le bouton s'appelle « bouton » dans les 2 scènes)
def logique_scene(cible):
    L = Logique()
    e = L.evenement('tap', 'NoeudEventClicObjet', cible='bouton')
    L.action(e, 'go', 'changer_scene_transition', {'forme': 'h_tr_rond', 'couleur': '#000000', 'fermeture': 0.5, 'pause': 0.1, 'ouverture': 0.5})
    L.noeud('go')['cibleSceneNom'] = cible
    return L.ranger().json()

# logique GLOBALE
G = Logique()
e = G.evenement('g_start', 'NoeudEventStart')
G.action(e, 'g_zero', 'modifier_variable', {'valeur': 0}, None, 'visites')
e = G.evenement('g_scene', 'NoeudEventNouvelleScene')
G.chaine(e, [('g_plus', 'ajouter_variable', {'valeur': 1}, None, 'visites'),
             ('g_texte', 'modifier_propriete', {'propriete': 'texte', 'valeur': '="Scenes opened: " + visites'}, 'info')])

with tempfile.TemporaryDirectory() as tmp:
    p = os.path.join(tmp, 'projet')
    ecrire_projet(p, [A, B], {'Carte 1': logique_scene('Carte 2'), 'Carte 2': logique_scene('Carte 1')}, variables(P, [('visites', 0)]))
    ecrire(os.path.join(p, 'logique', 'global.json'), G.ranger().json())
    ecrire(os.path.join(p, 'meta.json'), {'nom': 'Test logique globale', 'dateCreation': '2026-10-26 12:00:00', 'dateModif': '2026-10-26 12:00:00'})
    sortie = os.path.join(SITE_RACINE, 'tests', 'global-test.zip')
    zipper_projet(p, sortie)
print('%d + %d nœuds -> tests/global-test.zip (%d Ko)' % (len(G.noeuds), 2, os.path.getsize(sortie) // 1024))
