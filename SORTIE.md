# Liste de sortie du site (prochaine version du moteur sur Google Play)

À relire le jour de la publication, dans l'ordre. Les demandes des utilisateurs sont dans `DEMANDES.md`. Mise à jour : 05/11/2026.

## Avant la publication (côté moteur, par l'utilisateur et l'autre session)
- [ ] Le changement des statistiques (PostHog) et `minSdk 26` (abandon d'Android 7) sont faits dans le même build : voir `Doc/STATISTIQUES_POSTHOG.md` du dépôt privé du moteur.
- [ ] Build de test donné aux testeurs ; dans PostHog, l'événement `yop2d_ouvert` arrive sans personne identifiée.
- [ ] Build normal avec la case `aab` cochée ; récupérer `Yop2D.aab` dans les Releases du dépôt privé.
- [ ] Console Google Play : envoyer l'AAB, lire le **rapport de pré-lancement** (plantages sur de vrais appareils), regarder combien d'appareils ne recevront plus la mise à jour (Android 7).
- [ ] Publier avec un **déploiement progressif** : 20 à 50 % des joueurs, puis 100 % après 2 ou 3 jours sans hausse de plantages (*Android vitals*). En cas de bug grave : « Arrêter le déploiement ».
- [ ] Release GitHub « Latest » dans `zinzin66/yop2d` (fichier nommé exactement `Yop2D.apk`, tag `v1.0.<build>`) et itch.io : les installations hors Google Play y cherchent leurs mises à jour.

## Sur le site, le jour de la publication
1. **Fusionner la demande « brouillon »** du guide Tower defense (PR #118) : elle décrit l'outil Parcours, absent de la version Google Play actuelle. Y mettre la date du jour dans le sitemap si on veut.
2. **Vider la liste des nouveautés** : `aide/source/nouveautes.json` (`noms_en` vide, `depuis` vide). Les 64 nœuds cachés deviennent publics.
3. **Relancer les générateurs**, dans cet ordre (clone du moteur = `<moteur>`) :
   `python3 outils/generer_aide_noeuds.py <moteur>` → `python3 outils/generer_pages_noeuds.py` → `python3 outils/generer_guides.py <moteur>` → `python3 outils/generer_exemples.py` → `python3 outils/generer_accueil.py` → `python3 outils/generer_llms_full.py`.
4. **Exemples** : dans `outils/exemples/source.json`, mettre `moteur_min` = numéro du build de sortie pour les exemples récents (`hana_moustique`, `tower_defense`, `tactics_*`, `day_night`, `nuit_village`, `ui_kit`, `missile_tutorial`, `bounce`, `flock`, `crystal_breaker`). Puis `generer_exemples.py`. Le build de sortie doit être supérieur ou égal à 1235.
5. **Compteurs** à changer à la main (nombre de modèles du moteur : compter ceux qui ne sont pas des guides, 59 au 05/11/2026) :
   - `outils/accueil/<langue>.json` : « 50 modèles » (plusieurs endroits par langue, 9 langues) ;
   - `outils/generer_accueil.py` : lignes « 50 templates, 21 example games » (deux endroits) et « version 1.0, October 2026 ».
   - Le nombre de nœuds et d'exemples se met à jour tout seul. Vérifier le nombre de cartes de l'accueil.
6. **Android 8+** (abandon d'Android 7) : remplacer « Android 7+ » dans `outils/accueil/<langue>.json`, `generer_accueil.py`, les FAQ, `llms.txt` (par le générateur), la page testeurs (`generer_testeur.py`) et dans la section « Faits à respecter » de `CLAUDE.md`.
7. **Page confidentialité** (`confidentialite.html`, français et anglais, lignes qui citent Aptabase) : « Les statistiques sont reçues par PostHog, hébergé en Europe (Francfort). Le pays est estimé à partir de la connexion, sans conserver d'adresse IP. »
8. Régénérer, vérifier une page de chaque sorte (accueil, un guide, aide des nœuds, `llms.txt`), puis fusionner. Le site est à jour 1 à 2 minutes après.

## Décisions à prendre ce jour-là
- [ ] `AFFICHER_APK` (aujourd'hui `False` : le bouton « Télécharger l'APK » est caché de l'accueil).
- [ ] `FORMULAIRE_ENSEIGNANTS` (aujourd'hui vide : le bouton enseignants est caché ; il faut créer le formulaire).
- [ ] Wording des exemples : « 31 jeux d'exemple » ou « 20 jeux d'exemple, 11 de plus avec la mise à jour » (11 exemples demandent la nouvelle version tant qu'elle n'est pas publiée).
- [ ] Vidéo YouTube de la sortie : l'ajouter en tête de `VIDEOS` (`generer_accueil.py`) et dans les 9 fichiers `outils/accueil/<langue>.json`.

## À faire par l'utilisateur (hors dépôt)
- [ ] Fiche Google Play : « Android 8 ou plus », notes de version, captures si l'interface a changé.
- [ ] Page itch.io et devlog ; annonce Discord (anglais) et Mastodon.
- [ ] Console Google Play, 2 à 3 jours après : plantages, puis relever le déploiement à 100 %.
- [ ] Tableau de bord PostHog : le construire quand les vrais événements arrivent (demander la recette).

## Règle « version minimale » (08/11/2026, idée de l'utilisateur) : plus d'attente de la sortie pour publier une documentation
- On PUBLIE tout de suite le guide, la carte de l'accueil et la description du nœud d'une fonction qui existe déjà dans un build de test, avec le **numéro du PREMIER build qui la contient** (dernier nombre de la version : build 1262 = version 1.0.1262).
- Guide : `"depuis": 1262` dans `guides/source/<guide>/<langue>.json` (les 10 langues) → bandeau « Demande la version 1262 de Yop2D ou plus récente » (`gen.NOTICE`, `bandeau_version` de generer_guides.py).
- Nœud : `aide/source/nouveautes.json`, `"noms_en": {"nom anglais du nœud": build}` → même phrase au début de sa description (aide, pages `noeuds/`, llms.txt « [from version N] »).
- Accueil : une phrase « À partir de la version N » en fin de carte.
- **Rien à modifier le jour de la sortie** : un utilisateur dont la version est plus récente voit que la sienne est supérieure. Ne PAS vider `nouveautes.json`.
- Le numéro de build d'un test = `run_number` de l'action « Build Yop2D » (page Actions du dépôt privé), ou `versionName` dans l'APK de test.
- Premiers cas : capteurs (inclinaison 1255, secousse 1261, « Remettre l'inclinaison à zéro » 1262 → guide et carte « à partir de 1262 »).
