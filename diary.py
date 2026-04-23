from datetime import date

ROTATING_QUESTIONS = [
    "今日、小さくてもよかったことを1つ教えて",
    "今日、自分でよくやったと思うことある？",
    "今日だれかと話した？どんな感じだった？",
    "今、体はどんな感じ？重い・軽い・疲れてる・なんでも",
    "明日、ちょっとでも楽しみなことある？",
    "最近ずっと頭の片隅にあることって何？",
]


def get_today_opening(config: dict) -> str:
    user_name = config.get("user_name", "あなた")
    rotating_q = ROTATING_QUESTIONS[date.today().weekday() % len(ROTATING_QUESTIONS)]
    return (
        f"{user_name}、おかえり。\n\n"
        f"まず2つだけ聞かせて。\n\n"
        f"① 今日の気分を色にたとえると何色？理由も教えて\n"
        f"② {rotating_q}"
    )


def build_diary_prompt(messages: list, config: dict) -> str:
    user_name = config.get("user_name", "あなた")
    name = config.get("name", "AI")
    conversation = "\n".join(
        f"{'【' + user_name + '】' if m['role'] == 'user' else '【' + name + '】'}: {m['content']}"
        for m in messages
    )
    return f"""以下は{user_name}と{name}の今日の会話です。

{conversation}

この会話をもとに、以下の形式で出力してください。

---

**今日の気分**
（色と感情を一言で）

**今日あったこと**
（会話から読み取れる出来事・感情を自然な文章で）

**一言まとめ**
（今日を象徴する一文）

---

**カウンセラーより**
（{user_name}の会話を読んで、気づいたことを2〜3文で伝える。
アドバイスは不要。{user_name}が自分で気づいていない感情や傾向を、
押しつけず、やさしく言葉にする。最後に問いを一つ添える。）

---

ルール：
- 日記部分は日記文体（「〜した」「〜だった」）で書く
- {user_name}の言葉をできるだけ活かす
- カウンセラーのひとことは「{user_name}さん、」で始める
- 全体で300字以内"""
