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
- `guides/*.html` : guides complets (`deplacer-personnage.html` en français,
  `move-character.html` en anglais).

## Aide (aide.html)
- Deux onglets : **Nœuds** et **Guides**.
- Contenu en JSON, un dossier par langue (fr, en, es, de, it, pt, ru, zh, ja) :
  - `aide/noeuds/<langue>/NN-nom.json` → `{ "categorie", "noeuds": [ { "nom", "schema", "role", "exemple" } ] }`
    (`schema` peut contenir du HTML simple comme `<b>`, `exemple` est facultatif) ;
  - `aide/guides/<langue>/NN-nom.json` → `{ "titre", "description", "lien" }`.
- Les mêmes noms de fichiers dans chaque langue. L'ordre d'affichage suit le
  numéro au début du nom.
- La page liste les fichiers avec l'API GitHub : un fichier ajouté sur `main`
  apparaît sans modifier `aide.html`.
- Langue affichée : `?lang=xx` dans l'adresse (envoyé par le moteur), sinon le
  dernier choix du menu, sinon la langue du téléphone, sinon le français. Si
  une langue n'a pas de fichiers, la page affiche le français.
- Textes de la page (onglets, messages) : objet `TEXTES` dans `aide.html`.
- Couleurs : celles de `Palette.java` du moteur (variables CSS dans `:root`).
- Noms des nœuds : repris exactement de
  `app/src/main/assets/doc_noeuds_<langue>.txt` du moteur. Garder les deux
  synchronisés.

## Tester
Pas de GitHub Pages pour une branche : tester `aide.html` en local dans un
navigateur (Playwright + Chromium préinstallé) en simulant l'API GitHub avec
les fichiers locaux, puis envoyer des captures à l'utilisateur.

## Historique
- 27/09/2026 : aide en 9 langues, menu de langue, palette du moteur, noms
  officiels des nœuds (PR #1 et #2).

## Reste à faire
- Traduire le guide « Déplacer un personnage » dans les 7 autres langues
  (aujourd'hui fr et en seulement ; les autres renvoient vers la page anglaise).
