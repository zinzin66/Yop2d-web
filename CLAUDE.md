# Yop2D — site web (mémoire pour Claude)

Site officiel de Yop2D, moteur de jeu 2D no-code pour Android, publié avec
GitHub Pages : `https://zinzin66.github.io/Yop2d-web/` (branche `main`).
Le code du moteur est dans un autre dépôt : `zinzin66/yop2d`
(branche la plus avancée : `Yop2d-animation`).

## L'utilisateur
- Ne sait pas programmer : expliquer simplement, en français, sans jargon.
- Travaille uniquement sur une tablette Android, avec GitHub dans le navigateur.
- Quand il doit modifier un fichier lui-même, lui donner des sections complètes
  prêtes à coller, repérées par `//haut1` … `//bas1`, `//haut2` … `//bas2`.
- Les changements passent par une demande de fusion (pull request) vers `main` :
  l'utilisateur la valide avec « Merge ». Le site est à jour 1 à 2 minutes après.

## Pages
- `index.html` : accueil. `testeur.html` : page testeurs.
  `confidentialite.html` : confidentialité.
- `aide.html` : aide ouverte depuis le moteur dans une WebView.
- `guides/*.html` : guides complets, style commun `guides/guide.css`
  (`deplacer-personnage.html` et `move-character.html` en anglais, `sauter.html`,
  `pieces-score.html`, `vie-game-over.html`, `niveau-suivant.html`).

## Aide (aide.html)
- Deux onglets : **Nœuds** et **Guides**.
- Contenu en JSON, un dossier par langue (fr, en, es, de, it, pt, ru, zh, ja) :
  - `aide/noeuds/<langue>/NN-categorie.json` → `{ "categorie", "noeuds": [ { "nom", "schema", "role", "exemple" } ] }`
    **généré, ne pas modifier à la main** (voir plus bas) ;
  - `aide/guides/<langue>/NN-nom.json` → `{ "titre", "description", "lien" }` (écrit à la main).
- La page liste les fichiers avec l'API GitHub : un fichier ajouté sur `main`
  apparaît sans modifier `aide.html`. L'ordre suit le numéro au début du nom.
- Langue affichée : `?lang=xx` dans l'adresse (envoyé par le moteur), sinon le
  dernier choix du menu, sinon la langue du téléphone, sinon le français. Si
  une langue n'a pas de fichiers, la page affiche le français.
- Textes de la page (onglets, messages) : objet `TEXTES` dans `aide.html`.
- Couleurs : celles de `Palette.java` du moteur (variables CSS dans `:root`).

## Onglet Nœuds : généré depuis le moteur
- Script : `python3 outils/generer_aide_noeuds.py <chemin du clone de zinzin66/yop2d>`
  (branche `Yop2d-animation`). Il lit `catalogue_noeuds.json` et `lang_<langue>.json`
  du moteur (noms, catégories, réglages, sorties : exactement ceux de l'éditeur)
  et remplace tous les fichiers de `aide/noeuds/<langue>/`.
- Les 18 événements sont des classes Java : leur liste, leurs cibles et réglages
  sont recopiés en haut du script (`EVENEMENTS`, `CIBLES_EVENEMENTS`…), à mettre
  à jour si `RegistreNoeuds.java` change.
- Rôle et exemple de chaque nœud : `aide/source/descriptions/<langue>.json`,
  `{ "id": ["rôle", "exemple ou null"] }` (id = clé du catalogue ou nom de la
  classe d'événement). Pour citer un autre nœud, une sortie ou un réglage, écrire
  un repère `[[id_du_noeud]]` ou `[[lang:cle]]` (ex. `[[lang:port_ensuite]]`) :
  le script met le nom exact du moteur, entre guillemets de la langue.
- Nouveau nœud dans le moteur → relancer le script : il liste les descriptions
  manquantes (en attendant, il affiche l'anglais puis le français).

## Tester
Pas de GitHub Pages pour une branche : tester `aide.html` en local dans un
navigateur (Playwright + Chromium préinstallé) en simulant l'API GitHub avec
les fichiers locaux, puis envoyer des captures à l'utilisateur.

## Historique
- 27/09/2026 : aide en 9 langues, menu de langue, palette du moteur, noms
  officiels des nœuds (PR #1 et #2).
- 28/09/2026 : 4 guides débutant (fr) ; onglet Nœuds reconstruit depuis le
  catalogue du moteur (115 nœuds, 9 langues).

## Reste à faire
- Traduire les guides (fr) dans les 8 autres langues, après test des étapes
  sur tablette par l'utilisateur. Aujourd'hui : « Déplacer » existe en fr et en,
  les 4 autres guides en fr seulement.
