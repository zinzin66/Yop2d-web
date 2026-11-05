# Demandes des utilisateurs (Discord, testeurs)

Liste à relire facilement. Le détail technique est dans le `CLAUDE.md` du moteur (dépôt privé `yop2d-moteur`).
Mise à jour : 07/11/2026.

## Encore ouvert
- **Plateaux hexagonaux ou en isométrique** avec un ancrage « pieds » (un objet qui dépasse de sa case) : idée Discord récente.
- **Gyroscope** : contrôler un personnage en inclinant l'appareil : idée Discord récente.
- **AdMob** (publicité dans les jeux exportés) : pas avant l'AAB des jeux. Le site dit « jamais de pub » pour Yop2D lui-même : décider de la formulation avant d'en parler.
- **« Mode Studio »** vu sur Max2D : **à clarifier**. On ne sait pas ce que c'est (rien dans les sources publiques, la documentation de Max2D n'a pas pu être lue). Question à poser à l'utilisateur Discord : « C'est quoi exactement, et que peux-tu y faire que tu ne peux pas faire dans Yop2D ? » (idéalement avec une capture). Ne rien construire avant sa réponse.
- **Jeu de combat (type Street Fighter), à deux personnages** : demandé par plusieurs utilisateurs ; **un sondage Discord est prévu avant de décider**. Faisable aujourd'hui en version simple (boutons à l'écran, zone de coup créée à la main, vie, arrêt sur image). Ce qui manque : 1) une zone de contact **par image d'animation** (une zone qui frappe, rouge, et une zone qui encaisse, bleue ; la zone de contact d'un objet est aujourd'hui fixe et aucun nœud ne peut la modifier) ; 2) un événement « quand une zone qui frappe touche une zone qui encaisse », qui ne part qu'une fois par coup ; 3) un nœud « état du combattant » (garde, étourdi, en l'air, mort) ; 4) des séquences de touches pour les coups spéciaux ; 5) une caméra qui cadre les deux combattants. Trois niveaux proposés : **léger** = un nœud « Frapper » qui crée une zone de coup invisible devant le combattant (petit chantier, sans fenêtre) ; **moyen** = fenêtre « zones de coup par image » dans l'éditeur d'animations, rectangles seulement (chantier moyen, comparable à l'éditeur de mouvement) ; **complet** = contours à plusieurs points, plusieurs zones par image, états, enchaînements. Maquette de la fenêtre : montrée et aimée (aucun code). Personnages possibles : pack en ligne « duelyst » (héros animés : repos, marche, attaque, touché, mort) et les packs 3D rendus en 2D.
- **« Vérifier mon jeu » : repérer une zone sans nœud de contact.** Exemple vu le 06/11/2026 : un débutant a posé deux zones « but » et deux textes de score, mais aucun nœud ne les utilise ; la balle sort de l'écran et le jeu s'arrête, sans aucun message. Règle proposée (conseil, pas erreur) : un objet de type zone (ou dont le nom commence par « Arco », « But », « Goal »…) qu'aucun nœud ne cite = « Cette zone ne sert à rien : relie-la à un événement de contact ». Autre piège du même débutant : « Maintenu sur objet » sur un bouton (le nœud part 60 fois par seconde) → conseil « Pour un bouton, préfère « Au clic sur un objet » ».
- **Aide aux débutants : montrer la logique avec des post-it et des cadres.** Un projet corrigé (pong avec buts, robot et scores) a été préparé avec des cadres et post-it. **Modèle « Pong » (jeu de raquette)** à ajouter côté moteur : base prête dans `tests/pong-modele.zip` (une scène « Game », noms en anglais : Ball, Player, Bot, WallLeft, WallRight, GoalPlayer, GoalBot, ScorePlayer, ScoreBot ; 37 nœuds ; 14 cadres et post-it EN ANGLAIS dans le Blueprint, dont un « Before you press Play : check the objects »). À faire pour en faire un vrai modèle : passer les textes des cadres en 9 langues (repères `{{t:cle}}`), vignette, catégorie « Règles du jeu » ; l'image de la balle est `Kenney/Tuiles/saw.png` (CC0 : joindre la licence) ; non testé sur tablette. Tutoriel « Pong » du site (guide en 9 langues, lié au guide « casse-briques ») à écrire une fois le modèle validé.
- **Notes dans la scène (pas seulement dans le Blueprint)** : idée retenue = une **zone invisible avec du texte**, jaune dans l'éditeur, jamais dessinée en jeu (le moteur saute déjà les zones rectangulaires : VueJeu ~1519). Petit chantier sans toucher aux fichiers protégés : 1) l'éditeur (CanvasEditeur) dessine la zone en jaune avec son texte ; 2) champ « Texte de la note » dans l'Inspecteur d'une zone (fenêtre de texte existante) ; 3) entrée « Note » dans « Ajouter un objet » : zone SANS physique, repérée par un tag « note » ; 4) « Vérifier mon jeu » ignore ces zones ; 5) la mettre derrière les objets et verrouillée (sinon elle gêne la sélection). Exemple d'usage : à côté de la balle, « N'oublie pas de donner le bon comportement à ton objet ». Plus simple en attendant : objets texte posés hors de la zone du jeu (limites : invisibles seulement si la caméra ne défile pas, et le débutant doit défiler pour les voir).

## Testeur espagnol (jeux au tour par tour)
Pas encore fait :
- les hexagones ;
- une hauteur qui bloque le déplacement ;
- la peinture des hauteurs dans l'éditeur de tuiles ;
- les menus d'action et les armées en prefabs ;
- la campagne ;
- le tour simultané.

Déjà fait :
- une logique qui marche dans toutes les scènes (nœuds globaux) ;
- portées libres : portée minimale, cavalier, anneau, croix, saut ;
- nœud « Choisir une cible » ;
- statistiques personnalisées et calcul de dégâts libre ;
- kit tactique : fichier de règles, états (poison…), effets de zone, expérience, IA, brouillard de guerre, couleurs d'équipe ;
- nœuds de sélection d'unité, chemins qui restent dans la zone, joystick qui va jusqu'au bord, groupe « L'objet choisi (unité) » dans le panneau des valeurs ;
- fenêtres coupées par les boutons d'Android : réglé (« Ya se arregló el problema »).

## Autres demandes, déjà réalisées
- Russe : langue des jeux exportés et retour à l'écran titre.
- Personnaliser les boutons « Nouvelle partie ».
- Nœud « Bouton retour pressé ».
- Sauvegarde et chargement de variables.
- Ranger les fichiers en dossiers.
- Grille aimantée, joystick qui sort du cercle, recherche de chemin.
- Icône du jeu exporté.
- Formules fps et delta.
- Vitesse d'apparition des personnages.
- Transparence de la boîte de dialogue.
- Bug d'export à 0 Ko.
- Musique qui ne bouclait pas.
- Changer de scène depuis le Blueprint.
- Langues de l'interface (demande du développeur de Star2D).

## Exemples du site à publier avec la sortie
- Bounce, Flock, Crystal breaker : `moteur_min` provisoire **1235** dans `outils/exemples/source.json` (mettre le build de sortie). Images de Flock : autorisées.
