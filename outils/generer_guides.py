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
  - guides/index.html (français) et guides/<langue>/index.html : page « Tous les guides »
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
GUIDES = ["deplacer-personnage", "sauter", "comportements", "pieces-score", "vie-game-over", "niveau-suivant", "particules-effets"]

spec = importlib.util.spec_from_file_location("gen", os.path.join(RACINE, "outils", "generer_aide_noeuds.py"))
gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gen)
LANGUES = gen.LANGUES

NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
                "pt": "Português", "ru": "Русский", "zh": "中文", "ja": "日本語"}
UI = {
    "fr": dict(noeuds="Référence des nœuds", sous_titre="Guide débutant · sans code", besoin="Il te faut :", precedent="←", suivant="Guide suivant :",
               tous="Tous les guides", pied="Yop2D, moteur de jeu 2D gratuit et sans code pour Android", site="Site officiel",
               outil="Yop2D (moteur de jeu 2D sans code pour Android)"),
    "en": dict(noeuds="Node reference", sous_titre="Beginner guide · no code", besoin="You need:", precedent="←", suivant="Next guide:",
               tous="All guides", pied="Yop2D, free no-code 2D game engine for Android", site="Official website",
               outil="Yop2D (no-code 2D game engine for Android)"),
    "es": dict(noeuds="Referencia de nodos", sous_titre="Guía para principiantes · sin código", besoin="Necesitas:", precedent="←", suivant="Siguiente guía:",
               tous="Todas las guías", pied="Yop2D, motor de juegos 2D gratuito y sin código para Android", site="Sitio oficial",
               outil="Yop2D (motor de juegos 2D sin código para Android)"),
    "de": dict(noeuds="Knotenreferenz", sous_titre="Anleitung für Einsteiger · ohne Code", besoin="Du brauchst:", precedent="←", suivant="Nächste Anleitung:",
               tous="Alle Anleitungen", pied="Yop2D, kostenlose 2D-Spiel-Engine ohne Code für Android", site="Offizielle Website",
               outil="Yop2D (2D-Spiel-Engine ohne Code für Android)"),
    "it": dict(noeuds="Riferimento dei nodi", sous_titre="Guida per principianti · senza codice", besoin="Ti serve:", precedent="←", suivant="Guida successiva:",
               tous="Tutte le guide", pied="Yop2D, motore di gioco 2D gratuito e senza codice per Android", site="Sito ufficiale",
               outil="Yop2D (motore di gioco 2D senza codice per Android)"),
    "pt": dict(noeuds="Referência de nós", sous_titre="Guia para iniciantes · sem código", besoin="Você precisa de:", precedent="←", suivant="Próximo guia:",
               tous="Todos os guias", pied="Yop2D, motor de jogos 2D gratuito e sem código para Android", site="Site oficial",
               outil="Yop2D (motor de jogos 2D sem código para Android)"),
    "ru": dict(noeuds="Справочник узлов", sous_titre="Руководство для новичков · без кода", besoin="Тебе понадобится:", precedent="←", suivant="Следующее руководство:",
               tous="Все руководства", pied="Yop2D — бесплатный 2D-движок без кода для Android", site="Официальный сайт",
               outil="Yop2D (2D-движок без кода для Android)"),
    "zh": dict(noeuds="节点参考", sous_titre="新手教程 · 无需代码", besoin="你需要：", precedent="←", suivant="下一篇：",
               tous="全部教程", pied="Yop2D，免费、无需代码的 Android 2D 游戏引擎", site="官方网站",
               outil="Yop2D（无需代码的 Android 2D 游戏引擎）"),
    "ja": dict(noeuds="ノードリファレンス", sous_titre="初心者ガイド · コード不要", besoin="用意するもの：", precedent="←", suivant="次のガイド：",
               tous="すべてのガイド", pied="Yop2D、Android 向けの無料・コード不要の 2D ゲームエンジン", site="公式サイト",
               outil="Yop2D（Android 向けのコード不要 2D ゲームエンジン）"),
}

# Page « Tous les guides » : titre (balise title), introduction, bouton de lecture, téléchargement
TOUS = {
    "fr": ("Tous les guides Yop2D pour débuter | Créer un jeu sans code sur Android",
           "Guides pas à pas pour créer ton premier jeu 2D avec Yop2D, sans code, sur tablette ou téléphone Android : déplacer un personnage, sauter, score, vies, niveaux.",
           "Des guides pas à pas pour créer ton premier jeu avec Yop2D, sans écrire de code. Suis-les dans l'ordre : chaque guide réutilise ce que tu as appris dans le précédent.",
           "Lire le guide", "Télécharger Yop2D"),
    "en": ("All Yop2D beginner guides | Make a game without code on Android",
           "Step-by-step guides to make your first 2D game with Yop2D, without code, on an Android tablet or phone: move a character, jump, score, health, levels.",
           "Step-by-step guides to make your first game with Yop2D, without writing code. Follow them in order: each guide builds on what you learned in the previous one.",
           "Read the guide", "Download Yop2D"),
    "es": ("Todas las guías de Yop2D para principiantes | Crea un juego sin código en Android",
           "Guías paso a paso para crear tu primer juego 2D con Yop2D, sin código, en una tableta o un móvil Android: mover un personaje, saltar, puntuación, vidas, niveles.",
           "Guías paso a paso para crear tu primer juego con Yop2D, sin escribir código. Síguelas en orden: cada guía aprovecha lo que aprendiste en la anterior.",
           "Leer la guía", "Descargar Yop2D"),
    "de": ("Alle Yop2D-Anleitungen für Einsteiger | Ein Spiel ohne Code auf Android erstellen",
           "Schritt-für-Schritt-Anleitungen für dein erstes 2D-Spiel mit Yop2D, ohne Code, auf einem Android-Tablet oder -Handy: Figur bewegen, springen, Punkte, Leben, Levels.",
           "Schritt-für-Schritt-Anleitungen für dein erstes Spiel mit Yop2D, ganz ohne Code. Folge ihnen der Reihe nach: Jede Anleitung baut auf der vorherigen auf.",
           "Anleitung lesen", "Yop2D herunterladen"),
    "it": ("Tutte le guide Yop2D per principianti | Creare un gioco senza codice su Android",
           "Guide passo passo per creare il tuo primo gioco 2D con Yop2D, senza codice, su tablet o telefono Android: muovere un personaggio, saltare, punteggio, vite, livelli.",
           "Guide passo passo per creare il tuo primo gioco con Yop2D, senza scrivere codice. Seguile in ordine: ogni guida riprende quello che hai imparato nella precedente.",
           "Leggi la guida", "Scarica Yop2D"),
    "pt": ("Todos os guias do Yop2D para iniciantes | Crie um jogo sem código no Android",
           "Guias passo a passo para criar seu primeiro jogo 2D com o Yop2D, sem código, no tablet ou celular Android: mover um personagem, pular, pontuação, vidas, fases.",
           "Guias passo a passo para criar seu primeiro jogo com o Yop2D, sem escrever código. Siga-os em ordem: cada guia aproveita o que você aprendeu no anterior.",
           "Ler o guia", "Baixar o Yop2D"),
    "ru": ("Все руководства Yop2D для начинающих | Игра без кода на Android",
           "Пошаговые руководства: первая 2D-игра в Yop2D без кода на Android-планшете или телефоне — движение персонажа, прыжок, очки, здоровье, уровни.",
           "Пошаговые руководства, чтобы сделать первую игру в Yop2D, не написав ни строчки кода. Проходите их по порядку: каждое опирается на предыдущее.",
           "Читать руководство", "Скачать Yop2D"),
    "zh": ("Yop2D 全部新手教程 | 在安卓上无需代码制作游戏",
           "分步教程：用 Yop2D 在安卓平板或手机上无需代码制作你的第一个 2D 游戏——移动角色、跳跃、得分、生命值、关卡。",
           "分步教程，教你用 Yop2D 制作第一个游戏，完全不用写代码。建议按顺序学习：每篇教程都会用到上一篇学过的内容。",
           "阅读教程", "下载 Yop2D"),
    "ja": ("Yop2D 初心者ガイド一覧 | Android でコードなしのゲーム作り",
           "Yop2D で、Android のタブレットやスマホを使ってコードなしで初めての 2D ゲームを作るためのステップごとのガイド：キャラクターの移動、ジャンプ、スコア、ライフ、レベル。",
           "コードを書かずに Yop2D で初めてのゲームを作るための、ステップごとのガイドです。順番に進めてください。どのガイドも前のガイドで学んだことを使います。",
           "ガイドを読む", "Yop2D をダウンロード"),
}


def chemin_tous(langue):
    return "guides/index.html" if langue == "fr" else f"guides/{langue}/index.html"


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
            elif t == "video":
                # ["video", "identifiant YouTube", "légende"]
                h.append(f'<figure class="video"><div class="video-cadre"><iframe src="https://www.youtube-nocookie.com/embed/{b[1]}" '
                         f'title="{html.escape(self.brut(b[2]))}" loading="lazy" allowfullscreen '
                         f'allow="accelerometer; encrypted-media; gyroscope; picture-in-picture"></iframe></div>'
                         f'<figcaption>{self.texte(b[2])}</figcaption></figure>')
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
    # Page d'accueil dans la même langue (anglais : racine du site)
    accueil = base + "../" + ("index.html" if langue == "en" else f"{langue}/index.html")
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
        nav.append(f'<a href="index.html">{ui["precedent"]} {ui["tous"]}</a>')
    if i + 1 < len(GUIDES) and (GUIDES[i + 1], langue) in sources:
        s = GUIDES[i + 1]
        nav.append(f'<a href="{lien_relatif(langue, s, langue)}">{ui["suivant"]} {html.escape(r.brut(sources[(s, langue)]["carte"][0]))} →</a>')
    else:
        nav.append(f'<a href="index.html">{ui["tous"]} →</a>')
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
<a href="{accueil}">← Yop2D</a>
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
<p>{ui["pied"]} · <a href="{accueil}">{ui["site"]}</a> · <a href="{base}../noeuds/{langue}.html">{ui["noeuds"]}</a></p>
</footer>
</body>
</html>
"""


def page_tous(langue, sources):
    """Page « Tous les guides » d'une langue (liste des guides dans l'ordre de GUIDES)."""
    ui = UI[langue]
    titre, description, intro, lire, telecharger = TOUS[langue]
    base = "" if langue == "fr" else "../"
    accueil = base + "../" + ("index.html" if langue == "en" else f"{langue}/index.html")
    alternates = "\n".join(f'<link rel="alternate" hreflang="{l}" href="{SITE}{chemin_tous(l)}">' for l in LANGUES)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE}{chemin_tous("en")}">'
    langues_liens = " · ".join(
        f"<strong>{NOMS_LANGUES[l]}</strong>" if l == langue
        else f'<a href="{base}{chemin_tous(l)[len("guides/"):]}" hreflang="{l}">{NOMS_LANGUES[l]}</a>'
        for l in LANGUES)
    cartes, elements = [], []
    for i, g in enumerate([g for g in GUIDES if (g, langue) in sources], 1):
        carte = json.load(open(os.path.join(RACINE, "aide", "guides", langue, f"{GUIDES.index(g) + 1:02d}-{g}.json"), encoding="utf-8"))
        lien = lien_relatif(langue, g, langue)
        etapes = sources[(g, langue)].get("etapes", [])
        liste = ("<ol>" + "".join(f"<li>{html.escape(re.sub(r'<[^>]+>', '', n))}</li>" for n, _ in etapes) + "</ol>") if etapes else ""
        cartes.append(f'''<div class="method carte-guide">
<h2><span class="num">{i}</span> <a href="{lien}">{html.escape(carte["titre"])}</a></h2>
<p>{html.escape(carte["description"])}</p>
{liste}
<p><a href="{lien}"><strong>{lire} →</strong></a></p>
</div>''')
        elements.append({"@type": "ListItem", "position": i, "name": carte["titre"], "url": SITE + chemin_page(g, langue)})
    donnees = {"@context": "https://schema.org", "@type": "ItemList", "name": ui["tous"], "inLanguage": langue,
               "itemListElement": elements}
    return f"""<!DOCTYPE html>
<html lang="{langue}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html.escape(titre)}</title>
<meta name="description" content="{html.escape(description)}">
<link rel="canonical" href="{SITE}{chemin_tous(langue)}">
{alternates}
<link rel="stylesheet" href="{base}guide.css">
<style>
.carte-guide {{ margin-top: 1.25rem; }}
.carte-guide h2 {{ margin-top: 0; border: 0; padding: 0; font-size: 1.25rem; }}
.carte-guide h2 a {{ color: var(--ambre); text-decoration: none; }}
.carte-guide ol {{ color: var(--text-dim); margin: 0.5rem 0; }}
.num {{ display: inline-block; min-width: 1.8rem; height: 1.8rem; line-height: 1.8rem; text-align: center; border-radius: 50%; background: var(--teal); color: var(--background); font-size: 1rem; margin-right: 0.3rem; }}
</style>
<script type="application/ld+json">
{json.dumps(donnees, ensure_ascii=False, indent=1)}
</script>
</head>
<body>
<header>
<a href="{accueil}">← Yop2D</a>
<h1>{html.escape(ui["tous"])}</h1>
<p>{ui["sous_titre"]}</p>
<p class="langues">{langues_liens}</p>
</header>
<main>
<p>{html.escape(intro)}</p>
{chr(10).join(cartes)}
<div class="nav">
<a href="{base}../noeuds/{langue}.html">{ui["noeuds"]} →</a>
<a href="https://github.com/zinzin66/yop2d/releases/latest/download/Yop2D.apk">⬇️ {telecharger}</a>
</div>
</main>
<footer>
<p>{ui["pied"]} · <a href="{accueil}">{ui["site"]}</a> · <a href="{base}../noeuds/{langue}.html">{ui["noeuds"]}</a></p>
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

    for l in LANGUES:
        with open(os.path.join(RACINE, chemin_tous(l)), "w", encoding="utf-8") as f:
            f.write(page_tous(l, sources))

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
