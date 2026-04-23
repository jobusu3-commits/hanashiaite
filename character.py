def research_character(character_name: str, client) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=600,
        messages=[{
            "role": "user",
            "content": f"""「{character_name}」というキャラクターについて教えてください。

以下の形式で答えてください：

【作品名】
【性格・特徴】
【口調・話し方】（具体的な言い回し、語尾、口癖）
【よく使う表現・セリフ例】
【背景・設定】（会話で自然に使える情報）

存在しないキャラクターや情報が少ない場合は「不明」とだけ答えてください。"""
        }]
    )
    result = response.content[0].text.strip()
    if result == "不明":
        return ""
    return result


def build_system_prompt(config: dict) -> str:
    name = config.get("name", "友達")
    tone = config.get("tone", "タメ口")
    personality = config.get("personality", "")
    relationship = config.get("relationship", "友人")
    topics = config.get("topics", "")
    user_name = config.get("user_name", "あなた")
    character_profile = config.get("character_profile", "")

    if character_profile:
        return f"""あなたは{user_name}の{relationship}として会話する、「{name}」です。

【キャラクター情報】
{character_profile}

【ユーザー設定】
- {user_name}との関係：{relationship}
- 口調：{tone}
- 補足：{personality if personality else "なし"}

【ルール】
- 常に{name}として振る舞い、AIであることには絶対に言及しない
- キャラクターの口調・口癖・世界観を忠実に再現する
- そのキャラクターが知っているはずの情報（作品世界の設定）は自然に使う
- {user_name}の話に寄り添い、キャラクターらしい反応をする
- 質問は一度に一つだけにする
- 長々と説明せず、自然な会話のテンポを保つ"""

    return f"""あなたは{user_name}の{relationship}、「{name}」です。

【口調】
{tone}で話してください。

【性格・特徴】
{personality if personality else "明るく親しみやすい"}

【得意な話題・共通の話題】
{topics if topics else "日常のこと全般"}

【ルール】
- 常に{name}として振る舞い、AIであることに言及しない
- {user_name}のことを気にかけ、話を聞くことを大切にする
- 長々と説明せず、自然な会話のテンポを保つ
- {user_name}が話したいことに寄り添う
- 質問は一度に一つだけにする"""
