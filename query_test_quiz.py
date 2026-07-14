import sqlite3
conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row

rows = conn.execute(
    "SELECT * FROM quiz_attempt ORDER BY answered_at DESC LIMIT 10"
).fetchall()

print(f"Showing last {len(rows)} quiz attempts:\n")
for r in rows:
    status = "correct" if r["is_correct"] else "incorrect"
    print(f"word_id {r['word_id']} -> {status} at {r['answered_at']}")

conn.close()