#!/usr/bin/env python3
"""Aide à la traduction des guides.
  extraire <guide>            → affiche les phrases à traduire de guides/source/<guide>/en.json (une par ligne, numérotées)
  appliquer <guide> <langue> <fichier.txt>  → crée guides/source/<guide>/<langue>.json à partir de en.json
      et du fichier texte (une phrase traduite par ligne, dans le même ordre).
Les textes faits uniquement de repères ({{...}}, [[...]]), de chiffres ou vides sont recopiés tels quels."""
import json, os, re, sys
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def a_traduire(s):
    reste = re.sub(r"\{\{[^}]+\}\}|\[\[[^\]]+\]\]", "", s)
    return re.search(r"[^\W\d_]", reste) is not None

def parcourir(o, f):
    if isinstance(o, list):
        return [parcourir(x, f) for x in o]
    if isinstance(o, dict):
        return {k: parcourir(v, f) for k, v in o.items()}
    if isinstance(o, str) and o not in ("p", "h2", "ol", "ul", "tip", "attention", "chaine", "besoin", "bloc", "ev", "cond", "n", "→") and a_traduire(o):
        return f(o)
    return o

src = json.load(open(os.path.join(RACINE, "guides", "source", sys.argv[2], "en.json"), encoding="utf-8"))
if sys.argv[1] == "extraire":
    liste = []
    parcourir(src, lambda s: liste.append(s) or s)
    for s in liste:
        print(s)
else:
    lignes = [l.rstrip("\n") for l in open(sys.argv[4], encoding="utf-8") if l.strip()]
    it = iter(lignes)
    res = parcourir(src, lambda s: next(it))
    reste = list(it)
    if reste:
        sys.exit(f"Trop de lignes : {len(reste)} en trop")
    json.dump(res, open(os.path.join(RACINE, "guides", "source", sys.argv[2], sys.argv[3] + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("ok", sys.argv[2], sys.argv[3])
