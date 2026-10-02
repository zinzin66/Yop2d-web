# Packs de la bibliothèque Yop2D

Chaque dossier ici est un **pack** que les moteurs Yop2D peuvent télécharger
(Bibliothèque → onglet « Packs à télécharger »). Pas besoin de nouvelle version du moteur.

## Ajouter un pack (depuis la tablette, GitHub dans le navigateur)

1. Ouvre le dossier `packs`, touche **Add file → Upload files**.
2. Glisse tes fichiers en les rangeant dans des dossiers. Le chemin se tape dans le nom :
   par exemple `foret/Arbres/sapin.png`. Le premier mot (`foret`) est le nom du pack.
3. Touche **Commit changes** (sur `main`). Un robot fabrique le pack en 1 à 2 minutes.

## Rangement d'un pack

```
packs/foret/
  Arbres/            ← chaque dossier devient un onglet (images, sons ou polices)
  Animaux/
  Sons/
  Animations/
    papillon/        ← les images d'une animation : papillon_1.png, papillon_2.png...
    renard/          ← un personnage : un dossier par action
      repos/
      marche/
      saut/
  Licence.txt        ← (conseillé) la licence des images : elle suit les fichiers dans les projets
  pack.json          ← (facultatif) nom et description en 9 langues
  vignette.png       ← (facultatif) l'image du pack ; sinon elle est composée toute seule
```

- Images : `.png` `.jpg` `.webp` — Sons et musiques : `.ogg` `.mp3` `.wav` — Polices : `.ttf` `.otf`
- Les noms d'actions reconnus par les comportements : `repos`, `marche`, `saut`, `grimpe`, `accroupi`
  (ou en anglais `idle`, `walk`, `jump`, `climb`).
- Utilise seulement des fichiers **libres de droits** (CC0, OFL...) ou que tu as faits toi-même.
- Ne touche pas aux fichiers fabriqués par le robot (`*.zip`, `*.png` et `packs.json` à la racine de `packs`).
