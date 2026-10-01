# Yop2D — site web (mémoire pour Claude)

Site officiel de Yop2D, moteur de jeu 2D no-code pour Android, publié avec
GitHub Pages : `https://zinzin66.github.io/Yop2d-web/` (branche `main`).
Le code du moteur est dans le dépôt **PRIVÉ** `zinzin66/yop2d-moteur` (branche la plus avancée :
`Yop2d-animation`). Le dépôt **public** `zinzin66/yop2d` ne contient QUE les versions publiées
(Releases, fichier `Yop2D.apk`) : le bouton « Télécharger » du site et la recherche de mises à jour
du moteur lisent ses Releases. Ne jamais y mettre de code (depuis le 29/09/2026).

## L'utilisateur
- Ne sait pas programmer : expliquer simplement, en français, sans jargon.
- Travaille uniquement sur une tablette Android, avec GitHub dans le navigateur.
- Quand il doit modifier un fichier lui-même, lui donner des sections complètes
  prêtes à coller, repérées par `//haut1` … `//bas1`, `//haut2` … `//bas2`.
- Les changements passent par une demande de fusion (pull request) vers `main` :
  l'utilisateur la valide avec « Merge ». Le site est à jour 1 à 2 minutes après.

## Pages
- Nouvelle vidéo YouTube : l'ajouter en tête de `VIDEOS` (`generer_accueil.py`) avec ses textes
  dans "videos" des 9 fichiers `outils/accueil/<langue>.json`, et dans le guide concerné (bloc "video").
- Accueil (présentation, comparatif avec d'autres moteurs, FAQ) en 9 langues,
  **généré** par `python3 outils/generer_accueil.py` depuis `outils/accueil/<langue>.json`.
  Anglais : `index.html` (racine) ; autres : `<langue>/index.html` (ex. `/fr/`).
  Dans les textes, `@/` = racine du site ; `{nb_noeuds}` = nombre de nœuds de l'aide (calculé). La racine envoie vers `/<langue>/` si
  `?lang=xx` ou si le visiteur a déjà choisi une langue (clé `yop2d-langue`),
  sinon propose la langue du téléphone dans un bandeau. Captures : liste `IMAGES`
  du script, toutes en `.png` à la racine (depuis le 30/09/2026), dans l'ordre des blocs « vitrine » :
  interface_demarage, interface_modeles, interface_editeur, interface_tuiles, interface_animation,
  interface_titre, interface_text (dialogues.txt), interface_noeuds, interface_editeur_noeuds, exemples_jeux,
  et côte à côte (un élément de `IMAGES` peut être une liste) interface_editeur_telephone +
  interface_editeur_noeuds_telephone. Une image absente est masquée. Nouvelles captures fournies le 30/09/2026 :
  à refaire avec la 0.1.948 (nouvelle barre d'outils et nouvelle fenêtre de réglage) : interface_editeur,
  interface_editeur_noeuds, interface_noeuds, interface_modeles (carte du guide) et les 2 captures téléphone.
  Faits à respecter : gratuit, jamais de pub, code source fermé, jeux libres
  (donner, vendre), aucun logo/filigrane dans les jeux, Android 7+, hors ligne,
  APK mais pas encore AAB, statistiques Aptabase anonymes désactivables,
  « développeur indépendant » (jamais de nationalité).
- `llms.txt` : résumé en anglais pour les IA (faits, liens, liste des nœuds,
  comparatif, FAQ), **généré** en même temps que l'accueil par `generer_accueil.py`.
  Relancer ce script après un changement des guides ou des nœuds.
- `testeur.html` : page testeurs en 9 langues, **générée**
  par `python3 outils/generer_testeur.py` (textes dans le script ; une seule langue
  affichée selon `?lang=`, le dernier choix ou le téléphone). Le moteur l'ouvre avec
  `?lang=<langue du moteur>`.
  `confidentialite.html` : confidentialité.
- `aide.html` : aide ouverte depuis le moteur dans une WebView.
- `guides/` : 6 guides débutant en 9 langues, **générés** (voir « Guides » plus bas).
  Français : `guides/<guide>.html` ; autres langues : `guides/<langue>/<guide>.html`.
  Page « Tous les guides » (générée aussi) : `guides/index.html` (fr), `guides/<langue>/index.html` ;
  textes dans `TOUS` de `generer_guides.py`. Accueil et `llms.txt` y renvoient.
  `guides/move-character.html` = redirection vers `guides/en/deplacer-personnage.html`.
- `exemples/` : **exemples téléchargeables par le moteur** (depuis le 30/09/2026). `<id>.zip` (projet Yop2D) +
  `<id>.png` (vignette 300 x 300) ; textes (nom, description en 9 langues, `version`, `moteur_min` = build minimal)
  dans `outils/exemples/source.json`. `python3 outils/generer_exemples.py` écrit `exemples/exemples.json` (lu par
  l'onglet Exemples du moteur, tailles calculées) et la page `exemples/<langue>.html` ; relancer ensuite
  `generer_accueil.py` (`llms.txt` liste les exemples). Exemple modifié → augmenter sa `version` (le moteur
  retélécharge). Nouvel exemple → zip + png dans `exemples/`, entrée dans `source.json`, générer.
  Le moteur (à partir de la version qui suit la 0.1.948) n'intègre plus que Platformer et Neon shooter.

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
- Script : `python3 outils/generer_aide_noeuds.py <chemin du clone de zinzin66/yop2d-moteur>`
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
- Pages lisibles par les moteurs de recherche et les IA : `noeuds/<langue>.html`
  (tous les nœuds sur une page), générées depuis `aide/noeuds/` par
  `python3 outils/generer_pages_noeuds.py` : **à relancer après** `generer_aide_noeuds.py`.
  (L'onglet Nœuds de `aide.html` se remplit par JavaScript : les robots ne le voient pas.)

## Guides : générés
- Source : `guides/source/<guide>/<langue>.json` (titre, description, carte de
  l'onglet Guides, étapes pour le référencement, blocs du texte). Mise en forme :
  `**gras**`, `` `code` ``, `[texte](lien)`, `(guide:sauter)` pour un autre guide.
  Noms du moteur : `{{id}}` / `{{lang:cle}}` sans guillemets, `[[id]]` /
  `[[lang:cle]]` entre guillemets (mêmes repères que les descriptions des nœuds).
- Générer : `python3 outils/generer_guides.py <clone de zinzin66/yop2d-moteur>` → pages
  HTML + `aide/guides/<langue>/*.json`. Ordre des guides : liste `GUIDES` du script.
- Traduire : `python3 outils/traduire_guides.py extraire <guide>` liste les phrases
  de la version anglaise ; `appliquer <guide> <langue> fichier.txt` fabrique la
  source d'une langue (une phrase traduite par ligne, même ordre).
- Nouveau guide : écrire `fr.json` et `en.json`, l'ajouter à `GUIDES`, traduire,
  générer (la page « Tous les guides » suit), relancer `generer_accueil.py`
  (pour `llms.txt`), ajouter les pages au `sitemap.xml`.

## Tester
Pas de GitHub Pages pour une branche : tester `aide.html` en local dans un
navigateur (Playwright + Chromium préinstallé) en simulant l'API GitHub avec
les fichiers locaux, puis envoyer des captures à l'utilisateur.

## Historique
- 27/09/2026 : aide en 9 langues, menu de langue, palette du moteur, noms
  officiels des nœuds (PR #1 et #2).
- 28/09/2026 : 4 guides débutant (fr) ; onglet Nœuds reconstruit depuis le
  catalogue du moteur (115 nœuds, 9 langues) ; guides traduits en 9 langues ;
  page testeurs en 9 langues ; pages `noeuds/<langue>.html` pour le référencement ;
  accueil + comparatif + FAQ (19 questions) en 9 langues ; `llms.txt` ;
  page « Tous les guides » en 9 langues ; Yandex, Google et Bing (voir plus bas).
- 28/09/2026 (soir) : chantier « effets visuels » du moteur (branche Yop2d-animation) :
  8 nouveaux nœuds décrits en 9 langues (123 nœuds), guide « particules-effets »
  (6e guide), carte « Particules et effets d'écran » sur l'accueil.
- 28/09/2026 (nuit) : aide mise à jour pour « Tirer » (détruire hors de l'écran) et
  « Afficher un dialogue » (dialogues en plusieurs langues : `cle.fr = ...`, variable `langue`).
  Nouvel exemple du moteur « Lost on the moon » (quiz angoissant en 9 langues). L'utilisateur
  prévoit 1 ou 2 exemples de plus avant de publier une nouvelle version du moteur.
- 29/09/2026 : nœuds « Électrocution » et « Limites de la caméra » (127 nœuds) ; accueil : 5 exemples
  (Neon shooter, Neon jump, Lost on the moon, Effects showcase, Parallaxe), carte « Jeux en plusieurs
  langues », cartes particules et caméra mises à jour ; guide particules-effets : étape 4 (électrocution,
  arrêt sur image) et renvoi vers l'exemple Effects showcase. Moteur validé : build 921.
- 29/09/2026 : version 0.1.926 publiée (retours téléphones : bandeau qui défile, zoom, sélecteur de couleur
  unique, fenêtre de texte, mode « déplacer seulement » du Blueprint, choix des images d'animation par
  dossier). Accueil : carte « Un éditeur confortable » et phrase ajoutée à la carte « Sur tablette et téléphone ».
- 29/09/2026 : 1re vidéo YouTube (effets de particules, a6wVvJh9uyQ) : section vidéo en haut de l'accueil
  (liste `VIDEOS` de `generer_accueil.py`, titre/description dans "videos" de `outils/accueil/<langue>.json`,
  balises VideoObject, lien dans `llms.txt`) et bloc `["video", "id", "légende"]` dans le guide
  particules-effets (nouveau type de bloc des guides, légende traduite par `traduire_guides.py`).
  Titres et descriptions YouTube en 9 langues donnés à l'utilisateur (traductions ajoutées dans YouTube Studio).

- 30/09/2026 : recherche de chemin dans le moteur (demande d'un utilisateur Discord) : 3 nœuds « Aller vers un
  objet (chemin) », « Aller à un point (chemin) », « Arrêter le chemin » décrits en 9 langues (130 nœuds) ;
  aide, pages `noeuds/`, accueil et `llms.txt` régénérés. Côté moteur (branche Yop2d-animation) : 31 modèles
  de projet pour débutants (onglet « Modèles », 6 catégories) et 2 nouveaux exemples (Platformer, Maze chase).
- 30/09/2026 : version 0.1.933 publiée par l'utilisateur. Accueil (9 langues) : bloc vitrine « 31 modèles pour
  apprendre » (image `interface_modeles.png`), cartes « 31 modèles pour débutants » et « Recherche de chemin »,
  7 exemples, FAQ « Comment apprendre » (onglet Modèles d'abord). Captures renommées en `.png`.
- 30/09/2026 : version 0.1.935 (avis de mise à jour au démarrage, bouton orange). Nouvelles captures de
  l'utilisateur intégrées ; bloc vitrine « Textes et dialogues en plusieurs langues » (11 blocs) ; bloc
  téléphone avec 2 captures côte à côte (classe CSS `duo`).
- 30/09/2026 : noms clairs dans le moteur (Toast, Z-Order, Clamp, Scale, Glow, Blink, Cooldown... remplacés,
  « oui / non » au lieu de « true / false », millisecondes expliquées) : aide, pages `noeuds/`, guides, accueil et
  `llms.txt` régénérés depuis le catalogue du moteur (branche Yop2d-animation).
- 30/09/2026 : exemples téléchargeables : dossier `exemples/` (7 exemples, 3,4 Mo), page « Exemples » en 9 langues,
  lien sur l'accueil (bloc des exemples), `llms.txt`, `sitemap.xml`. Côté moteur : `ExemplesEnLigne.java`.
  Puis exemple « Parallaxe » retiré (jugé moche par l'utilisateur ; à refaire en MODÈLE du moteur) : 6 exemples.
- 01/10/2026 : exemples Pirate battle (PR #22) puis Candy match (style Candy Crush). Moteur : 3 nœuds « grille »
  (Remplir la grille, Jouer sur la grille (aligner 3), Mélanger la grille), catégorie « Grilles et puzzles » (133 nœuds) :
  aide, pages `noeuds/`, `llms.txt` régénérés. Candy match demande le build 956 (`moteur_min`, bonbons sous le panneau de fin). Nœuds des exemples rangés (Logique.ranger).
- 01/10/2026 : exemple « Dungeon escape » (escape game en vue iso, pack 3D Kenney Mini Dungeon rendu en images par
  `outils/iso/` du moteur), 9 exemples.
- 01/10/2026 : exemple « Dungeon walk » (vue iso, promenade au joystick, moteur_min 957 : ordre d'affichage selon la
  position, marche iso du joystick, zone de contact respectée par les murs), 10 exemples. Aide : réglage « image » des particules.
- 30/09/2026 : version 0.1.948 publiée (guide « Ton premier jeu en 5 minutes », nouvelle fenêtre de réglage
  « ① Sur quoi ? / ② Réglages » avec aides et ligne « En clair », barre d'outils réduite, style sobre bleu néon).
  Accueil (9 langues) : cartes « Ton premier jeu en 5 minutes » et « Des réglages en clair » (17 cartes),
  carte « Un éditeur simple et confortable », blocs vitrine modèles et « Le cerveau de vos jeux », FAQ « Comment apprendre ».
  Captures de l'éditeur (barre d'outils, fenêtre de réglage) à refaire par l'utilisateur avec la 0.1.948.

## Moteurs de recherche
- Google Search Console : propriété `https://zinzin66.github.io/Yop2d-web/`, fichiers
  `google74fcdd47f85fa058.html` et `google55621bdcee9caacd.html` (ne pas supprimer).
- Bing : `BingSiteAuth.xml`. Yandex (28/09/2026) : fichier dans le dépôt
  `zinzin66/zinzin66.github.io` (racine de l'adresse, avec `robots.txt` et une
  redirection vers `/Yop2d-web/`). Baidu : inutile tant que le site est sur GitHub
  (GitHub bloque son robot).

## Reste à faire
- Sécurité (29/09/2026) : le dépôt du moteur était PUBLIC (code et builds visibles par tous). Il est
  maintenant privé et renommé `yop2d-moteur` ; licence « tous droits réservés » ajoutée ; nouveau
  dépôt public `yop2d` pour les téléchargements (release v0.1.921). Chaque nouvelle version publique :
  Release dans `zinzin66/yop2d` avec un fichier nommé exactement `Yop2D.apk`, tag `v0.1.<build>`.
- FAIT le 30/09/2026 (voir « Pages ») : exemples téléchargeables depuis le site. Plan d'origine : Dossier `exemples/`
  (zip + vignettes) + `exemples/exemples.json` (nom et description en 9 langues, taille, version minimale
  du moteur) ; le moteur lit la liste au démarrage, garde 1 ou 2 exemples intégrés pour le hors-ligne,
  télécharge les autres à la demande et les garde. Page « Exemples » sur le site (référencement).
- Référencement (objectif : faire connaître Yop2D partout, y compris Russie et
  Chine) : aide pour les messages de forums et vidéos. itch.io :
  https://yop2d-dev.itch.io/yop2d-no-code-game-engine
- Ajouter les 3 captures manquantes de l'accueil (voir « Pages »).
- Faire tester les étapes des guides sur tablette (projets zip de test, voir
  `Doc/MEMO_NOEUDS.md` du moteur : bouton `{ }` du Blueprint et import de zip).
- Idées de guides suivants : caméra qui suit, sons et musique, animations,
  ennemi qui poursuit, tirer, apparitions d'ennemis, dialogue, clé et porte.
- Version 0.1.921 publiée par l'utilisateur sur GitHub et itch.io (29/09/2026) : effets, nouveaux
  nœuds et 5 exemples disponibles pour tous ; on peut en faire la promotion. Captures à faire par
  l'utilisateur (vitrine des effets, Neon jump) pour l'accueil et les vidéos.
