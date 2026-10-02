#!/usr/bin/env python3
"""Fabrique les PACKS EN LIGNE de la bibliothèque Yop2D (onglet « Packs à télécharger » du moteur).

Source : un dossier par pack dans packs/ :
    packs/<id>/pack.json            (facultatif) nom, description, noms des dossiers en 9 langues
    packs/<id>/<Dossier>/...        images (.png .jpg .webp), sons (.ogg .mp3 .wav), polices (.ttf .otf) :
                                    chaque dossier devient un onglet ; ses sous-dossiers sont rangés dedans
    packs/<id>/Animations/<nom>/    les images d'UNE animation (dans l'ordre des noms : 1, 2, 3... 10)
    packs/<id>/Animations/<nom>/<action>/   un personnage : une animation par action (repos, marche, saut,
                                    grimpe, accroupi...) -> animations <nom>_<action>, reconnues par les comportements
    packs/<id>/Licence.txt          (facultatif) copiée dans le projet avec ce qu'on prend du pack
    packs/<id>/vignette.png         (facultatif) sinon une vignette est composée avec les premières images

Résultat (dans packs/) : <id>-<empreinte>.zip (le nom change quand le contenu change : le cache du site ne peut
pas servir l'ancien), <id>.png (vignette 300 x 300), packs.json (la liste lue par le moteur).
Lancé tout seul par le robot GitHub (.github/workflows/packs.yml) quand un fichier change dans packs/<id>/.
"""
import hashlib, io, json, os, re, zipfile
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKS = os.path.join(RACINE, 'packs')
LANGUES = ['fr', 'en', 'es', 'de', 'it', 'pt', 'ru', 'zh', 'ja']
IMAGES, SONS, POLICES = ('.png', '.jpg', '.jpeg', '.webp'), ('.ogg', '.mp3', '.wav'), ('.ttf', '.otf')
DOSSIER_ZIP = {'image': 'Images', 'son': 'Sons', 'police': 'Fonts'}


def genre(nom):
    n = nom.lower()
    if n.endswith(IMAGES): return 'image'
    if n.endswith(SONS): return 'son'
    if n.endswith(POLICES): return 'police'
    return None


def propre(nom):
    """Nom de fichier sans espaces ni parenthèses (« ship (1).png » -> « ship_1.png »)."""
    base, ext = os.path.splitext(nom)
    base = re.sub(r'[^A-Za-z0-9_-]+', '_', base).strip('_') or 'fichier'
    return base + ext.lower()


def ordre_naturel(nom):
    return [int(m) if m.isdigit() else m.lower() for m in re.split(r'(\d+)', nom)]


def lisible(nom):
    return re.sub(r'[_-]+', ' ', os.path.splitext(nom)[0]).strip()


def fichiers(dossier):
    return sorted((f for f in os.listdir(dossier) if os.path.isfile(os.path.join(dossier, f)) and genre(f)), key=ordre_naturel)


def construire(id_pack):
    src = os.path.join(PACKS, id_pack)
    infos = {}
    if os.path.exists(os.path.join(src, 'pack.json')):
        infos = json.load(open(os.path.join(src, 'pack.json'), encoding='utf-8'))
    noms_dossiers = infos.get('dossiers', {})
    contenu = {}                      # chemin dans le zip -> fichier source
    themes = []

    def ajouter(chemin_src, sous_dossier):
        g = genre(chemin_src)
        dest = '%s/Packs/%s/%s/%s' % (DOSSIER_ZIP[g], id_pack, '/'.join(propre(p) for p in sous_dossier), propre(os.path.basename(chemin_src)))
        dest = dest.replace('//', '/')
        contenu[dest] = chemin_src
        return dest, g

    def nom_theme(d):
        n = noms_dossiers.get(d)
        return n if isinstance(n, dict) else lisible(d)

    for d in sorted(os.listdir(src), key=ordre_naturel):
        chemin = os.path.join(src, d)
        if not os.path.isdir(chemin):
            continue
        elements = []
        if d.lower() == 'animations':
            for a in sorted(os.listdir(chemin), key=ordre_naturel):
                ca = os.path.join(chemin, a)
                if not os.path.isdir(ca): continue
                actions = [x for x in sorted(os.listdir(ca), key=ordre_naturel) if os.path.isdir(os.path.join(ca, x))]
                animations = {}
                if actions:
                    for act in actions:
                        imgs = [ajouter(os.path.join(ca, act, f), [d, a, act])[0] for f in fichiers(os.path.join(ca, act)) if genre(f) == 'image']
                        if imgs: animations[propre(a) + '_' + propre(act)] = imgs
                else:
                    imgs = [ajouter(os.path.join(ca, f), [d, a])[0] for f in fichiers(ca) if genre(f) == 'image']
                    if imgs: animations[propre(a)] = imgs
                if not animations: continue
                premiere = next(iter(animations.values()))
                apercu = next((v for k, v in animations.items() if 'marche' in k or 'walk' in k), premiere)
                repos = next((v for k, v in animations.items() if 'repos' in k or 'idle' in k), premiere)
                elements.append({'t': 'anim', 'n': lisible(a), 'c': repos[0], 'ap': apercu, 'a': animations})
        else:
            for racine, _, fs in sorted(os.walk(chemin)):
                rel = os.path.relpath(racine, src).split(os.sep)
                for f in sorted(fs, key=ordre_naturel):
                    if not genre(f): continue
                    dest, g = ajouter(os.path.join(racine, f), rel)
                    e = {'t': {'image': 'img', 'son': 'son', 'police': 'police'}[g], 'c': dest, 'n': lisible(f)}
                    elements.append(e)
        if not elements:
            continue
        genres = [e['t'] for e in elements]
        type_theme = 'son' if genres.count('son') > len(genres) / 2 else 'police' if genres.count('police') > len(genres) / 2 else 'image'
        themes.append({'id': id_pack + '/' + d, 'nom': nom_theme(d), 'type': type_theme, 'e': elements})

    licence = None
    for f in os.listdir(src):
        if f.lower().startswith(('licence', 'license')) and f.lower().endswith('.txt'):
            licence = 'Images/Packs/%s/Licence.txt' % id_pack
            contenu[licence] = os.path.join(src, f)
    nom = infos.get('nom') or lisible(id_pack)
    index = {'format': 1, 'id': id_pack, 'nom': nom, 'licence': licence, 'themes': themes}

    # zip reproductible (même contenu -> même empreinte)
    tampon = io.BytesIO()
    with zipfile.ZipFile(tampon, 'w', zipfile.ZIP_DEFLATED) as z:
        info = zipfile.ZipInfo('index.json', date_time=(2026, 1, 1, 0, 0, 0))
        z.writestr(info, json.dumps(index, ensure_ascii=False, separators=(',', ':')))
        for dest in sorted(contenu):
            info = zipfile.ZipInfo(dest, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, open(contenu[dest], 'rb').read())
    octets = tampon.getvalue()
    empreinte = hashlib.sha1(octets).hexdigest()[:8]
    nom_zip = '%s-%s.zip' % (id_pack, empreinte)
    for f in os.listdir(PACKS):
        if f.startswith(id_pack + '-') and f.endswith('.zip') and f != nom_zip:
            os.remove(os.path.join(PACKS, f))
    open(os.path.join(PACKS, nom_zip), 'wb').write(octets)

    # vignette
    nom_vignette = id_pack + '.png'
    perso = os.path.join(src, 'vignette.png')
    if os.path.exists(perso):
        v = Image.open(perso).convert('RGBA').resize((300, 300), Image.LANCZOS)
    else:
        v = Image.new('RGBA', (300, 300), (30, 34, 54, 255))
        # les plus grandes images de chaque onglet, tour à tour (un aperçu varié du pack)
        par_theme = []
        for t in themes:
            cs = [contenu[e['c']] for e in t['e'] if e['t'] in ('img', 'anim')]
            cs.sort(key=lambda c: -(lambda im: im.width * im.height)(Image.open(c)))
            par_theme.append(cs)
        imgs = []
        while len(imgs) < 9 and any(par_theme):
            for cs in par_theme:
                if cs and len(imgs) < 9: imgs.append(cs.pop(0))
        for k, chemin in enumerate(imgs):
            im = Image.open(chemin).convert('RGBA')
            im.thumbnail((90, 90), Image.LANCZOS)
            x, y = 10 + (k % 3) * 95 + (90 - im.width) // 2, 10 + (k // 3) * 95 + (90 - im.height) // 2
            v.alpha_composite(im, (x, y))
    v.convert('RGB').save(os.path.join(PACKS, nom_vignette), optimize=True)

    nb = lambda t: sum(1 for th in themes for e in th['e'] if e['t'] in t)
    return {'id': id_pack, 'nom': nom, 'description': infos.get('description', ''), 'fichier': nom_zip,
            'taille': len(octets), 'vignette': nom_vignette, 'version': empreinte,
            'images': nb(('img', 'anim')), 'sons': nb(('son',)), 'polices': nb(('police',))}


def main():
    liste = []
    for id_pack in sorted(os.listdir(PACKS)):
        if os.path.isdir(os.path.join(PACKS, id_pack)) and not id_pack.startswith('.'):
            p = construire(id_pack)
            liste.append(p)
            print('%-12s %4d images %3d sons %2d polices  %5d Ko  %s' % (p['id'], p['images'], p['sons'], p['polices'], p['taille'] // 1024, p['fichier']))
    with open(os.path.join(PACKS, 'packs.json'), 'w', encoding='utf-8') as f:
        json.dump({'format': 1, 'packs': liste}, f, ensure_ascii=False, indent=1)
        f.write('\n')


if __name__ == '__main__':
    main()
