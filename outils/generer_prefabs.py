#!/usr/bin/env python3
"""Fabrique les PREFABS EN LIGNE de Yop2D (objets prêts à l'emploi à télécharger depuis le moteur).

Source : un dossier par prefab dans prefabs/ (voir prefabs/LISEZMOI.md) :
    prefabs/<id>/prefab.json     nom et description en 9 langues, licence, auteur
    prefabs/<id>/...             un petit projet Yop2D à UNE scène (projet_sauvegarde.json, logique/, assets_ludexa/)
    prefabs/<id>/vignette.png    (facultatif) sinon composée avec la dernière image du dossier assets_ludexa/Images

Résultat (dans prefabs/) : <id>-<empreinte>.zip (le nom change quand le contenu change : le cache du site ne peut pas
servir l'ancien), <id>.png (vignette 300 x 300), prefabs.json (la liste lue par le moteur).
Lancé tout seul par le robot GitHub (.github/workflows/prefabs.yml) quand un fichier change dans prefabs/<id>/.
"""
import hashlib, io, json, os, re, zipfile
from PIL import Image

RACINE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PREFABS = os.path.join(RACINE, 'prefabs')
IGNORER = {'prefab.json', 'vignette.png', 'diag_ludexa.txt', 'meta.json'}


def fichiers(src):
    sortie = []
    for dossier, _, noms in os.walk(src):
        for n in noms:
            chemin = os.path.join(dossier, n)
            rel = os.path.relpath(chemin, src).replace(os.sep, '/')
            if rel in IGNORER:
                continue
            sortie.append((rel, chemin))
    return sorted(sortie)


def vignette(src):
    v = os.path.join(src, 'vignette.png')
    if os.path.exists(v):
        im = Image.open(v).convert('RGBA')
    else:
        images = sorted(f for f in os.listdir(os.path.join(src, 'assets_ludexa', 'Images'))
                        if f.lower().endswith(('.png', '.webp', '.jpg')))
        im = Image.open(os.path.join(src, 'assets_ludexa', 'Images', images[-1])).convert('RGBA')
    fond = Image.new('RGBA', (300, 300), (30, 34, 46, 255))
    echelle = min(260 / im.width, 260 / im.height)
    im = im.resize((max(1, int(im.width * echelle)), max(1, int(im.height * echelle))), Image.LANCZOS)
    fond.alpha_composite(im, ((300 - im.width) // 2, (300 - im.height) // 2))
    tampon = io.BytesIO()
    fond.convert('RGB').save(tampon, 'PNG', optimize=True)
    return tampon.getvalue()


def construire(id_prefab):
    src = os.path.join(PREFABS, id_prefab)
    infos = json.load(open(os.path.join(src, 'prefab.json'), encoding='utf-8'))
    liste = fichiers(src)
    h = hashlib.sha256()
    for rel, chemin in liste:
        h.update(rel.encode('utf-8'))
        h.update(open(chemin, 'rb').read())
    h.update(vignette(src))
    h.update(json.dumps(infos, sort_keys=True).encode('utf-8'))
    version = h.hexdigest()[:8]
    nom_zip = '%s-%s.zip' % (id_prefab, version)
    # zip reproductible : même contenu = mêmes octets (dates fixes, ordre fixe)
    with zipfile.ZipFile(os.path.join(PREFABS, nom_zip), 'w', zipfile.ZIP_DEFLATED) as z:
        vignette_png = vignette(src)
        z.writestr(zipfile.ZipInfo('vignette.png', (2026, 1, 1, 0, 0, 0)), vignette_png)
        for rel, chemin in liste:
            info = zipfile.ZipInfo(rel, (2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            z.writestr(info, open(chemin, 'rb').read())
    open(os.path.join(PREFABS, id_prefab + '.png'), 'wb').write(vignette(src))
    for f in os.listdir(PREFABS):          # efface les anciennes versions du zip
        if re.fullmatch(re.escape(id_prefab) + r'-[0-9a-f]{8}\.zip', f) and f != nom_zip:
            os.remove(os.path.join(PREFABS, f))
    res = {
        'id': id_prefab,
        'nom': infos['nom'],
        'description': infos['description'],
        'licence': infos.get('licence', ''),
        'auteur': infos.get('auteur', ''),
        'fichier': nom_zip,
        'taille': os.path.getsize(os.path.join(PREFABS, nom_zip)),
        'vignette': id_prefab + '.png',
        'version': version,
    }
    if infos.get('moteur_min'):          # build minimal de Yop2D pour ce prefab (le moteur dit « mets Yop2D à jour »)
        res['moteur_min'] = int(infos['moteur_min'])
    return res


def main():
    ids = sorted(d for d in os.listdir(PREFABS)
                 if os.path.isdir(os.path.join(PREFABS, d)) and os.path.exists(os.path.join(PREFABS, d, 'prefab.json')))
    liste = [construire(i) for i in ids]
    json.dump({'format': 1, 'prefabs': liste}, open(os.path.join(PREFABS, 'prefabs.json'), 'w', encoding='utf-8'),
              ensure_ascii=False, indent=1)
    print(len(liste), 'prefab(s) :', ', '.join(ids))


if __name__ == '__main__':
    main()
