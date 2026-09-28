#!/usr/bin/env python3
"""Construit les pages des guides (guides/*.html) dans les 9 langues.

Sources : guides/source/<guide>/<langue>.json (un fichier par guide et par langue).
Les noms de nœuds, de réglages et de boutons viennent du moteur (comme pour l'onglet Nœuds) :
  {{id}}        nom exact du nœud (clé du catalogue ou classe d'événement), sans guillemets
  {{lang:cle}}  texte exact d'une clé des fichiers de langue du moteur, sans guillemets
  [[id]] / [[lang:cle]]  pareil, entre les guillemets de la langue
Mise en forme dans les textes : **gras**, `code`, [texte](lien) ; un lien (guide:sauter) vise un autre guide.

Résultat :
  - français : guides/<guide>.html ; autres langues : guides/<langue>/<guide>.html
  - aide/guides/<langue>/NN-<guide>.json (fiches de l'onglet Guides de aide.html)
  - guides/move-character.html : redirection vers guides/en/deplacer-personnage.html

Utilisation :
  python3 outils/generer_guides.py /chemin/vers/yop2d
"""
import html
import importlib.util
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zinzin66.github.io/Yop2d-web/"
GUIDES = ["deplacer-personnage", "sauter", "pieces-score", "vie-game-over", "niveau-suivant"]

spec = importlib.util.spec_from_file_location("gen", os.path.join(RACINE, "outils", "generer_aide_noeuds.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
LANGUES = gen.LANGUES

NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
                "pt": "Português", "ru": "Русский", "zh": "中文", "ja": "日本語"}
UI = {
    "fr": dict(sous_titre="Guide débutant · sans code", besoin="Il te faut :", precedent="←", suivant="Guide suivant :",
               tous="Tous les guides", pied="Yop2D, moteur de jeu 2D gratuit et sans code pour Android", site="Site officiel",
               outil="Yop2D (moteur de jeu 2D sans code pour Android)"),
    "en": dict(sous_titre="Beginner guide · no code", besoin="You need:", precedent="←", suivant="Next guide:",
               tous="All guides", pied="Yop2D, free no-code 2D game engine for Android", site="Official website",
               outil="Yop2D (no-code 2D game engine for Android)"),
    "es": dict(sous_titre="Guía para principiantes · sin código", besoin="Necesitas:", precedent="←", suivant="Siguiente guía:",
               tous="Todas las guías", pied="Yop2D, motor de juegos 2D gratuito y sin código para Android", site="Sitio oficial",
               outil="Yop2D (motor de juegos 2D sin código para Android)"),
    "de": dict(sous_titre="Anleitung für Einsteiger · ohne Code", besoin="Du brauchst:", precedent="←", suivant="Nächste Anleitung:",
               tous="Alle Anleitungen", pied="Yop2D, kostenlose 2D-Spiel-Engine ohne Code für Android", site="Offizielle Website",
               outil="Yop2D (2D-Spiel-Engine ohne Code für Android)"),
    "it": dict(sous_titre="Guida per principianti · senza codice", besoin="Ti serve:", precedent="←", suivant="Guida successiva:",
               tous="Tutte le guide", pied="Yop2D, motore di gioco 2D gratuito e senza codice per Android", site="Sito ufficiale",
               outil="Yop2D (motore di gioco 2D senza codice per Android)"),
    "pt": dict(sous_titre="Guia para iniciantes · sem código", besoin="Você precisa de:", precedent="←", suivant="Próximo guia:",
               tous="Todos os guias", pied="Yop2D, motor de jogos 2D gratuito e sem código para Android", site="Site oficial",
               outil="Yop2D (motor de jogos 2D sem código para Android)"),
    "ru": dict(sous_titre="Руководство для новичков · без кода", besoin="Тебе понадобится:", precedent="←", suivant="Следующее руководство:",
               tous="Все руководства", pied="Yop2D — бесплатный 2D-движок без кода для Android", site="Официальный сайт",
               outil="Yop2D (2D-движок без кода для Android)"),
    "zh": dict(sous_titre="新手教程 · 无需代码", besoin="你需要：", precedent="←", suivant="下一篇：",
               tous="全部教程", pied="Yop2D，免费、无需代码的 Android 2D 游戏引擎", site="官方网站",
               outil="Yop2D（无需代码的 Android 2D 游戏引擎）"),
    "ja": dict(sous_titre="初心者ガイド · コード不要", besoin="用意するもの：", precedent="←", suivant="次のガイド：",
               tous="すべてのガイド", pied="Yop2D、Android 向けの無料・コード不要の 2D ゲームエンジン", site="公式サイト",
               outil="Yop2D（Android 向けのコード不要 2D ゲームエンジン）"),
}


def chemin_page(guide, langue):
    return f"guides/{guide}.html" if langue == "fr" else f"guides/{langue}/{guide}.html"


def lien_relatif(depuis_langue, guide, langue):
    """Lien d'une page de guide (dans la langue depuis_langue) vers un autre guide."""
    cible = chemin_page(guide, langue)[len("guides/"):]
    return cible if depuis_langue == "fr" else "../" + cible


class Rendu:
    def __init__(self, langue, tr, noms_noeuds):
        self.l, self.tr, self.noms = langue, tr, noms_noeuds

    def nom(self, cle):
        v = self.tr.get(cle[5:], self.l) if cle.startswith("lang:") else self.noms.get(cle, {}).get(self.l)
        if not v:
            raise SystemExit(f"Repère inconnu {cle} ({self.l})")
        return v.strip().strip("[] ")

    def texte(self, t):
        """Texte d'un guide → HTML."""
        o, f = gen.GUILLEMETS[self.l]
        t = re.sub(r"\[\[([^\]]+)\]\]", lambda m: "\x01" + o + self.nom(m.group(1)) + f + "\x02", t)
        t = re.sub(r"\{\{([^}]+)\}\}", lambda m: "\x01" + self.nom(m.group(1)) + "\x02", t)
        t = re.sub(r"«\s*([^»]+?)\s*»", lambda m: o + m.group(1) + f, t)
        # Les noms venus du moteur sont échappés ; le reste aussi, puis on applique la mise en forme.
        morceaux = re.split(r"(\x01[^\x02]*\x02)", t)
        t = "".join(html.escape(m[1:-1], quote=False) if m.startswith("\x01") else html.escape(m, quote=False) for m in morceaux)
        t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
        t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)

        def lien(m):
            cible = m.group(2)
            if cible.startswith("guide:"):
                cible = lien_relatif(self.l, cible[6:], self.l)
            return f'<a href="{cible}">{m.group(1)}</a>'
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lien, t)

    def brut(self, t):
        """Texte sans balises (titre, description, données structurées)."""
        return re.sub(r"<[^>]+>", "", self.texte(t)).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

    def chaine(self, elements):
        h = ['<div class="chaine">']
        for e in elements:
            if e[0] == "→":
                sortie = f"<em>{self.texte(e[1])}</em> " if len(e) > 1 else ""
                h.append(f'<div class="fleche">{sortie}→</div>')
            else:
                classe = {"ev": " evenement", "cond": " condition", "n": ""}[e[0]]
                sous = f"<span>{self.texte(e[2])}</span>" if len(e) > 2 and e[2] else ""
                h.append(f'<div class="noeud{classe}"><b>{self.texte(e[1])}</b>{sous}</div>')
        h.append("</div>")
        return "\n".join(h)

    def blocs(self, liste):
        h = []
        for b in liste:
            t = b[0]
            if t == "p":
                h.append(f"<p>{self.texte(b[1])}</p>")
            elif t == "h2":
                h.append(f"<h2>{self.texte(b[1])}</h2>")
            elif t in ("ol", "ul"):
                h.append(f"<{t}>" + "".join(f"<li>{self.texte(x)}</li>" for x in b[1]) + f"</{t}>")
            elif t == "tip":
                h.append(f'<div class="tip">👉 {self.texte(b[1])}</div>')
            elif t == "attention":
                h.append(f'<div class="tip attention">⚠️ {self.texte(b[1])}</div>')
            elif t == "chaine":
                h.append(self.chaine(b[1]))
            elif t == "besoin":
                h.append(f'<div class="besoin">\n<b>{UI[self.l]["besoin"]}</b>\n<ul>'
                         + "".join(f"<li>{self.texte(x)}</li>" for x in b[1]) + "</ul>\n</div>")
            elif t == "bloc":
                h.append('<div class="method">\n' + self.blocs(b[1]) + "\n</div>")
            else:
                raise SystemExit(f"Bloc inconnu : {t}")
        return "\n".join(h)


def page(guide, langue, src, sources, r):
    ui = UI[langue]
    base = "" if langue == "fr" else "../"
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE}{chemin_page(guide, l)}">' for l in LANGUES if (guide, l) in sources)
    langues_liens = " · ".join(
        (f"<strong>{NOMS_LANGUES[l]}</strong>" if l == langue else
         f'<a href="{lien_relatif(langue, guide, l)}" hreflang="{l}">{NOMS_LANGUES[l]}</a>')
        for l in LANGUES if (guide, l) in sources)
    howto = {
        "@context": "https://schema.org", "@type": "HowTo", "name": r.brut(src["h1"]),
        "description": r.brut(src["description"]), "inLanguage": langue,
        "tool": [{"@type": "HowToTool", "name": ui["outil"]}],
        "step": [{"@type": "HowToStep", "name": r.brut(n), "text": r.brut(t)} for n, t in src.get("etapes", [])],
    }
    i = GUIDES.index(guide)
    nav = []
    if i > 0:
        p = GUIDES[i - 1]
        nav.append(f'<a href="{lien_relatif(langue, p, langue)}">{ui["precedent"]} {html.escape(r.brut(sources[(p, langue)]["carte"][0]))}</a>')
    else:
        nav.append(f'<a href="{base}../index.html#guides">{ui["precedent"]} {ui["tous"]}</a>')
    if i + 1 < len(GUIDES) and (GUIDES[i + 1], langue) in sources:
        s = GUIDES[i + 1]
        nav.append(f'<a href="{lien_relatif(langue, s, langue)}">{ui["suivant"]} {html.escape(r.brut(sources[(s, langue)]["carte"][0]))} →</a>')
    else:
        nav.append(f'<a href="{base}../index.html#guides">{ui["tous"]} →</a>')
    return f"""<!DOCTYPE html>
<html lang="{langue}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(r.brut(src["titre_page"]))}</title>
<meta name="description" content="{html.escape(r.brut(src["description"]))}">
<link rel="canonical" href="{SITE}{chemin_page(guide, langue)}">
{alternates}
<link rel="stylesheet" href="{base}guide.css">
<script type="application/ld+json">
{json.dumps(howto, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<header>
<a href="{base}../index.html">← Yop2D</a>
<h1>{r.texte(src["h1"])}</h1>
<p>{ui["sous_titre"]}</p>
<p class="langues">{langues_liens}</p>
</header>
<main>
{r.blocs(src["blocs"])}

<div class="nav">
{chr(10).join(nav)}
</div>
</main>
<footer>
<p>{ui["pied"]} · <a href="{base}../index.html">{ui["site"]}</a></p>
</footer>
</body>
</html>
"""


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    assets = os.path.join(sys.argv[1], "app", "src", "main", "assets")
    catalogue = gen.lire_json(os.path.join(assets, "catalogue_noeuds.json"))
    tr = gen.Traductions(assets, catalogue)
    noms = {classe: {l: tr.get(cle, l) for l in LANGUES} for cle, classe in gen.EVENEMENTS}
    for n in catalogue["noeuds"]:
        noms[n["cle"]] = {l: tr.get(n.get("nomCle") or "noeud_" + n["cle"], l) for l in LANGUES}

    sources = {}
    for g in GUIDES:
        for l in LANGUES:
            p = os.path.join(RACINE, "guides", "source", g, f"{l}.json")
            if os.path.exists(p):
                sources[(g, l)] = json.load(open(p, encoding="utf-8"))

    for l in LANGUES:
        dossier = os.path.join(RACINE, "aide", "guides", l)
        os.makedirs(dossier, exist_ok=True)
        for f in os.listdir(dossier):
            if f.endswith(".json"):
                os.remove(os.path.join(dossier, f))
    for (g, l), src in sources.items():
        r = Rendu(l, tr, noms)
        sortie = os.path.join(RACINE, chemin_page(g, l))
        os.makedirs(os.path.dirname(sortie), exist_ok=True)
        open(sortie, "w", encoding="utf-8").write(page(g, l, src, sources, r))
        carte = {"titre": r.brut(src["carte"][0]), "description": r.brut(src["carte"][1]), "lien": chemin_page(g, l)}
        with open(os.path.join(RACINE, "aide", "guides", l, f"{GUIDES.index(g) + 1:02d}-{g}.json"), "w", encoding="utf-8") as f:
            json.dump(carte, f, ensure_ascii=False, indent=2)
            f.write("\n")

    # Ancienne adresse anglaise du premier guide : redirection.
    open(os.path.join(RACINE, "guides", "move-character.html"), "w", encoding="utf-8").write(
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n<meta charset="UTF-8">\n'
        '<meta http-equiv="refresh" content="0; url=en/deplacer-personnage.html">\n'
        f'<link rel="canonical" href="{SITE}guides/en/deplacer-personnage.html">\n<title>Yop2D</title>\n</head>\n'
        '<body><p><a href="en/deplacer-personnage.html">How to move a character in Yop2D</a></p></body>\n</html>\n')

    manque = [(g, l) for g in GUIDES for l in LANGUES if (g, l) not in sources]
    print(f"{len(sources)} pages générées." + (f" Manquantes : {manque}" if manque else ""))


if __name__ == "__main__":
    main()
