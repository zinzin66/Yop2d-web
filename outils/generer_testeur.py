#!/usr/bin/env python3
"""Construit testeur.html (page « Devenir testeur ») dans les 9 langues.

Toutes les langues sont dans la même page (lisibles par les moteurs de recherche) ;
un petit script n'affiche que celle du visiteur : ?lang=xx, sinon son dernier choix,
sinon la langue du téléphone, sinon l'anglais. Sans script, tout reste visible.

Utilisation : python3 outils/generer_testeur.py
"""
import html
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GROUPE = "https://groups.google.com/g/yop2d-testeurs"
TEST = "https://play.google.com/apps/testing/com.ludexa.moteur"
DISCORD = "https://discord.gg/nHqCcqHZNQ"
TELEGRAM = "https://t.me/+7PQ9WKw7n645Y2Zk"

# Pour chaque langue : nom affiché, puis les textes. {discord} et {telegram} deviennent des liens.
T = {
 "fr": dict(nom="Français", titre="Devenir testeur de Yop2D", sous="Aidez Yop2D à arriver sur le Google Play Store",
   intro="Pour publier Yop2D sur le Play Store, Google demande qu'au moins 12 personnes le testent pendant 14 jours. En devenant testeur, vous aidez Yop2D à être disponible pour tout le monde, avec des mises à jour automatiques.",
   comment="Comment faire (2 minutes)",
   e1="Rejoignez le groupe des testeurs.", e1t="Il faut être connecté avec votre compte Google (celui de votre appareil Android). Votre adresse n'est pas visible par les autres membres, et vous ne recevrez aucun e-mail.", b1="Rejoindre le groupe",
   e2="Inscrivez-vous au test", e2t=", avec le même compte Google.", b2="S'inscrire au test",
   e3="Installez Yop2D depuis le Play Store.", e3t="Après l'inscription, la page du test vous propose le lien vers le Play Store.",
   att="Vous avez déjà Yop2D (itch.io ou GitHub) ?", att1="Android peut refuser d'installer la version du Play Store par-dessus. Avant de désinstaller l'ancienne version,", att2="exportez vos projets en .zip", att3="(bouton Exporter de l'écran d'accueil), car la désinstallation les efface. Réimportez-les ensuite dans la version du Play Store.",
   attente="Ce qu'on attend de vous", a1="Garder Yop2D installé pendant au moins 14 jours.", a2="L'utiliser vraiment : ouvrir un jeu d'exemple, le modifier, créer un petit jeu.", a3="Signaler les bugs et vos idées sur {discord} ou {telegram}.",
   fin="Si le lien d'inscription affiche une erreur, réessayez un peu plus tard. Merci pour votre aide !",
   desc="Aidez Yop2D, moteur de jeu 2D gratuit et sans code pour Android, à arriver sur le Google Play Store : rejoignez le test fermé en 2 minutes.",
   pied="Yop2D, moteur de jeu 2D gratuit et sans code pour Android", site="Site officiel"),
 "en": dict(nom="English", titre="Become a Yop2D tester", sous="Help Yop2D get onto the Google Play Store",
   intro="To publish Yop2D on the Play Store, Google requires at least 12 people to test it for 14 days. By becoming a tester, you help make Yop2D available to everyone, with automatic updates.",
   comment="How to join (2 minutes)",
   e1="Join the testers group.", e1t="You need to be signed in with your Google account (the one on your Android device). Your address is not visible to other members, and you won't receive any email.", b1="Join the group",
   e2="Sign up for the test", e2t=", with the same Google account.", b2="Join the test",
   e3="Install Yop2D from the Play Store.", e3t="After signing up, the test page gives you the Play Store link.",
   att="Already using Yop2D (itch.io or GitHub)?", att1="Android may refuse to install the Play Store version over it. Before uninstalling the old version,", att2="export your projects as .zip files", att3="(Export button on the home screen), because uninstalling deletes them. Then import them into the Play Store version.",
   attente="What we ask", a1="Keep Yop2D installed for at least 14 days.", a2="Really use it: open an example game, change it, make a small game.", a3="Report bugs and ideas on {discord} or {telegram}.",
   fin="If the sign-up link shows an error, please try again a little later. Thank you for your help!",
   desc="Help Yop2D, the free no-code 2D game engine for Android, get onto the Google Play Store: join the closed test in 2 minutes.",
   pied="Yop2D, free no-code 2D game engine for Android", site="Official website"),
 "es": dict(nom="Español", titre="Conviértete en tester de Yop2D", sous="Ayuda a Yop2D a llegar a Google Play Store",
   intro="Para publicar Yop2D en la Play Store, Google pide que al menos 12 personas lo prueben durante 14 días. Al ser tester, ayudas a que Yop2D esté disponible para todos, con actualizaciones automáticas.",
   comment="Cómo hacerlo (2 minutos)",
   e1="Únete al grupo de testers.", e1t="Debes iniciar sesión con tu cuenta de Google (la de tu dispositivo Android). Tu dirección no es visible para otros miembros, y no recibirás ningún correo.", b1="Unirse al grupo",
   e2="Regístrate en la prueba", e2t=", con la misma cuenta de Google.", b2="Unirse a la prueba",
   e3="Instala Yop2D desde la Play Store.", e3t="Tras registrarte, la página de la prueba te da el enlace a la Play Store.",
   att="¿Ya tienes Yop2D (itch.io o GitHub)?", att1="Android puede rechazar instalar la versión de la Play Store encima. Antes de desinstalar la versión anterior,", att2="exporta tus proyectos en .zip", att3="(botón Exportar de la pantalla de inicio), ya que al desinstalar se borran. Luego impórtalos en la versión de la Play Store.",
   attente="Lo que te pedimos", a1="Mantener Yop2D instalado al menos 14 días.", a2="Usarlo de verdad: abrir un juego de ejemplo, modificarlo, crear un pequeño juego.", a3="Reportar errores e ideas en {discord} o {telegram}.",
   fin="Si el enlace de registro muestra un error, vuelve a intentarlo un poco más tarde. ¡Gracias por tu ayuda!",
   desc="Ayuda a Yop2D, motor de juegos 2D gratuito y sin código para Android, a llegar a Google Play Store: únete a la prueba cerrada en 2 minutos.",
   pied="Yop2D, motor de juegos 2D gratuito y sin código para Android", site="Sitio oficial"),
 "pt": dict(nom="Português", titre="Torne-se testador do Yop2D", sous="Ajude o Yop2D a chegar à Google Play Store",
   intro="Para publicar o Yop2D na Play Store, o Google exige que pelo menos 12 pessoas o testem durante 14 dias. Ao se tornar testador, você ajuda o Yop2D a ficar disponível para todos, com atualizações automáticas.",
   comment="Como participar (2 minutos)",
   e1="Entre no grupo de testadores.", e1t="É preciso estar conectado com sua conta Google (a do seu aparelho Android). Seu endereço não fica visível para outros membros, e você não receberá nenhum e-mail.", b1="Entrar no grupo",
   e2="Inscreva-se no teste", e2t=", com a mesma conta Google.", b2="Participar do teste",
   e3="Instale o Yop2D pela Play Store.", e3t="Depois de se inscrever, a página do teste mostra o link para a Play Store.",
   att="Já tem o Yop2D (itch.io ou GitHub)?", att1="O Android pode recusar instalar a versão da Play Store por cima. Antes de desinstalar a versão antiga,", att2="exporte seus projetos em .zip", att3="(botão Exportar na tela inicial), pois a desinstalação os apaga. Depois importe-os na versão da Play Store.",
   attente="O que pedimos a você", a1="Manter o Yop2D instalado por pelo menos 14 dias.", a2="Usá-lo de verdade: abrir um jogo de exemplo, modificá-lo, criar um jogo pequeno.", a3="Reportar bugs e ideias no {discord} ou no {telegram}.",
   fin="Se o link de inscrição mostrar um erro, tente de novo um pouco mais tarde. Obrigado pela sua ajuda!",
   desc="Ajude o Yop2D, motor de jogos 2D gratuito e sem código para Android, a chegar à Google Play Store: participe do teste fechado em 2 minutos.",
   pied="Yop2D, motor de jogos 2D gratuito e sem código para Android", site="Site oficial"),
 "de": dict(nom="Deutsch", titre="Werde Yop2D-Tester", sous="Hilf Yop2D in den Google Play Store",
   intro="Um Yop2D im Play Store zu veröffentlichen, verlangt Google, dass mindestens 12 Personen es 14 Tage lang testen. Als Tester hilfst du, dass Yop2D für alle verfügbar wird, mit automatischen Updates.",
   comment="So machst du mit (2 Minuten)",
   e1="Tritt der Testergruppe bei.", e1t="Du musst mit deinem Google-Konto angemeldet sein (dem deines Android-Geräts). Deine Adresse ist für andere Mitglieder nicht sichtbar, und du bekommst keine E-Mails.", b1="Der Gruppe beitreten",
   e2="Melde dich zum Test an", e2t=", mit demselben Google-Konto.", b2="Am Test teilnehmen",
   e3="Installiere Yop2D aus dem Play Store.", e3t="Nach der Anmeldung zeigt dir die Testseite den Link zum Play Store.",
   att="Du hast Yop2D schon (itch.io oder GitHub)?", att1="Android kann sich weigern, die Play-Store-Version darüber zu installieren. Bevor du die alte Version deinstallierst,", att2="exportiere deine Projekte als .zip", att3="(Taste Exportieren auf dem Startbildschirm), denn beim Deinstallieren werden sie gelöscht. Importiere sie danach in die Play-Store-Version.",
   attente="Was wir uns wünschen", a1="Yop2D mindestens 14 Tage lang installiert lassen.", a2="Es wirklich benutzen: ein Beispielspiel öffnen, verändern, ein kleines Spiel bauen.", a3="Fehler und Ideen auf {discord} oder {telegram} melden.",
   fin="Wenn der Anmeldelink einen Fehler zeigt, versuche es etwas später noch einmal. Danke für deine Hilfe!",
   desc="Hilf Yop2D, der kostenlosen 2D-Spiel-Engine ohne Code für Android, in den Google Play Store: Nimm in 2 Minuten am geschlossenen Test teil.",
   pied="Yop2D, kostenlose 2D-Spiel-Engine ohne Code für Android", site="Offizielle Website"),
 "it": dict(nom="Italiano", titre="Diventa tester di Yop2D", sous="Aiuta Yop2D ad arrivare sul Google Play Store",
   intro="Per pubblicare Yop2D sul Play Store, Google chiede che almeno 12 persone lo provino per 14 giorni. Diventando tester, aiuti Yop2D a essere disponibile per tutti, con aggiornamenti automatici.",
   comment="Come partecipare (2 minuti)",
   e1="Entra nel gruppo dei tester.", e1t="Devi essere connesso con il tuo account Google (quello del tuo dispositivo Android). Il tuo indirizzo non è visibile agli altri membri e non riceverai nessuna e-mail.", b1="Entra nel gruppo",
   e2="Iscriviti al test", e2t=", con lo stesso account Google.", b2="Iscriviti al test",
   e3="Installa Yop2D dal Play Store.", e3t="Dopo l'iscrizione, la pagina del test ti propone il link al Play Store.",
   att="Hai già Yop2D (itch.io o GitHub)?", att1="Android potrebbe rifiutare di installare sopra la versione del Play Store. Prima di disinstallare la vecchia versione,", att2="esporta i tuoi progetti in .zip", att3="(pulsante Esporta nella schermata iniziale), perché la disinstallazione li cancella. Poi reimportali nella versione del Play Store.",
   attente="Cosa ti chiediamo", a1="Tenere Yop2D installato per almeno 14 giorni.", a2="Usarlo davvero: aprire un gioco di esempio, modificarlo, creare un piccolo gioco.", a3="Segnalare bug e idee su {discord} o {telegram}.",
   fin="Se il link di iscrizione mostra un errore, riprova un po' più tardi. Grazie per il tuo aiuto!",
   desc="Aiuta Yop2D, motore di gioco 2D gratuito e senza codice per Android, ad arrivare sul Google Play Store: partecipa al test chiuso in 2 minuti.",
   pied="Yop2D, motore di gioco 2D gratuito e senza codice per Android", site="Sito ufficiale"),
 "ru": dict(nom="Русский", titre="Стань тестировщиком Yop2D", sous="Помоги Yop2D попасть в Google Play",
   intro="Чтобы опубликовать Yop2D в Google Play, Google требует, чтобы минимум 12 человек тестировали его 14 дней. Став тестировщиком, ты помогаешь сделать Yop2D доступным для всех, с автоматическими обновлениями.",
   comment="Как присоединиться (2 минуты)",
   e1="Вступи в группу тестировщиков.", e1t="Нужно войти в свой аккаунт Google (тот, что на твоём Android-устройстве). Твой адрес не виден другим участникам, и писем ты получать не будешь.", b1="Вступить в группу",
   e2="Запишись на тест", e2t=" с тем же аккаунтом Google.", b2="Записаться на тест",
   e3="Установи Yop2D из Google Play.", e3t="После записи страница теста даст ссылку на Google Play.",
   att="У тебя уже есть Yop2D (itch.io или GitHub)?", att1="Android может не установить версию из Google Play поверх старой. Перед удалением старой версии", att2="экспортируй свои проекты в .zip", att3="(кнопка «Экспорт» на главном экране), потому что при удалении они стираются. Затем импортируй их в версию из Google Play.",
   attente="Что мы просим", a1="Не удалять Yop2D минимум 14 дней.", a2="Действительно им пользоваться: открыть пример игры, изменить его, сделать маленькую игру.", a3="Сообщать об ошибках и идеях в {discord} или {telegram}.",
   fin="Если ссылка для записи показывает ошибку, попробуй чуть позже. Спасибо за помощь!",
   desc="Помоги Yop2D, бесплатному 2D-движку без кода для Android, попасть в Google Play: присоединяйся к закрытому тесту за 2 минуты.",
   pied="Yop2D — бесплатный 2D-движок без кода для Android", site="Официальный сайт"),
 "zh": dict(nom="中文", titre="成为 Yop2D 测试者", sous="帮助 Yop2D 登上 Google Play 商店",
   intro="要在 Play 商店发布 Yop2D，Google 要求至少 12 个人连续测试 14 天。成为测试者，你就能帮助 Yop2D 向所有人开放，并获得自动更新。",
   comment="如何参加（2 分钟）",
   e1="加入测试者群组。", e1t="需要登录你的 Google 账号（就是你安卓设备上的那个）。其他成员看不到你的邮箱地址，你也不会收到任何邮件。", b1="加入群组",
   e2="报名参加测试", e2t="，使用同一个 Google 账号。", b2="参加测试",
   e3="从 Play 商店安装 Yop2D。", e3t="报名后，测试页面会给出 Play 商店的链接。",
   att="你已经装了 Yop2D（itch.io 或 GitHub 版本）？", att1="安卓可能无法在它上面直接安装 Play 商店版本。卸载旧版本之前，", att2="请把你的项目导出为 .zip", att3="（主界面上的“导出”按钮），因为卸载会删除它们。之后再把它们导入 Play 商店版本。",
   attente="我们希望你", a1="让 Yop2D 保持安装至少 14 天。", a2="真正用起来：打开一个示例游戏，改一改，做一个小游戏。", a3="在 {discord} 或 {telegram} 反馈错误和想法。",
   fin="如果报名链接显示错误，请稍后再试。谢谢你的帮助！",
   desc="帮助 Yop2D——免费、无需代码的安卓 2D 游戏引擎——登上 Google Play：2 分钟加入封闭测试。",
   pied="Yop2D，免费、无需代码的 Android 2D 游戏引擎", site="官方网站"),
 "ja": dict(nom="日本語", titre="Yop2D のテスターになる", sous="Yop2D を Google Play ストアに届けるために",
   intro="Yop2D を Play ストアで公開するには、12 人以上が 14 日間テストすることを Google が求めています。テスターになると、Yop2D を誰でも使えるようにする手助けになり、アップデートも自動で届きます。",
   comment="参加のしかた（2 分）",
   e1="テスターのグループに参加します。", e1t="Google アカウント（Android 端末で使っているもの）でログインしている必要があります。あなたのアドレスはほかのメンバーには見えず、メールが届くこともありません。", b1="グループに参加",
   e2="テストに登録します", e2t="（同じ Google アカウントで）。", b2="テストに登録",
   e3="Play ストアから Yop2D をインストールします。", e3t="登録すると、テストのページに Play ストアへのリンクが表示されます。",
   att="すでに Yop2D（itch.io または GitHub 版）を使っていますか？", att1="Android が Play ストア版を上からインストールできないことがあります。古いバージョンをアンインストールする前に、", att2="プロジェクトを .zip で書き出してください", att3="（ホーム画面の「書き出し」ボタン）。アンインストールすると消えてしまうからです。そのあと Play ストア版に読み込みます。",
   attente="お願いしたいこと", a1="Yop2D を 14 日以上インストールしたままにする。", a2="実際に使う：サンプルゲームを開いて、少し変えて、小さなゲームを作る。", a3="バグやアイデアを {discord} や {telegram} で知らせる。",
   fin="登録リンクでエラーが出たときは、少し時間をおいてもう一度お試しください。ご協力ありがとうございます！",
   desc="Android 向けの無料・コード不要の 2D ゲームエンジン Yop2D を Google Play へ：2 分でクローズドテストに参加できます。",
   pied="Yop2D、Android 向けの無料・コード不要の 2D ゲームエンジン", site="公式サイト"),
}
ORDRE = ["fr", "en", "es", "de", "it", "pt", "ru", "zh", "ja"]


def e(s):
    return html.escape(s, quote=False)


def section(l, t):
    a3 = e(t["a3"]).replace("{discord}", f'<a href="{DISCORD}">Discord</a>').replace("{telegram}", f'<a href="{TELEGRAM}">Telegram</a>')
    return f"""<section class="lang" lang="{l}" id="{l}">
<h2 class="titre-langue">{e(t["titre"])}</h2>
<p>{e(t["intro"])}</p>

<h2>{e(t["comment"])}</h2>

<div class="etape"><div class="num">1</div><div>
<strong>{e(t["e1"])}</strong> {e(t["e1t"])}<br>
<a class="btn" href="{GROUPE}">{e(t["b1"])}</a>
</div></div>

<div class="etape"><div class="num">2</div><div>
<strong>{e(t["e2"])}</strong>{e(t["e2t"])}<br>
<a class="btn" href="{TEST}">{e(t["b2"])}</a>
</div></div>

<div class="etape"><div class="num">3</div><div>
<strong>{e(t["e3"])}</strong> {e(t["e3t"])}
</div></div>

<p class="attention"><strong>{e(t["att"])}</strong> {e(t["att1"])} <strong>{e(t["att2"])}</strong> {e(t["att3"])}</p>

<h2>{e(t["attente"])}</h2>
<ul>
<li>{e(t["a1"])}</li>
<li>{e(t["a2"])}</li>
<li>{a3}</li>
</ul>
<p>{e(t["fin"])}</p>
<p class="pied">{e(t["pied"])} · <a href="index.html">{e(t["site"])}</a></p>
</section>"""


def main():
    options = "\n".join(f'<option value="{l}">{T[l]["nom"]}</option>' for l in ORDRE)
    sections = "\n\n".join(section(l, T[l]) for l in ORDRE)
    textes = {l: {"titre": T[l]["titre"], "sous": T[l]["sous"]} for l in ORDRE}
    import json
    page = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Become a Yop2D tester | Devenir testeur | Стань тестировщиком | 成为测试者</title>
<meta name="description" content="{html.escape(T["en"]["desc"])}">
<link rel="canonical" href="https://zinzin66.github.io/Yop2d-web/testeur.html">
<style>
/* Couleurs du moteur (Palette.java) */
:root {{ --background: #1A1F26; --entete: #242A33; --card: #252B33; --bordure: #3A4048; --fond-sombre: #161A20; --text: #ECEEF0; --text-dim: #9AA0A8; --teal: #5DCAA5; --ambre: #FAC775; }}
* {{ box-sizing: border-box; }}
body {{ font-family: system-ui, -apple-system, sans-serif; line-height: 1.7; color: var(--text); background: var(--background); margin: 0; }}
header {{ background: var(--entete); border-bottom: 1px solid var(--bordure); padding: 2rem 1rem; text-align: center; }}
header a {{ color: var(--teal); }}
header h1 {{ font-size: 1.8rem; margin: 0.5rem 0; color: white; }}
header p {{ margin: 0; color: var(--text-dim); }}
.barre {{ display: flex; justify-content: space-between; align-items: center; max-width: 820px; margin: 0 auto; gap: 1rem; }}
select {{ background: var(--card); color: var(--text); border: 1px solid var(--bordure); border-radius: 6px; padding: 0.3rem 0.4rem; font-size: 0.95rem; }}
main {{ max-width: 820px; margin: 0 auto; padding: 1.5rem 1rem 2rem; }}
h2 {{ color: var(--ambre); border-bottom: 1px solid var(--bordure); padding-bottom: 0.4rem; margin-top: 2rem; font-size: 1.3rem; }}
a {{ color: var(--teal); }}
strong {{ color: white; }}
section.lang {{ background: var(--card); border: 1px solid var(--bordure); padding: 1rem 1.25rem; border-radius: 10px; margin-bottom: 2rem; }}
.etape {{ display: flex; gap: 1rem; align-items: flex-start; margin: 1.25rem 0; }}
.num {{ flex: 0 0 2.2rem; height: 2.2rem; border-radius: 50%; background: var(--teal); color: var(--fond-sombre); font-weight: bold; display: flex; align-items: center; justify-content: center; }}
.btn {{ display: inline-block; color: var(--fond-sombre); background: var(--ambre); padding: 0.7rem 1.4rem; border-radius: 50px; text-decoration: none; font-weight: bold; margin-top: 0.4rem; }}
.attention {{ background: var(--fond-sombre); border-left: 4px solid var(--ambre); padding: 0.75rem 1rem; border-radius: 6px; }}
.pied {{ color: var(--text-dim); font-size: 0.9rem; text-align: center; margin-top: 2rem; }}
/* Quand le script choisit une langue, les autres sont cachées et le titre de la section fait doublon */
body.une-langue section.lang {{ display: none; }}
body.une-langue section.lang.active {{ display: block; }}
body.une-langue .titre-langue {{ display: none; }}
@media (max-width: 600px) {{ header h1 {{ font-size: 1.4rem; }} }}
</style>
</head>
<body>
<header>
<div class="barre"><a href="index.html">← Yop2D</a>
<select id="choix-langue" aria-label="Language" onchange="choisir(this.value, true)">
{options}
</select></div>
<h1 id="titre">{e(T["en"]["titre"])}</h1>
<p id="sous">{e(T["en"]["sous"])}</p>
</header>
<main>

{sections}

</main>
<script>
const TEXTES = {json.dumps(textes, ensure_ascii=False)};
function choisir(l, memoriser) {{
  if (!TEXTES[l]) l = "en";
  document.body.classList.add("une-langue");
  document.querySelectorAll("section.lang").forEach(s => s.classList.toggle("active", s.id === l));
  document.documentElement.lang = l;
  document.getElementById("titre").textContent = TEXTES[l].titre;
  document.getElementById("sous").textContent = TEXTES[l].sous;
  document.title = TEXTES[l].titre + " | Yop2D";
  document.getElementById("choix-langue").value = l;
  if (memoriser) {{ try {{ localStorage.setItem("yop2d-langue", l); }} catch (e) {{}} }}
}}
(function () {{
  let l = new URLSearchParams(location.search).get("lang");
  const ancres = {{ "#english": "en", "#espanol": "es", "#portugues": "pt" }};  // anciennes adresses
  if (!l && location.hash) l = ancres[location.hash] || (location.hash.length === 3 ? location.hash.slice(1) : null);
  if (!l) {{ try {{ l = localStorage.getItem("yop2d-langue"); }} catch (e) {{}} }}
  if (!l) l = (navigator.language || "en").slice(0, 2);
  choisir(l.slice(0, 2).toLowerCase(), false);
}})();
</script>
</body>
</html>
"""
    open(os.path.join(RACINE, "testeur.html"), "w", encoding="utf-8").write(page)
    print("testeur.html : 9 langues")


if __name__ == "__main__":
    main()
