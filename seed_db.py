import sqlite3

def get_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    with open("schema.sql", "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("Database initialized with schema.")

def seed_words():
    starter_words = [
        ("食べる", "たべる", "to eat", "JLPT N5"),
        ("飲む", "のむ", "to drink", "JLPT N5"),
        ("行く", "いく", "to go", "JLPT N5"),
        ("来る", "くる", "to come", "JLPT N5"),
        ("見る", "みる", "to see / watch", "JLPT N5"),
        ("聞く", "きく", "to listen / ask", "JLPT N5"),
        ("話す", "はなす", "to speak", "JLPT N5"),
        ("読む", "よむ", "to read", "JLPT N5"),
        ("書く", "かく", "to write", "JLPT N5"),
        ("買う", "かう", "to buy", "JLPT N5"),
        ("学校", "がっこう", "school", "JLPT N5"),
        ("先生", "せんせい", "teacher", "JLPT N5"),
        ("学生", "がくせい", "student", "JLPT N5"),
        ("会社", "かいしゃ", "company", "JLPT N5"),
        ("電車", "でんしゃ", "train", "JLPT N5"),
        ("飛行機", "ひこうき", "airplane", "JLPT N5"),
        ("空港", "くうこう", "airport", "JLPT N4"),
        ("駅", "えき", "station", "JLPT N5"),
        ("旅行", "りょこう", "travel / trip", "JLPT N5"),
        ("地図", "ちず", "map", "JLPT N4"),
        ("水", "みず", "water", "JLPT N5"),
        ("お茶", "おちゃ", "tea", "JLPT N5"),
        ("米", "こめ", "rice", "JLPT N5"),
        ("肉", "にく", "meat", "JLPT N5"),
        ("魚", "さかな", "fish", "JLPT N5"),
        ("野菜", "やさい", "vegetable", "JLPT N5"),
        ("果物", "くだもの", "fruit", "JLPT N5"),
        ("朝ごはん", "あさごはん", "breakfast", "JLPT N5"),
        ("昼ごはん", "ひるごはん", "lunch", "JLPT N5"),
        ("晩ごはん", "ばんごはん", "dinner", "JLPT N5"),
        ("天気", "てんき", "weather", "JLPT N5"),
        ("雨", "あめ", "rain", "JLPT N5"),
        ("雪", "ゆき", "snow", "JLPT N5"),
        ("風", "かぜ", "wind", "JLPT N5"),
        ("暑い", "あつい", "hot (weather)", "JLPT N5"),
        ("寒い", "さむい", "cold (weather)", "JLPT N5"),
        ("大きい", "おおきい", "big", "JLPT N5"),
        ("小さい", "ちいさい", "small", "JLPT N5"),
        ("新しい", "あたらしい", "new", "JLPT N5"),
        ("古い", "ふるい", "old", "JLPT N5"),
    ]
    conn = get_connection()
    conn.executemany(
        "INSERT INTO word (word, reading, meaning, category) VALUES (?, ?, ?, ?)",
        starter_words
    )
    conn.commit()
    conn.close()
    print(f"Inserted {len(starter_words)} starter words.")

if __name__ == "__main__":
    init_db()
    seed_words()