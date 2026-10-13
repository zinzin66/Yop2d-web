#!/usr/bin/env python3
"""Configure le serveur Discord de Yop2D (salons et rôles).

Usage : python3 outils/discord/configurer.py list    -> affiche ce qui existe, ne change RIEN
        python3 outils/discord/configurer.py apply   -> crée ce qui manque (ne supprime jamais rien)

Variables d'environnement (secrets GitHub) : DISCORD_BOT_TOKEN, DISCORD_GUILD_ID.
Un salon ou un rôle est considéré comme déjà présent si son nom (sans émoji, sans majuscules) existe déjà.
"""
import json
import os
import re
import sys
import unicodedata
import urllib.error
import urllib.request

API = "https://discord.com/api/v10"
TOKEN = os.environ.get("DISCORD_BOT_TOKEN", "")
GUILD = os.environ.get("DISCORD_GUILD_ID", "")

# Droits Discord utilisés
VOIR = 1 << 10
ECRIRE = 1 << 11

# Rôles à créer : (nom, couleur, affiché à part)
ROLES = [
    ("Beta tester", 0xF5A623, True),
    ("Game maker", 0x4A90E2, True),
]

# Salons à avoir : (catégorie, autres noms possibles de la catégorie, liste de salons)
# salon = (nom, texte d'aide, lecture seule, autres noms possibles déjà utilisés)
STRUCTURE = [
    ("Informations", ["informations", "info"], [
        ("welcome-and-rules", "Welcome to the Yop2D community! Please read the rules.", True, ["regles", "rules", "reglement", "bienvenue", "welcome"]),
    ]),
    ("questions", ["questions", "aide", "help"], [
        ("beta-testing", "Test versions: feedback welcome.", False, ["beta", "test", "tests", "testeurs"]),
    ]),
    ("🌍 Languages", ["languages", "langues"], [
        ("francais", "Discussion en français.", False, []),
        ("espanol", "Conversación en español.", False, []),
        ("deutsch", "Gespräche auf Deutsch.", False, []),
        ("italiano", "Conversazione in italiano.", False, []),
        ("portugues", "Conversa em português.", False, []),
        ("russkiy", "Общение на русском.", False, []),
        ("zhongwen", "中文交流。", False, []),
        ("nihongo", "日本語で話そう。", False, []),
    ]),
]


def appel(methode, chemin, corps=None):
    donnees = json.dumps(corps).encode() if corps is not None else None
    req = urllib.request.Request(API + chemin, data=donnees, method=methode)
    req.add_header("Authorization", "Bot " + TOKEN)
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "DiscordBot (https://zinzin66.github.io/Yop2d-web/, 1.0)")
    try:
        with urllib.request.urlopen(req) as r:
            texte = r.read().decode()
            return json.loads(texte) if texte else None
    except urllib.error.HTTPError as e:
        print("ERREUR Discord", e.code, e.read().decode()[:300])
        sys.exit(1)


def propre(nom):
    """Nom sans accent, sans émoji ni majuscules, pour comparer."""
    nom = unicodedata.normalize("NFKD", nom).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "", nom.lower())


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    if not TOKEN or not GUILD:
        print("Il manque le secret DISCORD_BOT_TOKEN ou DISCORD_GUILD_ID.")
        sys.exit(1)
    salons = appel("GET", f"/guilds/{GUILD}/channels")
    roles = appel("GET", f"/guilds/{GUILD}/roles")

    print("=== Ce qui existe déjà ===")
    for c in sorted(salons, key=lambda c: (c.get("parent_id") or c["id"], c["position"])):
        genre = {0: "salon", 4: "catégorie", 2: "vocal", 5: "annonces", 15: "forum"}.get(c["type"], str(c["type"]))
        print(f"  [{genre}] {c['name']}")
    print("  Rôles :", ", ".join(r["name"] for r in roles))
    if mode != "apply":
        print("\n=== Ce que « apply » créerait ===")
        existants = {propre(r["name"]) for r in roles}
        for nom, _, _ in ROLES:
            if propre(nom) not in existants:
                print("  rôle :", nom)
        for nom_cat, alias_cat, liste in STRUCTURE:
            noms_cat = {propre(nom_cat)} | {propre(x) for x in alias_cat}
            cat = next((c for c in salons if c["type"] == 4 and propre(c["name"]) in noms_cat), None)
            print("  catégorie", ("existante : " + cat["name"]) if cat else "NOUVELLE : " + nom_cat)
            for nom, _, _, alias in liste:
                noms = {propre(nom)} | {propre(x) for x in alias}
                if not any(c["type"] in (0, 5) and propre(c["name"]) in noms for c in salons):
                    print("    salon :", nom)
        print("\nMode « list » : rien n'a été modifié.")
        return

    print("\n=== Création de ce qui manque ===")
    tous = GUILD  # le rôle @everyone a le même numéro que le serveur
    existants_roles = {propre(r["name"]) for r in roles}
    for nom, couleur, separe in ROLES:
        if propre(nom) in existants_roles:
            print("  déjà là :", nom)
        else:
            appel("POST", f"/guilds/{GUILD}/roles", {"name": nom, "color": couleur, "hoist": separe, "mentionable": True})
            print("  rôle créé :", nom)

    for nom_cat, alias_cat, liste in STRUCTURE:
        noms_cat = {propre(nom_cat)} | {propre(x) for x in alias_cat}
        cat = next((c for c in salons if c["type"] == 4 and propre(c["name"]) in noms_cat), None)
        if cat is None:
            cat = appel("POST", f"/guilds/{GUILD}/channels", {"name": nom_cat, "type": 4})
            salons.append(cat)
            print("  catégorie créée :", nom_cat)
        else:
            print("  catégorie déjà là :", cat["name"])
        for nom, aide, lecture_seule, alias in liste:
            noms = {propre(nom)} | {propre(x) for x in alias}
            if any(c["type"] in (0, 5) and propre(c["name"]) in noms for c in salons):
                print("    déjà là :", nom)
                continue
            corps = {"name": nom, "type": 0, "parent_id": cat["id"], "topic": aide}
            if lecture_seule:
                corps["permission_overwrites"] = [
                    {"id": tous, "type": 0, "allow": str(VOIR), "deny": str(ECRIRE)}
                ]
            nouveau = appel("POST", f"/guilds/{GUILD}/channels", corps)
            salons.append(nouveau)
            print("    salon créé :", nom)
    print("\nTerminé.")


main()
