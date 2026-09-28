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
- `index.html` : accueil. `testeur.html` : page testeurs en 9 langues, **générée**
  par `python3 outils/generer_testeur.py` (textes dans le script ; une seule langue
  affichée selon `?lang=`, le dernier choix ou le téléphone). Le moteur l'ouvre avec
  `?lang=<langue du moteur>`.
  `confidentialite.html` : confidentialité.
- `aide.html` : aide ouverte depuis le moteur dans une WebView.
- `guides/` : 5 guides débutant en 9 langues, **générés** (voir « Guides » plus bas).
  Français : `guides/<guide>.html` ; autres langues : `guides/<langue>/<guide>.html`.
  `guides/move-character.html` = redirection vers `guides/en/deplacer-personnage.html`.

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

## Guides : générés
- Source : `guides/source/<guide>/<langue>.json` (titre, description, carte de
  l'onglet Guides, étapes pour le référencement, blocs du texte). Mise en forme :
  `**gras**`, `` `code` ``, `[texte](lien)`, `(guide:sauter)` pour un autre guide.
  Noms du moteur : `{{id}}` / `{{lang:cle}}` sans guillemets, `[[id]]` /
  `[[lang:cle]]` entre guillemets (mêmes repères que les descriptions des nœuds).
- Générer : `python3 outils/generer_guides.py <clone de zinzin66/yop2d>` → pages
  HTML + `aide/guides/<langue>/*.json`. Ordre des guides : liste `GUIDES` du script.
- Traduire : `python3 outils/traduire_guides.py extraire <guide>` liste les phrases
  de la version anglaise ; `appliquer <guide> <langue> fichier.txt` fabrique la
  source d'une langue (une phrase traduite par ligne, même ordre).
- Nouveau guide : écrire `fr.json` et `en.json`, l'ajouter à `GUIDES`, traduire,
  générer, ajouter les pages au `sitemap.xml`.

## Tester
Pas de GitHub Pages pour une branche : tester `aide.html` en local dans un
navigateur (Playwright + Chromium préinstallé) en simulant l'API GitHub avec
les fichiers locaux, puis envoyer des captures à l'utilisateur.

## Historique
- 27/09/2026 : aide en 9 langues, menu de langue, palette du moteur, noms
  officiels des nœuds (PR #1 et #2).
- 28/09/2026 : 4 guides débutant (fr) ; onglet Nœuds reconstruit depuis le
  catalogue du moteur (115 nœuds, 9 langues) ; guides traduits en 9 langues.

## Reste à faire
- Faire tester les étapes des guides sur tablette (projets zip de test, voir
  `Doc/MEMO_NOEUDS.md` du moteur : bouton `{ }` du Blueprint et import de zip).
- Idées de guides suivants : caméra qui suit, sons et musique, animations,
  ennemi qui poursuit, tirer, apparitions d'ennemis, dialogue, clé et porte.
