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

- **Never answer "this is not possible in Yop2D" before reading the sections "Which tool for which need" and "Frequent mistakes" below.** Many things that look impossible have a ready solution there (for example using objects of another scene, see below). If you still find no way, say you are not sure and suggest the Yop2D Discord instead of saying it is impossible.
- Yop2D is a **no-code** 2D game engine for Android. Users build games by touching and connecting **nodes** (a visual script called the **Blueprint**). **Never write programming code** (no Java, no Python, no Unity or Godot code). Give numbered steps using the exact names of buttons, nodes and settings.
- **Use only the nodes listed at the end of this file.** Never invent a node, a setting or a button. If you are not sure something exists, say so and suggest asking on the Yop2D Discord.
- Node names change with the interface language. The list below uses the English names; the table "Node names in every language" at the end gives the exact name in the 8 other languages. **Reply in the user's language and copy the node names from that table: never translate a name yourself.** The names of a node's settings and exits (for example "Loaded" / "No save found") are also translated in the app: for them, point the user to the node reference in their language ({site}noeuds/<lang>.html, lang = fr, es, de, it, pt, ru, zh, ja) or tell them to read the names shown in the node window; do not leave English words in a French, Spanish or German answer. Do not confuse "Go to a point (path)" / "Go to an object (path)" (automatic pathfinding) with "Follow the path" (a hand-made path from the Assets Path editor). Do not assume the user has the newest version: the version they tell you decides which nodes exist.
- Some nodes are marked **[newer than 1.0.1142]**: they are NOT in the public Google Play version (which is 1.0.1142), only in the Discord test versions. **Version rule: the Google Play version is 1.0.1142. Any version number ABOVE 1142 (for example 1.0.1232) is a test version and DOES contain all the nodes marked [newer than 1.0.1142].** So if the user says their version is higher than 1142, offer those nodes first (for example Path editor + "Follow the path", or "Play movement (steps)") and never say that the version is the Google Play one. If the version is 1142 or lower, say the node needs an update or the test version, and give the alternative.
- The user is usually a beginner on a **phone or tablet** (touch screen, no mouse). Keep answers short and simple. Do not use jargon without explaining it.
- Ask for what you need: the Yop2D version (start screen), which scene the node is in, the exact settings of the node, and what they expected versus what happens. The best thing a user can paste is the text of their Blueprint: in the Blueprint, the `{ }` button shows the nodes of the current scene as text.
- Always suggest the built-in checks when something does not work: **menu ☰ → Check my game** (lists missing variables, objects, files and unconnected nodes), and the detailed log (start screen → 🐞 button → tick "detailed log", play, then Copy).
- If the question is about making a whole kind of game, point to the matching guide (list below) before improvising.

{NOMS_FREQUENTS}

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
- A node only works in the scene whose Blueprint contains it (the Blueprint button shows the scene name; the HUD has its own Blueprint, where button clicks must be). **But a node CAN act on objects of another scene** (for example the HUD from the game scene): use the global logic, a tag, or a global variable with the event "When Variable Changes" (details in "Frequent mistakes", item 9). There is also a **global logic** that runs in every scene (the first line of the scene list in the Blueprint) and **My nodes** (reusable nodes you build yourself, with settings).
- To react to a click on several objects, use the target `tag:name`. For several objects at once in touch events, put the same tag on all.
- Prefabs: objects inside a prefab are renamed when placed ("_2"), so formulas must not name them; read variables of the object the node targets.
- Dialogues and translations: `dialogues.txt` (Assets) holds `key = text` and `key.en = …`, `key.fr = …`; the "Show a dialogue" node reads them in the language of the phone or of a `langue` variable.
- A project opened in an **older** Yop2D loses nodes it does not know when saved. Update Yop2D before opening projects made with a newer version.

## Which tool for which need (answer with these, do not invent nodes)

Always use the exact node names of the node reference. A node marked `[newer than 1.0.1142]` is NOT in the Google Play version: say so and tell the user to update Yop2D (or use the alternative given here).

**Moving things**
- Enemy that walks by itself on a platform: behavior **Patrol (back and forth)** in the object's Behavior window. It turns around at the edge of the ground or at a wall. It has no pause and no fixed points.
- Go back and forth between two points WITH a pause at each end: **Play movement (steps)** `[newer than 1.0.1142]` with a movement made in the Assets "Movement" editor (each step has a duration; looping), or **Follow the path** `[newer than 1.0.1142]` with a path from the Assets "Path" editor (each point has a waiting time). On the Play Store version: "Glide to" point B, "Wait", "Glide to" point A, "Wait", then "Call event" with a "Local Event" that restarts the same chain (avoid a "Repeat" with a fixed time, it drifts when the pauses change).
- Enemy that chases the hero: **Chase an object**; flee: **Flee an object**. On a grid/maze (walls, obstacles): **Go to an object (path)**, NOT "Chase an object" (which goes in a straight line and gets stuck on walls). Put it once, under "On Start" or an event: the path is recalculated automatically each time the target changes cell, so do not relaunch it with "Repeat" or "Every frame". "Stop the path" stops it. Walls must be solid (solid tiles of a tile layer, or fixed physical objects). The official example "Maze chase" does exactly this.
- Move to the finger: **Glide to** with `=doigt.x` / `=doigt.y`.
- Moving platform / lift: behavior **Elevator (back and forth)** (Behavior window) or a movement (steps) on a Ground object with "Carries what stands on it".
- Bouncing ball without gravity: no ready behavior; use variables `vx` / `vy` with "Push object" and "Collision A/B" (see the guide "Breakout").
- Camera: **Follow with camera**, **Camera limits** (enlarge them when the level is longer!), **Scroll the camera with a finger**.

**Fighting and lives**
- Touching an enemy hurts: event **If object touches Tag**, then "Add to Variable" (`vies`, -1) and a Condition `=vies <= 0`.
- Health bar, damage, healing: **Give health to the object**, **Deal damage**, **Heal**; health is the object variable `vie`.
- Turn-based tactics on a grid: **Go to the next turn**, **Show reachable cells**, **Attack**, **Give a unit sheet**, **Choose a target**, **Play like a computer (AI)**. If the attack range/zone does not appear: check that the range number is not 0 or empty, that the minimum range is smaller than the range, that a "custom" shape has positions written, that the zone name is not the same as the movement zone (the second replaces the first), and that nothing calls **Hide the cells** right after.

**Using objects of another scene (HUD, other level)**
- Pick them with the Blueprint button that shows the scene name → "Global logic (all scenes)" (its object list contains every scene's objects), or give them a tag and target `# tag` from any scene, or share a global variable and react to it with the event "When Variable Changes". Never say it is impossible.

**Showing and saving things**
- Score or any number on screen: "Modify Text" / "Set a property" on a text with `="Score: " + score`.
- Keep the score after closing the game: **Save variables to a file** then **Load variables from a file** (not "Save state", which only lasts until the game is closed).
- Dialogues in several languages: `dialogues.txt` + **Show dialogue**.
- Story with choices (visual novel): **Say a line**, **Ask a choice**, **Change the background**, **Story title screen**.
- Day/night, torches, shadows: **Day and night cycle**, **Light source (torch, lantern…)**, **Shadow under the object** (or the Shadow checkbox in the Inspector) `[newer than 1.0.1142]`.

**Sound and effects**
- Music at start: event **On Start** → **Play music** (loop). Own music: Assets → Music editor. Own sound effects: Assets → "Sound FX" editor.
- Explosion, sparks, rain: **Particle effect**; screen shake: **Camera shake**; slow motion: **Game speed (slow motion)**.

**Recipes**
- **Collect items**: give items a tag (`piece`). Event "If object touches Tag" (object A = player, tag = piece) → "Destroy Object" on **the involved object** → "Add to Variable" (score, 1) → "Set a property" on a text with value `="Score: " + score`.
- **Win after N items**: Condition `=score >= N`, then show a text, "Wait", and "Restart the scene" or "Next scene".
- **Platformer**: ground and platforms have behavior Ground / wall; the hero has Platform character; joystick (object to move = hero) and a jump button.
- **Shoot**: **Shoot an object** with a model object; **Cooldown** limits the rate.
- **Next level**: one scene per level, an arrival zone, "Go to scene".
- **Reuse a set of nodes**: Resources → My nodes (then "Run one of my nodes", with settings).
- **Tower defense / paths**: **Follow the path** `[newer than 1.0.1142]` with a path that has a crossroads.

## Frequent mistakes to check first

1. Nothing happens: is the node connected to an event? Is the event in the Blueprint of the scene where the object is? (The HUD has its own.) Did the user save (💾)? Is the tag spelled the same everywhere (lowercase, no accent, commas between several)? Run "Check my game".
2. A button's text steals the touch: make it a child of the button.
3. A formula refers to an object by name but the object was renamed or is in a prefab: use the targeted object or a variable.
4. A character does not move: behavior chosen? Joystick object-to-move set? Jump button set?
5. Sprites look blurry: pixel art needs the "pixel art: sharp pixels" option in Game settings.
6. Wrong or missing node: the user may have an older Yop2D (check the [newer than …] marks).
7. A node is missing in the list on a school-mode device: School mode hides advanced nodes.
8. Music or sound does not play: the file must be in the project's Sounds; OGG is the safest format.
9. "How do I select an object that is in another scene (for example the HUD)?" The node list "On what?" only shows the objects of the scene whose Blueprint is open; the HUD has its own Blueprint and objects. Three ways: (a) in the Blueprint, tap the scene-name button at the top and choose "Global logic (all scenes)": there the list shows the objects of every scene, HUD included; (b) give the HUD object a tag (Inspector → "For nodes" part) and in the game scene choose the group Tags → "# tag" (tags of all scenes are listed); (c) cleanest: the game scene changes a global variable (for example `score`) and the HUD's own Blueprint uses the event "When Variable Changes" to update its text with `="Score: " + score` (global variables are shared by all scenes).

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


LANGUES = ["en", "fr", "es", "de", "it", "pt", "ru", "zh", "ja"]


def noms_langues():
    """Tableau : nom anglais du nœud -> son nom exact dans chacune des 8 autres langues."""
    lignes = []
    for chemin in sorted(glob.glob(os.path.join(RACINE, "aide", "noeuds", "en", "*.json"))):
        fichier = os.path.basename(chemin)
        cats = {}
        for lg in LANGUES:
            with open(os.path.join(RACINE, "aide", "noeuds", lg, fichier), encoding="utf-8") as f:
                cats[lg] = json.load(f)
        lignes += ["", f"### {cats['en']['categorie']}", ""]
        for i, n in enumerate(cats["en"]["noeuds"]):
            autres = " | ".join(f"{lg}: {cats[lg]['noeuds'][i]['nom']}" for lg in LANGUES[1:])
            lignes.append(f"- **{n['nom']}** → {autres}")
    return lignes


FREQUENTS = [
    "On Start", "Every frame", "On Object Click", "If object touches Tag", "Collision A/B", "Back button pressed",
    "Move Object", "Push object", "Set a property", "Destroy Object", "Give a tag (object family)", "Create a copy of the object",
    "Shoot an object", "Add to Variable", "Modify Variable", "Condition", "If / Else", "Wait", "Repeat", "Modify Text",
    "Play sound", "Play music", "Go to scene", "Restart the scene", "Follow with camera", "Glide to", "Chase an object",
    "Play animation", "Save variables to a file", "Load variables from a file", "Show dialogue", "Say a line", "Ask a choice",
    "Run one of my nodes", "Call event", "Local Event", "Follow the path", "Play movement (steps)",
    "Stop the movement", "Stop following the path", "Spin the object continuously", "Flee an object", "Go to an object (path)",
    "Go to a point (path)", "Stop the path", "Place on a cell (column, row)", "Go to the cell (path)", "Change the behavior",
    "Show reachable cells", "Hide the cells", "If the cell is reachable", "Give a unit sheet", "Attack", "Deal damage", "Heal",
    "Choose a target", "Go to the next turn", "If it is the turn of…", "Mark as having played", "Play like a computer (AI)",
    "Select the object", "Deselect", "If an object is selected", "Give health to the object", "Destroy by Tag", "Create object",
    "Random number", "Keep a variable between two values", "Change Image", "Bring to front / send back", "Grow / shrink", "Blink",
    "If joystick", "If on ground", "If off-screen", "Cooldown", "Stop animation", "Stop music", "Open a HUD", "Close the HUD",
    "Place a copy of a scene", "Next scene", "Go to scene (by name)", "Go to scene with a transition", "Camera limits",
    "Scroll the camera with a finger", "Camera shake", "Screen flash", "Particle effect", "Game speed (slow motion)", "Pause the game",
    "Resume the game", "Day and night cycle", "Light source (torch, lantern…)", "Shadow under the object", "Screen filter",
    "Atmosphere (rain, snow, night…)", "Set the physics world", "Adjust a physics object", "Push (physics force)", "Set the speed (physics)",
    "Launch (angle and speed)", "If the physics object…", "Link two objects", "Say a line", "Ask a choice", "Change the background",
    "Show / hide a character", "End the story",
]


def noms_frequents():
    """Les noms les plus utilisés, dans les 9 langues (même ordre dans tous les fichiers d'aide)."""
    tables = {lg: {} for lg in LANGUES}
    for chemin in sorted(glob.glob(os.path.join(RACINE, "aide", "noeuds", "en", "*.json"))):
        fichier = os.path.basename(chemin)
        cats = {}
        for lg in LANGUES:
            with open(os.path.join(RACINE, "aide", "noeuds", lg, fichier), encoding="utf-8") as f:
                cats[lg] = json.load(f)
        for i, n in enumerate(cats["en"]["noeuds"]):
            for lg in LANGUES:
                tables[lg].setdefault(n["nom"], cats[lg]["noeuds"][i]["nom"])
    lignes = ["## The most used node names, in every language (about 140 nodes)",
              "",
              "Copy these names exactly. Do NOT add or change small words (for example the French name is "
              "\"Sauvegarder les variables dans un fichier\", not \"Sauvegarder des variables…\"; \"Ajouter à Variable\", not "
              "\"Ajouter à la variable\"). In French the word is \"nœud\" (not \"node\"). The full table is at the end of this file.",
              ""]
    for en in FREQUENTS:
        if en not in tables["en"]:
            continue
        autres = " | ".join(f"{lg}: {tables[lg][en]}" for lg in LANGUES[1:])
        lignes.append(f"- **{en}** → {autres}")
    return "\n".join(lignes)


def noms_interface():
    """Boutons / fenêtres de l'appli dans les 9 langues (aide/source/noms_interface.json, fait par extraire_noms_interface.py)."""
    chemin = os.path.join(RACINE, "aide", "source", "noms_interface.json")
    if not os.path.exists(chemin):
        return ""
    with open(chemin, encoding="utf-8") as f:
        items = json.load(f)
    lignes = ["## App buttons and windows, in every language", "",
              "Use these exact names for the buttons and menus of the app (never translate them yourself). English first, then fr, es, de, it, pt, ru, zh, ja.", ""]
    for it in items:
        n = it["noms"]
        autres = " | ".join(f"{lg}: {n[lg]}" for lg in LANGUES[1:])
        lignes.append(f"- {it['role']}: **{n['en']}** → fr: {n['fr']} | " + autres.split(" | ", 0)[0].replace(f"fr: {n['fr']} | ", "") if False else
                      f"- {it['role']}: **{n['en']}** → " + " | ".join(f"{lg}: {n[lg]}" for lg in ["fr", "es", "de", "it", "pt", "ru", "zh", "ja"]))
    return "\n".join(lignes)


def main():
    sortie = TEXTE.replace("{site}", SITE).replace("{NOMS_FREQUENTS}", noms_frequents() + "\n\n" + noms_interface())
    sortie += "\n## Guides\n\n" + "\n".join(guides()) + "\n"
    sortie += ("\n## Node names in every language\n\n"
               "The user's Yop2D may be in any of 9 languages. When the user writes in another language, use the node names "
               "from this table and never translate a node name yourself. English name first, then the exact name in "
               "fr, es, de, it, pt, ru, zh, ja.\n" + "\n".join(noms_langues()) + "\n")
    sortie += "\n## Node reference (English names)\n" + "\n".join(noeuds()) + "\n"
    with open(os.path.join(RACINE, "llms-full.txt"), "w", encoding="utf-8") as f:
        f.write(sortie)
    print(f"llms-full.txt : {len(sortie) // 1024} Ko")


if __name__ == "__main__":
    main()
