#!/usr/bin/env python3
"""Construit l'onglet « Nœuds » de aide.html à partir du moteur Yop2D.

Sources :
  - le moteur (dépôt zinzin66/yop2d-moteur) : app/src/main/assets/catalogue_noeuds.json
    et lang_<langue>.json → noms des nœuds, catégories, réglages, sorties ;
  - aide/source/descriptions/<langue>.json (ce dépôt) → rôle et exemple de chaque nœud.

Résultat : aide/noeuds/<langue>/NN-<categorie>.json (les anciens fichiers sont remplacés).

Utilisation :
  python3 outils/generer_aide_noeuds.py /chemin/vers/yop2d
"""
import json
import os
import re
import sys

LANGUES = ["fr", "en", "es", "de", "it", "pt", "ru", "zh", "ja"]
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Événements écrits en Java : même ordre que RegistreNoeuds.java (clé de nom, classe).
EVENEMENTS = [
    ("noeud_au_demarrage", "NoeudEventStart"),
    ("noeud_chaque_image", "NoeudEventChaqueImage"),
    ("noeud_fin_de_clic", "NoeudEventFinClic"),
    ("noeud_au_clic_sur_objet", "NoeudEventClicObjet"),
    ("noeud_fin_clic_sur_objet", "NoeudEventFinClicObjet"),
    ("noeud_event_maintenu_objet", "NoeudEventMaintenuObjet"),
    ("noeud_event_doigt_appuye", "NoeudEventDoigtAppuye"),
    ("noeud_event_bouton_retour", "NoeudEventBoutonRetour"),
    ("noeud_debut_de_glisser", "NoeudEventDebutGlisser"),
    ("noeud_fin_de_glisser", "NoeudEventFinGlisser"),
    ("noeud_collision_ab", "NoeudEventCollisionAB"),
    ("noeud_sortie_de_zone", "NoeudEventSortieZone"),
    ("noeud_au_survol", "NoeudEventSurvolObjet"),
    ("noeud_fin_de_survol", "NoeudEventFinSurvol"),
    ("noeud_au_choc_physique", "NoeudEventChoc"),
    ("noeud_quand_variable_change", "NoeudEventVariableChange"),
    ("noeud_evenement_local", "NoeudEventPersonnalise"),
    ("noeud_au_clic_action_aventure", "NoeudEventBoutonAction"),
    ("noeud_si_objet_touche_tag", "NoeudEventCollisionTag"),
]
# Cibles et réglages des événements (lus dans les classes Java).
CIBLES_EVENEMENTS = {
    "NoeudEventClicObjet": ["objet"], "NoeudEventFinClicObjet": ["objet"],
    "NoeudEventMaintenuObjet": ["objet"], "NoeudEventDebutGlisser": ["objet"],
    "NoeudEventFinGlisser": ["objet"], "NoeudEventCollisionAB": ["objet", "objetB"],
    "NoeudEventSortieZone": ["objet", "objetB"], "NoeudEventSurvolObjet": ["objet"],
    "NoeudEventFinSurvol": ["objet"], "NoeudEventChoc": ["objet"],
    "NoeudEventVariableChange": ["variable"], "NoeudEventCollisionTag": ["objet"],
}
REGLAGES_EVENEMENTS = {"NoeudEventPersonnalise": ["Nom de l'événement"], "NoeudEventCollisionTag": ["Tag"]}

# Étiquettes du schéma (propres à l'aide).
ETIQUETTES = {
    "fr": ("Entrée :", "Entrées :", "Sortie :", "Sorties :", "aucune (fin du script)"),
    "en": ("Input:", "Inputs:", "Output:", "Outputs:", "none (end of script)"),
    "es": ("Entrada:", "Entradas:", "Salida:", "Salidas:", "ninguna (fin del script)"),
    "de": ("Eingang:", "Eingänge:", "Ausgang:", "Ausgänge:", "keiner (Ende des Skripts)"),
    "it": ("Ingresso:", "Ingressi:", "Uscita:", "Uscite:", "nessuna (fine dello script)"),
    "pt": ("Entrada:", "Entradas:", "Saída:", "Saídas:", "nenhuma (fim do script)"),
    "ru": ("Вход:", "Входы:", "Выход:", "Выходы:", "нет (конец скрипта)"),
    "zh": ("输入：", "输入：", "输出：", "输出：", "无（脚本结束）"),
    "ja": ("入力：", "入力：", "出力：", "出力：", "なし（スクリプト終了）"),
}
ARRIVEE = " &nbsp;→&nbsp; "
# Guillemets de chaque langue (les descriptions sont écrites avec « »).
GUILLEMETS = {"fr": ("« ", " »"), "en": ("“", "”"), "es": ("«", "»"), "de": ("„", "“"), "it": ("«", "»"),
              "pt": ("“", "”"), "ru": ("«", "»"), "zh": ("“", "”"), "ja": ("「", "」")}


def lire_json(chemin):
    """Lit un JSON du moteur, en ignorant les lignes de repère // haut / // bas."""
    with open(chemin, encoding="utf-8") as f:
        lignes = [l for l in f.read().split("\n") if not l.strip().startswith("//")]
    return json.loads("\n".join(lignes))


def echapper(texte):
    return texte.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Traductions:
    def __init__(self, assets, catalogue):
        self.lang = {l: lire_json(os.path.join(assets, f"lang_{l}.json")) for l in LANGUES}
        self.secours = {}
        # Traductions déclarées dans le catalogue (même logique que CatalogueNoeuds.java).
        for valeur, noms in catalogue.get("libelles", {}).items():
            self._secours("option." + valeur, noms)
        for cle, noms in catalogue.get("categories", {}).items():
            self._secours(cle, noms)
        for n in catalogue["noeuds"]:
            if not n.get("nomCle"):
                self._secours("noeud_" + n["cle"], n.get("nom"))
            for s in n.get("sorties", []):
                if isinstance(s, dict):
                    self._secours("port_" + s["cle"], s.get("nom"))
            for c in n.get("champs", []):
                self._secours(n["cle"] + "." + c["cle"], c.get("nom"))

    def _secours(self, cle, noms):
        if isinstance(noms, str):
            noms = {"fr": noms}
        if isinstance(noms, dict) and noms:
            self.secours[cle] = noms

    def get(self, cle, langue):
        """Même ordre que Traducteur.get : fichier de langue, puis catalogue (langue, en, fr)."""
        if cle in self.lang[langue]:
            return self.lang[langue][cle]
        s = self.secours.get(cle)
        if s:
            return s.get(langue) or s.get("en") or s.get("fr")
        return None


def remplir(texte, langue, tr, noms_noeuds):
    """Remplace [[id_du_noeud]] et [[lang:cle]] par le nom affiché dans le moteur, entre guillemets,
    et met les guillemets « » de la description aux normes de la langue."""
    ouvre, ferme = GUILLEMETS[langue]

    def nom(m):
        cle = m.group(1)
        if cle.startswith("lang:"):
            valeur = tr.get(cle[5:], langue)
        else:
            valeur = noms_noeuds.get(cle, {}).get(langue)
        if not valeur:
            raise SystemExit(f"Repère inconnu [[{cle}]] ({langue})")
        return ouvre + valeur.strip().strip("[] ") + ferme

    texte = re.sub(r"\[\[([^\]]+)\]\]", nom, texte)
    return re.sub(r"«\s*([^»]+?)\s*»", lambda m: ouvre + m.group(1) + ferme, texte)


def schema(langue, cibles, reglages, sorties, tr):
    e1, e2, s1, s2, aucune = ETIQUETTES[langue]
    entrees = []
    for c in cibles:
        cle = {"objet": "noeud_cible_objet_a" if "objetB" in cibles else "noeud_cible_objet",
               "objetB": "noeud_cible_objet_b", "variable": "noeud_cible_variable",
               "scene": "noeud_cible_scene"}[c]
        entrees.append(tr.get(cle, langue))
    entrees += reglages
    morceaux = []
    if entrees:
        morceaux.append(f"<b>{e2 if len(entrees) > 1 else e1}</b> " + ", ".join(echapper(x) for x in entrees))
    if sorties is not None:
        if sorties:
            morceaux.append(f"<b>{s2 if len(sorties) > 1 else s1}</b> " + " / ".join(echapper(x) for x in sorties))
        else:
            morceaux.append(f"<b>{s1}</b> {aucune}")
    return ARRIVEE.join(morceaux)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    assets = os.path.join(sys.argv[1], "app", "src", "main", "assets")
    catalogue = lire_json(os.path.join(assets, "catalogue_noeuds.json"))
    tr = Traductions(assets, catalogue)
    descriptions = {}
    for l in LANGUES:
        chemin = os.path.join(RACINE, "aide", "source", "descriptions", f"{l}.json")
        descriptions[l] = json.load(open(chemin, encoding="utf-8")) if os.path.exists(chemin) else {}

    # Liste des nœuds dans l'ordre de l'éditeur : (clé de description, catégorie, nom, cibles, réglages, sorties)
    noeuds = []
    for cle_nom, classe in EVENEMENTS:
        noeuds.append(dict(id=classe, categorie="cat_evenements", cle_nom=cle_nom,
                           cibles=CIBLES_EVENEMENTS.get(classe, []),
                           reglages=REGLAGES_EVENEMENTS.get(classe, []), sorties=None, champs=[]))
    for n in catalogue["noeuds"]:
        cibles = [c for c in ("objet", "objetB", "variable", "scene") if n.get(c)]
        sorties = n.get("sorties", ["suivant"])
        noeuds.append(dict(id=n["cle"], categorie=n.get("categorie"), cache=n.get("cache", False),
                           cle_nom=n.get("nomCle") or "noeud_" + n["cle"], cibles=cibles,
                           reglages=[], champs=[n["cle"] + "." + c["cle"] for c in n.get("champs", [])],
                           sorties=[s["cle"] if isinstance(s, dict) else s for s in sorties]))

    noms_noeuds = {n["id"]: {l: tr.get(n["cle_nom"], l) for l in LANGUES} for n in noeuds}
    # anciens nœuds ("cache": true) : plus dans le menu de l'éditeur, donc plus dans l'aide (leur nom reste citable)
    noeuds = [n for n in noeuds if not n.get("cache")]

    ordre_categories = []
    for n in noeuds:
        if n["categorie"] not in ordre_categories:
            ordre_categories.append(n["categorie"])

    manques = []
    for l in LANGUES:
        dossier = os.path.join(RACINE, "aide", "noeuds", l)
        os.makedirs(dossier, exist_ok=True)
        for f in os.listdir(dossier):
            if f.endswith(".json"):
                os.remove(os.path.join(dossier, f))
        for i, cat in enumerate(ordre_categories, 1):
            liste = []
            for n in noeuds:
                if n["categorie"] != cat:
                    continue
                nom = tr.get(n["cle_nom"], l) or n["id"]
                reglages = [tr.get(r, l) or r for r in n["reglages"]]
                reglages += [tr.get(c, l) or c.split(".")[1] for c in n["champs"]]
                sorties = None
                # Sorties affichées seulement quand elles ne sont pas la simple « suite » habituelle.
                if n["sorties"] is not None and n["sorties"] != ["suivant"]:
                    sorties = [tr.get("port_" + s, l) or s for s in n["sorties"]]
                entree = {"nom": nom}
                s = schema(l, n["cibles"], reglages, sorties, tr)
                if s:
                    entree["schema"] = s
                d = descriptions[l].get(n["id"]) or descriptions["en"].get(n["id"]) or descriptions["fr"].get(n["id"])
                if not descriptions[l].get(n["id"]):
                    manques.append((l, n["id"]))
                if d:
                    langue_texte = l if descriptions[l].get(n["id"]) else ("en" if descriptions["en"].get(n["id"]) else "fr")
                    entree["role"] = remplir(d[0], langue_texte, tr, noms_noeuds)
                    if len(d) > 1 and d[1]:
                        entree["exemple"] = remplir(d[1], langue_texte, tr, noms_noeuds)
                liste.append(entree)
            slug = re.sub(r"[^a-z0-9]+", "-", cat.replace("cat_", "")).strip("-")
            with open(os.path.join(dossier, f"{i:02d}-{slug}.json"), "w", encoding="utf-8") as f:
                json.dump({"categorie": tr.get(cat, l) or cat, "noeuds": liste}, f, ensure_ascii=False, indent=2)
                f.write("\n")
    print(f"{len(noeuds)} nœuds, {len(ordre_categories)} catégories, {len(LANGUES)} langues.")
    if manques:
        print(f"Descriptions manquantes : {len(manques)}")
        for l, i in manques[:40]:
            print("  ", l, i)


if __name__ == "__main__":
    main()
