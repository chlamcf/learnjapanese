"""
test_all.py — Comprehensive test suite for the Kanji Quiz App
Covers: schema, CRUD operations, quiz logic, and SM-2 spaced repetition.

Run with:  python test_all.py
Or with pytest:  pytest test_all.py -v
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sm2 import sm2_update, quality_from_correctness

TEST_DB = "test_database.db"


# ---------------------------------------------------------------------------
# Setup / teardown helpers
# ---------------------------------------------------------------------------

def fresh_db():
    """Create a clean test database with the real schema."""
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)
    conn = sqlite3.connect(TEST_DB)
    conn.row_factory = sqlite3.Row
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    return conn


def cleanup():
    if os.path.exists(TEST_DB):
        os.remove(TEST_DB)


# ---------------------------------------------------------------------------
# 1. Schema tests
# ---------------------------------------------------------------------------

def test_schema_creates_tables():
    conn = fresh_db()
    tables = {row["name"] for row in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()}
    assert "word" in tables, "word table missing"
    assert "quiz_attempt" in tables, "quiz_attempt table missing"
    conn.close()


def test_word_table_has_sm2_columns():
    conn = fresh_db()
    cols = {row["name"] for row in conn.execute("PRAGMA table_info(word)").fetchall()}
    for expected in ["ef", "repetition", "interval_days", "next_review"]:
        assert expected in cols, f"missing column: {expected}"
    conn.close()


def test_word_defaults():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("食べる", "たべる", "to eat", "JLPT N5")
    )
    conn.commit()
    row = conn.execute("SELECT * FROM word WHERE word = ?", ("食べる",)).fetchone()
    assert row["ef"] == 2.5, "default ef should be 2.5"
    assert row["repetition"] == 0, "default repetition should be 0"
    assert row["interval_days"] == 0, "default interval_days should be 0"
    assert row["next_review"] is not None, "next_review should default to a timestamp"
    conn.close()


# ---------------------------------------------------------------------------
# 2. CRUD tests
# ---------------------------------------------------------------------------

def test_create_word():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("飲む", "のむ", "to drink", "JLPT N5")
    )
    conn.commit()
    count = conn.execute("SELECT COUNT(*) AS c FROM word").fetchone()["c"]
    assert count == 1
    conn.close()


def test_read_word():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("行く", "いく", "to go", "JLPT N5")
    )
    conn.commit()
    row = conn.execute("SELECT * FROM word WHERE word = ?", ("行く",)).fetchone()
    assert row["reading"] == "いく"
    assert row["meaning"] == "to go"
    conn.close()


def test_update_word():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("来る", "くる", "to come", "JLPT N5")
    )
    conn.commit()
    word_id = conn.execute("SELECT id FROM word WHERE word = ?", ("来る",)).fetchone()["id"]
    conn.execute("UPDATE word SET meaning = ? WHERE id = ?", ("to arrive", word_id))
    conn.commit()
    row = conn.execute("SELECT meaning FROM word WHERE id = ?", (word_id,)).fetchone()
    assert row["meaning"] == "to arrive"
    conn.close()


def test_delete_word():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("見る", "みる", "to see", "JLPT N5")
    )
    conn.commit()
    word_id = conn.execute("SELECT id FROM word WHERE word = ?", ("見る",)).fetchone()["id"]
    conn.execute("DELETE FROM word WHERE id = ?", (word_id,))
    conn.commit()
    row = conn.execute("SELECT * FROM word WHERE id = ?", (word_id,)).fetchone()
    assert row is None
    conn.close()


# ---------------------------------------------------------------------------
# 3. Quiz attempt logging tests
# ---------------------------------------------------------------------------

def test_quiz_attempt_logs_correctly():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("読む", "よむ", "to read", "JLPT N5")
    )
    conn.commit()
    word_id = conn.execute("SELECT id FROM word WHERE word = ?", ("読む",)).fetchone()["id"]

    conn.execute("INSERT INTO quiz_attempt (word_id, is_correct) VALUES (?, ?)", (word_id, 1))
    conn.execute("INSERT INTO quiz_attempt (word_id, is_correct) VALUES (?, ?)", (word_id, 0))
    conn.commit()

    attempts = conn.execute("SELECT * FROM quiz_attempt WHERE word_id = ?", (word_id,)).fetchall()
    assert len(attempts) == 2
    assert attempts[0]["is_correct"] == 1
    assert attempts[1]["is_correct"] == 0
    conn.close()


def test_quiz_attempt_foreign_key_matches_word():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("書く", "かく", "to write", "JLPT N5")
    )
    conn.commit()
    word_id = conn.execute("SELECT id FROM word WHERE word = ?", ("書く",)).fetchone()["id"]
    conn.execute("INSERT INTO quiz_attempt (word_id, is_correct) VALUES (?, ?)", (word_id, 1))
    conn.commit()

    joined = conn.execute(
        """SELECT w.word, qa.is_correct FROM quiz_attempt qa
           JOIN word w ON w.id = qa.word_id WHERE qa.word_id = ?""",
        (word_id,)
    ).fetchone()
    assert joined["word"] == "書く"
    assert joined["is_correct"] == 1
    conn.close()


# ---------------------------------------------------------------------------
# 4. SM-2 algorithm unit tests
# ---------------------------------------------------------------------------

def test_sm2_first_correct_review_is_one_day():
    ef, rep, interval, next_review = sm2_update(2.5, 0, 0, quality=4)
    assert interval == 1
    assert rep == 1


def test_sm2_second_correct_review_is_six_days():
    ef, rep, interval, _ = sm2_update(2.5, 0, 0, quality=4)
    ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=4)
    assert interval == 6
    assert rep == 2


def test_sm2_third_correct_review_multiplies_by_ef():
    ef, rep, interval, _ = sm2_update(2.5, 0, 0, quality=4)
    ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=4)
    ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=4)
    assert rep == 3
    assert interval == int(6 * ef) or interval > 6


def test_sm2_wrong_answer_resets_repetition_and_interval():
    ef, rep, interval, _ = sm2_update(2.5, 0, 0, quality=4)
    ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=4)
    ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=2)  # wrong
    assert rep == 0, "repetition should reset to 0 on wrong answer"
    assert interval == 1, "interval should reset to 1 day on wrong answer"


def test_sm2_ef_never_drops_below_1_3():
    ef, rep, interval = 1.3, 5, 10
    for _ in range(10):
        ef, rep, interval, _ = sm2_update(ef, rep, interval, quality=0)
    assert ef >= 1.3, "EF floor of 1.3 must be respected"


def test_sm2_wrong_word_due_sooner_than_correct_word():
    ef_a, rep_a, int_a = 2.5, 0, 0  # always correct
    ef_b, rep_b, int_b = 2.5, 0, 0  # always incorrect
    next_a = next_b = None
    for _ in range(3):
        ef_a, rep_a, int_a, next_a = sm2_update(ef_a, rep_a, int_a, quality=4)
        ef_b, rep_b, int_b, next_b = sm2_update(ef_b, rep_b, int_b, quality=2)
    assert next_b < next_a, "incorrectly-answered word must be due before correctly-answered word"
    assert int_b == 1
    assert int_a > int_b


def test_quality_mapping_helper():
    assert quality_from_correctness(True) == 4
    assert quality_from_correctness(False) == 2


# ---------------------------------------------------------------------------
# 5. End-to-end simulation: full quiz cycle updates the word row correctly
# ---------------------------------------------------------------------------

def test_end_to_end_quiz_cycle_updates_word_row():
    conn = fresh_db()
    conn.execute(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        ("話す", "はなす", "to speak", "JLPT N5")
    )
    conn.commit()
    word = conn.execute("SELECT * FROM word WHERE word = ?", ("話す",)).fetchone()
    word_id = word["id"]

    is_correct = 0  # simulate a wrong answer
    conn.execute("INSERT INTO quiz_attempt (word_id, is_correct) VALUES (?, ?)", (word_id, is_correct))

    quality = quality_from_correctness(bool(is_correct))
    new_ef, new_rep, new_interval, next_review = sm2_update(
        word["ef"], word["repetition"], word["interval_days"], quality
    )
    conn.execute(
        "UPDATE word SET ef=?, repetition=?, interval_days=?, next_review=? WHERE id=?",
        (new_ef, new_rep, new_interval, next_review.isoformat(), word_id)
    )
    conn.commit()

    updated = conn.execute("SELECT * FROM word WHERE id = ?", (word_id,)).fetchone()
    assert updated["repetition"] == 0
    assert updated["interval_days"] == 1
    assert updated["next_review"] is not None
    conn.close()


# ---------------------------------------------------------------------------
# Simple runner (works without pytest installed)
# ---------------------------------------------------------------------------

def run_all_tests():
    test_functions = [obj for name, obj in list(globals().items())
                       if name.startswith("test_") and callable(obj)]
    passed, failed = 0, []

    for fn in test_functions:
        try:
            fn()
            print(f"PASS: {fn.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {fn.__name__} -> {e}")
            failed.append(fn.__name__)
        except Exception as e:
            print(f"ERROR: {fn.__name__} -> {e}")
            failed.append(fn.__name__)

    cleanup()
    print(f"\n{passed}/{len(test_functions)} tests passed.")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    run_all_tests()
