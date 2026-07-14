import sqlite3

conn = sqlite3.connect("database.db")
conn.row_factory = sqlite3.Row
cur = conn.cursor()

cur.execute("SELECT * FROM word")
rows = cur.fetchall()

print(f"Total words in database: {len(rows)}\n")
for row in rows[:10]:
    print(f"ID {row['id']}: {row['word']} ({row['reading']}) - {row['meaning']} [{row['category']}]")

conn.close()