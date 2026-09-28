#!/usr/bin/env python3
"""Construit les pages « Référence des nœuds », lisibles par les moteurs de recherche et les IA.

Source : aide/noeuds/<langue>/*.json (produits par generer_aide_noeuds.py : le lancer d'abord).
Résultat : noeuds/<langue>.html, une page par langue avec tous les nœuds, rangés par catégorie.

Utilisation : python3 outils/generer_pages_noeuds.py
"""
import glob
import html
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zinzin66.github.io/Yop2d-web/"
LANGUES = ["fr", "en", "es", "de", "it", "pt", "ru", "zh", "ja"]
NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
                "pt": "Português", "ru": "Русский", "zh": "中文", "ja": "日本語"}
UI = {
 "fr": dict(titre="Tous les nœuds de Yop2D ({n}) | Référence", h1="Référence des nœuds de Yop2D",
   intro="Yop2D est un moteur de jeu 2D gratuit et sans code pour Android. La logique d'un jeu se construit avec des nœuds (blocs visuels) reliés entre eux dans le Blueprint : les événements lancent une chaîne, les actions et conditions s'enchaînent. Cette page décrit les {n} nœuds de l'éditeur, avec leurs réglages (entrées) et leurs sorties.",
   sommaire="Catégories", exemple="Exemple :", guides="Guides pour débutants", telecharger="Télécharger Yop2D",
   desc="Liste complète des {n} nœuds visuels de Yop2D, moteur de jeu 2D sans code pour Android : rôle, réglages, sorties et exemple de chaque nœud.",
   pied="Yop2D, moteur de jeu 2D gratuit et sans code pour Android", site="Site officiel"),
 "en": dict(titre="All Yop2D nodes ({n}) | Reference", h1="Yop2D node reference",
   intro="Yop2D is a free, no-code 2D game engine for Android. A game's logic is built with nodes (visual blocks) linked together in the Blueprint: events start a chain, then actions and conditions follow. This page describes the {n} nodes of the editor, with their settings (inputs) and outputs.",
   sommaire="Categories", exemple="Example:", guides="Beginner guides", telecharger="Download Yop2D",
   desc="Complete list of the {n} visual nodes of Yop2D, the no-code 2D game engine for Android: role, settings, outputs and an example for each node.",
   pied="Yop2D, free no-code 2D game engine for Android", site="Official website"),
 "es": dict(titre="Todos los nodos de Yop2D ({n}) | Referencia", h1="Referencia de nodos de Yop2D",
   intro="Yop2D es un motor de juegos 2D gratuito y sin código para Android. La lógica de un juego se construye con nodos (bloques visuales) unidos en el Blueprint: los eventos inician una cadena y luego siguen las acciones y condiciones. Esta página describe los {n} nodos del editor, con sus ajustes (entradas) y sus salidas.",
   sommaire="Categorías", exemple="Ejemplo:", guides="Guías para principiantes", telecharger="Descargar Yop2D",
   desc="Lista completa de los {n} nodos visuales de Yop2D, motor de juegos 2D sin código para Android: función, ajustes, salidas y un ejemplo de cada nodo.",
   pied="Yop2D, motor de juegos 2D gratuito y sin código para Android", site="Sitio oficial"),
 "de": dict(titre="Alle Yop2D-Knoten ({n}) | Referenz", h1="Yop2D-Knotenreferenz",
   intro="Yop2D ist eine kostenlose 2D-Spiel-Engine ohne Code für Android. Die Logik eines Spiels baust du mit Knoten (visuellen Blöcken), die im Blueprint verbunden werden: Ereignisse starten eine Kette, danach folgen Aktionen und Bedingungen. Diese Seite beschreibt die {n} Knoten des Editors mit ihren Einstellungen (Eingänge) und Ausgängen.",
   sommaire="Kategorien", exemple="Beispiel:", guides="Anleitungen für Einsteiger", telecharger="Yop2D herunterladen",
   desc="Vollständige Liste der {n} visuellen Knoten von Yop2D, der 2D-Spiel-Engine ohne Code für Android: Aufgabe, Einstellungen, Ausgänge und ein Beispiel für jeden Knoten.",
   pied="Yop2D, kostenlose 2D-Spiel-Engine ohne Code für Android", site="Offizielle Website"),
 "it": dict(titre="Tutti i nodi di Yop2D ({n}) | Riferimento", h1="Riferimento dei nodi di Yop2D",
   intro="Yop2D è un motore di gioco 2D gratuito e senza codice per Android. La logica di un gioco si costruisce con nodi (blocchi visivi) collegati nel Blueprint: gli eventi avviano una catena, poi seguono azioni e condizioni. Questa pagina descrive i {n} nodi dell'editor, con le loro impostazioni (ingressi) e uscite.",
   sommaire="Categorie", exemple="Esempio:", guides="Guide per principianti", telecharger="Scarica Yop2D",
   desc="Elenco completo dei {n} nodi visivi di Yop2D, motore di gioco 2D senza codice per Android: ruolo, impostazioni, uscite e un esempio per ogni nodo.",
   pied="Yop2D, motore di gioco 2D gratuito e senza codice per Android", site="Sito ufficiale"),
 "pt": dict(titre="Todos os nós do Yop2D ({n}) | Referência", h1="Referência de nós do Yop2D",
   intro="O Yop2D é um motor de jogos 2D gratuito e sem código para Android. A lógica de um jogo é montada com nós (blocos visuais) ligados no Blueprint: os eventos iniciam uma cadeia, depois vêm as ações e condições. Esta página descreve os {n} nós do editor, com seus ajustes (entradas) e suas saídas.",
   sommaire="Categorias", exemple="Exemplo:", guides="Guias para iniciantes", telecharger="Baixar o Yop2D",
   desc="Lista completa dos {n} nós visuais do Yop2D, motor de jogos 2D sem código para Android: função, ajustes, saídas e um exemplo de cada nó.",
   pied="Yop2D, motor de jogos 2D gratuito e sem código para Android", site="Site oficial"),
 "ru": dict(titre="Все узлы Yop2D ({n}) | Справочник", h1="Справочник узлов Yop2D",
   intro="Yop2D — бесплатный 2D-движок без кода для Android. Логика игры собирается из узлов (визуальных блоков), соединённых в Blueprint: события запускают цепочку, за ними идут действия и условия. На этой странице описаны все {n} узлов редактора, с их настройками (входами) и выходами.",
   sommaire="Категории", exemple="Пример:", guides="Руководства для новичков", telecharger="Скачать Yop2D",
   desc="Полный список {n} визуальных узлов Yop2D, 2D-движка без кода для Android: назначение, настройки, выходы и пример для каждого узла.",
   pied="Yop2D — бесплатный 2D-движок без кода для Android", site="Официальный сайт"),
 "zh": dict(titre="Yop2D 全部节点（{n} 个）| 参考", h1="Yop2D 节点参考",
   intro="Yop2D 是一款免费、无需代码的 Android 2D 游戏引擎。游戏逻辑由在 Blueprint 中相互连接的节点（可视化积木块）组成：事件启动一条链，接着是动作和条件。本页介绍编辑器中的全部 {n} 个节点，以及它们的设置（输入）和输出。",
   sommaire="分类", exemple="示例：", guides="新手教程", telecharger="下载 Yop2D",
   desc="Yop2D（无需代码的 Android 2D 游戏引擎）全部 {n} 个可视化节点的完整列表：每个节点的作用、设置、输出和示例。",
   pied="Yop2D，免费、无需代码的 Android 2D 游戏引擎", site="官方网站"),
 "ja": dict(titre="Yop2D の全ノード（{n} 個）| リファレンス", h1="Yop2D ノードリファレンス",
   intro="Yop2D は、Android 向けの無料・コード不要の 2D ゲームエンジンです。ゲームのロジックは、Blueprint の中でつないだノード（ビジュアルブロック）で作ります。イベントがつながりを始め、そのあとにアクションや条件が続きます。このページでは、エディターの {n} 個のノードを、設定（入力）と出力とともに説明します。",
   sommaire="カテゴリー", exemple="例：", guides="初心者ガイド", telecharger="Yop2D をダウンロード",
   desc="Android 向けコード不要 2D ゲームエンジン Yop2D の {n} 個のビジュアルノードの一覧：各ノードの役割、設定、出力、使用例。",
   pied="Yop2D、Android 向けの無料・コード不要の 2D ゲームエンジン", site="公式サイト"),
}
CSS = """
.sommaire { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 1rem 0; }
.sommaire a { background: var(--card); border: 1px solid var(--bordure); border-radius: 20px; padding: 0.2rem 0.8rem; text-decoration: none; font-size: 0.9rem; }
.fiche { border-top: 1px solid var(--bordure); padding: 0.8rem 0; }
.fiche:first-of-type { border-top: none; }
.fiche h3 { margin: 0 0 0.3rem; color: white; font-size: 1.05rem; }
.schema { font-size: 0.88rem; color: var(--text-dim); background: var(--fond-sombre); border-radius: 6px; padding: 0.45rem 0.7rem; margin-bottom: 0.4rem; }
.schema b { color: var(--bleu); }
.exemple { color: var(--text-dim); }
.exemple b { color: var(--teal); }
.liens-bas { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; margin-top: 2rem; font-weight: bold; }
"""


def slug(texte):
    s = re.sub(r"[^\w]+", "-", texte.lower(), flags=re.UNICODE).strip("-")
    return s or "c"


def page(l, categories):
    ui = UI[l]
    n = sum(len(c["noeuds"]) for c in categories)
    e = lambda s: html.escape(s, quote=False)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{x}" href="{SITE}noeuds/{x}.html">' for x in LANGUES)
    langues = " · ".join(f"<strong>{NOMS_LANGUES[x]}</strong>" if x == l else f'<a href="{x}.html" hreflang="{x}">{NOMS_LANGUES[x]}</a>' for x in LANGUES)
    ancres = []
    blocs = []
    for i, c in enumerate(categories, 1):
        a = f"c{i}-{slug(c['categorie'])}"
        ancres.append(f'<a href="#{a}">{e(c["categorie"])}</a>')
        fiches = []
        for nd in c["noeuds"]:
            f = [f'<div class="fiche"><h3>{e(nd["nom"])}</h3>']
            if nd.get("schema"):
                f.append(f'<div class="schema">{nd["schema"]}</div>')   # HTML simple produit par le générateur
            if nd.get("role"):
                f.append(f"<p>{e(nd['role'])}</p>")
            if nd.get("exemple"):
                f.append(f'<p class="exemple"><b>{e(ui["exemple"])}</b> {e(nd["exemple"])}</p>')
            f.append("</div>")
            fiches.append("\n".join(f))
        blocs.append(f'<h2 id="{a}">{e(c["categorie"])}</h2>\n<div class="method">\n' + "\n".join(fiches) + "\n</div>")
    guides = "../guides/deplacer-personnage.html" if l == "fr" else f"../guides/{l}/deplacer-personnage.html"
    return f"""<!DOCTYPE html>
<html lang="{l}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(ui["titre"].format(n=n))}</title>
<meta name="description" content="{html.escape(ui["desc"].format(n=n))}">
<link rel="canonical" href="{SITE}noeuds/{l}.html">
{alternates}
<link rel="stylesheet" href="../guides/guide.css">
<style>{CSS}</style>
</head>
<body>
<header>
<a href="../index.html">← Yop2D</a>
<h1>{e(ui["h1"])}</h1>
<p class="langues">{langues}</p>
</header>
<main>
<p>{e(ui["intro"].format(n=n))}</p>
<p><strong>{e(ui["sommaire"])}</strong></p>
<nav class="sommaire">{"".join(ancres)}</nav>
{chr(10).join(blocs)}
<div class="liens-bas">
<a href="{guides}">{e(ui["guides"])} →</a>
<a href="https://github.com/zinzin66/yop2d/releases/latest/download/Yop2D.apk">⬇️ {e(ui["telecharger"])}</a>
</div>
</main>
<footer>
<p>{e(ui["pied"])} · <a href="../index.html">{e(ui["site"])}</a></p>
</footer>
</body>
</html>
"""


def main():
    os.makedirs(os.path.join(RACINE, "noeuds"), exist_ok=True)
    for l in LANGUES:
        fichiers = sorted(glob.glob(os.path.join(RACINE, "aide", "noeuds", l, "*.json")))
        categories = [json.load(open(f, encoding="utf-8")) for f in fichiers]
        open(os.path.join(RACINE, "noeuds", f"{l}.html"), "w", encoding="utf-8").write(page(l, categories))
    print(f"noeuds/<langue>.html : {len(LANGUES)} pages")


if __name__ == "__main__":
    main()
