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
        # word, reading, meaning, category, distractors
        ("食べる", "たべる", "to eat", "JLPT N5", "あべる,とべる,しべる"),
        ("飲む", "のむ", "to drink", "JLPT N5", "よむ,すむ,たのむ"),
        ("行く", "いく", "to go", "JLPT N5", "つづく,さく,まく"),
        ("来る", "くる", "to come", "JLPT N5", "かえる,はいる,とおる"),
        ("見る", "みる", "to see / watch", "JLPT N5", "きる,おりる,おきる"),
        ("聞く", "きく", "to listen / ask", "JLPT N5", "なく,とく,ひく"),
        ("話す", "はなす", "to speak", "JLPT N5", "だす,おす,けす"),
        ("読む", "よむ", "to read", "JLPT N5", "のむ,すむ,たのむ"),
        ("書く", "かく", "to write", "JLPT N5", "さく,まく,とく"),
        ("買う", "かう", "to buy", "JLPT N5", "あう,すう,つかう"),
        ("学校", "がっこう", "school", "JLPT N5", "がくせい,せんせい,まなぶ"),
        ("先生", "せんせい", "teacher", "JLPT N5", "がくせい,がっこう,あおい"),
        ("学生", "がくせい", "student", "JLPT N5", "せんせい,がっこう,うまれる"),
        ("会社", "かいしゃ", "company", "JLPT N5", "やしろ,しゃかい,いまべつ"),
        ("電車", "でんしゃ", "train", "JLPT N5", "れっしゃ,うんてん,てんしゃ"),
        ("飛行機", "ひこうき", "airplane", "JLPT N5", "くうこう,とぶき,ひごうき"),
        ("空港", "くうこう", "airport", "JLPT N4", "ぐうこう,くうごう,ぐうごう"),
        ("駅", "えき", "station", "JLPT N5", "うまや,てつどう,えぎ"),
        ("旅行", "りょこう", "travel / trip", "JLPT N5", "たび,りょうこう,りょごう"),
        ("地図", "ちず", "map", "JLPT N4", "じず,ちつ,ちづ"),
        ("水", "みず", "water", "JLPT N5", "みす,みつ,みづ"),
        ("お茶", "おちゃ", "tea", "JLPT N5", "おしゃ,おれい,おむすび"),
        ("米", "こめ", "rice", "JLPT N5", "こみ,こむ,こま"),
        ("肉", "にく", "meat", "JLPT N5", "にぐ,さけ,つむ"),
        ("魚", "さかな", "fish", "JLPT N5", "さかた,ちょう,さかい"),
        ("野菜", "やさい", "vegetable", "JLPT N5", "くだもの,やざい,くたもの"),
        ("果物", "くだもの", "fruit", "JLPT N5", "くたもの,やさい,やざい"),
        ("朝ごはん", "あさごはん", "breakfast", "JLPT N5", "ひるごはん,ばんこはん,なにごはん"),
        ("昼ごはん", "ひるごはん", "lunch", "JLPT N5", "あさごはん,ばんごはん,よるごはん"),
        ("晩ごはん", "ばんごはん", "dinner", "JLPT N5", "あさごはん,ひるごはん,さきごはん"),
        ("天気", "てんき", "weather", "JLPT N5", "でんぎ,てんぎ,でんき"),
        ("雨", "あめ", "rain", "JLPT N5", "だめ,あみ,あむ"),
        ("雪", "ゆき", "snow", "JLPT N5", "ゆく,ゆつ,ゆち"),
        ("風", "かぜ", "wind", "JLPT N5", "かせ,がせ,がぜ"),
        ("暑い", "あつい", "hot (weather)", "JLPT N5", "しろい,くろい,ながい"),
        ("寒い", "さむい", "cold (weather)", "JLPT N5", "ふとい,まるい,あかい"),
        ("大きい", "おおきい", "big", "JLPT N5", "おきい,あたらきい,つるきい"),
        ("小さい", "ちいさい", "small", "JLPT N5", "まなさい,ふさい,そさい"),
        ("新しい", "あたらしい", "new", "JLPT N5", "おいしい,あらたしい,いおしい"),
        ("古い", "ふるい", "old", "JLPT N5", "あつい,さむい,ながい"),
        ("憧れる", "あこがれる", "to admire / long for", "JLPT N2", "わすれる,うまれる,おくれる"),
        ("謝る", "あやまる", "to apologize", "JLPT N4", "がんばる,まがる,あつまる"),
        ("旅", "たび", "trip / journey", "JLPT N5", "たぶ,りょこう,せん"),
        ("恋", "こい", "love", "JLPT N3", "こう,れんあい,こころ"),
        ("少年", "しょうねん", "boy (teenager)", "JLPT N3", "しょねん,しょうねい,しょねい"),
        ("花火", "はなび", "fireworks", "JLPT N3", "はなか,はなひ,はなが"),
        ("小雨", "こさめ", "light rain", "JLPT N2", "こざめ,こあめ,こすめ"),
        ("結ぶ", "むすぶ", "to tie / bind", "JLPT N3", "よぶ,あそぶ,えらぶ"),
        ("選択", "せんたく", "choice / selection", "JLPT N3", "せいたく,せいたつ,せんたつ"),
        ("政", "まつりごと", "government", "JLPT N1", "まづりごと,まつりこと,まづりこと"),
        ("取る", "とる", "to take", "JLPT N5", "はしる,とまる,おくる"),
        ("超える", "こえる", "to exceed", "JLPT N3", "ひえる,きえる,はえる"),
        ("叫ぶ", "さけぶ", "to shout", "JLPT N3", "よぶ,あそぶ,えらぶ"),
        ("痛む", "いたむ", "to hurt / ache", "JLPT N3", "たのむ,すすむ,すむ"),
        ("悩む", "なやむ", "to worry", "JLPT N3", "いたむ,たのむ,すむ"),
        ("続く", "つづく", "to continue", "JLPT N4", "さく,まく,きく"),
        ("離す", "はなす", "to separate", "JLPT N3", "だす,おす,けす"),
        ("信じる", "しんじる", "to believe", "JLPT N3", "かんじる,まじる,とじる"),
        ("違う", "ちがう", "to differ / be wrong", "JLPT N4", "かう,あう,つかう"),
        ("埋める", "うめる", "to bury", "JLPT N2", "あつめる,きめる,とめる"),
        ("行う", "おこなう", "to conduct / carry out", "JLPT N3", "うたう,ねがう,さそう"),
        ("瞳", "ひとみ", "pupil (of the eye)", "JLPT N2", "ひとめ,まなざし,ひとつ"),
        ("眩しい", "まぶしい", "dazzling", "JLPT N2", "たのしい,かなしい,こいしい"),
        ("狭い", "せまい", "narrow", "JLPT N4", "あまい,よわい,かるい"),
        ("描く", "かく", "to draw / depict", "JLPT N3", "さく,まく,なく"),
        ("揺れる", "ゆれる", "to sway / shake", "JLPT N2", "わかれる,たおれる,なれる"),
        ("消す", "けす", "to erase / turn off", "JLPT N4", "だす,おす,かす"),
        ("一人", "ひとり", "one person", "JLPT N5", "いちじん,いちひと,ひとつ"),
        ("二つ", "ふたつ", "two (things)", "JLPT N5", "みっつ,よっつ,いつつ"),
        ("未来", "みらい", "future", "JLPT N4", "げんざい,さき,みらん"),
        ("現在", "げんざい", "present (time)", "JLPT N4", "みらい,けんさい,いま"),
        ("戦う", "たたかう", "to fight", "JLPT N3", "うたう,さそう,ねがう"),
        ("結局", "けっきょく", "in the end", "JLPT N3", "けつきょく,けきょく,けつぎょく"),
        ("優しい", "やさしい", "kind / gentle", "JLPT N4", "たのしい,かなしい,いそがしい"),
        ("騙す", "だます", "to deceive", "JLPT N2", "なおす,かす,はなす"),
        ("遠慮", "えんりょ", "reservation / restraint", "JLPT N2", "えんがる,えんゆ,えんりょう"),
        ("磨く", "みがく", "to polish", "JLPT N3", "あく,やく,なく"),
        ("守る", "まもる", "to protect", "JLPT N3", "がんばる,まがる,あつまる"),
        ("溢れる", "あふれる", "to overflow", "JLPT N2", "こわれる,つかれる,たおれる"),
        ("誠", "まこと", "sincerity / truth", "JLPT N1", "まこん,まさと,まもり"),
        ("航空", "こうくう", "aviation", "JLPT N2", "こうくん,こうこう,ごうくう"),
        ("全て", "すべて", "all / everything", "JLPT N3", "したて,まかて,おきて"),
        ("笑う", "わらう", "to laugh", "JLPT N4", "かよう,ならう,つかう"),
        ("幸せ", "しあわせ", "happiness", "JLPT N4", "にあわせ,おわらせ,きあわせ"),
        ("場所", "ばしょ", "place", "JLPT N5", "ばんしょ,ばしょう,はしょ"),
        ("場合", "ばあい", "case / situation", "JLPT N4", "ばわい,ばがい,はあい"),
        ("紡ぐ", "つむぐ", "to spin (thread)", "JLPT N1", "つなぐ,つぐぐ,つまぐ"),
        ("繋ぐ", "つなぐ", "to connect", "JLPT N2", "かつぐ,ふさぐ,あおぐ"),
        ("隣", "となり", "next to / neighbor", "JLPT N4", "とまり,とおり,となえ"),
        ("生まれる", "うまれる", "to be born", "JLPT N4", "あまれる,こまれる,たまれる"),
        ("関係", "かんけい", "relation / relationship", "JLPT N3", "かんせい,がんけい,かんげい"),
        ("確認", "かくにん", "confirmation", "JLPT N3", "がくにん,かくにい,かくじん"),
        ("私", "わたし", "I / me", "JLPT N5", "わたす,あたし,わだし"),
        ("走る", "はしる", "to run", "JLPT N4", "おどる,かえる,まわる"),
        ("軽く", "かるく", "lightly", "JLPT N4", "たるく,はるく,かろく"),
        ("早く", "はやく", "quickly / early", "JLPT N5", "おそく,ちかく,とおく"),
        ("負ける", "まける", "to lose", "JLPT N4", "つける,とける,ぬける"),
        ("光", "ひかり", "light", "JLPT N4", "ひがり,ひたり,ひなり"),
        ("輝く", "かがやく", "to shine / sparkle", "JLPT N2", "かがよく,かかやく,かたやく"),
        ("桜", "さくら", "cherry blossom", "JLPT N4", "さくろ,さぐら,さぎら"),
        ("翼", "つばさ", "wing", "JLPT N2", "つばき,つぼさ,つばざ"),
        ("意味", "いみ", "meaning", "JLPT N4", "いび,いま,いも"),
        ("響く", "ひびく", "to resound / echo", "JLPT N2", "ひひく,びびく,ひみく"),
        ("霞", "かすみ", "mist / haze", "JLPT N1", "かすり,かずみ,かさみ"),
        ("登る", "のぼる", "to climb", "JLPT N4", "すわる,まわる,とおる"),
        ("社", "やしろ", "shrine", "JLPT N1", "やしり,やしる,やじろ"),
        ("背景", "はいけい", "background", "JLPT N2", "はいけん,ばいけい,はいげい"),
        ("配信", "はいしん", "broadcast / streaming", "JLPT N2", "はいじん,ばいしん,はいさん"),
        ("泳ぐ", "およぐ", "to swim", "JLPT N5", "いそぐ,かつぐ,かせぐ"),
        ("誘う", "さそう", "to invite", "JLPT N3", "おそう,したう,にあう"),
        ("勇気", "ゆうき", "courage", "JLPT N3", "ゆうぎ,ゆうけ,ゆおき"),
        ("気づく", "きづく", "to notice", "JLPT N3", "きずく,みづく,なづく"),
    ]
    conn = get_connection()
    conn.executemany(
        "INSERT INTO word (word, reading, meaning, category, distractors) VALUES (?, ?, ?, ?, ?)",
        starter_words
    )
    conn.commit()
    conn.close()
    print(f"Inserted {len(starter_words)} starter words.")

if __name__ == "__main__":
    init_db()
    seed_words()