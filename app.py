import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, g, session
import sqlite3
from sm2 import sm2_update, quality_from_correctness
import json

app = Flask(__name__)
app.secret_key = "dev-secret-key"
DATABASE = "database.db"

JLPT_LEVELS = ["N5", "N4", "N3", "N2", "N1"]

def get_db():
    """Open a new database connection if one doesn't already exist
    for the current request context, and reuse it if it does."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

# ---------- READ: list all words ----------
@app.route("/")
def index():
    db = get_db()
    level = request.args.get("level", "").strip()

    base_query = """
        SELECT *,
        CASE category
            WHEN 'JLPT N5' THEN 1
            WHEN 'JLPT N4' THEN 2
            WHEN 'JLPT N3' THEN 3
            WHEN 'JLPT N2' THEN 4
            WHEN 'JLPT N1' THEN 5
            ELSE 6
        END AS lvl_order
        FROM word
    """

    if level in JLPT_LEVELS:
        query = base_query + " WHERE category = ? ORDER BY lvl_order ASC, id DESC"
        words = db.execute(query, (f"JLPT {level}",)).fetchall()
    else:
        query = base_query + " ORDER BY lvl_order ASC, id DESC"
        words = db.execute(query).fetchall()

    return render_template("index.html", words=words, jlpt_levels=JLPT_LEVELS, selected_level=level)

# ---------- CREATE: add a new word ----------
@app.route("/add", methods=["GET", "POST"])
def add_word():
    if request.method == "POST":
        word = request.form["word"].strip()
        reading = request.form["reading"].strip()
        meaning = request.form["meaning"].strip()
        level = request.form.get("category", "").strip()
        category = f"JLPT {level}" if level in JLPT_LEVELS else ""

        if word and reading and meaning:
            db = get_db()
            db.execute(
                "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
                (word, reading, meaning, category),
            )
            db.commit()
            return redirect(url_for("index"))

    return render_template("add_word.html", jlpt_levels=JLPT_LEVELS)

# ---------- UPDATE: edit an existing word ----------
@app.route("/edit/<int:word_id>", methods=["GET", "POST"])
def edit_word(word_id):
    db = get_db()
    word = db.execute("SELECT * FROM word WHERE id = ?", (word_id,)).fetchone()

    if word is None:
        return redirect(url_for("index"))

    if request.method == "POST":
        new_word = request.form["word"].strip()
        new_reading = request.form["reading"].strip()
        new_meaning = request.form["meaning"].strip()
        new_level = request.form.get("category", "").strip()
        new_category = f"JLPT {new_level}" if new_level in JLPT_LEVELS else ""

        db.execute(
            "UPDATE word SET word = ?, reading = ?, meaning = ?, category = ? WHERE id = ?",
            (new_word, new_reading, new_meaning, new_category, word_id),
        )
        db.commit()
        return redirect(url_for("index"))

    current_level = word["category"].replace("JLPT ", "") if word["category"] else ""
    return render_template("edit_word.html", word=word, jlpt_levels=JLPT_LEVELS, current_level=current_level)

# ---------- DELETE: remove a word ----------
@app.route("/delete/<int:word_id>", methods=["POST"])
def delete_word(word_id):
    db = get_db()
    db.execute("DELETE FROM word WHERE id = ?", (word_id,))
    db.commit()
    return redirect(url_for("index"))

app.secret_key = "dev-secret-key"

@app.route("/quiz")
def quiz():
    db = get_db()
    now = datetime.now().isoformat()

    due_words = db.execute(
        "SELECT * FROM word WHERE next_review <= ? ORDER BY next_review ASC",
        (now,)
    ).fetchall()

    all_words = db.execute("SELECT * FROM word").fetchall()
    if len(all_words) < 4:
        return "Add at least 4 words before starting a quiz."

    correct_word = due_words[0] if due_words else random.choice(all_words)

    if correct_word["distractors"]:
        fake_readings = [r.strip() for r in correct_word["distractors"].split(",") if r.strip()][:3]
        choices = [{"id": -(i + 1), "reading": r} for i, r in enumerate(fake_readings)]
        choices.append({"id": correct_word["id"], "reading": correct_word["reading"]})
    else:
        distractors = random.sample(
            [w for w in all_words if w["id"] != correct_word["id"]],
            min(3, len(all_words) - 1)
        )
        choices = [{"id": w["id"], "reading": w["reading"]} for w in distractors]
        choices.append({"id": correct_word["id"], "reading": correct_word["reading"]})

    random.shuffle(choices)

    session.setdefault("score", {"correct": 0, "incorrect": 0})

    return render_template(
        "quiz.html",
        word=correct_word,
        choices=choices,
        score=session["score"],
        due_count=len(due_words)
    )

@app.route("/quiz/answer", methods=["POST"])
def quiz_answer():
    db = get_db()
    word_id = int(request.form["word_id"])
    selected_id = int(request.form["selected_id"])
    is_correct = 1 if word_id == selected_id else 0

    db.execute(
        "INSERT INTO quiz_attempt (word_id, is_correct) VALUES (?, ?)",
        (word_id, is_correct)
    )

    word = db.execute("SELECT * FROM word WHERE id = ?", (word_id,)).fetchone()
    quality = quality_from_correctness(bool(is_correct))

    new_ef, new_rep, new_interval, next_review = sm2_update(
        ef=word["ef"],
        repetition=word["repetition"],
        interval_days=word["interval_days"],
        quality=quality
    )

    db.execute(
        """UPDATE word
           SET ef = ?, repetition = ?, interval_days = ?, next_review = ?
           WHERE id = ?""",
        (new_ef, new_rep, new_interval, next_review.isoformat(), word_id)
    )
    db.commit()

    session.setdefault("score", {"correct": 0, "incorrect": 0})
    if is_correct:
        session["score"]["correct"] += 1
    else:
        session["score"]["incorrect"] += 1
    session.modified = True

    return render_template(
        "quiz_feedback.html",
        is_correct=is_correct,
        word=word,
        next_review=next_review
    )

@app.route("/quiz/end")
def quiz_end():
    score = session.pop("score", {"correct": 0, "incorrect": 0})
    return render_template("quiz_summary.html", score=score)

@app.route("/stats")
def stats():
    db = get_db()
    rows = db.execute("""
        SELECT DATE(answered_at) AS day,
               SUM(is_correct) AS correct,
               SUM(1 - is_correct) AS incorrect
        FROM quiz_attempt
        GROUP BY day
        ORDER BY day ASC
    """).fetchall()

    labels = [r["day"] for r in rows]
    correct = [r["correct"] for r in rows]
    incorrect = [r["incorrect"] for r in rows]

    total_words = db.execute("SELECT COUNT(*) AS c FROM word").fetchone()["c"]
    words_reviewed = db.execute(
        "SELECT COUNT(DISTINCT word_id) AS c FROM quiz_attempt"
    ).fetchone()["c"]

    return render_template(
        "stats.html",
        labels=json.dumps(labels),
        correct=json.dumps(correct),
        incorrect=json.dumps(incorrect),
        total_words=total_words,
        words_reviewed=words_reviewed,
    )

if __name__ == "__main__": 
    app.run(debug=True)
