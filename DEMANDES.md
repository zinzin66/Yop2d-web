# Demandes des utilisateurs (Discord, testeurs)

Liste à relire facilement. Le détail technique est dans le `CLAUDE.md` du moteur (dépôt privé `yop2d-moteur`).
Mise à jour : 05/11/2026.

## Encore ouvert
- **Plateaux hexagonaux ou en isométrique** avec un ancrage « pieds » (un objet qui dépasse de sa case) : idée Discord récente.
- **Gyroscope** : contrôler un personnage en inclinant l'appareil : idée Discord récente.
- **AdMob** (publicité dans les jeux exportés) : pas avant l'AAB des jeux. Le site dit « jamais de pub » pour Yop2D lui-même : décider de la formulation avant d'en parler.
- **« Mode Studio »** vu sur Max2D : attend la réponse d'un utilisateur Discord.

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
