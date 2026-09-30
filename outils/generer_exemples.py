#!/usr/bin/env python3
"""Exemples téléchargeables : liste lue par le moteur + page « Exemples » en 9 langues.

Source : outils/exemples/source.json (nom, description en 9 langues, version, moteur_min)
         et les fichiers exemples/<id>.zip + exemples/<id>.png.
Résultat : exemples/exemples.json (lu par le moteur, onglet Exemples)
           et exemples/<langue>.html (page du site, pour les visiteurs et le référencement).

Utilisation : python3 outils/generer_exemples.py
"""
import html
import json
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zinzin66.github.io/Yop2d-web/"
LANGUES = ["fr", "en", "es", "de", "it", "pt", "ru", "zh", "ja"]
NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
                "pt": "Português", "ru": "Русский", "zh": "中文", "ja": "日本語"}
UI = {
 "fr": dict(titre="Jeux d'exemple de Yop2D ({n})", h1="Jeux d'exemple",
   intro="Des jeux complets faits avec Yop2D, le moteur de jeu 2D gratuit et sans code pour Android. Ouvrez-les dans Yop2D (onglet « Exemples » de l'écran d'accueil), jouez-y, puis regardez leurs nœuds et modifiez-les pour apprendre.",
   zip="Télécharger le projet", aide="Dans Yop2D, ces exemples se téléchargent tout seuls depuis l'onglet « Exemples ». Vous pouvez aussi importer le fichier zip avec « Ouvrir un projet téléchargé ».",
   desc="Jeux d'exemple gratuits faits avec Yop2D, moteur de jeu 2D sans code pour Android : plateforme, shooter, labyrinthe, histoire à choix, effets visuels.",
   ko="Ko", mo="Mo", telecharger="Télécharger Yop2D", guides="Guides pour débutants", pied="Yop2D, moteur de jeu 2D gratuit et sans code pour Android", site="Site officiel"),
 "en": dict(titre="Yop2D example games ({n})", h1="Example games",
   intro="Complete games made with Yop2D, the free no-code 2D game engine for Android. Open them in Yop2D (\"Examples\" tab of the start screen), play them, then look at their nodes and change them to learn.",
   zip="Download the project", aide="In Yop2D, these examples download by themselves from the \"Examples\" tab. You can also import the zip file with \"Open a downloaded project\".",
   desc="Free example games made with Yop2D, the no-code 2D game engine for Android: platformer, shooter, maze, choice-based story, visual effects.",
   ko="KB", mo="MB", telecharger="Download Yop2D", guides="Beginner guides", pied="Yop2D, free no-code 2D game engine for Android", site="Official website"),
 "es": dict(titre="Juegos de ejemplo de Yop2D ({n})", h1="Juegos de ejemplo",
   intro="Juegos completos hechos con Yop2D, el motor de juegos 2D gratuito y sin código para Android. Ábrelos en Yop2D (pestaña «Ejemplos» de la pantalla de inicio), juega y luego mira sus nodos y modifícalos para aprender.",
   zip="Descargar el proyecto", aide="En Yop2D, estos ejemplos se descargan solos desde la pestaña «Ejemplos». También puedes importar el archivo zip con «Abrir proyecto descargado».",
   desc="Juegos de ejemplo gratuitos hechos con Yop2D, motor de juegos 2D sin código para Android: plataformas, shooter, laberinto, historia de decisiones, efectos visuales.",
   ko="KB", mo="MB", telecharger="Descargar Yop2D", guides="Guías para principiantes", pied="Yop2D, motor de juegos 2D gratuito y sin código para Android", site="Sitio oficial"),
 "de": dict(titre="Yop2D-Beispielspiele ({n})", h1="Beispielspiele",
   intro="Komplette Spiele, gemacht mit Yop2D, der kostenlosen 2D-Spiel-Engine ohne Code für Android. Öffne sie in Yop2D (Tab „Beispiele“ im Startbildschirm), spiele sie, schau dir dann ihre Knoten an und ändere sie, um zu lernen.",
   zip="Projekt herunterladen", aide="In Yop2D laden sich diese Beispiele im Tab „Beispiele“ von selbst herunter. Du kannst die ZIP-Datei auch mit „Heruntergeladenes Projekt öffnen“ importieren.",
   desc="Kostenlose Beispielspiele, gemacht mit Yop2D, der 2D-Spiel-Engine ohne Code für Android: Jump'n'Run, Shooter, Labyrinth, Entscheidungsgeschichte, visuelle Effekte.",
   ko="KB", mo="MB", telecharger="Yop2D herunterladen", guides="Anleitungen für Einsteiger", pied="Yop2D, kostenlose 2D-Spiel-Engine ohne Code für Android", site="Offizielle Website"),
 "it": dict(titre="Giochi di esempio di Yop2D ({n})", h1="Giochi di esempio",
   intro="Giochi completi fatti con Yop2D, il motore di gioco 2D gratuito e senza codice per Android. Aprili in Yop2D (scheda «Esempi» della schermata iniziale), giocaci, poi guarda i loro nodi e modificali per imparare.",
   zip="Scarica il progetto", aide="In Yop2D questi esempi si scaricano da soli dalla scheda «Esempi». Puoi anche importare il file zip con «Apri un progetto scaricato».",
   desc="Giochi di esempio gratuiti fatti con Yop2D, motore di gioco 2D senza codice per Android: platform, sparatutto, labirinto, storia a scelte, effetti visivi.",
   ko="KB", mo="MB", telecharger="Scarica Yop2D", guides="Guide per principianti", pied="Yop2D, motore di gioco 2D gratuito e senza codice per Android", site="Sito ufficiale"),
 "pt": dict(titre="Jogos de exemplo do Yop2D ({n})", h1="Jogos de exemplo",
   intro="Jogos completos feitos com o Yop2D, o motor de jogos 2D gratuito e sem código para Android. Abra-os no Yop2D (aba «Exemplos» da tela inicial), jogue e depois veja seus nós e modifique-os para aprender.",
   zip="Baixar o projeto", aide="No Yop2D, estes exemplos são baixados sozinhos pela aba «Exemplos». Você também pode importar o arquivo zip com «Abrir projeto baixado».",
   desc="Jogos de exemplo gratuitos feitos com o Yop2D, motor de jogos 2D sem código para Android: plataforma, tiro, labirinto, história de escolhas, efeitos visuais.",
   ko="KB", mo="MB", telecharger="Baixar o Yop2D", guides="Guias para iniciantes", pied="Yop2D, motor de jogos 2D gratuito e sem código para Android", site="Site oficial"),
 "ru": dict(titre="Примеры игр Yop2D ({n})", h1="Примеры игр",
   intro="Готовые игры, сделанные в Yop2D — бесплатном 2D-движке без кода для Android. Откройте их в Yop2D (вкладка «Примеры» на стартовом экране), поиграйте, затем посмотрите их узлы и измените их, чтобы научиться.",
   zip="Скачать проект", aide="В Yop2D эти примеры скачиваются сами на вкладке «Примеры». Можно также импортировать zip-файл через «Открыть скачанный проект».",
   desc="Бесплатные примеры игр, сделанные в Yop2D, 2D-движке без кода для Android: платформер, шутер, лабиринт, история с выбором, визуальные эффекты.",
   ko="КБ", mo="МБ", telecharger="Скачать Yop2D", guides="Руководства для новичков", pied="Yop2D — бесплатный 2D-движок без кода для Android", site="Официальный сайт"),
 "zh": dict(titre="Yop2D 示例游戏（{n} 个）", h1="示例游戏",
   intro="用 Yop2D（免费、无需代码的 Android 2D 游戏引擎）制作的完整游戏。在 Yop2D 中打开它们（开始界面的「示例」标签），玩一玩，再看看它们的节点并动手修改，边玩边学。",
   zip="下载项目", aide="在 Yop2D 中，这些示例会从「示例」标签自动下载。你也可以通过「打开已下载的项目」导入 zip 文件。",
   desc="用 Yop2D（无需代码的 Android 2D 游戏引擎）制作的免费示例游戏：平台跳跃、射击、迷宫、选择式故事、视觉效果。",
   ko="KB", mo="MB", telecharger="下载 Yop2D", guides="新手教程", pied="Yop2D，免费、无需代码的 Android 2D 游戏引擎", site="官方网站"),
 "ja": dict(titre="Yop2D のサンプルゲーム（{n} 本）", h1="サンプルゲーム",
   intro="Android 向けの無料・コード不要 2D ゲームエンジン Yop2D で作った完成済みのゲームです。Yop2D で開き（スタート画面の「サンプル」タブ）、遊んでから、ノードを見て変更しながら学びましょう。",
   zip="プロジェクトをダウンロード", aide="Yop2D では、これらのサンプルは「サンプル」タブから自動でダウンロードされます。zip ファイルを「ダウンロードしたプロジェクトを開く」で読み込むこともできます。",
   desc="Android 向けコード不要 2D ゲームエンジン Yop2D で作った無料のサンプルゲーム：アクション、シューティング、迷路、選択式ストーリー、視覚効果。",
   ko="KB", mo="MB", telecharger="Yop2D をダウンロード", guides="初心者ガイド", pied="Yop2D、Android 向けの無料・コード不要の 2D ゲームエンジン", site="公式サイト"),
}
CSS = """
.exemples { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; margin: 1.2rem 0; }
.carte { background: var(--card); border: 1px solid var(--bordure); border-radius: 12px; overflow: hidden; display: flex; flex-direction: column; }
.carte img { width: 100%; aspect-ratio: 1 / 1; object-fit: cover; display: block; background: var(--fond-sombre); }
.carte div { padding: 0.8rem 1rem 1rem; display: flex; flex-direction: column; gap: 0.5rem; flex: 1; }
.carte h2 { margin: 0; font-size: 1.15rem; color: white; border: none; padding: 0; }
.carte p { margin: 0; color: var(--text-dim); flex: 1; }
.carte a { font-weight: bold; }
.note { color: var(--text-dim); font-size: 0.92rem; }
.liens-bas { display: flex; flex-wrap: wrap; gap: 1rem; justify-content: space-between; margin-top: 2rem; font-weight: bold; }
"""


def taille_lisible(octets, ui):
    if octets >= 1024 * 1024:
        return f"{octets / (1024 * 1024):.1f} {ui['mo']}"
    return f"{round(octets / 1024)} {ui['ko']}"


def page(l, exemples):
    ui = UI[l]
    e = lambda s: html.escape(s, quote=False)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{x}" href="{SITE}exemples/{x}.html">' for x in LANGUES)
    langues = " · ".join(f"<strong>{NOMS_LANGUES[x]}</strong>" if x == l else f'<a href="{x}.html" hreflang="{x}">{NOMS_LANGUES[x]}</a>' for x in LANGUES)
    cartes = []
    for ex in exemples:
        desc = ex["description"].get(l) or ex["description"]["en"]
        cartes.append(f"""<article class="carte">
<img src="{ex['image']}" alt="{html.escape(ex['nom'])}" loading="lazy" width="300" height="300">
<div><h2>{e(ex['nom'])}</h2>
<p>{e(desc)}</p>
<a href="{ex['fichier']}" download>⬇️ {e(ui['zip'])} ({taille_lisible(ex['taille'], ui)})</a></div>
</article>""")
    accueil = "../" + ("index.html" if l == "en" else f"{l}/index.html")
    guides = "../guides/index.html" if l == "fr" else f"../guides/{l}/index.html"
    return f"""<!DOCTYPE html>
<html lang="{l}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(ui["titre"].format(n=len(exemples)))}</title>
<meta name="description" content="{html.escape(ui["desc"])}">
<link rel="canonical" href="{SITE}exemples/{l}.html">
{alternates}
<link rel="stylesheet" href="../guides/guide.css">
<style>{CSS}</style>
</head>
<body>
<header>
<a href="{accueil}">← Yop2D</a>
<h1>{e(ui["h1"])}</h1>
<p class="langues">{langues}</p>
</header>
<main>
<p>{e(ui["intro"])}</p>
<div class="exemples">
{chr(10).join(cartes)}
</div>
<p class="note">{e(ui["aide"])}</p>
<div class="liens-bas">
<a href="{guides}">{e(ui["guides"])} →</a>
<a href="https://github.com/zinzin66/yop2d/releases/latest/download/Yop2D.apk">⬇️ {e(ui["telecharger"])}</a>
</div>
</main>
<footer>
<p>{e(ui["pied"])} · <a href="{accueil}">{e(ui["site"])}</a></p>
</footer>
</body>
</html>
"""


def main():
    dossier = os.path.join(RACINE, "exemples")
    source = json.load(open(os.path.join(RACINE, "outils", "exemples", "source.json"), encoding="utf-8"))
    exemples = []
    for ex in source["exemples"]:
        fichier, image = ex["id"] + ".zip", ex["id"] + ".png"
        chemin = os.path.join(dossier, fichier)
        if not os.path.exists(chemin):
            raise SystemExit(f"Fichier manquant : exemples/{fichier}")
        if not os.path.exists(os.path.join(dossier, image)):
            raise SystemExit(f"Vignette manquante : exemples/{image}")
        manque = [l for l in LANGUES if l not in ex["description"]]
        if manque:
            print(f"  {ex['id']} : description manquante en {', '.join(manque)} (l'anglais sera affiché)")
        exemples.append({
            "id": ex["id"], "nom": ex["nom"], "version": ex["version"], "moteur_min": ex["moteur_min"],
            "fichier": fichier, "image": image, "taille": os.path.getsize(chemin),
            "description": ex["description"],
        })
    liste = {"format": 1, "exemples": exemples}
    with open(os.path.join(dossier, "exemples.json"), "w", encoding="utf-8") as f:
        json.dump(liste, f, ensure_ascii=False, indent=1)
        f.write("\n")
    for l in LANGUES:
        open(os.path.join(dossier, f"{l}.html"), "w", encoding="utf-8").write(page(l, exemples))
    total = sum(x["taille"] for x in exemples)
    print(f"exemples/exemples.json : {len(exemples)} exemples ({total / 1024 / 1024:.1f} Mo) ; exemples/<langue>.html : {len(LANGUES)} pages")


if __name__ == "__main__":
    main()
