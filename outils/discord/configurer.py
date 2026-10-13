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

# Salons : catégorie -> liste de (nom, texte d'aide, lecture seule)
STRUCTURE = [
    ("📢 INFO", [
        ("welcome-and-rules", "Welcome to the Yop2D community! Please read the rules.", True),
        ("announcements", "New versions, test versions, new examples, packs and guides.", True),
    ]),
    ("💬 COMMUNITY", [
        ("general", "Chat about Yop2D and game making.", False),
        ("show-your-games", "Share your games, screenshots and videos!", False),
        ("ideas-and-suggestions", "Your ideas for new nodes and features.", False),
        ("off-topic", "Anything else.", False),
    ]),
    ("🆘 HELP", [
        ("help-and-questions", "Stuck? Ask here. Say what you tried and send a screenshot.", False),
        ("bug-reports", "Found a bug? Tell us the Yop2D version and how to reproduce it.", False),
        ("beta-testing", "Test versions: feedback welcome.", False),
    ]),
    ("🌍 LANGUAGES", [
        ("francais", "Discussion en français.", False),
        ("espanol", "Conversación en español.", False),
        ("deutsch", "Gespräche auf Deutsch.", False),
        ("italiano", "Conversazione in italiano.", False),
        ("portugues", "Conversa em português.", False),
        ("russkiy", "Общение на русском.", False),
        ("zhongwen", "中文交流。", False),
        ("nihongo", "日本語で話そう。", False),
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
    """Nom sans émoji ni majuscules, pour comparer."""
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

    for nom_cat, liste in STRUCTURE:
        cat = next((c for c in salons if c["type"] == 4 and propre(c["name"]) == propre(nom_cat)), None)
        if cat is None:
            cat = appel("POST", f"/guilds/{GUILD}/channels", {"name": nom_cat, "type": 4})
            salons.append(cat)
            print("  catégorie créée :", nom_cat)
        else:
            print("  déjà là :", nom_cat)
        for nom, aide, lecture_seule in liste:
            if any(c["type"] in (0, 5) and propre(c["name"]) == propre(nom) for c in salons):
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
