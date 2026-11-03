#!/usr/bin/env python3
"""Fabrique llms-full.txt (racine du site) : le fichier détaillé pour les IA qui aident les utilisateurs de Yop2D.
Usage : python3 outils/generer_llms_full.py
- Partie écrite à la main : TEXTE ci-dessous (anglais). À relire quand le moteur change vraiment de fonctionnement.
- Partie générée : liste des guides (aide/guides/en) et référence des nœuds (aide/noeuds/en, nœuds « nouveau » marqués).
Relancer après generer_aide_noeuds.py (comme llms.txt)."""
import glob, json, os, re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://zinzin66.github.io/Yop2d-web/"

TEXTE = """# Yop2D, full guide for AI assistants

> Read this file before answering a question about Yop2D. It explains how the engine thinks, the mistakes people (and AIs) make most often, and ends with the list of every node. A shorter summary is at {site}llms.txt.

## How to answer a Yop2D user

- Yop2D is a **no-code** 2D game engine for Android. Users build games by touching and connecting **nodes** (a visual script called the **Blueprint**). **Never write programming code** (no Java, no Python, no Unity or Godot code). Give numbered steps using the exact names of buttons, nodes and settings.
- **Use only the nodes listed at the end of this file.** Never invent a node, a setting or a button. If you are not sure something exists, say so and suggest asking on the Yop2D Discord.
- Node names change with the interface language. The names below are the English ones. Other languages: {site}noeuds/fr.html (also es, de, it, pt, ru, zh, ja).
- Some nodes are marked **[newer than 1.0.1142]**: they are NOT in the public Google Play version yet, only in the Discord test version. If the user cannot find one, tell them to update Yop2D or join the test version.
- The user is usually a beginner on a **phone or tablet** (touch screen, no mouse). Keep answers short and simple. Do not use jargon without explaining it.
- Ask for what you need: the Yop2D version (start screen), which scene the node is in, the exact settings of the node, and what they expected versus what happens. The best thing a user can paste is the text of their Blueprint: in the Blueprint, the `{ }` button shows the nodes of the current scene as text.
- Always suggest the built-in checks when something does not work: **menu ☰ → Check my game** (lists missing variables, objects, files and unconnected nodes), and the detailed log (start screen → 🐞 button → tick "detailed log", play, then Copy).
- If the question is about making a whole kind of game, point to the matching guide (list below) before improvising.

## The big picture

- A **project** contains one or more **scenes** (levels, menus). A special scene called a **HUD** can be shown over a game scene for score, buttons and joystick. The start scene is the first one in the Scenes list (the star marks it).
- A scene contains **objects**. Each object has a **name** and optionally a **tag**. In the editor, the left panel lists the objects (Hierarchy), the canvas shows the scene, the right panel (Inspector) shows the settings of the selected object. The top bar has: Object (add), Save, Undo, Redo, Copy, Delete, Move, Hand, Grid, Center, Zoom, Blueprint, Help, Menu, Play. On a phone some of these are in a menu.
- **Play** runs the game; the stop button returns to the editor. Saving is automatic (every minute by default), and the 💾 button saves now.
- Objects: image, text, shapes (square, circle…), zone (invisible area, can have several points), joystick, buttons, particles, tile layer ("tile scenery"), scene instance (a scene placed inside another = a **prefab**), and interface elements (button, switch, checkbox, slider, panel, counter).
- **Assets**: images, sounds, fonts, texts live in the project. The **Yop2D Library** has ready images (with animations), sounds, music, fonts, titles. Free packs, prefabs and examples can be downloaded from the Library and the Examples tab.
- The editor has small tools in the Assets window: Music, Sound effect, Movement (animation by steps), Parcours (paths for enemies), Sheet (cut a sprite sheet), Character, Animations, Titles, Start screen.

## Objects, inspector, behaviors

- Inspector fields: name, ⚙ **Behavior**, position, size, scale, rotation, Z (front/back: a higher Z is drawn in front), color, opacity, visible, shadow under the object, **Tag**, object variables, invisible touch area, parent, parallax, contact area (a custom area used for collisions).
- **Tags**: one object can have several tags. **Separate them with commas** (`enemy, danger`), never with spaces. A tag is a family name: one setup works for every object with that tag.
- **Behavior** (⚙ in the inspector) says how an object moves, with no nodes: Scenery (nothing), **Ground / wall** (does not move, you walk on it), Falls and bounces, **Platform character** (walks, jumps, climbs ladders; needs a joystick or buttons, and a jump button), **Patrol (back and forth)** (walks alone, turns at edges: for enemies), Top-down character, Dragged with a finger, **Elevator**, **Realistic physics**. An object can also be a ladder, traversable, pickable, drawn in front/behind by position. **Nodes always win**: if a node moves an object, it overrides the behavior.
- A joystick object has an **object to move** setting: pick the character in the inspector of the joystick.
- Text on a button: a text object must be a **child** of the button (parent) or share its tag, otherwise the text object captures the touch.
- A text drawn behind a panel is invisible: give the text a higher **Z** than the panel.
- Position coordinates are in game pixels. The default game is 1920 x 1080 (landscape) or 1080 x 1920 (portrait); the screen adaptation (keep shape / stretch / fill) is in Menu → Game settings.

## Variables and formulas

- **Variables** are created in the left panel (section Variables) with a type (integer, text, yes/no, list) and a scope: **local** (this scene, reset when the scene restarts) or **global** (whole game). **Object variables** belong to one object and are read with `objectname.variable`.
- Any numeric or text setting can be a **formula**, written with `=` in front: `=score + 1`, `="Score: " + score`, `=score >= 3`. Beginners should only use: a variable name, a simple comparison, a sum, a text. Do not suggest `&&`, `||`, nested parentheses or code-like functions.
- Handy values: `doigt.x`, `doigt.y` (finger position on screen), `joystick.x`, `joystick.y`, `ecran.largeur`, `ecran.hauteur`, `camera.x`, `camera.y`, `temps`, `langue_telephone`, `fps`, `delta`, `objectname.x`, `objectname.y`, `objectname.largeur`, `objectname.vitesse`. Functions: `random(a, b)`, `distance(a, b)`, `angle(a, b)`, `round`, `floor`, `ceil`, `abs`, `min`, `max`, `clamp`, `reste(a, b)`, `si(condition, a, b)`. The settings window has a left panel with these ready to tap, and a line "In plain words" that explains the formula.
- **Green nodes** ("value nodes": random number, object value, variable value, calculation, distance, touched column…) can be plugged into a setting with the 🔗 button instead of typing a formula.

## The Blueprint (nodes)

- Open it with the **Blueprint** button. Nodes are boxes. **Events** (red, e.g. On Start, Every frame, On Object Click, If object touches Tag) start a chain. **Actions** are connected after them with wires: drag a wire from an output (right side) to the input of the next node. An **output accepts one wire; an input accepts many**. The "Next" output runs the next node. **Conditions** have True/False outputs.
- Touch a node's frame to open its **settings window**: ① On what? (which object), ② Settings. The left list inserts objects, variables, tags and values.
- Dropping a wire into empty space opens a list of nodes to add. The wand button tidies the nodes. The ⬚ button selects several nodes to copy, paste or delete. Note and frame tools add sticky notes and titled frames to explain the nodes.
- **"The involved object"** (in English; "L'objet impliqué" in French) is the other object in a touch or click event: for "If object touches Tag", it is the object that was touched. This is how one setup affects the right pearl, enemy or card. "The selected object" is the one chosen with the selection nodes.
- A node only works in the scene whose Blueprint contains it (the Blueprint button shows the scene name; the HUD has its own Blueprint, where button clicks must be). There is also a **global logic** that runs in every scene (the first line of the scene list in the Blueprint) and **My nodes** (reusable nodes you build yourself, with settings).
- To react to a click on several objects, use the target `tag:name`. For several objects at once in touch events, put the same tag on all.
- Prefabs: objects inside a prefab are renamed when placed ("_2"), so formulas must not name them; read variables of the object the node targets.
- Dialogues and translations: `dialogues.txt` (Assets) holds `key = text` and `key.en = …`, `key.fr = …`; the "Show a dialogue" node reads them in the language of the phone or of a `langue` variable.
- A project opened in an **older** Yop2D loses nodes it does not know when saved. Update Yop2D before opening projects made with a newer version.

## Frequent recipes (beginner level)

- **Collect items**: give items a tag (`piece`). Event "If object touches Tag" (object A = player, tag = piece) → "Destroy object" on **the involved object** → "Add to variable" (score, 1) → "Set a property" on a text with value `="Score: " + score`.
- **Win after N items**: add a Condition `=score >= N`, then show a text, wait, and restart or go to the next scene.
- **Enemy that walks by itself**: behavior Patrol (no node). Touching it: event "If object touches Tag" with tag `ennemi` → flash, wait, "Restart the scene". Lives: variable `vies`, "Add to variable" (-1), Condition `=vies <= 0`.
- **Platformer**: ground and platforms have behavior Ground / wall; the hero has Platform character; joystick (object to move = hero) and a jump button.
- **Shoot**: the "Shoot" node with a model object; "Cooldown" limits the rate.
- **Next level**: one scene per level, an arrival zone, "Go to scene".
- **Save a score**: "Save variables" / "Load variables" nodes (they survive closing the game).

## Frequent mistakes to check first

1. Nothing happens: is the node connected to an event? Is the event in the Blueprint of the scene where the object is? (The HUD has its own.) Did the user save (💾)? Is the tag spelled the same everywhere (lowercase, no accent, commas between several)? Run "Check my game".
2. A button's text steals the touch: make it a child of the button.
3. A formula refers to an object by name but the object was renamed or is in a prefab: use the targeted object or a variable.
4. A character does not move: behavior chosen? Joystick object-to-move set? Jump button set?
5. Sprites look blurry: pixel art needs the "pixel art: sharp pixels" option in Game settings.
6. Wrong or missing node: the user may have an older Yop2D (check the [newer than …] marks).
7. A node is missing in the list on a school-mode device: School mode hides advanced nodes.
8. Music or sound does not play: the file must be in the project's Sounds; OGG is the safest format.

## Links

- Summary for AIs: {site}llms.txt
- Node reference in each language: {site}noeuds/en.html (also fr, es, de, it, pt, ru, zh, ja)
- Beginner guides: {site}guides/index.html (English: {site}guides/en/index.html)
- Examples (downloadable projects): {site}exemples/en.html
- Official site: {site}en/ (English home page is {site})
- Community: Discord, Telegram and Mastodon (links on the site).
"""


def sans_html(t):
    return re.sub(r"<[^>]+>", "", t).replace("&nbsp;", " ").replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").strip()


def guides():
    lignes = []
    for chemin in sorted(glob.glob(os.path.join(RACINE, "aide", "guides", "en", "*.json"))):
        with open(chemin, encoding="utf-8") as f:
            g = json.load(f)
        lignes.append(f"- {g['titre']}: {g['description']} ({SITE}{g['lien'].replace('guides/', 'guides/en/') if '/en/' not in g['lien'] else g['lien']})")
    return lignes


def noeuds():
    lignes = []
    for chemin in sorted(glob.glob(os.path.join(RACINE, "aide", "noeuds", "en", "*.json"))):
        with open(chemin, encoding="utf-8") as f:
            cat = json.load(f)
        lignes += ["", f"### {cat['categorie']}", ""]
        for n in cat["noeuds"]:
            marque = f" [newer than {n['nouveau']}]" if n.get("nouveau") else ""
            ligne = f"- **{n['nom']}**{marque}"
            if n.get("schema"):
                ligne += f" ({sans_html(n['schema'])})"
            role = sans_html(n.get("role", ""))
            # la phrase « pas encore dans la version… » est déjà dans la marque
            role = re.sub(r"^Not in the Google Play version [^:]+: available in the test version \(Discord\), coming with the next update\.\s*", "", role)
            if role:
                ligne += f": {role}"
            if n.get("exemple"):
                ligne += f" Example: {sans_html(n['exemple'])}"
            lignes.append(ligne)
    return lignes


def main():
    sortie = TEXTE.replace("{site}", SITE)
    sortie += "\n## Guides\n\n" + "\n".join(guides()) + "\n"
    sortie += "\n## Node reference (English names)\n" + "\n".join(noeuds()) + "\n"
    with open(os.path.join(RACINE, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write(sortie)
    print(f"llms-full.txt : {len(sortie) // 1024} Ko")


if __name__ == "__main__":
    main()
