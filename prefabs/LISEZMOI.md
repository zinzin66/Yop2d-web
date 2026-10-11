# Prefabs (objets prêts à l'emploi) de Yop2D

Un **prefab** est un objet qui a déjà son comportement : par exemple un bouton qui s'anime quand on le survole.
Dans Yop2D : **Ressources → icône « Prefabs à télécharger »** (ou **+ → Prefab → Image → Prefabs à télécharger**) :
le prefab est copié dans le projet, puis on le pose dans la scène.

## Ajouter un prefab sur le site
1. Créer un dossier `prefabs/<id>/` (lettres minuscules, chiffres, `_`).
2. Y mettre un petit projet Yop2D **avec UNE seule scène** (exporté depuis Yop2D, ou fabriqué à la main) :
   `projet_sauvegarde.json`, `logique/`, `assets_ludexa/` (images, polices avec leur licence, `Textes/animations.txt`).
   Enlever le journal `diag_ludexa.txt`.
3. Y mettre `prefab.json` : `{ "nom": {fr, en, es, de, it, pt, ru, zh, ja}, "description": {…9 langues…}, "licence": "CC0", "auteur": "…" }`.
   Facultatif : `vignette.png` (sinon une vignette est composée avec l'image du bouton).
4. Déposer sur `main` : le robot `.github/workflows/prefabs.yml` lance `python3 outils/generer_prefabs.py` et fabrique
   `prefabs/<id>-<empreinte>.zip`, `prefabs/<id>.png` et `prefabs/prefabs.json` (la liste lue par le moteur).

## Règles pour un prefab partagé
- Noms uniques : l'objet, ses images et son animation commencent par l'id du prefab (`bouton_bleu`, `bouton_bleu_survol`),
  pour que plusieurs prefabs ou plusieurs copies ne se mélangent pas.
- Licence libre (CC0 de préférence) pour TOUT ce qui est dedans (images, sons, polices). Mettre la licence de la police avec elle.
- Les événements ciblent l'objet par son **nom** : le moteur renomme tout seul (`_2`, `_3`…) quand on en pose plusieurs.
