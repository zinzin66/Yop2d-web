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
  interface_demarage, interface_modeles, interface_bibliotheque, interface_editeur, interface_tuiles, interface_animation,
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
- `guides/` : 9 guides débutant en 9 langues, **générés** (voir « Guides » plus bas).
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
  Depuis le 02/10/2026, le zip publié s'appelle `<id>-<version>.zip` (le cache du site, ~10 min, servait l'ancien zip
  sous le même nom) : les générateurs du moteur écrivent `<id>.zip`, `generer_exemples.py` le renomme et efface les
  versions précédentes. Un exemple modifié SANS changer sa `version` ne sera pas retéléchargé.
- `packs/` : **packs de la bibliothèque du moteur** (depuis le 02/10/2026, onglet « Packs à télécharger »). Un dossier
  par pack (`packs/<id>/<Dossier>/...`, `Animations/<nom>/`, `Licence.txt`, `pack.json` facultatif : voir
  `packs/LISEZMOI.md`). `python3 outils/generer_packs.py` fabrique `packs/<id>-<empreinte>.zip`, `packs/<id>.png` et
  `packs/packs.json` ; le robot `.github/workflows/packs.yml` le lance tout seul à chaque dépôt sur `main`
  (l'utilisateur peut déposer ses propres fichiers libres de droits). Packs : pirates, espace (Kenney, CC0)… ; depuis le
  10/10/2026 aussi medieval, combat_rpg, tir_dessus, tir_spatial, western (Superpowers, Pixel-boy, CC0), fabriqués par
  outils/modeles/preparer_packs_superpowers.py du moteur ; duelyst (30 héros et monstres animés repos/marche/attaque/touche/
  mort, Open Duelyst CC0, outils/modeles/preparer_pack_duelyst.py du moteur, choix dans CHOIX) ; squelettes (KayKit CC0, 3D
  rendue en images par outils/iso/preparer_pack_squelettes.py du moteur : de côté + vus de dessus 4 directions) ; donjon
  (KayKit Dungeon Remastered CC0, vue plongeante case par case : case = 192 x 144 px, cadre commun 240 x 324, grille 48 ;
  outils/iso/preparer_pack_donjon.py du moteur).

- `prefabs/` : **objets prêts à l'emploi à télécharger par le moteur** (depuis le 11/10/2026 : panneau Ressources → icône « Prefabs à télécharger »,
  ou + → Prefab → Image de l'emplacement → « Prefabs à télécharger »). Un dossier par prefab (`prefabs/<id>/` = petit projet Yop2D à UNE scène +
  `prefab.json` nom/description 9 langues, licence), mode d'emploi `prefabs/LISEZMOI.md`. `python3 outils/generer_prefabs.py` fabrique
  `prefabs/<id>-<empreinte>.zip`, `<id>.png`, `prefabs.json` ; le robot `.github/workflows/prefabs.yml` le lance tout seul à chaque dépôt sur `main`.
  Premiers prefabs (CC0, de l'utilisateur) : bouton animé rectangulaire en 6 couleurs + variante « texte animé ».
  11/10/2026 : 7 prefabs « boutons de styles » (étoile qui tourne, ninja pixel à cheval, néon, discret avec halo, verre, texte souligné,
  rond ▶) fabriqués par `python3 outils/creer_prefabs_styles.py <clone du moteur>` (images dessinées, sprites ninja Superpowers CC0, sons Yop2D,
  polices OFL) puis `generer_prefabs.py`. DOCUMENTATION FAITE le 11/10/2026 (demande de l'utilisateur) : 9e guide « prefabs » (9 langues), accueil
  (cartes « Objets prêts à l'emploi à télécharger » et « Un style de dialogue à votre goût », FAQ « Qu'est-ce qu'un prefab ? » : 24 questions,
  35 cartes), llms.txt (section prefabs lue dans prefabs/prefabs.json), sitemap. Ne pas confondre avec la carte « Scènes comme objets (prefabs) ».
  11/10/2026 (soir) : 2e lot « Interface » (4 prefabs, `python3 outils/creer_prefabs_styles.py <clone du moteur> interface`, ne pas relancer
  sans l'argument : chaque lancement refait des identifiants neufs) : `interrupteur` (ON/OFF, variable locale « etat », animation 7 images),
  `barre_vie` (remplissage = image dont la largeur suit « =vie * 6 », 3 couleurs, clignote sous 30, se remplit à zéro), `score_pop` (variable
  « score », le chiffre grossit + étincelles), `fenetre_pause` (bouton ⏸ + fenêtre Reprendre / Recommencer / Quitter, voile sombre, bouton
  retour du téléphone ; masquée par « Au démarrage »). Les formules ne nomment JAMAIS un objet (l'import renomme « _2 » sans changer les
  formules) : elles lisent la variable de l'objet visé par le nœud. Pas encore testés sur tablette ; documentation (guide, accueil) à ajouter. 11/10/2026 : dans le moteur (pas encore publié), un prefab ajouté devient une VRAIE SCÈNE du projet liée à la scène ouverte (liste des Scènes : « ↳ nom » sous la scène qui l'utilise) : guide « prefabs » et FAQ à réécrire en 9 langues quand le moteur sera validé.

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
- 01/10/2026 : exemple « Climb & run » (l'animation change selon le mouvement : marche, accroupi, saut, échelles), 11 exemples.
- 01/10/2026 : RÈGLE DES FORMULES (demande de l'utilisateur : pas de code de programmeur dans les exemples) : une
  condition = une comparaison simple ; `outils/modeles/verifier_formules.py` du moteur vérifie les zips. Les 11 exemples
  réécrits (conditions « a && b » découpées en nœuds à la suite, Climb & run et Dungeon walk avec les nouveaux
  COMPORTEMENTS du moteur, cadenas avec « Revenir à 0 après ») ; moteur_min 961 (962 pour Dungeon escape).
- 01/10/2026 : aide à jour pour les COMPORTEMENTS du moteur : nœud « Changer le comportement », option « Revenir à 0
  après » de « Ajouter à une variable » ; anciens nœuds marqués "cache" dans le catalogue (activer_physique,
  changer_rebond, modifier_deplacable) retirés de l'aide par generer_aide_noeuds.py (131 nœuds). Guides « Faire sauter » et
  « Déplacer » réécrits pour la fenêtre « ⚙ Comportement de l'objet » (plus de « Physique » dans l'Inspecteur) ; nouveau
  guide « comportements » (7 guides, 3e de la liste ; noms de la fenêtre écrits en clair dans chaque langue car ils
  viennent de TextesEditeur.java du moteur, pas de lang_<langue>.json : les repères {{lang:comp_...}} ne marchent pas).
- 30/09/2026 : version 0.1.948 publiée (guide « Ton premier jeu en 5 minutes », nouvelle fenêtre de réglage
  « ① Sur quoi ? / ② Réglages » avec aides et ligne « En clair », barre d'outils réduite, style sobre bleu néon).
  Accueil (9 langues) : cartes « Ton premier jeu en 5 minutes » et « Des réglages en clair » (17 cartes),
  carte « Un éditeur simple et confortable », blocs vitrine modèles et « Le cerveau de vos jeux », FAQ « Comment apprendre ».
  Captures de l'éditeur (barre d'outils, fenêtre de réglage) à refaire par l'utilisateur avec la 0.1.948.
- 01/10/2026 : bouton « Ranger les nœuds » du Blueprint (moteur build 968, validé). SORTIE préparée (build 969, version
  normale) : accueil (9 langues) : 35 modèles, 11 exemples listés (vitrine et FAQ), carte « Comportements prêts à l'emploi »
  (remplace « Physique et comportements »), nouvelles cartes « Grilles et puzzles », « Vue isométrique », « Un Inspecteur
  clair » (20 cartes), phrase « Ranger les nœuds » dans le bloc vitrine des nœuds.
- 02/10/2026 : exemple « Memory cards » (jeu de memory, 12 exemples, moteur_min 971). Moteur : événements « Au clic sur un
  objet »… ciblables par « # tag » (l'objet touché = objet impliqué) et nœud « Mélanger les places » (132 nœuds) : aide,
  pages `noeuds/`, exemples, accueil (vitrine et FAQ : douze exemples) et `llms.txt` régénérés.
- 02/10/2026 : packs en ligne de la bibliothèque (`packs/`, générateur, robot GitHub, mode d'emploi) : Pirates et Espace.
- 02/10/2026 : comportement « Patrouille (va-et-vient) » du moteur (build 1002, pas encore publié) : aide du nœud « Changer
  le comportement », guide « comportements » (paragraphe « Un ennemi qui marche tout seul »). Accueil (9 langues) : carte
  « Mon héros animé et 4 missions » (guide intégré + missions pièces, ennemi, victoire, APK ; 21 cartes), phrase Patrouille
  dans « Comportements prêts à l'emploi », FAQ « Comment apprendre » complétée + question « reprendre une mission »
  (☰ → Missions pas à pas, Passer / ◀ ; 20 questions). Boutons cités = textes du moteur (guide_passer, gp_faire_pour_moi).
- 03/10/2026 : version 0.1.1013 publiée (GitHub, itch.io, test fermé Google Play). PR #42 (Patrouille, missions) fusionnée.
  Accueil (9 langues) : 3 nouvelles cartes « Bibliothèque Yop2D intégrée », « Découvrir l'éditeur », « Choisissez votre
  langue » (24 cartes) ; phrases ajoutées aux FAQ « images, sons et musiques » et « Comment apprendre ». `llms.txt` régénéré.
- 03/10/2026 : nouveau bloc vitrine « Une bibliothèque qui contient tout » (capture `interface_bibliotheque.png` fournie par
  l'utilisateur, 12 blocs, 3e de la liste). Bloc « modèles » corrigé : le moteur ne s'ouvre plus sur l'onglet Modèles au 1er lancement.
- 07/10/2026 : NOUVELLE VERSION (build 1039, normale + AAB ; le 1038 avait un défaut). Site (PR #43) : bloc « À l'école et pour les enfants »
  (clé « ecole » des fichiers accueil, section #school, mode école en 5 étapes, contact Discord = profil
  https://discord.com/users/557189525437153290 + nom zinzin0000 ; formulaire enseignants : FORMULAIRE_ENSEIGNANTS de
  generer_accueil.py, None tant que l'utilisateur n'a pas créé de Google Forms), FAQ 22 questions, 36 modèles, 13 exemples
  (Nexus UI), 26 cartes, 5 packs en ligne (hologramme, effets, avion, monstres, gestes ; sources préparées par
  outils/modeles/preparer_packs_en_ligne.py du moteur), aide des 5 nœuds verts.

- 08/10/2026 : SORTIE « jeux de dialogue » (build final 1045, APK + AAB) : aide et pages `noeuds/` régénérées (146 nœuds :
  Dire une phrase, Poser un choix, Changer le décor, Montrer / cacher un personnage, Terminer l'histoire, Demander un texte,
  Ambiance, Zoomer l'écran, Transition de l'écran) ; accueil (9 langues) : 37 modèles, 14 exemples (Firefly Night dans les
  listes), 2 cartes « Jeux de dialogue (visual novel) » et « Ambiances, zoom et transitions » (28 cartes), FAQ « visual novel
  comme avec Ren'Py ? » (23 questions) ; llms.txt. Pack personnages_vn et exemple Firefly Night publiés (PR #47).
- 09/10/2026 : SORTIE « visual novel complet » (build final 1062, APK + AAB) : écran titre (Continuer, Nouvelle partie,
  Fins et galerie avec photos souvenirs), sauvegarde auto + 5 emplacements, ◀ Retour, ⚙ réglages du joueur, menu ☰ repliable,
  portrait, nœuds « Amitié (cœurs) » et « Si l'amitié… » (149 nœuds), voix lue, réponses en images, 🗺 carte de l'histoire,
  guide intégré « Ma première histoire » (4e guide, cadre jaune aussi dans les fenêtres). Site : aide des nœuds, accueil
  (cartes « Un vrai visual novel, complet » et « Ma première histoire en 5 minutes », 30 cartes ; FAQ Ren'Py complétée),
  Firefly Night v2 (moteur_min 1053), llms.txt.
- 09/10/2026 : 0.1.1062 publiée (PR #50 fusionnée). Comparatif de l'accueil (9 langues) : ligne Ren'Py (5 moteurs), puce
  « histoire à choix sans script » dans « fait pour vous si », Ren'Py = meilleur choix pour un long visual novel sur ordinateur
  (rester humble : Ren'Py est la référence) ; note « octobre 2026 ».
- 10/10/2026 : 8e guide « histoire-choix » (visual novel : Hana tout prête, Dire une phrase, Poser un choix, fins + écran titre,
  amitié, pour aller plus loin) en 9 langues, sitemap, llms.txt. 2e vidéo YouTube (histoires à choix,
  JPe2HYy0XvE, 09/10/2026) : en tête de VIDEOS (accueil, llms.txt) et bloc "video" du guide histoire-choix (9 langues).
- 10/10/2026 : Mastodon https://mastodon.social/@Yop2d (MASTODON de generer_accueil.py) : <link rel="me"> dans l'en-tête,
  bouton dans « Rejoindre la communauté », lien en bas de page (rel="me" = coche verte « site vérifié » sur le profil), sameAs, llms.txt.
- 10/10/2026 : exemple « Crypt key » (15 exemples, moteur_min 1062) fait avec le pack donjon : salle case par case, trappes qui
  s'ouvrent (Répéter + Changer l'image + zone « hole » déplacée), pics, gardien squelette piloté par les nœuds (commandes « aucune »
  + Glisser vers), clé, porte en bois qui s'ouvre (nouvelles images `mur_porte_ouverte_<côté>` du pack). Générateur :
  outils/modeles/generer_exemple_crypte.py du moteur. Accueil (9 langues) : exemple dans la liste, « quinze » partout.
- 10/10/2026 : pack en ligne « cartoon » (garçon et pingouin HD animés, Segel / OpenGameArt, CC0 ; outils/modeles/
  preparer_pack_cartoon.py du moteur). Servira à la vitrine des filtres (exemple « Filters showcase », à publier à la sortie).
- 10/10/2026 : exemple « Filters showcase » (32 filtres d'écran + 19 transitions, moteur_min 1072) ajouté dans exemples/ (16 exemples) :
  les versions plus anciennes du moteur affichent « Mets Yop2D à jour pour y jouer ». Fabriqué par outils/modeles/generer_exemple_filtres.py
  du moteur. Accueil (compteurs « quinze » -> « seize ») et aide des nœuds filtres/transitions : À FAIRE à la prochaine sortie.
- 10/10/2026 (soir) : SORTIE PRÉPARÉE (moteur build 1077, version normale, APK seul, SANS AAB ; à publier : release v0.1.1077 Latest,
  Yop2D.apk, + itch.io). Site (branche ccr-e5a50d19-voomo0, PR à fusionner À LA PUBLICATION) : aide des nœuds 153 (descriptions 9 langues
  de filtre_ecran, arreter_filtre, changer_scene_transition, transition_ecran mis à jour, événement NoeudEventBoutonRetour ajouté à
  EVENEMENTS de generer_aide_noeuds.py ; catégories renumérotées : 10-transitions ... 15-filtres), pages noeuds/, accueil (9 langues :
  33 cartes dont « Filtres d'écran et transitions », « Plein écran sur tous les téléphones », « Le bouton retour du téléphone » ;
  16 exemples avec Filters showcase), llms.txt, exemple Filters showcase (moteur_min 1072).

## Moteurs de recherche
- Google Search Console : propriété `https://zinzin66.github.io/Yop2d-web/`, fichiers
  `google74fcdd47f85fa058.html` et `google55621bdcee9caacd.html` (ne pas supprimer).
- Bing : `BingSiteAuth.xml`. Yandex (28/09/2026) : fichier dans le dépôt
  `zinzin66/zinzin66.github.io` (racine de l'adresse, avec `robots.txt` et une
  redirection vers `/Yop2d-web/`). Baidu : inutile tant que le site est sur GitHub
  (GitHub bloque son robot).

## Reste à faire
- EN ATTENTE (09/10/2026) : réponse d'un joueur sur des objets « pas collés aux bords de l'écran » (bandes noires quand
  l'écran est plus allongé que le jeu). Détails et solutions proposées dans le CLAUDE.md du moteur (« À corriger »).
  Si une solution est construite : mettre à jour l'accueil (carte ou FAQ) à la sortie.
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
- 08/10/2026 : JEUX DE DIALOGUE dans le moteur (« visual novel », build de test 1042) : 5 nouveaux nœuds (Dire une phrase,
  Poser un choix, Changer le décor, Montrer / cacher un personnage, Terminer l'histoire), fiches Personnage, Style des
  dialogues, Hana (IAMST, CC0) et 3 décors aquarelle (Clifton Lambert, CC0) intégrés, modèle « Histoire à choix ». Exemple « Firefly Night » (Pen, Angie, Iris : pack en ligne personnages_vn = DoubleFree CC0, sans les images d’Angie blessée ; ne pas mélanger avec Hana, autre style).
  Descriptions des 5 nœuds écrites en 9 langues dans aide/source/descriptions/. À LA SORTIE : relancer
  generer_aide_noeuds.py + generer_pages_noeuds.py + generer_accueil.py (llms.txt), carte « Jeux de dialogue » sur l'accueil,
  pack en ligne des personnages de Breezy (FAIT : packs/personnages_breezy, CC0, ne pas servir à entraîner des IA). Licences : Rachel Chen et Potat0Master
  interdisent la redistribution (pas dans nos packs).
- 10/10/2026 : 3e vidéo YouTube (filtres d'écran et transitions, szUu6p-jNmY) : en tête de VIDEOS (accueil 9 langues, llms.txt).
- 11/10/2026 (soir) : descriptions des 3 nouveaux nœuds de dialogue (animer_personnage, mode_roman, scene_rejouable) écrites en 9 langues dans aide/source/descriptions (PAS ENCORE régénérées : à la sortie du moteur, lancer generer_aide_noeuds.py puis generer_pages_noeuds.py puis generer_accueil.py ; ajouter à l'accueil les cartes « Animer les personnages », « Galerie, scènes à rejouer et musiques », « Mode roman »).
- 11/10/2026 (nuit) : SORTIE PRÉPARÉE (moteur build 1088, version normale, APK seul, SANS AAB ; à publier : release v0.1.1088 Latest, Yop2D.apk, + itch.io). Site (branche ccr-e5a50d19-voomo0, PR à fusionner À LA PUBLICATION) : aide des nœuds 156 (Animer un personnage, Mode roman, Scène à rejouer), pages noeuds/, accueil (9 langues : 38 cartes dont « Animer les personnages », « Galerie, scènes à rejouer et musiques », « Mode roman » ; carte et FAQ prefab : un prefab ajouté devient sa propre scène + éléments d'interface ; FAQ visual novel complétée), guide « prefabs » réécrit (scène à part, éléments d'interface), llms.txt, 4 nouveaux prefabs d'interface déjà en ligne (PR #67). Dans le moteur : prefab = vraie scène liée, liste des Scènes avec prefabs décalés dessous, mouvement de celui qui parle réglable (durée + allure), bouton « Prefabs à télécharger » retiré de la fenêtre des assets.


- 14/10/2026 (soir) : SORTIE PRÉPARÉE (moteur : build de test 1098 validé par les testeurs avant sortie ; à publier : release Latest + itch.io + éventuellement AAB). Site (PR à fusionner À LA PUBLICATION) : aide des nœuds 158 (missile_guide, detruire_apres décrits en 9 langues), pages noeuds/, exemple « Space 1 » (exemples/space_1-1.zip, vertical, moteur_min 1098 : mettre le numéro du build de sortie si les missiles guidés ont changé), accueil (9 langues : 17 exemples, 4 nouvelles cartes « Jeux en portrait », « Missiles guidés et explosions », « Dialogues entièrement personnalisables », « Compteur de FPS et temps » = 42 cartes), llms.txt. Formules fps et delta : citées dans la carte, pas de page d'aide à part (elles sont dans la liste « Temps et jeu » du moteur).

- 15/10/2026 (soir) : SORTIE PRÉPARÉE (suite, moteur : build de test 1104+ ; PR #72 à fusionner À LA PUBLICATION). Space 1 RETIRÉ de la sortie (l'utilisateur veut encore améliorer le sol et placer des décors ; zip gardé chez lui, à remettre dans exemples/ + source.json quand il sera fini). Exemple « Hana a une question urgente » AJOUTÉ (hana_question-1.zip, 9 langues, 104 nœuds, moteur_min 1072, généré par outils/modeles/generer_exemple_hana.py du moteur ; pas testé sur tablette par l'utilisateur) : toujours 17 exemples. Accueil (9 langues) : 39 modèles (au lieu de 37), 5 nouvelles cartes (icône du jeu, jeux dans la langue du joueur, éditeur de tuiles, boutons et écrans de dialogue stylables, MP3 converti en OGG) = 47 cartes, FAQ « Comment changer l'icône ? » (25 questions). Aide des nœuds inchangée (158). Remarque de l'utilisateur : l'onglet Exemples est peu regardé par les nouveaux utilisateurs ; il trouve les dialogues (Afficher un dialogue / texte) plus puissants que les visuels pour l'instant.
- 16/10/2026 : accueil (9 langues) : 3 nouvelles cartes « Enregistrement automatique », « Changer de scène sans quitter le Blueprint », « Une zone caméra bien visible » (50 cartes). Aide des nœuds inchangée (158), 39 modèles confirmés (40 dossiers publics moins les guides).
- 16/10/2026 : PACK EN LIGNE « ruines » (packs/ruines, Quaternius « Ultimate Modular Ruins », CC0, 213 images, ~600 Ko ; fabriqué par outils/iso/preparer_pack_ruines.py du moteur à partir des .obj fournis par l'utilisateur) : VUE ISOMÉTRIQUE 2:1, case = losange 128 x 64 px (voisine = +64/+32 ou -64/+32), cadres communs par famille et ancre dans packs/ruines/cadres.json, mode d'emploi dans Licence.txt. Dossiers : Sols, Murs (4 côtés : haut_droite, bas_droite, bas_gauche, haut_gauche), Courbes (4 coins arrondis), Arches (2 cases), Objets, Decors. Le robot packs.yml fabrique le zip après fusion sur main. À faire ensuite : exemple jouable de labyrinthe (lampe torche + compteur) et, peut-être, zone de contact à plusieurs points dans le moteur.
- 16/10/2026 : exemple « Ruins maze » (labyrinthe de ruines iso, lampe torche, moteur_min 1077) ajouté dans exemples/ : 18 exemples (accueil 9 langues : « dix-huit » + phrase, llms.txt) ; validé par l'utilisateur sur tablette (2e version). Pack « ruines » + exemple à publier avec la sortie (PR #72).
- 16/10/2026 : « Ruins maze » v2 (ruins_maze-2.zip, moteur_min 1108) : les ~674 petits murs invisibles sont remplacés par 4 ZONES À PLUSIEURS POINTS (1 enclos « interdit de sortir » de 213 points autour du sol + 3 îlots « interdit d'entrer »), fabriquées par generer_exemple_ruines.py du moteur (contour suivi sur les cases). Les anciens moteurs (< build avec ZonePolygone) verraient un rectangle géant : d'où moteur_min. METTRE le numéro du build de SORTIE dans moteur_min si différent de 1108. À publier avec la sortie (PR #72).
- 16/10/2026 (soir) : exemple « Space 1 » (exemples/space_1-1.zip, vertical 1080 x 1920, moteur_min 1108 : mettre le build de SORTIE si différent) : shoot'em up vertical dessiné en croquis par l'utilisateur (zip validé « impeccable ») + corrections de Claude (chiffres seuls, bonus logo1 qui donne des vies, missiles plus longs, sons et musique Yop2D, écran de départ, meilleur score de la session, mention « Fait avec Yop2D », textes en 9 langues). Vignette composée (exemples/space_1.png). 19 exemples (accueil 9 langues : « dix-neuf » + phrase Space 1, llms.txt). À publier avec la sortie (PR #72).

- 17/10/2026 : SORTIE PRÉPARÉE (build normal à lancer, APK seul sauf demande contraire ; release v0.1.<build> Latest + itch.io ; PR #72 à fusionner À LA PUBLICATION). Contient tout depuis la 1089 : zones à plusieurs points, 7 nouveaux modèles (46 au total), Space 1 + Ruins maze v2 (moteur_min 1108), écran titre qui revient à la fin, mode roman lisible, correctifs Aptabase (guides Android 8/9, mémoire du bouton { }), capteurs gel / alertes / export APK, accueil avec logos et fenêtre Réglages de Yop2D. Site : accueil 46 modèles + carte « Zones libres » (51 cartes, 9 langues), compteur shields.io retiré, confidentialité mise à jour.
- 17/10/2026 : GUIDE « musique » (10e guide, 9 langues, outils/traduire_guides.py) pour l'outil « Créer une musique » du moteur (bouton « Musique » de la fenêtre des Assets, Android 10+, PAS ENCORE PUBLIÉ : le moteur est en test). Accueil (9 langues) : carte « Créer sa propre musique » (52 cartes) + question FAQ « Comment créer ma propre musique ? » (26 questions), llms.txt, sitemap. À FUSIONNER SEULEMENT À LA SORTIE du moteur qui contient l'outil. Les noms de boutons sont écrits en clair dans chaque langue (viennent de TextesMusique.java du moteur).
- 17/10/2026 (suite) : accueil (9 langues) : 47 modèles (nouveau modèle « Créer ta musique » du moteur, catégorie « Images et sons »), llms.txt régénéré. Même règle : à fusionner à la sortie du moteur qui contient l'outil Musique.
- 18/10/2026 (soir) : guide « musique » mis à jour (9 langues : pose au toucher, défilement au glissement, petite fenêtre du bloc avec volume / modifier / enlever, appui long = déplacer, volume de piste, repère de départ) ; accueil (9 langues) : 2 nouvelles cartes « Vérifier mon jeu » et « Options du jeu exporté » (54 cartes) ; pages et llms.txt régénérés. Sur la branche claude/discord-yop2d-config-ox8qgh (PAS de PR : à fusionner À LA SORTIE de la version qui suit la 0.1.1121 ; test fermé Google Play commencé le 16/10/2026, 12 testeurs).
- 18/10/2026 (nuit) : PR #74 fusionnée (guide musique mis à jour, cartes « Vérifier mon jeu » / « Options du jeu exporté », llms.txt avec la liste de ce que l'éditeur contient déjà + résumé honnête de la maturité : les IA conseillaient « petite appli bêta, prends GDevelop » et ignoraient annuler/refaire). FAQ « Qu'est-ce que Yop2D sait faire aujourd'hui ? » (27 questions, 9 langues) : même but. Le mot « bêta » n'est écrit nulle part sur le site : ne pas l'ajouter, dire les limites en faits (Android et 2D seulement, un développeur, pas d'AAB pour les jeux des utilisateurs).
- 18/10/2026 (nuit) : AFFICHER_APK = False dans generer_accueil.py : le bouton « Télécharger l'APK » et la note d'installation (Play Protect) sont CACHÉS de l'accueil (9 langues) ; « Test Google Play » passe en premier, puis itch.io. Remettre True pour les montrer. Le lien APK reste dans llms.txt et le moteur cherche toujours ses mises à jour dans les Releases de zinzin66/yop2d. L'AAB de la 1129 est envoyé sur le test fermé Google Play.
- 18/10/2026 (nuit) : llms.txt n'a plus le lien « Latest APK » tant que AFFICHER_APK = False (les IA envoient vers le test Google Play ou itch.io). À revoir quand le moteur sera public sur Google Play (décision de l'utilisateur).
- 22/10/2026 (nuit) : PRÉPARATION DE LA SORTIE (branche claude/discord-yop2d-config-ox8qgh, PR #82, à fusionner À LA PUBLICATION ; le moteur est GELÉ pour le test fermé Google Play jusqu'au ~30/10) : aide des nœuds 166 (Sauvegarder / Charger les variables décrits en 9 langues, passage_decor : réglages animation + vitesse), accueil 64 cartes (« Garder le score et la partie ») et 50 modèles (modèle « sauve_score » du moteur), 21 exemples (ajout « Hana et le moustique », moteur_min 1148 : METTRE le build de sortie si les nœuds changent), llms.txt. Il reste à la sortie : version 1.0 déjà dans llms.txt ; décider AFFICHER_APK ; l'utilisateur prépare des images moins pixelisées / plus colorées pour retoucher certains exemples (alors augmenter leur `version` dans outils/exemples/source.json).
- 23/10/2026 : GUIDES DE RÉFÉRENCE « INTERFACE » (idée de l'utilisateur après avoir lu le wiki de GDevelop : « la base, expliquer Yop2D, rien sur comment réaliser un jeu » ; PR #83) : 11e guide `interface-editeur` (le 0/0 de la scène, barre du haut, panneau de gauche, Inspecteur) et 12e `interface-blueprint` (barre du haut du Blueprint + écran des nœuds), 9 langues. Images dans `guides/img/` (icônes découpées dans les captures de l'utilisateur `blueprint_<nom>.png` / `editeur_<nom>.png`, captures numérotées `blueprint_ecran.png`, `editeur_ecran.png`, `editeur_inspecteur.png` = 2 captures portrait assemblées). Nouveaux blocs de `generer_guides.py` : `["icones", [[icône, nom, texte]]]`, `["image", fichier, alt, légende]`, `["legende", [[numéro, texte]]]` ; page sans « etapes » = schéma TechArticle. Les noms du moteur sont écrits tels quels dans les textes (clés de lang_*.json / TextesEditeur.java). Les captures restent en français dans toutes les langues (dit dans la légende). À FAIRE avec de nouvelles captures de l'utilisateur : panneau Ressources / fenêtre de réglage d'un nœud / écran de démarrage / Assets. Si l'interface change (bouton ajouté ou déplacé), refaire l'icône et la phrase correspondantes. Décision : tout reste sur le site (pas de wiki GitHub : 9 langues, référencement, lien depuis le moteur).
- 23/10/2026 (suite) : 2 guides de référence de plus, `interface-demarrage` (écran de démarrage) et `interface-assets` (fenêtre Assets), + section « La fenêtre de réglage d'un nœud » à la fin du guide `interface-blueprint` (captures `demarrage_ecran.png`, `assets_fenetre.png`, `reglage_noeud.png` et icônes `demarrage_*.png` / `assets_*.png` dans `guides/img/`). Ordre des guides : ... musique, interface-demarrage, interface-editeur, interface-assets, interface-blueprint (11 à 14). Reste à documenter : panneau Ressources de l'éditeur (déjà en partie dans interface-editeur), fenêtre ⚙ Comportement, Bibliothèque Yop2D, éditeurs Musique / Bruitage / Mouvement / Planche / Démarrage (chacun a son guide ou carte : musique existe), ☰ Réglages du jeu.
- 23/10/2026 (suite 2) : 3 guides de référence de plus : `interface-bibliotheque` (Bibliothèque Yop2D), `interface-comportement` (fenêtre « Comportement de l'objet » : 8 façons de bouger + réglages ; capture assemblée de 3 captures portrait) et `interface-mouvement` (éditeur de mouvement). Ordre : ... interface-demarrage, interface-editeur, interface-assets, interface-bibliotheque, interface-comportement, interface-mouvement, interface-blueprint (11 à 17). Les textes d'interface viennent des fichiers du moteur (clés comp_*, mv_*, bib_*) : attention, une clé peut exister dans 2 fichiers Textes*.java (mv_titre est aussi dans MissionVictoire : lire TextesMouvement.java en priorité). Reste : Réglages du jeu (☰), éditeurs Bruitage / Planche / Démarrage / Titre / Texte, Musique (guide existant).

- 24/10/2026 : GUIDE « atelier-personnage » (18e, 9 langues, 3e place après « musique », bouton « Personnage » de la fenêtre des Assets du moteur : squelette, contours, tampon / couleur / remplissage par points / gomme, animations repos-marche-course-saut-attaque-touché). Noms de boutons écrits en clair dans chaque langue (viennent de TextesAtelier.java du moteur, clés at_*). Ajouté à GUIDES de generer_guides.py (les guides suivants sont renumérotés 12 à 18 dans aide/guides), sitemap.xml, llms.txt et carte de l'accueil (régénérés). Sur la branche claude/discord-yop2d-config-ox8qgh, PAS de PR : à fusionner À LA SORTIE du moteur qui contient l'Atelier personnage (moteur gelé jusqu'au ~30/10). FAQ « Comment animer un personnage à partir d'une seule image ? » ajoutée à l'accueil (28 questions, 9 langues) + llms.txt.
