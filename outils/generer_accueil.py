#!/usr/bin/env python3
"""Génère la page d'accueil de Yop2D dans les 9 langues (présentation, comparatif, FAQ).

Textes : outils/accueil/<langue>.json (une langue par fichier).
Pages produites :
  - anglais  : index.html (racine du site, langue par défaut) ;
  - autres   : <langue>/index.html (ex. fr/index.html → https://…/Yop2d-web/fr/) ;
  - llms.txt : résumé en anglais pour les IA, tiré des textes anglais.

Dans les textes, « @/ » au début d'un lien désigne la racine du site
(ex. "@/testeur.html?lang=fr") : le script le remplace par le bon chemin.

Usage : python3 outils/generer_accueil.py
"""
import html
import json
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zinzin66.github.io/Yop2d-web/"
LANGUES = ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja"]
NOMS_LANGUES = {"fr": "Français", "en": "English", "es": "Español", "de": "Deutsch", "it": "Italiano",
                "pt": "Português", "ru": "Русский", "zh": "中文", "ja": "日本語"}
APK = "https://github.com/zinzin66/yop2d/releases/latest/download/Yop2D.apk"
ITCH = "https://yop2d-dev.itch.io/yop2d-no-code-game-engine"
YOUTUBE = "https://youtube.com/@yop2d"
DISCORD = "https://discord.gg/nHqCcqHZNQ"
TELEGRAM = "https://t.me/+7PQ9WKw7n645Y2Zk"
GITHUB = "https://github.com/zinzin66/yop2d"

# Captures d'écran, dans l'ordre des blocs « vitrine » des fichiers de textes.
# Une image absente du dépôt est simplement masquée dans la page : il suffit
# de l'ajouter avec ce nom exact pour qu'elle apparaisse.
IMAGES = ["interface_demarage.png", "interface_editeur.png", "interface_tuiles.png",
          "interfaceAnimation.jpg", "interfaceTitre.jpg", "interface_noeuds.png",
          "interface_editeur_noeuds.png", "exemples_jeux.png", "interface_telephone.png"]

CSS = """
:root {
--primary-color: #2563eb;
--secondary-color: #1e40af;
--accent-color: #f59e0b;
--youtube-color: #dc2626;
--discord-color: #5865f2;
--telegram-color: #229ed9;
--background: #f8fafc;
--text-dark: #0f172a;
}
body { font-family: system-ui, -apple-system, "Segoe UI", "Noto Sans", "PingFang SC", "Hiragino Sans", sans-serif; line-height: 1.6; color: var(--text-dark); background: var(--background); margin: 0; padding: 0; }
.lang-bar { background: #0f172a; color: #cbd5e1; font-size: 0.9rem; padding: 0.5rem 1rem; text-align: center; line-height: 1.9; }
.lang-bar a { color: #e2e8f0; text-decoration: none; margin: 0 0.35rem; white-space: nowrap; }
.lang-bar a:hover { text-decoration: underline; }
.lang-bar strong { color: var(--accent-color); margin: 0 0.35rem; white-space: nowrap; }
.lang-suggest { display: none; background: var(--accent-color); color: #0f172a; text-align: center; padding: 0.6rem 1rem; font-weight: bold; }
.lang-suggest a { color: #0f172a; }
header { background: linear-gradient(135deg, var(--primary-color), var(--secondary-color)); color: white; padding: 3.5rem 1rem 4rem; text-align: center; }
.logo { max-width: 120px; border-radius: 20%; box-shadow: 0 4px 10px rgba(0,0,0,0.2); margin-bottom: 1rem; }
header h1 { font-size: 3rem; margin: 0 0 0.5rem 0; }
header p { font-size: 1.25rem; max-width: 680px; margin: 0 auto; opacity: 0.95; }
.points { list-style: none; padding: 0; margin: 1.5rem auto 0; display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: center; max-width: 820px; }
.points li { background: rgba(255,255,255,0.15); border-radius: 30px; padding: 0.3rem 0.9rem; font-size: 0.95rem; }
.header-buttons, .community-buttons { display: flex; gap: 1rem; justify-content: center; flex-wrap: wrap; margin-top: 2rem; margin-bottom: 1.5rem; }
.btn { display: inline-block; color: white; padding: 1rem 2rem; border-radius: 50px; text-decoration: none; font-size: 1.15rem; font-weight: bold; box-shadow: 0 4px 6px rgba(0,0,0,0.1); transition: transform 0.2s; }
.btn:hover { transform: translateY(-3px); }
.btn-download { background: var(--accent-color); }
.btn-itch { background: #fa5c5c; }
.btn-play { background: #16a34a; }
.btn-youtube { background: var(--youtube-color); }
.btn-discord { background: var(--discord-color); }
.btn-telegram { background: var(--telegram-color); }
.install-note { max-width: 520px; margin: 1.5rem auto 0; font-size: 0.9rem; background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 8px; text-align: left; border-left: 4px solid var(--accent-color); }
.install-note a { color: white; }
.lang-badge { display: block; width: fit-content; max-width: 90%; background: rgba(255,255,255,0.2); padding: 0.5rem 1.5rem; border-radius: 30px; font-weight: bold; margin: 2rem auto 0 auto; font-size: 0.9rem; text-align: center; line-height: 1.4; }
main { max-width: 1000px; margin: 0 auto; padding: 2rem 1rem; }
section { margin-bottom: 4rem; }
h2 { font-size: 2rem; color: var(--primary-color); border-bottom: 2px solid #e2e8f0; padding-bottom: 0.5rem; margin-bottom: 1.5rem; }
.showcase { text-align: center; margin-bottom: 5rem; }
.showcase p { font-size: 1.1rem; text-align: left; background: white; padding: 1.5rem; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
.screenshot { width: 100%; max-width: 850px; height: auto; border-radius: 12px; box-shadow: 0 10px 20px rgba(0,0,0,0.15); margin: 0 auto 1.5rem auto; display: block; }
.grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1.5rem; }
.card { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.card h3 { color: var(--secondary-color); margin-top: 0; }
.card a { color: var(--primary-color); font-weight: bold; }
.bloc { background: white; padding: 1.5rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
.bloc a { color: var(--primary-color); }
.table-wrap { overflow-x: auto; background: white; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
table { border-collapse: collapse; width: 100%; min-width: 640px; font-size: 0.95rem; }
th, td { padding: 0.75rem; text-align: left; vertical-align: top; border-bottom: 1px solid #e2e8f0; }
thead th { background: #eff6ff; color: var(--secondary-color); }
tbody th { color: var(--secondary-color); white-space: nowrap; }
tr.nous { background: #fffbeb; }
.note { font-size: 0.85rem; color: #475569; margin-top: 0.75rem; }
.deux { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; margin-top: 1.5rem; }
.deux h3 { margin-top: 0; color: var(--secondary-color); }
.deux ul { margin: 0; padding-left: 1.2rem; }
.deux li { margin-bottom: 0.4rem; }
details.faq-item { background: white; padding: 1rem 1.25rem; border-radius: 8px; margin-bottom: 0.75rem; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border-left: 4px solid var(--primary-color); }
details.faq-item summary { font-weight: bold; font-size: 1.05rem; cursor: pointer; color: var(--secondary-color); list-style: none; }
details.faq-item summary::-webkit-details-marker { display: none; }
details.faq-item summary::before { content: '➕'; margin-right: 0.6rem; font-size: 0.85rem; opacity: 0.7; }
details.faq-item[open] summary::before { content: '➖'; }
details.faq-item p { margin: 0.75rem 0 0; }
details.faq-item a { color: var(--primary-color); }
code { background: #e2e8f0; padding: 0.1rem 0.4rem; border-radius: 4px; font-size: 0.9em; }
.community { text-align: center; background: white; padding: 2rem 1rem; border-radius: 12px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
footer { text-align: center; padding: 2rem 1rem; background: var(--text-dark); color: white; }
footer a { color: var(--accent-color); text-decoration: none; font-weight: bold; }
footer a:hover { text-decoration: underline; }
@media (max-width: 600px) {
  header { padding: 2.5rem 1rem 3rem; }
  header h1 { font-size: 2.2rem; }
  header p { font-size: 1.05rem; }
  .btn { font-size: 1rem; padding: 0.85rem 1.5rem; }
  h2 { font-size: 1.6rem; }
  /* Comparatif : une carte par moteur sur téléphone */
  table { min-width: 0; }
  thead { display: none; }
  tbody, tr, th, td { display: block; }
  tr { border-bottom: 3px solid #e2e8f0; padding: 0.5rem 0; }
  tbody th { font-size: 1.15rem; border: 0; padding-bottom: 0.25rem; }
  td { border: 0; padding: 0.3rem 0.75rem; }
  td::before { content: attr(data-label) ": "; font-weight: bold; color: var(--secondary-color); }
  html[lang="fr"] td::before { content: attr(data-label) " : "; }
  html[lang="zh"] td::before, html[lang="ja"] td::before { content: attr(data-label) "："; }
}
"""

# Script commun : mémorise la langue choisie dans le menu (même clé que la
# page testeurs). Sur la page anglaise (racine), il envoie vers la bonne
# langue si l'adresse contient ?lang=xx ou si le visiteur a déjà choisi une
# langue ; sinon il propose la langue du téléphone dans un bandeau.
JS = """
(function () {
  var CLE = 'yop2d-langue';
  var LANGUES = %s;
  var ICI = '%s';
  var SUGGESTIONS = %s;
  function lire() { try { return localStorage.getItem(CLE); } catch (e) { return null; } }
  function ecrire(l) { try { localStorage.setItem(CLE, l); } catch (e) {} }
  document.querySelectorAll('.lang-bar a[hreflang]').forEach(function (a) {
    a.addEventListener('click', function () { ecrire(a.getAttribute('hreflang')); });
  });
  if (ICI !== 'en') return;
  function adresse(l) { return l + '/'; }
  var demande = new URLSearchParams(location.search).get('lang');
  if (demande) {
    demande = demande.slice(0, 2).toLowerCase();
    if (demande !== 'en' && LANGUES.indexOf(demande) >= 0) { location.replace(adresse(demande) + location.hash); return; }
    if (demande === 'en') { ecrire('en'); return; }
  }
  var choix = lire();
  if (choix && choix !== 'en' && LANGUES.indexOf(choix) >= 0) { location.replace(adresse(choix) + location.hash); return; }
  if (choix === 'en') return;
  var tel = (navigator.language || '').slice(0, 2).toLowerCase();
  if (tel !== 'en' && SUGGESTIONS[tel]) {
    var b = document.getElementById('lang-suggest');
    b.innerHTML = '🌍 <a href="' + adresse(tel) + '" hreflang="' + tel + '">' + SUGGESTIONS[tel] + '</a>';
    b.querySelector('a').addEventListener('click', function () { ecrire(tel); });
    b.style.display = 'block';
  }
})();
"""


def e(texte):
    return html.escape(texte, quote=True)


def adresse_accueil(langue):
    """Chemin de la page d'accueil d'une langue, depuis la racine du site."""
    return "" if langue == "en" else f"{langue}/"


def liens(texte, base):
    """Remplace « @/ » (racine du site) par le bon chemin relatif."""
    return texte.replace("@/", base)


def sans_balises(texte):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", texte))).strip()


def nombre_noeuds():
    """Nombre de nœuds de l'aide (tous les fichiers aide/noeuds/en/*.json) : remplace {nb_noeuds} dans les textes."""
    dossier = os.path.join(RACINE, "aide", "noeuds", "en")
    total = 0
    for nom in os.listdir(dossier):
        if nom.endswith(".json"):
            with open(os.path.join(dossier, nom), encoding="utf-8") as f:
                total += len(json.load(f)["noeuds"])
    return total


def cartes_guides(langue):
    dossier = os.path.join(RACINE, "aide", "guides", langue)
    cartes = []
    for nom in sorted(os.listdir(dossier)):
        if nom.endswith(".json"):
            with open(os.path.join(dossier, nom), encoding="utf-8") as f:
                cartes.append(json.load(f))
    return cartes


def page(langue, t):
    base = "" if langue == "en" else "../"
    url = SITE + adresse_accueil(langue)

    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{l}" href="{SITE}{adresse_accueil(l)}">' for l in LANGUES)
    alternates += f'\n<link rel="alternate" hreflang="x-default" href="{SITE}">'
    menu = " ".join(
        f"<strong>{NOMS_LANGUES[l]}</strong>" if l == langue
        else f'<a href="{base}{adresse_accueil(l) or "index.html"}" hreflang="{l}" lang="{l}">{NOMS_LANGUES[l]}</a>'
        for l in LANGUES)

    logiciel = {
        "@context": "https://schema.org",
        "@type": "SoftwareApplication",
        "name": "Yop2D",
        "url": url,
        "operatingSystem": "Android 7.0+",
        "applicationCategory": "DeveloperApplication",
        "applicationSubCategory": "2D Game Engine",
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "downloadUrl": APK,
        "inLanguage": LANGUES,
        "image": SITE + "interface_editeur.png",
        "description": t["description"],
        "featureList": [c[0] for c in t["capacites"]["cartes"]],
        "sameAs": [YOUTUBE, DISCORD, TELEGRAM, GITHUB, ITCH],
    }
    faq = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "inLanguage": langue,
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": sans_balises(r)}}
            for q, r in t["faq"]["questions"]],
    }

    points = "\n".join(f"<li>{e(p)}</li>" for p in t["points"])

    vitrine = []
    for image, (alt, titre, texte) in zip(IMAGES, t["vitrine"]):
        vitrine.append(f"""<section class="showcase">
<h2>{e(titre)}</h2>
<img src="{base}{image}" alt="{e(alt)}" class="screenshot" loading="lazy" onerror="this.remove()">
<p>{liens(texte, base)}</p>
</section>""")

    cartes = "\n".join(
        f'<div class="card">\n<h3>{e(h)}</h3>\n<p>{liens(p, base)}</p>\n</div>'
        for h, p in t["capacites"]["cartes"])

    guides = "\n".join(
        f'<div class="card">\n<h3>{e(c["titre"])}</h3>\n<p>{e(c["description"])}</p>\n'
        f'<p><a href="{base}{c["lien"]}">{e(t["guides"]["lire"])} →</a></p>\n</div>'
        for c in cartes_guides(langue))

    comp = t["comparatif"]
    entete = "".join(f"<th scope=\"col\">{e(c)}</th>" for c in comp["colonnes"])
    lignes = []
    for i, ligne in enumerate(comp["lignes"]):
        cellules = f'<th scope="row">{e(ligne[0])}</th>' + "".join(f'<td data-label="{e(col)}">{e(c)}</td>' for col, c in zip(comp["colonnes"][1:], ligne[1:]))
        classe = ' class="nous"' if i == 0 else ""
        lignes.append(f"<tr{classe}>{cellules}</tr>")
    limites = "\n".join(f"<li>{liens(x, base)}</li>" for x in comp["limites"])
    choisir = "\n".join(f"<li>{liens(x, base)}</li>" for x in comp["choisir"])
    autres = "\n".join(f"<li>{liens(x, base)}</li>" for x in comp["autres"])

    questions = "\n".join(
        f'<details class="faq-item">\n<summary>{e(q)}</summary>\n<p>{liens(r, base)}</p>\n</details>'
        for q, r in t["faq"]["questions"])

    suggestions = {l: json.load(open(os.path.join(RACINE, "outils", "accueil", f"{l}.json"), encoding="utf-8"))["bandeau"]
                   for l in LANGUES if l != "en"}
    script = JS % (json.dumps(LANGUES), langue, json.dumps(suggestions, ensure_ascii=False))

    b = t["boutons"]
    return f"""<!DOCTYPE html>
<html lang="{langue}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(t["titre"])}</title>
<meta name="description" content="{e(t["description"])}">
<link rel="canonical" href="{url}">
{alternates}
<link rel="icon" href="{base}logo_yop2d.png">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Yop2D">
<meta property="og:title" content="{e(t["titre"])}">
<meta property="og:description" content="{e(t["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE}interface_editeur.png">
<meta property="og:locale" content="{t["locale"]}">
<meta name="twitter:card" content="summary_large_image">
<script type="application/ld+json">
{json.dumps(logiciel, ensure_ascii=False, indent=1)}
</script>
<script type="application/ld+json">
{json.dumps(faq, ensure_ascii=False, indent=1)}
</script>
<style>{CSS}</style>
</head>
<body>
<nav class="lang-bar" aria-label="{e(t["menu_langue"])}">🌍 {menu}</nav>
<div class="lang-suggest" id="lang-suggest"></div>
<header>
<img src="{base}logo_yop2d.png" alt="{e(t["alt_logo"])}" class="logo" width="120" height="120">
<h1>Yop2D</h1>
<p>{e(t["slogan"])}</p>
<ul class="points">
{points}
</ul>

<div class="header-buttons">
    <a href="{APK}" class="btn btn-download">⬇️ {e(b["apk"])}</a>
    <a href="{ITCH}" target="_blank" rel="noopener" class="btn btn-itch">🎮 {e(b["itch"])}</a>
    <a href="{base}testeur.html?lang={langue}" class="btn btn-play">▶️ {e(b["testeur"])}</a>
    <a href="{YOUTUBE}" target="_blank" rel="noopener" class="btn btn-youtube">📺 {e(b["youtube"])}</a>
</div>

<img src="https://img.shields.io/github/downloads/zinzin66/yop2d/total?style=for-the-badge&color=blue" alt="{e(t["alt_badge"])}">

<div class="install-note">{liens(t["note_installation"], base)}</div>
<div class="lang-badge">🌍 {e(t["langues_interface"])}</div>
</header>
<main>
{chr(10).join(vitrine)}

<section id="features">
<h2>{e(t["capacites"]["titre"])}</h2>
<div class="grid">
{cartes}
</div>
</section>

<section id="guides">
<h2>{e(t["guides"]["titre"])}</h2>
<p>{liens(t["guides"]["texte"], base)}</p>
<div class="grid">
{guides}
</div>
<p style="text-align:center;margin-top:1.5rem"><a class="btn btn-download" href="{base}{"guides/index.html" if langue == "fr" else f"guides/{langue}/index.html"}">📚 {e(t["guides"]["tous"])} →</a></p>
</section>

<section id="nodes-dictionary">
<h2>{e(t["noeuds"]["titre"])}</h2>
<div class="bloc">
<p>{liens(t["noeuds"]["texte"], base)}</p>
<p><a href="{base}noeuds/{langue}.html"><strong>{e(t["noeuds"]["lien"])} →</strong></a></p>
</div>
</section>

<section id="comparison">
<h2>{e(comp["titre"])}</h2>
<p>{liens(comp["intro"], base)}</p>
<div class="table-wrap">
<table>
<thead><tr>{entete}</tr></thead>
<tbody>
{chr(10).join(lignes)}
</tbody>
</table>
</div>
<p class="note">{e(comp["note"])}</p>
<div class="deux">
<div class="bloc">
<h3>{e(comp["choisir_titre"])}</h3>
<ul>
{choisir}
</ul>
</div>
<div class="bloc">
<h3>{e(comp["limites_titre"])}</h3>
<ul>
{limites}
</ul>
</div>
</div>
<div class="bloc" style="margin-top:1.5rem">
<h3 style="margin-top:0">{e(comp["autres_titre"])}</h3>
<ul>
{autres}
</ul>
</div>
</section>

<section id="faq">
<h2>{e(t["faq"]["titre"])}</h2>
{questions}
</section>

<section id="community">
<h2>{e(t["communaute"]["titre"])}</h2>
<div class="community">
<p>{liens(t["communaute"]["texte"], base)}</p>
<div class="community-buttons">
    <a href="{DISCORD}" target="_blank" rel="noopener" class="btn btn-discord">💬 Discord</a>
    <a href="{TELEGRAM}" target="_blank" rel="noopener" class="btn btn-telegram">✈️ Telegram</a>
</div>
</div>
</section>
</main>
<footer>
<p>© 2026 Yop2D · {e(t["pied"]["texte"])}<br>
<a href="{base}confidentialite.html">{e(t["pied"]["confidentialite"])}</a> ·
<a href="{base}testeur.html?lang={langue}">{e(t["pied"]["testeur"])}</a> ·
<a href="{YOUTUBE}" target="_blank" rel="noopener">YouTube</a> ·
<a href="{DISCORD}" target="_blank" rel="noopener">Discord</a> ·
<a href="{TELEGRAM}" target="_blank" rel="noopener">Telegram</a> ·
<a href="{ITCH}" target="_blank" rel="noopener">itch.io</a> ·
<a href="{GITHUB}" target="_blank" rel="noopener">GitHub</a></p>
</footer>
<script>{script}</script>
</body>
</html>
"""


def llms(t):
    """Résumé en texte simple pour les IA (format llms.txt, https://llmstxt.org)."""
    faq = t["faq"]["questions"]
    comp = t["comparatif"]
    lignes = [
        "# Yop2D",
        "",
        f"> {t['description']}",
        "",
        "Yop2D is made by an independent developer. The interface, built-in help, guides and "
        "node reference are available in 9 languages: " + ", ".join(NOMS_LANGUES[l] for l in LANGUES) + ".",
        "",
        "Key facts:",
        "",
    ]
    lignes += [f"- {p}" for p in t["points"]]
    lignes += [
        "- Runs on Android 7.0 or newer, tablets and phones (landscape). No iPhone, iPad or computer version.",
        "- Exports games as standalone Android APK files, built on the device itself, offline.",
        "- No AAB export yet (needed for Google Play); planned for a later version.",
        "- 2D only. Closed source. In closed testing on Google Play.",
        "",
        "## Download",
        "",
        f"- [Latest APK]({APK}): direct download from GitHub releases",
        f"- [itch.io page]({ITCH}): Yop2D on itch.io",
        f"- [Become a tester]({SITE}testeur.html): join the closed test on Google Play",
        "",
        "## Home page in each language",
        "",
    ]
    lignes += [f"- [{NOMS_LANGUES[l]}]({SITE}{adresse_accueil(l)})" for l in LANGUES]
    lignes += ["", "## Beginner guides", ""]
    for c in cartes_guides("en"):
        lignes.append(f"- [{c['titre']}]({SITE}{c['lien']}): {c['description']}")
    lignes.append(f"- [All guides]({SITE}guides/en/index.html): the list of all beginner guides, in order")
    lignes.append("")
    lignes.append("Guides also exist in the other 8 languages: French at guides/<guide>.html "
                  "(list: guides/index.html), others at guides/<language code>/<guide>.html "
                  "(list: guides/<language code>/index.html).")
    lignes += ["", "## Node reference", ""]
    lignes += [f"- [All nodes, {NOMS_LANGUES[l]}]({SITE}noeuds/{l}.html)" for l in LANGUES]
    dossier = os.path.join(RACINE, "aide", "noeuds", "en")
    lignes += ["", "Node categories and node names (as shown in the English editor):", ""]
    for nom in sorted(os.listdir(dossier)):
        if nom.endswith(".json"):
            with open(os.path.join(dossier, nom), encoding="utf-8") as f:
                cat = json.load(f)
            lignes.append(f"- {cat['categorie']}: " + "; ".join(n["nom"] for n in cat["noeuds"]))
    lignes += ["", "## Comparison with other engines", "", comp["intro"], ""]
    for ligne in comp["lignes"]:
        lignes.append(f"- {ligne[0]}: " + "; ".join(f"{c}: {v}" for c, v in zip(comp["colonnes"][1:], ligne[1:])))
    lignes += ["", comp["note"], "", comp["limites_titre"] + ":", ""]
    lignes += [f"- {sans_balises(x)}" for x in comp["limites"]]
    lignes += ["", comp["autres_titre"] + ":", ""]
    lignes += [f"- {sans_balises(x)}" for x in comp["autres"]]
    lignes += ["", "## FAQ", ""]
    for q, r in faq:
        lignes += [f"### {q}", "", sans_balises(r), ""]
    lignes += [
        "## Optional",
        "",
        f"- [Privacy policy]({SITE}confidentialite.html): anonymous statistics, opt-out, nothing sent by exported games",
        f"- [YouTube]({YOUTUBE}): video tutorials",
        f"- [Discord]({DISCORD}): community",
        f"- [Telegram]({TELEGRAM}): community",
        f"- [GitHub]({GITHUB}): releases",
        "",
    ]
    return "\n".join(lignes)


def main():
    for langue in LANGUES:
        with open(os.path.join(RACINE, "outils", "accueil", f"{langue}.json"), encoding="utf-8") as f:
            t = json.loads(f.read().replace("{nb_noeuds}", str(nombre_noeuds())))
        assert len(t["vitrine"]) == len(IMAGES), f"{langue} : {len(t['vitrine'])} blocs vitrine au lieu de {len(IMAGES)}"
        chemin = os.path.join(RACINE, adresse_accueil(langue), "index.html")
        os.makedirs(os.path.dirname(chemin), exist_ok=True)
        with open(chemin, "w", encoding="utf-8") as f:
            f.write(page(langue, t))
        print(f"{langue} : {os.path.relpath(chemin, RACINE)} ({len(t['faq']['questions'])} questions)")
        if langue == "en":
            with open(os.path.join(RACINE, "llms.txt"), "w", encoding="utf-8") as f:
                f.write(llms(t))
            print("llms.txt")


if __name__ == "__main__":
    main()
