#!/usr/bin/env python3
"""Construit testeur.html : depuis le 02/11/2026 Yop2D est public sur Google Play, la page « Devenir testeur »
devient une petite page qui envoie vers la fiche du Play Store (les anciennes versions du moteur et d'anciens
liens ouvrent encore testeur.html?lang=xx). Une seule langue affichée (?lang=, dernier choix, téléphone, anglais).

Utilisation : python3 outils/generer_testeur.py
"""
import html
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLAY = "https://play.google.com/store/apps/details?id=com.ludexa.moteur"
ACCUEIL = "https://zinzin66.github.io/Yop2d-web/"

T = {
 "fr": ("Français", "Yop2D est sur Google Play", "Le moteur de jeu 2D gratuit et sans code pour Android est disponible sur le Play Store.", "Télécharger sur Google Play", "Retour au site"),
 "en": ("English", "Yop2D is on Google Play", "The free, no-code 2D game engine for Android is now available on the Play Store.", "Get it on Google Play", "Back to the website"),
 "es": ("Español", "Yop2D está en Google Play", "El motor de juegos 2D gratuito y sin código para Android ya está disponible en Play Store.", "Descargar en Google Play", "Volver al sitio"),
 "de": ("Deutsch", "Yop2D ist bei Google Play", "Die kostenlose No-Code-2D-Spiele-Engine für Android ist jetzt im Play Store erhältlich.", "Bei Google Play laden", "Zurück zur Website"),
 "it": ("Italiano", "Yop2D è su Google Play", "Il motore di giochi 2D gratuito e senza codice per Android è ora disponibile sul Play Store.", "Scarica su Google Play", "Torna al sito"),
 "pt": ("Português", "O Yop2D está no Google Play", "O motor de jogos 2D gratuito e sem código para Android já está disponível na Play Store.", "Baixar no Google Play", "Voltar ao site"),
 "ru": ("Русский", "Yop2D в Google Play", "Бесплатный движок для 2D-игр без кода на Android теперь доступен в Play Маркете.", "Скачать в Google Play", "Вернуться на сайт"),
 "zh": ("中文", "Yop2D 已在 Google Play 上架", "适用于 Android 的免费免代码 2D 游戏引擎，现已在 Play 商店提供。", "在 Google Play 下载", "返回网站"),
 "ja": ("日本語", "Yop2D は Google Play で入手できます", "Android 用の無料ノーコード 2D ゲームエンジンが Play ストアで公開されました。", "Google Play で入手", "サイトに戻る"),
}

blocs = []
for l, (nom, titre, texte, bouton, retour) in T.items():
    blocs.append(
        f'<section lang="{l}" data-l="{l}"><h1>{html.escape(titre)}</h1><p>{html.escape(texte)}</p>'
        f'<p><a class="btn" href="{PLAY}">{html.escape(bouton)}</a></p>'
        f'<p><a href="{ACCUEIL}{"" if l == "en" else l + "/"}">{html.escape(retour)}</a></p></section>')

page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Yop2D - Google Play</title>
<meta name="robots" content="noindex">
<meta name="description" content="Yop2D, the free no-code 2D game engine for Android, is on Google Play.">
<link rel="canonical" href="{ACCUEIL}">
<link rel="icon" href="logo_yop2d.png">
<style>
body{{margin:0;font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;min-height:100vh;align-items:center;justify-content:center;text-align:center;padding:1rem}}
section{{display:none;max-width:32rem}} section.on{{display:block}}
h1{{font-size:1.6rem}} a{{color:#4cc9f0}}
.btn{{display:inline-block;background:#16a34a;color:#fff;padding:.9rem 1.6rem;border-radius:.6rem;text-decoration:none;font-weight:700}}
</style>
</head>
<body>
<main>
{chr(10).join(blocs)}
</main>
<script>
(function () {{
  var L = {list(T)!r};
  var l = (new URLSearchParams(location.search).get('lang') || '').slice(0, 2).toLowerCase();
  try {{ if (L.indexOf(l) < 0) l = localStorage.getItem('yop2d-langue') || ''; }} catch (e) {{}}
  if (L.indexOf(l) < 0) l = (navigator.language || 'en').slice(0, 2).toLowerCase();
  if (L.indexOf(l) < 0) l = 'en';
  var s = document.querySelector('section[data-l="' + l + '"]');
  if (s) s.className = 'on';
  setTimeout(function () {{ location.replace('{PLAY}'); }}, 2500);
}})();
</script>
<noscript><style>section{{display:block;margin-bottom:2rem}}</style></noscript>
</body>
</html>
"""
with open(os.path.join(RACINE, "testeur.html"), "w", encoding="utf-8") as f:
    f.write(page)
print("testeur.html : redirection vers Google Play,", len(T), "langues")
