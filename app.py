from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import pymysql
import json
import re

app = Flask(__name__)
CORS(app)

# ── Database Config ──────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     "localhost",
    "user":     "root",
    "password": "bhavya",          # ← change to your MySQL password
    "database": "recipe_manager",
    "charset":  "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

# ── Helpers ───────────────────────────────────────────────────────────────────

def row_to_recipe(row):
    """Convert a DB row to a clean dict with parsed JSON fields."""
    if row is None:
        return None
    row["ingredients"]  = json.loads(row["ingredients"])  if isinstance(row["ingredients"],  str) else row["ingredients"]
    row["instructions"] = json.loads(row["instructions"]) if isinstance(row["instructions"], str) else row["instructions"]
    row["tags"]         = json.loads(row["tags"])         if isinstance(row["tags"],         str) else row["tags"]
    return row

# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/recipes", methods=["GET"])
def get_recipes():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM recipes ORDER BY name")
            rows = [row_to_recipe(r) for r in cur.fetchall()]
        return jsonify({"success": True, "recipes": rows, "count": len(rows)})
    finally:
        db.close()


@app.route("/api/recipes/<int:recipe_id>", methods=["GET"])
def get_recipe(recipe_id):
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM recipes WHERE id=%s", (recipe_id,))
            row = row_to_recipe(cur.fetchone())
        if not row:
            return jsonify({"success": False, "message": "Recipe not found"}), 404
        return jsonify({"success": True, "recipe": row})
    finally:
        db.close()


@app.route("/api/recipes/search", methods=["GET"])
def search_recipes():
    q         = request.args.get("q", "").strip()
    category  = request.args.get("category", "").strip()
    difficulty= request.args.get("difficulty", "").strip()

    db = get_db()
    try:
        with db.cursor() as cur:
            sql    = "SELECT * FROM recipes WHERE 1=1"
            params = []
            if q:
                sql += " AND (name LIKE %s OR cuisine LIKE %s OR description LIKE %s)"
                like = f"%{q}%"
                params += [like, like, like]
            if category:
                sql += " AND category=%s"
                params.append(category)
            if difficulty:
                sql += " AND difficulty=%s"
                params.append(difficulty)
            sql += " ORDER BY name"
            cur.execute(sql, params)
            rows = [row_to_recipe(r) for r in cur.fetchall()]
        return jsonify({"success": True, "recipes": rows, "count": len(rows)})
    finally:
        db.close()


@app.route("/api/categories", methods=["GET"])
def get_categories():
    db = get_db()
    try:
        with db.cursor() as cur:
            cur.execute("SELECT DISTINCT category FROM recipes ORDER BY category")
            cats = [r["category"] for r in cur.fetchall()]
        return jsonify({"success": True, "categories": cats})
    finally:
        db.close()


# ── Voice Assistant ────────────────────────────────────────────────────────────

def process_voice_command(transcript: str, db):
    """
    Parse the voice transcript and return a matching recipe + spoken reply.
    Handles commands like:
      "show me butter chicken"
      "how do I make tiramisu"
      "find Italian recipes"
      "what are easy recipes"
      "ingredients for pad thai"
    """
    t = transcript.lower().strip()

    # 1 ─ Fetch all recipe names for fuzzy matching
    with db.cursor() as cur:
        cur.execute("SELECT id, name, category, cuisine, difficulty, prep_time, cook_time FROM recipes")
        all_recipes = cur.fetchall()

    # 2 ─ Check if transcript mentions a specific recipe name
    matched_recipe = None
    best_score = 0
    for r in all_recipes:
        name_lower = r["name"].lower()
        # Count matching words
        words = re.findall(r'\w+', name_lower)
        score = sum(1 for w in words if w in t and len(w) > 2)
        if score > best_score:
            best_score = score
            matched_recipe = r

    # Fetch full recipe if we have a good match
    full_recipe = None
    if matched_recipe and best_score >= 1:
        with db.cursor() as cur:
            cur.execute("SELECT * FROM recipes WHERE id=%s", (matched_recipe["id"],))
            full_recipe = row_to_recipe(cur.fetchone())

    # 3 ─ Determine intent
    is_ingredients = any(w in t for w in ["ingredient", "ingredients", "need", "shopping"])
    is_steps       = any(w in t for w in ["step", "steps", "instruction", "how to", "make", "cook", "prepare", "recipe"])
    is_time        = any(w in t for w in ["time", "minutes", "long", "quick", "fast"])
    is_search_cat  = any(w in t for w in ["italian", "indian", "french", "thai", "japanese", "mexican", "american", "dessert"])
    is_easy        = any(w in t for w in ["easy", "simple", "beginner", "quick"])
    is_hard        = any(w in t for w in ["hard", "difficult", "complex", "advanced"])

    # 4 ─ Build response
    if full_recipe:
        name = full_recipe["name"]
        if is_ingredients:
            items = full_recipe["ingredients"]
            ing_text = ", ".join([f"{i['amount']} {i['name']}" for i in items[:6]])
            if len(items) > 6:
                ing_text += f", and {len(items)-6} more"
            voice_text = (
                f"For {name} you will need: {ing_text}. "
                f"Total time is {full_recipe['prep_time'] + full_recipe['cook_time']} minutes."
            )
        elif is_time:
            total = full_recipe["prep_time"] + full_recipe["cook_time"]
            voice_text = (
                f"{name} takes {full_recipe['prep_time']} minutes to prepare "
                f"and {full_recipe['cook_time']} minutes to cook, "
                f"so about {total} minutes in total."
            )
        else:
            steps = full_recipe["instructions"]
            step1 = steps[0]["step"] if steps else ""
            voice_text = (
                f"Here is the recipe for {name}! "
                f"It is a {full_recipe['difficulty'].lower()} {full_recipe['cuisine']} dish "
                f"that serves {full_recipe['servings']} people. "
                f"Let's start: {step1}"
            )
        return {"found": True, "recipe": full_recipe, "voice_response": voice_text, "intent": "recipe_detail"}

    # 5 ─ Category / difficulty search
    category_map = {
        "italian": "Italian", "indian": "Indian", "french": "French",
        "thai": "Thai", "japanese": "Japanese", "mexican": "Mexican",
        "american": "American", "dessert": "Dessert", "chinese": "Chinese",
    }
    found_cat = None
    for kw, cat in category_map.items():
        if kw in t:
            found_cat = cat
            break

    difficulty_filter = None
    if is_easy:
        difficulty_filter = "Easy"
    elif is_hard:
        difficulty_filter = "Hard"

    if found_cat or difficulty_filter:
        with db.cursor() as cur:
            sql = "SELECT * FROM recipes WHERE 1=1"
            params = []
            if found_cat:
                sql += " AND category=%s"
                params.append(found_cat)
            if difficulty_filter:
                sql += " AND difficulty=%s"
                params.append(difficulty_filter)
            sql += " ORDER BY RAND() LIMIT 6"
            cur.execute(sql, params)
            recipes = [row_to_recipe(r) for r in cur.fetchall()]

        label = found_cat or difficulty_filter
        voice_text = (
            f"I found {len(recipes)} {label} recipes for you. "
            f"How about {recipes[0]['name']} or {recipes[1]['name']}?" if len(recipes) >= 2
            else f"I found {recipes[0]['name']} for you!" if recipes
            else f"Sorry, I couldn't find any {label} recipes."
        )
        return {"found": True, "recipes": recipes, "voice_response": voice_text, "intent": "category_search"}

    # 6 ─ Fallback
    with db.cursor() as cur:
        cur.execute("SELECT * FROM recipes ORDER BY RAND() LIMIT 3")
        suggestions = [row_to_recipe(r) for r in cur.fetchall()]

    voice_text = (
        "I'm not sure what you're looking for. "
        f"Here are some suggestions: {', '.join(r['name'] for r in suggestions)}. "
        "Try saying something like 'show me butter chicken' or 'find Italian recipes'."
    )
    return {"found": False, "recipes": suggestions, "voice_response": voice_text, "intent": "fallback"}


@app.route("/api/voice", methods=["POST"])
def voice_endpoint():
    data       = request.get_json(silent=True) or {}
    transcript = data.get("transcript", "").strip()
    if not transcript:
        return jsonify({"success": False, "message": "No transcript provided"}), 400

    db = get_db()
    try:
        result = process_voice_command(transcript, db)
        result["success"]    = True
        result["transcript"] = transcript
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True, port=5000)