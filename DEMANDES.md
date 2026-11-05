# Demandes des utilisateurs (Discord, testeurs)

Liste à relire facilement. Le détail technique est dans le `CLAUDE.md` du moteur (dépôt privé `yop2d-moteur`).
Mise à jour : 05/11/2026.

## Encore ouvert
- **Abandon d'Android 7 (décision du 05/11/2026)** : trop lent pour un moteur avec des effets, aucun testeur ne l'a. Côté moteur : `minSdk` 26 dans le même build que PostHog (consignes dans `Doc/STATISTIQUES_POSTHOG.md`, dépôt privé). Les joueurs sur Android 7 gardent leur version actuelle, sans nouvelles mises à jour. **Côté site, À FAIRE LE JOUR DE LA PUBLICATION** (pas avant, car la version Play actuelle accepte encore Android 7) : remplacer « Android 7+ » par « Android 8+ » dans l'accueil (`outils/accueil/<langue>.json`, 9 langues, et `generer_accueil.py`), les FAQ, `llms.txt` (relancer `generer_accueil.py`), la page testeurs, `CLAUDE.md` (« Faits à respecter ») ; et, à la main par l'utilisateur : fiche Google Play et page itch.io. Publier la mise à jour avec un **déploiement progressif** (20 à 50 % des joueurs puis 100 %) et regarder *Android vitals* de la console.
- **Plateaux hexagonaux ou en isométrique** avec un ancrage « pieds » (un objet qui dépasse de sa case) : idée Discord récente.
- **Gyroscope** : contrôler un personnage en inclinant l'appareil : idée Discord récente.
- **AdMob** (publicité dans les jeux exportés) : pas avant l'AAB des jeux. Le site dit « jamais de pub » pour Yop2D lui-même : décider de la formulation avant d'en parler.
- **« Mode Studio »** vu sur Max2D : **à clarifier**. On ne sait pas ce que c'est (rien dans les sources publiques, la documentation de Max2D n'a pas pu être lue). Question à poser à l'utilisateur Discord : « C'est quoi exactement, et que peux-tu y faire que tu ne peux pas faire dans Yop2D ? » (idéalement avec une capture). Ne rien construire avant sa réponse.
- **Jeu de combat (type Street Fighter), à deux personnages** : demandé par plusieurs utilisateurs ; **un sondage Discord est prévu avant de décider**. Faisable aujourd'hui en version simple (boutons à l'écran, zone de coup créée à la main, vie, arrêt sur image). Ce qui manque : 1) une zone de contact **par image d'animation** (une zone qui frappe, rouge, et une zone qui encaisse, bleue ; la zone de contact d'un objet est aujourd'hui fixe et aucun nœud ne peut la modifier) ; 2) un événement « quand une zone qui frappe touche une zone qui encaisse », qui ne part qu'une fois par coup ; 3) un nœud « état du combattant » (garde, étourdi, en l'air, mort) ; 4) des séquences de touches pour les coups spéciaux ; 5) une caméra qui cadre les deux combattants. Trois niveaux proposés : **léger** = un nœud « Frapper » qui crée une zone de coup invisible devant le combattant (petit chantier, sans fenêtre) ; **moyen** = fenêtre « zones de coup par image » dans l'éditeur d'animations, rectangles seulement (chantier moyen, comparable à l'éditeur de mouvement) ; **complet** = contours à plusieurs points, plusieurs zones par image, états, enchaînements. Maquette de la fenêtre : montrée et aimée (aucun code). Personnages possibles : pack en ligne « duelyst » (héros animés : repos, marche, attaque, touché, mort) et les packs 3D rendus en 2D.
- **« Vérifier mon jeu » : repérer une zone sans nœud de contact.** Exemple vu le 05/11/2026 : un débutant a posé deux zones « but » et deux textes de score, mais aucun nœud ne les utilise ; la balle sort de l'écran et le jeu s'arrête, sans aucun message. Règle proposée (conseil, pas erreur) : un objet de type zone (ou dont le nom commence par « Arco », « But », « Goal »…) qu'aucun nœud ne cite = « Cette zone ne sert à rien : relie-la à un événement de contact ». Autre piège du même débutant : « Maintenu sur objet » sur un bouton (le nœud part 60 fois par seconde) → conseil « Pour un bouton, préfère « Au clic sur un objet » ».
- **Aide aux débutants : montrer la logique avec des post-it et des cadres.** Un projet corrigé (pong avec buts, robot et scores) a été préparé avec des cadres et post-it. **Modèle « Pong » (jeu de raquette)** à ajouter côté moteur : base prête dans `tests/pong-modele.zip` (une scène « Game », noms en anglais : Ball, Player, Bot, WallLeft, WallRight, GoalPlayer, GoalBot, ScorePlayer, ScoreBot ; 37 nœuds ; 14 cadres et post-it EN ANGLAIS dans le Blueprint, dont un « Before you press Play : check the objects »). À faire pour en faire un vrai modèle : passer les textes des cadres en 9 langues (repères `{{t:cle}}`), vignette, catégorie « Règles du jeu » ; l'image de la balle est `Kenney/Tuiles/saw.png` (CC0 : joindre la licence) ; non testé sur tablette. Tutoriel « Pong » du site (guide en 9 langues, lié au guide « casse-briques ») à écrire une fois le modèle validé.
- **Notes dans la scène (pas seulement dans le Blueprint)** : idée retenue = une **zone invisible avec du texte**, jaune dans l'éditeur, jamais dessinée en jeu (le moteur saute déjà les zones rectangulaires : VueJeu ~1519). Petit chantier sans toucher aux fichiers protégés : 1) l'éditeur (CanvasEditeur) dessine la zone en jaune avec son texte ; 2) champ « Texte de la note » dans l'Inspecteur d'une zone (fenêtre de texte existante) ; 3) entrée « Note » dans « Ajouter un objet » : zone SANS physique, repérée par un tag « note » ; 4) « Vérifier mon jeu » ignore ces zones ; 5) la mettre derrière les objets et verrouillée (sinon elle gêne la sélection). Exemple d'usage : à côté de la balle, « N'oublie pas de donner le bon comportement à ton objet ». Plus simple en attendant : objets texte posés hors de la zone du jeu (limites : invisibles seulement si la caméra ne défile pas, et le débutant doit défiler pour les voir).

- **Statistiques : remplacer Aptabase (quota gratuit dépassé dès le 5 du mois).** Constat : l'offre gratuite d'Aptabase annonce 20 000 événements par mois (10 $/mois pour 200 000) ; les anciennes versions du moteur, très bavardes, continuent d'envoyer tant qu'elles ne sont pas mises à jour. Les plantages sont déjà vus par Google Play (Android vitals) : les statistiques ne servent qu'à mesurer l'usage (ouvertures, guides terminés, exports).
  **Piste gratuite retenue : PostHog Cloud UE** (1 million d'événements gratuits par mois ; données à Francfort ; sur le cloud UE l'adresse IP n'est pas conservée par défaut pour un nouveau projet, réglage « Discard client IP data »). Pas de SDK : un simple envoi HTTP depuis `Statistiques.java` du moteur.
  **Cahier des charges pour l'autre session (à vérifier dans la documentation de PostHog avant de construire ; le site posthog.com n'est pas accessible depuis la session du site) :**
  1) créer un projet PostHog **région UE** et prendre sa clé publique (clé d'envoi, sans danger dans l'appli) ;
  2) remplacer l'envoi vers Aptabase par un POST JSON vers l'adresse de capture de PostHog (la documentation indique `https://us.i.posthog.com/i/v0/e/` pour les États-Unis : prendre l'adresse équivalente UE) avec `api_key`, `event`, `distinct_id` et `properties` ;
  3) **événements anonymes** : `$process_person_profile` = `false` dans `properties` (jusqu'à 4 fois moins cher qu'un événement identifié) ; `distinct_id` = un identifiant au hasard **tiré à chaque ouverture de l'appli et jamais enregistré** (comme aujourd'hui : rien de personnel, pas de suivi du retour des joueurs) ;
  4) garder les mêmes événements, la même case de désactivation (⚙ Réglages de Yop2D) et les mêmes limites par ouverture (`MAXIMUM_PAR_OUVERTURE`) ; ne jamais envoyer de contenu de projet ;
  5) les versions déjà installées continuent d'envoyer à Aptabase (sans effet) : seules les nouvelles versions utilisent PostHog ;
  6) vérifier dans les réglages du projet PostHog : « Discard client IP data » activé, pas de cookies, pas de rejeu de session.
  **Côté site (À FAIRE seulement quand la version du moteur est publiée, pour ne pas dire une chose fausse avant)** : `confidentialite.html` (fr et en, lignes qui citent Aptabase) : « Les statistiques sont reçues par PostHog, hébergé en Europe (Francfort). Le pays est estimé à partir de la connexion, sans conserver d'adresse IP. » ; `CLAUDE.md` ; vérifier le formulaire « Sécurité des données » de Google Play (rien ne change : toujours anonyme, aucun identifiant d'appareil).
  Autres options regardées : Umami Cloud (100 000 événements gratuits, mais pensé pour le web, accès à l'API à vérifier), Firebase Analytics (gratuit mais SDK de Google et identifiants d'appareil : déconseillé), Aptabase auto-hébergé (demande un serveur).

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
- **Miroir de l'image du héros** (05/11/2026, utilisateur Discord : le garçon du pack « cartoon » marchait à l'envers) : réglage « Son image regarde : à gauche / à droite » dans ⚙ Comportement (Plateforme et Vue de dessus), ajouté dans le moteur (`Doc/MIROIR_IMAGE_HEROS.md`, dépôt privé), **pas encore publié** (build de test à faire, puis prochaine mise à jour). Les packs ne sont pas modifiés. À la sortie : phrase dans le guide « comportements » (9 langues) et, peut-être, une ligne dans la FAQ. Idée pour plus tard : un indice « regarde à gauche » dans le pack pour régler le champ tout seul.
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
