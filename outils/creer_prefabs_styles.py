#!/usr/bin/env python3
"""Fabrique les prefabs « boutons de styles » (dossiers prefabs/<id>/) : étoile qui tourne, ninja pixel à cheval, néon,
discret avec halo, verre, texte souligné, rond avec lecture.

Usage : python3 outils/creer_prefabs_styles.py <clone de zinzin66/yop2d-moteur> [boutons|interface]
(« boutons » = les 7 boutons ci-dessus, par défaut ; « interface » = 2e lot : interrupteur ON/OFF, barre de vie animée,
score qui pop, fenêtre de pause. Ne relancer que le lot voulu : chaque lancement refait des identifiants neufs.)
(les images sont DESSINÉES ici, les sprites du ninja viennent de la bibliothèque du moteur (Superpowers / Pixel-boy, CC0),
les sons Yop2D et les polices (OFL) aussi). Ensuite : python3 outils/generer_prefabs.py (ou le robot GitHub le fait).
"""
import copy, json, math, os, shutil, sys, uuid
from PIL import Image, ImageDraw, ImageFilter, ImageChops

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PREFABS = os.path.join(RACINE, 'prefabs')
MOTEUR = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else '/home/user/yop2d-moteur'
BIB = os.path.join(MOTEUR, 'app/src/editeur/assets/bibliotheque')
LANGUES = ['fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja']
SS = 3   # sur-échantillonnage du dessin (bords lisses)


# ------------------------------------------------------------------ textes (9 langues)
PREFIXE = ["Bouton animé", "Animated button", "Botón animado", "Animierter Button", "Pulsante animato", "Botão animado",
           "Анимированная кнопка", "动画按钮", "アニメボタン"]
OUVRIR = ["Ouvre sa scène pour changer l'image, le texte, la police ou les nœuds.",
          "Open its scene to change the image, the text, the font or the nodes.",
          "Abre su escena para cambiar la imagen, el texto, la fuente o los nodos.",
          "Öffne seine Szene, um Bild, Text, Schrift oder Nodes zu ändern.",
          "Apri la sua scena per cambiare immagine, testo, font o nodi.",
          "Abra a cena dele para mudar a imagem, o texto, a fonte ou os nós.",
          "Открой её сцену, чтобы изменить картинку, текст, шрифт или узлы.",
          "打开它的场景即可修改图像、文字、字体或节点。",
          "シーンを開いて、画像・文字・フォント・ノードを変更できます。"]

TEXTES = {
    'bouton_etoile': (
        ["étoile qui tourne", "spinning star", "estrella giratoria", "drehender Stern", "stella che gira", "estrela giratória", "вращающаяся звезда", "旋转的星星", "回る星"],
        ["Bouton doré avec une étoile qui tourne sans arrêt. Au toucher : étincelles, petit saut et son.",
         "Golden button with a star that never stops spinning. On tap: sparks, a little bounce and a sound.",
         "Botón dorado con una estrella que gira sin parar. Al tocar: chispas, un saltito y un sonido.",
         "Goldener Button mit einem Stern, der sich ständig dreht. Beim Antippen: Funken, ein kleiner Hüpfer und ein Ton.",
         "Pulsante dorato con una stella che gira senza sosta. Al tocco: scintille, un saltello e un suono.",
         "Botão dourado com uma estrela que gira sem parar. Ao tocar: faíscas, um pulinho e um som.",
         "Золотая кнопка с постоянно вращающейся звездой. При нажатии: искры, небольшой прыжок и звук.",
         "带有不停旋转星星的金色按钮。点按时：火花、小跳动和音效。",
         "ずっと回り続ける星が付いた金色のボタン。タップすると火花・小さなジャンプ・効果音。"]),
    'bouton_ninja': (
        ["ninja qui marche dessus", "ninja walking on it", "ninja que camina encima", "Ninja läuft darauf", "ninja che ci cammina sopra", "ninja caminhando em cima", "ниндзя идёт по кнопке", "忍者在上面行走", "上を歩く忍者"],
        ["Bouton pixel art avec un petit ninja qui se promène sur le dessus, à cheval sur le bouton. Au toucher : poussière et son.",
         "Pixel-art button with a little ninja strolling along its top edge, overlapping the button. On tap: dust and a sound.",
         "Botón pixel art con un ninja paseando por su borde superior, sobresaliendo del botón. Al tocar: polvo y un sonido.",
         "Pixel-Art-Button mit einem kleinen Ninja, der über die Oberkante spaziert und über den Button hinausragt. Beim Antippen: Staub und ein Ton.",
         "Pulsante pixel art con un piccolo ninja che passeggia sul bordo superiore, a cavallo del pulsante. Al tocco: polvere e un suono.",
         "Botão pixel art com um ninja passeando pela borda de cima, sobrepondo o botão. Ao tocar: poeira e um som.",
         "Пиксельная кнопка с маленьким ниндзя, который прогуливается по её верхнему краю. При нажатии: пыль и звук.",
         "像素风按钮，一个小忍者在按钮上沿散步，探出按钮之外。点按时：尘土和音效。",
         "ボタンの上をふちに沿って歩く小さな忍者が付いたドット絵ボタン。タップすると砂ぼこりと効果音。"]),
    'bouton_neon': (
        ["néon qui pulse", "pulsing neon", "neón que pulsa", "pulsierendes Neon", "neon che pulsa", "neon pulsante", "пульсирующий неон", "脉动霓虹", "脈打つネオン"],
        ["Bouton sombre au contour néon qui pulse doucement. Au toucher : flash lumineux, étincelles et son.",
         "Dark button with a softly pulsing neon outline. On tap: light flash, sparks and a sound.",
         "Botón oscuro con un contorno de neón que pulsa suavemente. Al tocar: destello, chispas y un sonido.",
         "Dunkler Button mit sanft pulsierendem Neonrand. Beim Antippen: Lichtblitz, Funken und ein Ton.",
         "Pulsante scuro con contorno neon che pulsa piano. Al tocco: lampo di luce, scintille e un suono.",
         "Botão escuro com contorno neon que pulsa suavemente. Ao tocar: clarão, faíscas e um som.",
         "Тёмная кнопка с мягко пульсирующим неоновым контуром. При нажатии: вспышка, искры и звук.",
         "深色按钮，霓虹轮廓轻柔脉动。点按时：闪光、火花和音效。",
         "ネオンの縁がやさしく脈打つ暗いボタン。タップすると閃光・火花・効果音。"]),
    'bouton_discret': (
        ["discret avec halo", "discreet with glow", "discreto con halo", "dezent mit Leuchten", "discreto con alone", "discreto com brilho", "сдержанная с сиянием", "低调光晕", "控えめな光"],
        ["Bouton simple et discret. Au survol il s'éclaire d'un halo bleu ; au toucher, petit saut et ondes.",
         "Plain, discreet button. On hover it lights up with a blue glow; on tap, a small bounce and ripples.",
         "Botón sencillo y discreto. Al pasar el dedo se ilumina con un halo azul; al tocar, un saltito y ondas.",
         "Schlichter, dezenter Button. Beim Überfahren leuchtet er blau auf; beim Antippen kleiner Hüpfer und Wellen.",
         "Pulsante semplice e discreto. Al passaggio si illumina con un alone blu; al tocco, un saltello e onde.",
         "Botão simples e discreto. Ao passar o dedo acende com um brilho azul; ao tocar, um pulinho e ondas.",
         "Простая сдержанная кнопка. При наведении загорается синим сиянием; при нажатии: небольшой прыжок и волны.",
         "简洁低调的按钮。悬停时亮起蓝色光晕；点按时轻轻跳动并泛起波纹。",
         "シンプルで控えめなボタン。ホバーすると青く光り、タップすると小さく跳ねて波紋が広がります。"]),
    'bouton_verre': (
        ["verre et reflet", "glass and shine", "cristal y reflejo", "Glas und Glanz", "vetro e riflesso", "vidro e reflexo", "стекло и блик", "玻璃与反光", "ガラスの輝き"],
        ["Bouton de verre brillant. Au survol, un reflet de lumière le traverse ; au toucher, étincelles et son.",
         "Glossy glass button. On hover a streak of light sweeps across it; on tap, sparks and a sound.",
         "Botón de cristal brillante. Al pasar el dedo un reflejo de luz lo recorre; al tocar, chispas y un sonido.",
         "Glänzender Glas-Button. Beim Überfahren streift ein Lichtreflex darüber; beim Antippen Funken und ein Ton.",
         "Pulsante di vetro lucido. Al passaggio un riflesso di luce lo attraversa; al tocco, scintille e un suono.",
         "Botão de vidro brilhante. Ao passar o dedo um reflexo de luz o atravessa; ao tocar, faíscas e um som.",
         "Глянцевая стеклянная кнопка. При наведении по ней пробегает блик; при нажатии: искры и звук.",
         "光泽玻璃按钮。悬停时一道光掠过；点按时：火花和音效。",
         "つやのあるガラス風ボタン。ホバーすると光が横切り、タップすると火花と効果音。"]),
    'bouton_ligne': (
        ["texte souligné", "underlined text", "texto subrayado", "unterstrichener Text", "testo sottolineato", "texto sublinhado", "текст с подчёркиванием", "下划线文字", "下線テキスト"],
        ["Bouton minimaliste : juste du texte. Au survol, un trait se déploie dessous ; au toucher, une onde discrète.",
         "Minimalist button: just text. On hover a line unfolds beneath it; on tap, a discreet ripple.",
         "Botón minimalista: solo texto. Al pasar el dedo se despliega una línea debajo; al tocar, una onda discreta.",
         "Minimalistischer Button: nur Text. Beim Überfahren entfaltet sich eine Linie darunter; beim Antippen eine dezente Welle.",
         "Pulsante minimalista: solo testo. Al passaggio si apre una linea sotto; al tocco, un'onda discreta.",
         "Botão minimalista: só texto. Ao passar o dedo uma linha se abre embaixo; ao tocar, uma onda discreta.",
         "Минималистичная кнопка: только текст. При наведении под ним раскрывается линия; при нажатии: лёгкая волна.",
         "极简按钮：只有文字。悬停时下方展开一条线；点按时泛起轻微波纹。",
         "文字だけのミニマルなボタン。ホバーすると下に線が広がり、タップすると控えめな波紋が出ます。"]),
    'bouton_rond': (
        ["rond avec lecture ▶", "round play ▶", "redondo con ▶", "rund mit ▶", "tondo con ▶", "redondo com ▶", "круглая ▶", "圆形播放 ▶", "丸い再生 ▶"],
        ["Bouton rond avec un ▶ et des ondes qui rayonnent en continu. Au toucher : saut, confettis et son.",
         "Round button with a ▶ and ripples that radiate continuously. On tap: bounce, confetti and a sound.",
         "Botón redondo con ▶ y ondas que se expanden sin parar. Al tocar: salto, confeti y un sonido.",
         "Runder Button mit ▶ und ständig ausstrahlenden Wellen. Beim Antippen: Hüpfer, Konfetti und ein Ton.",
         "Pulsante tondo con ▶ e onde che si irradiano di continuo. Al tocco: salto, coriandoli e un suono.",
         "Botão redondo com ▶ e ondas que se espalham sem parar. Ao tocar: pulo, confete e um som.",
         "Круглая кнопка с ▶ и непрерывно расходящимися волнами. При нажатии: прыжок, конфетти и звук.",
         "圆形按钮，带▶和不断扩散的波纹。点按时：跳动、彩纸和音效。",
         "▶と、広がり続ける波紋が付いた丸いボタン。タップするとジャンプ・紙吹雪・効果音。"]),
}

POLICES = {'Fredoka': 'OFL_fredoka.txt', 'PressStart2P': 'OFL_pressstart2p.txt', 'Orbitron': 'OFL_orbitron.txt',
           'LilitaOne': 'OFL_lilitaone.txt'}


# ------------------------------------------------------------------ dessin
def argb(h, a=255):
    h = h.lstrip('#')
    v = (a << 24) | int(h, 16)
    return v - (1 << 32) if v >= (1 << 31) else v


def rgb(h, a=255):
    h = h.lstrip('#')
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def degrade(w, h, haut, bas):
    """Dégradé vertical."""
    im = Image.new('RGBA', (w, h))
    px = im.load()
    c1, c2 = rgb(haut), rgb(bas)
    for y in range(h):
        t = y / max(1, h - 1)
        c = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(4))
        for x in range(w):
            px[x, y] = c
    return im


def masque_arrondi(w, h, rayon, marge=0):
    m = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle((marge * SS, marge * SS, (w - marge) * SS - 1, (h - marge) * SS - 1),
                                        radius=rayon * SS, fill=255)
    return m.resize((w, h), Image.LANCZOS)


def etoile_points(cx, cy, r1, r2, angle, branches=5):
    pts = []
    for i in range(branches * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(angle - 90 + i * 180 / branches)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def poly_lisse(im, pts, remplissage=None, contour=None, ep=0):
    """Polygone dessiné avec sur-échantillonnage sur une image RGBA (collée par-dessus)."""
    w, h = im.size
    calque = Image.new('RGBA', (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    p = [(x * SS, y * SS) for x, y in pts]
    if remplissage:
        d.polygon(p, fill=remplissage)
    if contour and ep:
        d.line(p + [p[0]], fill=contour, width=int(ep * SS), joint='curve')
    im.alpha_composite(calque.resize((w, h), Image.LANCZOS))


def lueur(im, couleur, flou, force=1.0):
    """Halo : une copie floue des pixels opaques, teintée."""
    a = im.split()[3].filter(ImageFilter.GaussianBlur(flou))
    a = a.point(lambda v: min(255, int(v * force)))
    g = Image.new('RGBA', im.size, couleur)
    g.putalpha(a)
    return g


def sauver(im, chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    im.save(chemin, 'PNG', optimize=True)


# ------------------------------------------------------------------ chaque prefab : images
def fond_pilule(w, h, haut, bas, bord1, bord2, ep=8):
    """Bouton en pilule : dégradé + bord dégradé + reflet en haut."""
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    r = h // 2
    contour = degrade(w, h, bord1, bord2)
    contour.putalpha(masque_arrondi(w, h, r))
    im.alpha_composite(contour)
    interieur = degrade(w, h, haut, bas)
    interieur.putalpha(masque_arrondi(w, h, r - ep, ep))
    im.alpha_composite(interieur)
    reflet = Image.new('RGBA', (w, h), (255, 255, 255, 0))
    m = Image.new('L', (w * SS, h * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle((ep * 3 * SS, ep * SS * 1.3, (w - ep * 3) * SS, (h * 0.46) * SS),
                                        radius=(h * 0.2) * SS, fill=70)
    reflet.putalpha(ImageChops.multiply(m.resize((w, h), Image.LANCZOS), masque_arrondi(w, h, r - ep, ep)))
    im.alpha_composite(reflet)
    return im


def images_etoile(dossier):
    W, H = 880, 260
    base = fond_pilule(W, H, '#6A2FB5', '#2A1060', '#FFE27A', '#FF9F1C')
    noms = []
    for k in range(12):                        # 5 branches : 72° / 12 images = 6° par image (boucle sans saut)
        im = base.copy()
        cx, cy = 150, H // 2
        halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        poly_lisse(halo, etoile_points(cx, cy, 96, 42, k * 6), (255, 200, 60, 255))
        im.alpha_composite(lueur(halo, (255, 190, 40, 255), 14, 1.1))
        poly_lisse(im, etoile_points(cx, cy, 84, 36, k * 6), (255, 213, 74, 255), (255, 140, 20, 255), 7)
        poly_lisse(im, etoile_points(cx, cy, 52, 22, k * 6), (255, 240, 160, 255))
        n = f'bouton_etoile_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_neon(dossier):
    W, H = 960, 320
    noms = []
    for k in range(8):
        t = 0.5 + 0.5 * math.sin(2 * math.pi * k / 8)      # 0..1 : intensité du halo
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        fond = degrade(W, H, '#10172B', '#070B16')
        fond.putalpha(masque_arrondi(W, H, 40, 52))
        im.alpha_composite(fond)
        trait = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        m = Image.new('L', (W * SS, H * SS), 0)
        d = ImageDraw.Draw(m)
        d.rounded_rectangle((52 * SS, 52 * SS, (W - 52) * SS, (H - 52) * SS), radius=40 * SS, outline=255, width=7 * SS)
        trait.putalpha(m.resize((W, H), Image.LANCZOS))
        couleur = Image.new('RGBA', (W, H), rgb('#46E6FF'))
        couleur.putalpha(trait.split()[3])
        im.alpha_composite(lueur(couleur, rgb('#2AA9FF')[:3] + (255,), 8 + 12 * t, 0.7 + 1.1 * t))
        im.alpha_composite(lueur(couleur, (120, 240, 255, 255), 4, 0.9))
        im.alpha_composite(couleur)
        n = f'bouton_neon_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_discret(dossier):
    W, H = 840, 220
    noms = []
    for k, (bord, haut, bas) in enumerate((('#46506A', '#262E40', '#1A2130'), ('#4CC9F0', '#2C3850', '#1D2638'))):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        contour = Image.new('RGBA', (W, H), rgb(bord))
        contour.putalpha(masque_arrondi(W, H, 36))
        im.alpha_composite(contour)
        fond = degrade(W, H, haut, bas)
        fond.putalpha(masque_arrondi(W, H, 34, 4))
        im.alpha_composite(fond)
        n = f'bouton_discret_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_verre(dossier):
    W, H = 880, 260
    noms = []
    for k in range(10):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        contour = Image.new('RGBA', (W, H), (200, 235, 255, 255))
        contour.putalpha(masque_arrondi(W, H, 70))
        im.alpha_composite(contour)
        fond = degrade(W, H, '#3FA7F0', '#1457B8')
        fond.putalpha(masque_arrondi(W, H, 64, 6))
        im.alpha_composite(fond)
        # reflet fixe en haut
        r = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        m = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(m).rounded_rectangle((26 * SS, 14 * SS, (W - 26) * SS, (H * 0.48) * SS), radius=50 * SS, fill=95)
        r.putalpha(m.resize((W, H), Image.LANCZOS))
        im.alpha_composite(r)
        # bande de lumière qui traverse (k = 1..8) : rien à la 1re et à la dernière image
        if 0 < k < 9:
            t = (k - 1) / 7
            x0 = -140 + t * (W + 280)
            band = Image.new('L', (W * SS, H * SS), 0)
            ImageDraw.Draw(band).polygon([((x0 + 40) * SS, 0), ((x0 + 140) * SS, 0), ((x0 + 60) * SS, H * SS), ((x0 - 40) * SS, H * SS)], fill=150)
            band = band.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(5))
            band = ImageChops.multiply(band, masque_arrondi(W, H, 64, 6))
            lum = Image.new('RGBA', (W, H), (255, 255, 255, 255))
            lum.putalpha(band)
            im.alpha_composite(lum)
        n = f'bouton_verre_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_ligne(dossier):
    W, H = 720, 180
    noms = []
    for k in range(8):
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        longueur = 14 + (W - 120) * (k / 7)                 # 14 px (un point) -> toute la largeur utile
        cx = W / 2
        m = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(m).rounded_rectangle(((cx - longueur / 2) * SS, 154 * SS, (cx + longueur / 2) * SS, 164 * SS), radius=5 * SS, fill=255)
        trait = Image.new('RGBA', (W, H), rgb('#4CC9F0'))
        trait.putalpha(m.resize((W, H), Image.LANCZOS))
        im.alpha_composite(trait)
        n = f'bouton_ligne_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_rond(dossier):
    W = 600
    noms = []
    for k in range(12):
        im = Image.new('RGBA', (W, W), (0, 0, 0, 0))
        c = W // 2
        for decal in (0.0, 0.5):                           # deux ondes décalées
            t = (k / 12 + decal) % 1.0
            r = 150 + t * 140
            m = Image.new('L', (W * SS, W * SS), 0)
            ImageDraw.Draw(m).ellipse(((c - r) * SS, (c - r) * SS, (c + r) * SS, (c + r) * SS), outline=255, width=int(8 * SS * (1 - t * 0.6)))
            onde = Image.new('RGBA', (W, W), rgb('#2DE3A8'))
            onde.putalpha(m.resize((W, W), Image.LANCZOS).point(lambda v, a=int(255 * (1 - t) ** 1.3): v * a // 255))
            im.alpha_composite(onde)
        disque = degrade(W, W, '#3BF2B6', '#0F9E7A')
        m = Image.new('L', (W * SS, W * SS), 0)
        ImageDraw.Draw(m).ellipse(((c - 150) * SS, (c - 150) * SS, (c + 150) * SS, (c + 150) * SS), fill=255)
        disque.putalpha(m.resize((W, W), Image.LANCZOS))
        im.alpha_composite(disque)
        poly_lisse(im, [(c - 38, c - 62), (c - 38, c + 62), (c + 70, c)], (255, 255, 255, 255))
        n = f'bouton_rond_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def images_ninja(dossier):
    """Bouton pixel art (cases de 8 px) + petit ninja (Superpowers, Pixel-boy, CC0) qui marche sur le dessus."""
    W, H, C = 440, 240, 8
    sprites = {}
    for sens in ('droite', 'gauche'):
        for i in range(1, 5):
            s = Image.open(os.path.join(BIB, f'Images/Ninja/Personnages/ninja1_{sens}_{i}.png')).convert('RGBA')
            sprites[(sens, i)] = s.resize((s.width * C, s.height * C), Image.NEAREST)
    bas = max(s.getbbox()[3] for s in sprites.values())      # ligne des pieds dans le sprite agrandi
    haut_bouton = 112
    base = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    cases = lambda x0, y0, x1, y1, col: d.rectangle((x0 * C, y0 * C, x1 * C - 1, y1 * C - 1), fill=col)
    cx0, cy0, cx1, cy1 = 0, haut_bouton // C, W // C, H // C
    cases(cx0 + 1, cy0, cx1 - 1, cy1, rgb('#0E1230'))                  # contour sombre
    cases(cx0, cy0 + 1, cx1, cy1 - 1, rgb('#0E1230'))
    cases(cx0 + 1, cy0 + 1, cx1 - 1, cy1 - 1, rgb('#3E5BD6'))          # corps bleu
    cases(cx0 + 1, cy0 + 1, cx1 - 1, cy0 + 2, rgb('#7C98FF'))          # reflet du haut
    cases(cx0 + 1, cy0 + 1, cx0 + 2, cy1 - 1, rgb('#6783F0'))
    cases(cx0 + 1, cy1 - 3, cx1 - 1, cy1 - 1, rgb('#2A3FA0'))          # ombre du bas
    cases(cx1 - 2, cy0 + 1, cx1 - 1, cy1 - 1, rgb('#2A3FA0'))
    pied = haut_bouton + 6                                              # les pieds s'enfoncent un peu dans le bouton
    noms = []
    positions = [(('droite', (i % 4) + 1), 24 + i * 30) for i in range(10)] + \
                [(('gauche', (i % 4) + 1), 24 + (9 - i) * 30 + 0) for i in range(10)]
    for k, ((sens, f), x) in enumerate(positions):
        im = base.copy()
        s = sprites[(sens, f)]
        im.alpha_composite(s, (x, pied - bas))
        # le devant du bouton passe devant les pieds
        n = f'bouton_ninja_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


# ------------------------------------------------------------------ projet (scène, objets, nœuds)
GAB = json.load(open(os.path.join(PREFABS, 'bouton_bleu/projet_sauvegarde.json'), encoding='utf-8'))[0]
GAB_BOUTON = [o for o in GAB['objets'] if o['type'] != 'texte'][0]
GAB_TEXTE = [o for o in GAB['objets'] if o['type'] == 'texte'][0]


def uid():
    return str(uuid.uuid4())


def objet_bouton(nom, image, w, h):
    o = copy.deepcopy(GAB_BOUTON)
    o.update({'id': uid(), 'nom': nom, 'cheminImage': image, 'largeur': float(w), 'hauteur': float(h), 'x': 0.0, 'y': 0.0,
              'zOrder': 0})
    return o


def objet_texte(nom, parent, texte, police, taille, couleur, w, h, x, y):
    o = copy.deepcopy(GAB_TEXTE)
    o.update({'id': uid(), 'nom': nom, 'parentId': parent['id'], 'contenuTexte': texte,
              'cheminPolice': f'assets_ludexa/Fonts/{police}.ttf', 'tailleFonte': float(taille), 'couleur': argb(couleur),
              'largeur': float(w), 'hauteur': float(h), 'x': float(x), 'y': float(y), 'zOrder': 1})
    return o


class Logique:
    def __init__(self):
        self.noeuds, self.liens, self.ligne = [], [], 0

    def evenement(self, classe, cible=None):
        n = {'classeType': 'com.ludexa.moteur.' + classe, 'id': uid(), 'parametres': {}, 'portsEntree': [],
             'x': 340.0, 'y': 120.0 + self.ligne * 330.0}
        if cible:
            n['cibleNom'] = cible
        self.noeuds.append(n)
        self.ligne += 1
        return n, 'Suivant'

    def action(self, depuis, cle, parametres, cible, variable=None):
        """depuis = (nœud, port) ou (nœud, port, rang du port) ; variable = variable de l'objet visé (nœuds variables)."""
        dep, port = depuis[0], depuis[1]
        rang = depuis[2] if len(depuis) > 2 else 0
        n = {'classeType': 'com.ludexa.moteur.NoeudGenerique', 'cleNoeud': cle, 'id': uid(), 'cibleNom': cible,
             'parametres': {f'{cle}.{k}': str(v) for k, v in parametres.items()}, 'portsEntree': [],
             'x': dep['x'] + 330.0, 'y': dep['y'] + rang * 260.0}
        if variable:
            n['cibleVariableNom'] = variable
        self.noeuds.append(n)
        self.liens.append({'idArrivee': n['id'], 'idDepart': dep['id'], 'indexPortArrivee': 0, 'indexPortDepart': rang,
                           'portArrivee': 'port_entrer', 'portDepart': port})
        return n, 'port_suivant'

    def chaine(self, depuis, etapes, cible):
        for etape in etapes:
            cle, p = etape[0], etape[1]
            depuis = self.action(depuis, cle, p, cible, etape[2] if len(etape) > 2 else None)
        return depuis

    def json(self):
        return {'liens': self.liens, 'noeuds': self.noeuds}


def son(nom, vol=80):
    return ('jouer_son', {'fichier': f'assets_ludexa/Sons/{nom}.ogg', 'volume': vol})


def particules(modele, quantite=0, taille=1):
    return ('effet_particules', {'modele': modele, 'quantite': quantite, 'couleur': '', 'taille': taille, 'image': ''})


def ecrire_prefab(id_, objets, logique, animations, polices, sons, lignes_anim=None, prefixe=None):
    dossier = os.path.join(PREFABS, id_)
    # on garde les images fabriquées, on refait tout le reste
    for sous in ('logique', 'assets_ludexa/Fonts', 'assets_ludexa/Sons', 'assets_ludexa/Textes'):
        shutil.rmtree(os.path.join(dossier, sous), ignore_errors=True)
    scene = copy.deepcopy(GAB)
    scene.update({'id': uid(), 'nom': 'SceneDepart', 'objets': objets, 'noeudsLogique': [], 'compteurZOrderLocal': len(objets)})
    os.makedirs(dossier, exist_ok=True)
    json.dump([scene], open(os.path.join(dossier, 'projet_sauvegarde.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    os.makedirs(os.path.join(dossier, 'logique'), exist_ok=True)
    json.dump(logique.json(), open(os.path.join(dossier, 'logique', scene['id'] + '.json'), 'w', encoding='utf-8'), indent=2, ensure_ascii=False)
    open(os.path.join(dossier, 'logique/blueprint.json'), 'w').write('{}')
    os.makedirs(os.path.join(dossier, 'assets_ludexa/Textes'), exist_ok=True)
    with open(os.path.join(dossier, 'assets_ludexa/Textes/animations.txt'), 'w', encoding='utf-8') as f:
        f.write('// Fichier généré automatiquement pour les animations (Nom=image1.png,image2.png)\n')
        for nom, images in animations.items():
            f.write(nom + '=' + ','.join(images) + '\n')
    for p in polices:
        os.makedirs(os.path.join(dossier, 'assets_ludexa/Fonts/Licences'), exist_ok=True)
        shutil.copy(os.path.join(BIB, 'Fonts', p + '.ttf'), os.path.join(dossier, 'assets_ludexa/Fonts', p + '.ttf'))
        shutil.copy(os.path.join(BIB, 'Fonts/Licences', POLICES[p]), os.path.join(dossier, 'assets_ludexa/Fonts/Licences', POLICES[p]))
    for s in sons:
        os.makedirs(os.path.join(dossier, 'assets_ludexa/Sons'), exist_ok=True)
        shutil.copy(os.path.join(BIB, 'Sons/Yop2D', s + '.ogg'), os.path.join(dossier, 'assets_ludexa/Sons', s + '.ogg'))
    for nom in ('reglages.json', 'variables_globales.json'):
        shutil.copy(os.path.join(PREFABS, 'bouton_bleu', nom), os.path.join(dossier, nom))
    nom_p, desc_p = TEXTES[id_]
    prefixe = prefixe or PREFIXE
    infos = {'nom': {l: f'{prefixe[i]} – {nom_p[i]}' for i, l in enumerate(LANGUES)},
             'description': {l: f'{desc_p[i]} {OUVRIR[i]}' for i, l in enumerate(LANGUES)},
             'licence': 'CC0', 'auteur': 'Yop2D'}
    json.dump(infos, open(os.path.join(dossier, 'prefab.json'), 'w', encoding='utf-8'), indent=1, ensure_ascii=False)


def vignette(id_, nom_image):
    """Vignette 300 x 300 : l'image choisie sur un fond sombre."""
    src = os.path.join(PREFABS, id_, nom_image)
    im = Image.open(src).convert('RGBA')
    fond = degrade(300, 300, '#222838', '#141824')
    e = min(264 / im.width, 264 / im.height)
    im = im.resize((max(1, int(im.width * e)), max(1, int(im.height * e))), Image.LANCZOS)
    fond.alpha_composite(im, ((300 - im.width) // 2, (300 - im.height) // 2))
    fond.convert('RGB').save(os.path.join(PREFABS, id_, 'vignette.png'), 'PNG', optimize=True)


# ------------------------------------------------------------------ les 7 prefabs
def construire():
    # 1. étoile qui tourne
    i = 'bouton_etoile'
    imgs = images_etoile(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 440, 130)
    t = objet_texte('txt_' + i, b, 'Play', 'Fredoka', 60, '#FFFFFF', 270, 90, 150, 20)
    L = Logique()
    e = L.evenement('NoeudEventStart')
    L.action(e, 'jouer_animation', {'animation': i + '_tourne', 'vitesse': 12, 'boucle': 'true'}, i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [particules('Etincelles'), ('sautiller', {'intensite': 8, 'duree': 300, 'infini': 'false'}), son('power_up')], i)
    ecrire_prefab(i, [b, t], L, {i + '_tourne': imgs}, ['Fredoka'], ['power_up'])
    vignette(i, 'assets_ludexa/Images/bouton_etoile_3.png')

    # 2. ninja pixel à cheval
    i = 'bouton_ninja'
    imgs = images_ninja(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 440, 240)
    t = objet_texte('txt_' + i, b, 'Play', 'PressStart2P', 34, '#FFFFFF', 360, 60, 40, 146)
    L = Logique()
    e = L.evenement('NoeudEventStart')
    L.action(e, 'jouer_animation', {'animation': i + '_marche', 'vitesse': 9, 'boucle': 'true'}, i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [particules('Poussiere'), ('sautiller', {'intensite': 6, 'duree': 250, 'infini': 'false'}), son('ressort', 70)], i)
    ecrire_prefab(i, [b, t], L, {i + '_marche': imgs}, ['PressStart2P'], ['ressort'])
    vignette(i, 'assets_ludexa/Images/bouton_ninja_4.png')

    # 3. néon qui pulse
    i = 'bouton_neon'
    imgs = images_neon(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 480, 160)
    t = objet_texte('txt_' + i, b, 'PLAY', 'Orbitron', 44, '#C8F6FF', 360, 70, 60, 45)
    L = Logique()
    e = L.evenement('NoeudEventStart')
    L.action(e, 'jouer_animation', {'animation': i + '_pulse', 'vitesse': 8, 'boucle': 'true'}, i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [('surbrillance', {'etat': 'Activer', 'couleur': '#46E6FF', 'taille': 26}), particules('Etincelles'), son('teleporte', 70),
                 ('attendre', {'duree': 0.3}), ('surbrillance', {'etat': 'Désactiver', 'couleur': '#46E6FF', 'taille': 26})], i)
    ecrire_prefab(i, [b, t], L, {i + '_pulse': imgs}, ['Orbitron'], ['teleporte'])
    vignette(i, 'assets_ludexa/Images/bouton_neon_5.png')

    # 4. discret avec halo
    i = 'bouton_discret'
    imgs = images_discret(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 420, 110)
    t = objet_texte('txt_' + i, b, 'Play', 'Fredoka', 44, '#E6EDF7', 340, 70, 40, 20)
    L = Logique()
    e = L.evenement('NoeudEventSurvolObjet', i)
    L.chaine(e, [('changer_image', {'image': imgs[1]}), ('surbrillance', {'etat': 'Activer', 'couleur': '#4CC9F0', 'taille': 14})], i)
    e = L.evenement('NoeudEventFinSurvol', i)
    L.chaine(e, [('changer_image', {'image': imgs[0]}), ('surbrillance', {'etat': 'Désactiver', 'couleur': '#4CC9F0', 'taille': 14})], i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [('sautiller', {'intensite': 4, 'duree': 150, 'infini': 'false'}), particules('OndeChoc'), son('pop', 70)], i)
    ecrire_prefab(i, [b, t], L, {}, ['Fredoka'], ['pop'])
    vignette(i, 'assets_ludexa/Images/bouton_discret_2.png')

    # 5. verre et reflet
    i = 'bouton_verre'
    imgs = images_verre(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 440, 130)
    t = objet_texte('txt_' + i, b, 'Play', 'LilitaOne', 58, '#FFFFFF', 360, 90, 40, 20)
    L = Logique()
    e = L.evenement('NoeudEventSurvolObjet', i)
    L.action(e, 'jouer_animation', {'animation': i + '_reflet', 'vitesse': 18, 'boucle': 'false'}, i)
    e = L.evenement('NoeudEventFinSurvol', i)
    L.chaine(e, [('arreter_animation', {}), ('changer_image', {'image': imgs[0]})], i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [particules('Etincelles'), son('pop', 70)], i)
    ecrire_prefab(i, [b, t], L, {i + '_reflet': imgs[1:9]}, ['LilitaOne'], ['pop'])
    vignette(i, 'assets_ludexa/Images/bouton_verre_5.png')

    # 6. texte souligné
    i = 'bouton_ligne'
    imgs = images_ligne(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 360, 90)
    t = objet_texte('txt_' + i, b, 'Play', 'Fredoka', 52, '#E6EDF7', 340, 62, 10, 6)
    L = Logique()
    e = L.evenement('NoeudEventSurvolObjet', i)
    L.action(e, 'jouer_animation', {'animation': i + '_trait', 'vitesse': 14, 'boucle': 'false'}, i)
    e = L.evenement('NoeudEventFinSurvol', i)
    L.chaine(e, [('arreter_animation', {}), ('changer_image', {'image': imgs[0]})], i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [particules('OndeChoc'), son('pop', 60)], i)
    ecrire_prefab(i, [b, t], L, {i + '_trait': imgs}, ['Fredoka'], ['pop'])
    vignette(i, 'assets_ludexa/Images/bouton_ligne_8.png')

    # 7. rond avec lecture
    i = 'bouton_rond'
    imgs = images_rond(os.path.join(PREFABS, i))
    b = objet_bouton(i, imgs[0], 300, 300)
    L = Logique()
    e = L.evenement('NoeudEventStart')
    L.action(e, 'jouer_animation', {'animation': i + '_ondes', 'vitesse': 10, 'boucle': 'true'}, i)
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [('sautiller', {'intensite': 14, 'duree': 400, 'infini': 'false'}), particules('Confettis'), son('power_up')], i)
    ecrire_prefab(i, [b], L, {i + '_ondes': imgs}, [], ['power_up'])
    vignette(i, 'assets_ludexa/Images/bouton_rond_3.png')


# ------------------------------------------------------------------ 2e lot : éléments d'interface (4 prefabs)
PREFIXE_UI = ["Interface", "Interface", "Interfaz", "Oberfläche", "Interfaccia", "Interface", "Интерфейс", "界面", "インターフェース"]

TEXTES.update({
    'interrupteur': (
        ["interrupteur ON/OFF", "ON/OFF switch", "interruptor ON/OFF", "EIN/AUS-Schalter", "interruttore ON/OFF", "interruptor ON/OFF", "переключатель ВКЛ/ВЫКЛ", "开关 ON/OFF", "ON/OFFスイッチ"],
        ["Interrupteur à glissière : un toucher le passe de OFF (gris) à ON (vert) et inversement, avec une petite animation et un son. Il retient son état dans la variable « etat » (0 = éteint, 1 = allumé), idéal pour « Sons », « Musique » ou « Vibrations ».",
         "Slide switch: one tap flips it from OFF (grey) to ON (green) and back, with a small animation and a sound. It remembers its state in the variable \"etat\" (0 = off, 1 = on), perfect for \"Sounds\", \"Music\" or \"Vibration\".",
         "Interruptor deslizante: un toque lo pasa de OFF (gris) a ON (verde) y viceversa, con una pequeña animación y un sonido. Recuerda su estado en la variable «etat» (0 = apagado, 1 = encendido), ideal para «Sonidos», «Música» o «Vibración».",
         "Schiebeschalter: Ein Antippen schaltet von AUS (grau) auf EIN (grün) und zurück, mit kleiner Animation und Ton. Er merkt sich seinen Zustand in der Variable „etat“ (0 = aus, 1 = an), ideal für „Ton“, „Musik“ oder „Vibration“.",
         "Interruttore a scorrimento: un tocco lo porta da OFF (grigio) a ON (verde) e viceversa, con una piccola animazione e un suono. Ricorda il suo stato nella variabile «etat» (0 = spento, 1 = acceso), ideale per «Suoni», «Musica» o «Vibrazione».",
         "Interruptor deslizante: um toque o leva de OFF (cinza) para ON (verde) e vice-versa, com uma pequena animação e um som. Guarda o estado na variável «etat» (0 = desligado, 1 = ligado), ideal para «Sons», «Música» ou «Vibração».",
         "Ползунковый переключатель: одно нажатие переводит его из OFF (серый) в ON (зелёный) и обратно, с небольшой анимацией и звуком. Состояние хранится в переменной «etat» (0 = выкл, 1 = вкл) — удобно для «Звуков», «Музыки» или «Вибрации».",
         "滑动开关：点一下就在 OFF（灰色）和 ON（绿色）之间切换，带小动画和音效。状态保存在变量 “etat” 中（0 = 关，1 = 开），很适合“音效”“音乐”“震动”。",
         "スライド式のスイッチ。タップするとOFF（グレー）とON（緑）が切り替わり、小さなアニメと効果音が出ます。状態は変数「etat」（0 = オフ、1 = オン）に保存され、「効果音」「音楽」「バイブ」に最適です。"]),
    'barre_vie': (
        ["barre de vie animée", "animated health bar", "barra de vida animada", "animierte Lebensleiste", "barra della vita animata", "barra de vida animada", "анимированная полоска здоровья", "动画生命条", "アニメ付き体力バー"],
        ["Barre de vie brillante qui se vide en douceur : verte, puis orange, puis rouge qui clignote quand il reste peu de vie. Touche-la pour tester (-10 à chaque fois) ; à zéro, elle se remplit de nouveau. La vie est dans la variable « vie » (0 à 100).",
         "Glossy health bar that drains smoothly: green, then orange, then flashing red when little life is left. Tap it to test (-10 each time); at zero it refills. The life is stored in the variable \"vie\" (0 to 100).",
         "Barra de vida brillante que se vacía suavemente: verde, luego naranja y roja parpadeante cuando queda poca vida. Tócala para probar (-10 cada vez); al llegar a cero se rellena. La vida está en la variable «vie» (0 a 100).",
         "Glänzende Lebensleiste, die sich weich leert: grün, dann orange, dann blinkend rot bei wenig Leben. Zum Testen antippen (jedes Mal -10); bei null füllt sie sich wieder. Das Leben steht in der Variable „vie“ (0 bis 100).",
         "Barra della vita lucida che si svuota dolcemente: verde, poi arancione, poi rossa lampeggiante quando resta poca vita. Toccala per provare (-10 ogni volta); a zero si riempie di nuovo. La vita è nella variabile «vie» (da 0 a 100).",
         "Barra de vida brilhante que esvazia suavemente: verde, depois laranja e vermelha piscando quando resta pouca vida. Toque para testar (-10 a cada vez); ao chegar a zero ela enche de novo. A vida fica na variável «vie» (0 a 100).",
         "Глянцевая полоска здоровья, плавно уменьшающаяся: зелёная, затем оранжевая, затем мигающая красная при малом здоровье. Нажми для проверки (каждый раз −10); на нуле она наполняется снова. Здоровье хранится в переменной «vie» (0–100).",
         "有光泽的生命条，会平滑减少：绿色，然后橙色，生命很低时变成闪烁的红色。点一下试试（每次 -10）；归零后会重新充满。生命值保存在变量 “vie” 中（0 到 100）。",
         "つやのある体力バー。なめらかに減り、緑 → オレンジ → 残りわずかで赤く点滅します。タップで試せます（1回で -10）。ゼロになると満タンに戻ります。体力は変数「vie」（0〜100）に入っています。"]),
    'score_pop': (
        ["score qui « pop »", "popping score", "puntuación que salta", "hüpfender Punktestand", "punteggio che salta", "pontuação que pula", "подпрыгивающий счёт", "弹跳的分数", "はずむスコア"],
        ["Compteur de score avec une étoile. À chaque point gagné, le chiffre grossit un instant et lance des étincelles avec un son. Touche-le pour tester (+10) ; le score est dans la variable « score ».",
         "Score counter with a star. Each time you score, the number swells for a moment and throws sparks with a sound. Tap it to test (+10); the score is stored in the variable \"score\".",
         "Contador de puntos con una estrella. Cada vez que sumas, el número crece un instante y lanza chispas con un sonido. Tócalo para probar (+10); la puntuación está en la variable «score».",
         "Punktezähler mit Stern. Bei jedem Punkt wird die Zahl kurz größer und sprüht Funken mit einem Ton. Zum Testen antippen (+10); der Punktestand steht in der Variable „score“.",
         "Contatore di punti con una stella. A ogni punto il numero si ingrandisce un attimo e lancia scintille con un suono. Toccalo per provare (+10); il punteggio è nella variabile «score».",
         "Contador de pontos com uma estrela. A cada ponto o número cresce por um instante e solta faíscas com um som. Toque para testar (+10); a pontuação fica na variável «score».",
         "Счётчик очков со звездой. При каждом очке число на мгновение увеличивается и рассыпает искры со звуком. Нажми для проверки (+10); очки хранятся в переменной «score».",
         "带星星的得分计数器。每得一分，数字会短暂放大并迸出火花，伴有音效。点一下试试（+10）；分数保存在变量 “score” 中。",
         "星付きのスコア表示。得点のたびに数字が一瞬ふくらみ、火花と効果音が出ます。タップで試せます（+10）。スコアは変数「score」に入っています。"]),
    'fenetre_pause': (
        ["fenêtre de pause", "pause window", "ventana de pausa", "Pausenfenster", "finestra di pausa", "janela de pausa", "окно паузы", "暂停窗口", "ポーズ画面"],
        ["Bouton ⏸ qui met le jeu en pause et ouvre une fenêtre avec Reprendre, Recommencer et Quitter, sur un fond assombri. Le bouton retour du téléphone l'ouvre aussi. Les textes et les couleurs se changent dans la scène.",
         "A ⏸ button that pauses the game and opens a window with Resume, Restart and Quit over a dimmed background. The phone's back button opens it too. Texts and colours can be changed in the scene.",
         "Un botón ⏸ que pausa el juego y abre una ventana con Reanudar, Reiniciar y Salir sobre un fondo oscurecido. El botón atrás del teléfono también la abre. Los textos y colores se cambian en la escena.",
         "Ein ⏸-Button pausiert das Spiel und öffnet ein Fenster mit Fortsetzen, Neustart und Beenden auf abgedunkeltem Hintergrund. Die Zurück-Taste des Handys öffnet es ebenfalls. Texte und Farben lassen sich in der Szene ändern.",
         "Un pulsante ⏸ che mette in pausa il gioco e apre una finestra con Riprendi, Ricomincia ed Esci su sfondo oscurato. Anche il tasto indietro del telefono la apre. Testi e colori si cambiano nella scena.",
         "Um botão ⏸ que pausa o jogo e abre uma janela com Continuar, Reiniciar e Sair sobre um fundo escurecido. O botão voltar do celular também a abre. Textos e cores podem ser alterados na cena.",
         "Кнопка ⏸ ставит игру на паузу и открывает окно с пунктами «Продолжить», «Заново» и «Выйти» на затемнённом фоне. Его открывает и кнопка «Назад» телефона. Тексты и цвета меняются в сцене.",
         "⏸ 按钮会暂停游戏，并在变暗的背景上打开带有“继续”“重新开始”“退出”的窗口。手机的返回键也能打开它。文字和颜色可以在场景中修改。",
         "⏸ ボタンでゲームを一時停止し、暗くした背景の上に「再開」「やり直し」「終了」の画面を開きます。スマホの戻るボタンでも開きます。文字や色はシーンで変えられます。"]),
})


def melange(c1, c2, t):
    a, b = rgb(c1), rgb(c2)
    return '#%02X%02X%02X' % tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def pilule(w, h, haut, bas, bord1, bord2, ep=8):
    return fond_pilule(w, h, haut, bas, bord1, bord2, ep)


def disque(im, cx, cy, r, couleur):
    calque = Image.new('RGBA', (im.width * SS, im.height * SS), (0, 0, 0, 0))
    ImageDraw.Draw(calque).ellipse(((cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS), fill=couleur)
    im.alpha_composite(calque.resize(im.size, Image.LANCZOS))


def barres_arrondies(im, boites, rayon, couleur):
    calque = Image.new('RGBA', (im.width * SS, im.height * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    for x0, y0, x1, y1 in boites:
        d.rounded_rectangle((x0 * SS, y0 * SS, x1 * SS, y1 * SS), radius=rayon * SS, fill=couleur)
    im.alpha_composite(calque.resize(im.size, Image.LANCZOS))


def images_interrupteur(dossier):
    W, H = 440, 220
    noms = []
    for k in range(7):
        t = k / 6
        t = t * t * (3 - 2 * t)                           # départ et arrivée en douceur
        im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        piste = pilule(W, H, melange('#3C455E', '#35F0A8', t), melange('#262D42', '#12A06E', t),
                       melange('#58627F', '#C8FFE9', t), melange('#3A4258', '#47D9A0', t), 7)
        im.alpha_composite(piste)
        cx, cy, r = 110 + 220 * t, 110, 84
        ombre = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        disque(ombre, cx + 3, cy + 8, r, (0, 0, 0, 150))
        im.alpha_composite(ombre.filter(ImageFilter.GaussianBlur(7)))
        if t > 0:
            halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            disque(halo, cx, cy, r + 6, (120, 255, 200, 255))
            im.alpha_composite(lueur(halo, (60, 255, 180, 255), 12, 0.9 * t))
        bouton = degrade(W, H, '#FFFFFF', '#CBD3E6')
        masque = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(masque).ellipse(((cx - r) * SS, (cy - r) * SS, (cx + r) * SS, (cy + r) * SS), fill=255)
        bouton.putalpha(masque.resize((W, H), Image.LANCZOS))
        im.alpha_composite(bouton)
        # dans le bouton : un rond gris (OFF) qui s'efface, une coche verte (ON) qui apparaît
        marque = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        trace = Image.new('RGBA', (W * SS, H * SS), (0, 0, 0, 0))
        dt = ImageDraw.Draw(trace)
        coche = [(cx - 30, cy + 2), (cx - 9, cy + 24), (cx + 32, cy - 24)]
        dt.line([(x * SS, y * SS) for x, y in coche], fill=(24, 170, 118, int(255 * t)), width=13 * SS, joint='curve')
        for x, y in (coche[0], coche[2]):
            dt.ellipse(((x - 6.5) * SS, (y - 6.5) * SS, (x + 6.5) * SS, (y + 6.5) * SS), fill=(24, 170, 118, int(255 * t)))
        marque.alpha_composite(trace.resize((W, H), Image.LANCZOS))
        im.alpha_composite(marque)
        if t < 1:
            rond = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            disque(rond, cx, cy, 26, (120, 130, 155, int(255 * (1 - t))))
            disque(rond, cx, cy, 15, (232, 237, 248, int(255 * (1 - t))))
            im.alpha_composite(rond)
        n = f'interrupteur_{k + 1}.png'
        sauver(im, os.path.join(dossier, 'assets_ludexa/Images', n))
        noms.append('assets_ludexa/Images/' + n)
    return noms


def coeur_points(cx, cy, taille):
    pts = []
    for i in range(90):
        a = 2 * math.pi * i / 90
        x = 16 * math.sin(a) ** 3
        y = -(13 * math.cos(a) - 5 * math.cos(2 * a) - 2 * math.cos(3 * a) - math.cos(4 * a))
        pts.append((cx + x * taille, cy + y * taille))
    return pts


def images_barre_vie(dossier):
    noms = {}
    # le cadre (fond sombre + cœur)
    W, H = 1440, 168
    cadre = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bord = degrade(W, H, '#6B7596', '#3A4258')
    bord.putalpha(masque_arrondi(W, H, 84))
    cadre.alpha_composite(bord)
    fond = degrade(W, H, '#1B2133', '#0C101C')
    fond.putalpha(masque_arrondi(W, H, 78, 6))
    cadre.alpha_composite(fond)
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    poly_lisse(halo, coeur_points(84, 84, 3.1), (255, 90, 110, 255))
    cadre.alpha_composite(lueur(halo, (255, 60, 90, 255), 9, 0.9))
    poly_lisse(cadre, coeur_points(84, 84, 2.9), (255, 90, 110, 255), (255, 190, 200, 255), 4)
    poly_lisse(cadre, [(66, 66), (76, 58), (84, 64)], None, (255, 235, 238, 200), 5)
    sauver(cadre, os.path.join(dossier, 'assets_ludexa/Images/barre_vie_cadre.png'))
    noms['cadre'] = 'assets_ludexa/Images/barre_vie_cadre.png'
    # le remplissage dans 3 couleurs (même forme)
    W, H = 1200, 120
    for nom, haut, bas in (('vert', '#8CF5A8', '#1FB45F'), ('orange', '#FFD070', '#EE8610'), ('rouge', '#FF8C8C', '#D01B38')):
        im = degrade(W, H, haut, bas)
        im.putalpha(masque_arrondi(W, H, 60))
        reflet = Image.new('RGBA', (W, H), (255, 255, 255, 0))
        m = Image.new('L', (W * SS, H * SS), 0)
        ImageDraw.Draw(m).rounded_rectangle((24 * SS, 10 * SS, (W - 24) * SS, 50 * SS), radius=20 * SS, fill=95)
        reflet.putalpha(ImageChops.multiply(m.resize((W, H), Image.LANCZOS), masque_arrondi(W, H, 60)))
        im.alpha_composite(reflet)
        n = f'assets_ludexa/Images/barre_vie_{nom}.png'
        sauver(im, os.path.join(dossier, n))
        noms[nom] = n
    return noms


def image_score(dossier):
    W, H = 1120, 280
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bord = degrade(W, H, '#FFE27A', '#FF9F1C')
    bord.putalpha(masque_arrondi(W, H, 140))
    im.alpha_composite(bord)
    fond = degrade(W, H, '#2B2250', '#150F2E')
    fond.putalpha(masque_arrondi(W, H, 132, 8))
    im.alpha_composite(fond)
    reflet = Image.new('RGBA', (W, H), (255, 255, 255, 0))
    m = Image.new('L', (W * SS, H * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle((60 * SS, 22 * SS, (W - 60) * SS, 120 * SS), radius=48 * SS, fill=40)
    reflet.putalpha(ImageChops.multiply(m.resize((W, H), Image.LANCZOS), masque_arrondi(W, H, 132, 8)))
    im.alpha_composite(reflet)
    halo = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    poly_lisse(halo, etoile_points(150, 140, 100, 44, 0), (255, 200, 60, 255))
    im.alpha_composite(lueur(halo, (255, 190, 40, 255), 14, 1.0))
    poly_lisse(im, etoile_points(150, 140, 90, 38, 0), (255, 213, 74, 255), (255, 140, 20, 255), 7)
    poly_lisse(im, etoile_points(150, 140, 56, 24, 0), (255, 240, 160, 255))
    n = 'assets_ludexa/Images/score_panneau.png'
    sauver(im, os.path.join(dossier, n))
    return n


def images_pause(dossier):
    noms = {}
    # bouton ⏸ rond
    S = 300
    im = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    halo = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    disque(halo, S // 2, S // 2, 128, (76, 201, 240, 255))
    im.alpha_composite(lueur(halo, (60, 180, 255, 255), 9, 0.9))
    disque(im, S // 2, S // 2, 128, rgb('#4CC9F0'))
    fond = degrade(S, S, '#2C3652', '#141A2C')
    m = Image.new('L', (S * SS, S * SS), 0)
    ImageDraw.Draw(m).ellipse((16 * SS, 16 * SS, (S - 16) * SS, (S - 16) * SS), fill=255)
    fond.putalpha(m.resize((S, S), Image.LANCZOS))
    im.alpha_composite(fond)
    barres_arrondies(im, [(100, 88, 132, 212), (168, 88, 200, 212)], 12, (255, 255, 255, 255))
    noms['bouton'] = 'assets_ludexa/Images/pause_bouton.png'
    sauver(im, os.path.join(dossier, noms['bouton']))
    # panneau
    W, H = 1400, 1520
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    bord = degrade(W, H, '#4CC9F0', '#7B5CFF')
    bord.putalpha(masque_arrondi(W, H, 90))
    im.alpha_composite(bord)
    fond = degrade(W, H, '#222A42', '#11162A')
    fond.putalpha(masque_arrondi(W, H, 82, 8))
    im.alpha_composite(fond)
    noms['panneau'] = 'assets_ludexa/Images/pause_panneau.png'
    sauver(im, os.path.join(dossier, noms['panneau']))
    # 3 boutons
    for nom, h1, h2, b1, b2 in (('reprendre', '#3EE6A4', '#14A06E', '#C8FFE9', '#47D9A0'),
                                ('recommencer', '#5AD0F5', '#2A6FD8', '#CFF3FF', '#4C9BF0'),
                                ('quitter', '#FF8696', '#C42848', '#FFD0D6', '#E8566E')):
        n = f'assets_ludexa/Images/pause_{nom}.png'
        sauver(pilule(1040, 240, h1, h2, b1, b2), os.path.join(dossier, n))
        noms[nom] = n
    # voile sombre
    voile = Image.new('RGBA', (16, 16), (0, 0, 0, 150))
    noms['voile'] = 'assets_ludexa/Images/pause_voile.png'
    sauver(voile, os.path.join(dossier, noms['voile']))
    return noms


def variable_locale(nom, valeur):
    return {'id': uid(), 'nom': nom, 'scope': 'LOCALE', 'type': 'ENTIER', 'valeur': valeur}


def placer(o, x, y, z=None, parent=None, visible=None):
    o['x'], o['y'] = float(x), float(y)
    if z is not None:
        o['zOrder'] = z
    if parent is not None:
        o['parentId'] = parent['id']
    if visible is not None:
        o['visible'] = visible
    return o


def vignette_image(id_, im):
    """Vignette 300 x 300 composée à partir d'une image PIL (le dossier du prefab ne reçoit que vignette.png)."""
    fond = degrade(300, 300, '#222838', '#141824')
    e = min(264 / im.width, 264 / im.height)
    im = im.resize((max(1, int(im.width * e)), max(1, int(im.height * e))), Image.LANCZOS)
    fond.alpha_composite(im, ((300 - im.width) // 2, (300 - im.height) // 2))
    fond.convert('RGB').save(os.path.join(PREFABS, id_, 'vignette.png'), 'PNG', optimize=True)


def construire_interface():
    # 1. interrupteur ON/OFF -------------------------------------------------
    i = 'interrupteur'
    dossier = os.path.join(PREFABS, i)
    imgs = images_interrupteur(dossier)
    b = objet_bouton(i, imgs[0], 220, 110)
    b['variablesLocales'] = [variable_locale('etat', 0)]
    L = Logique()
    e = L.evenement('NoeudEventClicObjet', i)
    c = L.action(e, 'condition', {'condition': 'etat == 0'}, i)
    L.chaine((c[0], 'port_vrai', 0), [('modifier_variable', {'valeur': 1}, 'etat'),
                                      ('jouer_animation', {'animation': i + '_on', 'vitesse': 24, 'boucle': 'false'}),
                                      son('power_up', 60)], i)
    L.chaine((c[0], 'port_faux', 1), [('modifier_variable', {'valeur': 0}, 'etat'),
                                      ('jouer_animation', {'animation': i + '_off', 'vitesse': 24, 'boucle': 'false'}),
                                      son('pop', 60)], i)
    ecrire_prefab(i, [b], L, {i + '_on': imgs, i + '_off': imgs[::-1]}, [], ['power_up', 'pop'], prefixe=PREFIXE_UI)
    vignette_image(i, Image.open(os.path.join(dossier, imgs[-1])).convert('RGBA'))

    # 2. barre de vie animée -------------------------------------------------
    i = 'barre_vie'
    dossier = os.path.join(PREFABS, i)
    im = images_barre_vie(dossier)
    cadre = objet_bouton(i, im['cadre'], 720, 84)
    plein = objet_bouton(i + '_remplissage', im['vert'], 600, 60)
    placer(plein, 100, 12, 1, cadre)
    plein['variablesLocales'] = [variable_locale('vie', 100)]
    r = i + '_remplissage'
    L = Logique()
    e = L.evenement('NoeudEventClicObjet', r)
    fin = L.chaine(e, [('ajouter_variable', {'valeur': -10}, 'vie'),
                       ('limiter_valeur', {'min': 0, 'max': 100}, 'vie'),
                       ('modifier_propriete', {'propriete': 'largeur', 'valeur': '=vie * 6'}),
                       ('sautiller', {'intensite': 5, 'duree': 200, 'infini': 'false'}),
                       son('rate', 70)], r)
    c = L.action(fin, 'condition', {'condition': 'vie <= 0'}, r)
    # vie à zéro : la barre se remplit de nouveau
    L.chaine((c[0], 'port_vrai', 0), [('clignotement', {'etat': 'Désactiver', 'vitesse': 200, 'duree': 0}),
                                      son('game_over', 70), ('attendre', {'duree': 1.2}),
                                      ('modifier_variable', {'valeur': 100}, 'vie'),
                                      ('modifier_propriete', {'propriete': 'largeur', 'valeur': '=vie * 6'}),
                                      ('changer_image', {'image': im['vert']})], r)
    # sinon : la couleur suit la vie restante
    t = L.action((c[0], 'port_faux', 1), 'si_sinon', {'condition1': 'vie <= 30', 'condition2': 'vie <= 60'}, r)
    L.chaine((t[0], 'port_si', 0), [('changer_image', {'image': im['rouge']}),
                                    ('clignotement', {'etat': 'Activer', 'vitesse': 250, 'duree': 0})], r)
    L.chaine((t[0], 'port_sinon_si', 1), [('clignotement', {'etat': 'Désactiver', 'vitesse': 250, 'duree': 0}),
                                          ('changer_image', {'image': im['orange']})], r)
    L.chaine((t[0], 'port_sinon', 2), [('clignotement', {'etat': 'Désactiver', 'vitesse': 250, 'duree': 0}),
                                       ('changer_image', {'image': im['vert']})], r)
    ecrire_prefab(i, [cadre, plein], L, {}, [], ['rate', 'game_over'], prefixe=PREFIXE_UI)
    apercu = Image.open(os.path.join(dossier, im['cadre'])).convert('RGBA')
    v = Image.open(os.path.join(dossier, im['orange'])).convert('RGBA').resize((1000, 100), Image.LANCZOS)
    apercu.alpha_composite(v, (200, 34))
    vignette_image(i, apercu)

    # 3. score qui « pop » ---------------------------------------------------
    i = 'score_pop'
    dossier = os.path.join(PREFABS, i)
    img = image_score(dossier)
    panneau = objet_bouton(i, img, 560, 140)
    chiffre = objet_texte(i + '_valeur', panneau, '0', 'Fredoka', 80, '#FFFFFF', 320, 100, 190, 20)
    chiffre['variablesLocales'] = [variable_locale('score', 0)]
    v = i + '_valeur'
    L = Logique()
    e = L.evenement('NoeudEventClicObjet', i)
    L.chaine(e, [('ajouter_variable', {'valeur': 10}, 'score'),
                 ('modifier_propriete', {'propriete': 'texte', 'valeur': '=score'}),
                 ('modifier_taille', {'x': 1.4, 'y': 1.4}), particules('Etincelles'), son('power_up', 70),
                 ('attendre', {'duree': 0.12}), ('modifier_taille', {'x': 1, 'y': 1})], v)
    ecrire_prefab(i, [panneau, chiffre], L, {}, ['Fredoka'], ['power_up'], prefixe=PREFIXE_UI)
    vignette_image(i, Image.open(os.path.join(dossier, img)).convert('RGBA'))

    # 4. fenêtre de pause ----------------------------------------------------
    i = 'fenetre_pause'
    dossier = os.path.join(PREFABS, i)
    im = images_pause(dossier)
    bouton = placer(objet_bouton('pause_bouton', im['bouton'], 150, 150), 0, 0, 900)
    fenetre = placer(objet_bouton('pause_fenetre', im['panneau'], 700, 760), 250, 0, 900)
    voile = placer(objet_bouton('pause_voile', im['voile'], 4000, 3000), -1650, -1120, 899, fenetre, False)
    titre = placer(objet_texte('pause_titre', fenetre, 'PAUSE', 'Fredoka', 84, '#E6EDF7', 600, 110, 50, 40), 50, 40, 901, fenetre)
    objets = [bouton, fenetre, voile, titre]
    boutons = {}
    for k, (cle, libelle) in enumerate((('reprendre', 'Resume'), ('recommencer', 'Restart'), ('quitter', 'Quit'))):
        bt = placer(objet_bouton('pause_' + cle, im[cle], 520, 120), 90, 200 + k * 170, 901, fenetre)
        tx = placer(objet_texte('pause_txt_' + cle, bt, libelle, 'Fredoka', 60, '#FFFFFF', 480, 90, 20, 14), 20, 14, 902, bt)
        objets += [bt, tx]
        boutons[cle] = bt
    L = Logique()
    e = L.evenement('NoeudEventStart')
    L.action(e, 'visibilite', {'valeur': 'false'}, 'pause_fenetre')
    for classe, cible in (('NoeudEventClicObjet', 'pause_bouton'), ('NoeudEventBoutonRetour', None)):
        e = L.evenement(classe, cible)
        p = L.action(e, 'visibilite', {'valeur': 'true'}, 'pause_fenetre')
        p = L.action(p, 'visibilite', {'valeur': 'true'}, 'pause_voile')
        p = L.action(p, 'pause_jeu', {}, None)
        L.action(p, 'jouer_son', {'fichier': 'assets_ludexa/Sons/pop.ogg', 'volume': 70}, None)
    e = L.evenement('NoeudEventClicObjet', 'pause_reprendre')
    p = L.action(e, 'reprendre_jeu', {}, None)
    p = L.action(p, 'visibilite', {'valeur': 'false'}, 'pause_fenetre')
    p = L.action(p, 'visibilite', {'valeur': 'false'}, 'pause_voile')
    L.action(p, 'jouer_son', {'fichier': 'assets_ludexa/Sons/pop.ogg', 'volume': 70}, None)
    e = L.evenement('NoeudEventClicObjet', 'pause_recommencer')
    p = L.action(e, 'reprendre_jeu', {}, None)
    p = L.action(p, 'visibilite', {'valeur': 'false'}, 'pause_fenetre')
    p = L.action(p, 'visibilite', {'valeur': 'false'}, 'pause_voile')
    L.action(p, 'recommencer_scene', {}, None)
    e = L.evenement('NoeudEventClicObjet', 'pause_quitter')
    L.action(e, 'quitter_jeu', {}, None)
    ecrire_prefab(i, objets, L, {}, ['Fredoka'], ['pop'], prefixe=PREFIXE_UI)
    apercu = Image.open(os.path.join(dossier, im['panneau'])).convert('RGBA')
    for k, cle in enumerate(('reprendre', 'recommencer', 'quitter')):
        apercu.alpha_composite(Image.open(os.path.join(dossier, im[cle])).convert('RGBA'), (180, 400 + k * 340))
    vignette_image(i, apercu)


if __name__ == '__main__':
    lot = sys.argv[2] if len(sys.argv) > 2 else 'boutons'
    if lot == 'interface':
        construire_interface()
        print('4 prefabs d\'interface écrits dans', PREFABS)
    else:
        construire()
        print('7 prefabs écrits dans', PREFABS)
