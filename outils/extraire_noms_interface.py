#!/usr/bin/env python3
"""Extrait les noms des boutons / fenêtres de l'appli (9 langues) depuis le moteur -> aide/source/noms_interface.json.

Usage : python3 outils/extraire_noms_interface.py <clone de zinzin66/yop2d-moteur>
Lu par generer_llms_full.py (section « App buttons and windows »). Relancer si le moteur renomme un bouton.
"""
import glob
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LANGUES = ["fr", "en", "es", "de", "it", "pt", "ru", "zh", "ja"]
ORDRE_JAVA = ["fr", "en", "es", "pt", "de", "it", "ru", "zh", "ja"]   # ordre des textes dans les fichiers Textes*.java

# (clé du moteur, description courte en anglais)
CLES_JAVA = [
    ("bt_blueprint", "Blueprint button (opens the node editor)"),
    ("bt_aide", "Help button (top bar)"),
    ("bt_menu", "Menu button (top bar)"),
    ("bt_jouer", "Play button (top bar)"),
    ("bt_aide_en_ligne", "Help menu entry: online help and guides"),
    ("ia_menu", "Help menu entry: ask an AI"),
    ("vj_menu", "Menu entry that checks the game for mistakes"),
    ("bib_titre", "Yop2D Library window"),
    ("mu_bouton", "Assets button: music maker"),
    ("bz_bouton", "Assets button: sound effects maker"),
    ("mv_bouton", "Assets button: movement (steps) editor"),
    ("pc_bouton", "Assets button: path editor"),
    ("pl_bouton", "Assets button: cut a sprite sheet"),
    ("at_bouton", "Assets button: character workshop"),
    ("dm_bouton", "Assets button: start screen editor"),
    ("lg_nom", "Blueprint scene list: the global logic (all scenes)"),
    ("bp_scenes_titre", "Blueprint top button: change of Blueprint (scene, global logic, my nodes)"),
    ("comp_bouton", "Inspector button: object behavior window"),
    ("menu_missions", "Menu entry: step-by-step missions"),
]
CLES_LANG = [
    ("bandeau_reglages_jeu", "Menu entry: game settings"),
    ("bouton_quitter", "Quit"),
    ("bouton_editer", "Edit (project list)"),
    ("demarrage_langue", "Language button (start screen)"),
    ("panneau_ress_scenes", "Resources panel: Scenes"),
    ("panneau_ress_assets", "Resources panel: Assets"),
    ("panneau_ress_variables", "Resources panel: Variables"),
]


def lire_java(dossier):
    """{clé: [fr, en, es, pt, de, it, ru, zh, ja]} depuis les appels a("clé", ...) / ajouter("clé", ...)."""
    textes = {}
    for chemin in glob.glob(os.path.join(dossier, "**", "Textes*.java"), recursive=True):
        src = open(chemin, encoding="utf-8").read()
        for m in re.finditer(r'\b(?:a|ajouter)\(\s*"([a-z0-9_]+)"\s*,((?:\s*"(?:[^"\\]|\\.)*"\s*,?){9})\s*\)', src):
            valeurs = re.findall(r'"((?:[^"\\]|\\.)*)"', m.group(2))
            if len(valeurs) == 9:
                textes.setdefault(m.group(1), [v.replace('\\"', '"').replace("\\n", " ") for v in valeurs])
    return textes


def lire_lang(dossier):
    d = {lg: {} for lg in LANGUES}
    for lg in LANGUES:
        for ligne in open(os.path.join(dossier, f"lang_{lg}.json"), encoding="utf-8"):
            m = re.match(r'\s*"([^"]+)"\s*:\s*"((?:[^"\\]|\\.)*)"', ligne)
            if m:
                d[lg][m.group(1)] = m.group(2).replace('\\"', '"')
    return d


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    moteur = sys.argv[1]
    java = lire_java(os.path.join(moteur, "app", "src"))
    lang = lire_lang(os.path.join(moteur, "app", "src", "main", "assets"))
    sortie = []
    for cle, desc in CLES_JAVA:
        if cle not in java:
            print("manquant (Java) :", cle)
            continue
        par_lg = dict(zip(ORDRE_JAVA, java[cle]))
        sortie.append({"cle": cle, "role": desc, "noms": {lg: par_lg[lg] for lg in LANGUES}})
    for cle, desc in CLES_LANG:
        if not all(cle in lang[lg] for lg in LANGUES):
            print("manquant (lang) :", cle)
            continue
        sortie.append({"cle": cle, "role": desc, "noms": {lg: lang[lg][cle] for lg in LANGUES}})
    chemin = os.path.join(RACINE, "aide", "source", "noms_interface.json")
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(sortie, f, ensure_ascii=False, indent=1)
        f.write("\n")
    print(f"{len(sortie)} noms écrits dans {chemin}")


if __name__ == "__main__":
    main()
