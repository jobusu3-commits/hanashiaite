import os
import anthropic
import streamlit as st
from streamlit_js_eval import streamlit_js_eval
from datetime import date
from character import build_system_prompt, research_character
from storage import (
    save_config, load_config,
    save_history, load_history, clear_history,
    save_diary, load_diaries,
    get_greeted_date, set_greeted_date,
)
from diary import get_today_opening, build_diary_prompt

st.set_page_config(page_title="話し相手", page_icon="💬", layout="centered")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

if "config" not in st.session_state:
    st.session_state.config = load_config()
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# --- ヒアリング画面 ---
if st.session_state.config is None:
    st.title("💬 話し相手をつくる")
    st.caption("5つの質問に答えると、あなただけの話し相手が生まれます。")

    with st.form("setup"):
        user_name = st.text_input("あなたの名前（呼ばれたい名前）", placeholder="例：たかし、ゆい、けん")
        name = st.text_input("話し相手の名前", placeholder="例：ハル、リク、あやね")
        character_ref = st.text_input(
            "元にするキャラクター（任意）",
            placeholder="例：進撃の巨人のリヴァイ、ハイキューの影山、スパイファミリーのアーニャ"
        )
        st.caption("入力するとそのキャラクターの口調・性格を自動で反映します。空欄でも使えます。")
        relationship = st.selectbox("関係性", ["友人", "幼なじみ", "先輩", "後輩", "恋人", "メンター"])
        tone = st.selectbox("口調（キャラクター指定がない場合に使用）", ["タメ口・フレンドリー", "丁寧語・落ち着いた", "関西弁", "元気・テンション高め", "クール・寡黙"])
        personality = st.text_area("性格・補足（自由に）", placeholder="例：聞き上手で穏やか。たまに毒舌だけど根は優しい。", height=80)
        topics = st.text_area("よく話す話題・共通の趣味", placeholder="例：仕事のグチ、恋愛相談、映画、音楽、日常のできごと", height=80)
        submitted = st.form_submit_button("話し相手をつくる", use_container_width=True, type="primary")

    if submitted:
        if not name or not user_name:
            st.warning("名前を入力してください。")
        else:
            character_profile = ""
            if character_ref.strip():
                with st.spinner(f"「{character_ref}」を調べています…"):
                    character_profile = research_character(character_ref.strip(), client)
                if character_profile:
                    st.success(f"「{character_ref}」の情報を取得しました。")
                else:
                    st.warning("キャラクター情報が見つかりませんでした。通常モードで作成します。")

            config = {
                "user_name": user_name,
                "name": name,
                "relationship": relationship,
                "tone": tone,
                "personality": personality,
                "topics": topics,
                "character_ref": character_ref,
                "character_profile": character_profile,
            }
            save_config(config)
            st.session_state.config = config
            st.rerun()

# --- メイン画面 ---
else:
    config = st.session_state.config
    name = config["name"]
    today_str = date.today().isoformat()

    tab_chat, tab_diary = st.tabs(["💬 話す", "📔 日記"])

    # ==============================
    # タブ①：チャット
    # ==============================
    with tab_chat:
        col1, col2 = st.columns([4, 1])
        col1.title(f"💬 {name}")
        if col2.button("設定をリセット", use_container_width=True):
            st.session_state.config = None
            st.session_state.messages = []
            clear_history()
            if os.path.exists("character_config.json"):
                os.remove("character_config.json")
            st.rerun()

        # 今日の挨拶（日付が変わったら or 初回）
        if get_greeted_date() != today_str:
            opening = get_today_opening(config)
            st.session_state.messages.append({"role": "assistant", "content": opening})
            save_history(st.session_state.messages)
            set_greeted_date(today_str)

        # 履歴表示
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # 音声入力
        if "listen_mode" not in st.session_state:
            st.session_state.listen_mode = False

        if st.button("🎤 話す", disabled=st.session_state.listen_mode):
            st.session_state.listen_mode = True
            st.rerun()

        voice_input = None
        if st.session_state.listen_mode:
            st.info("🎤 聞いています…　話し終わったら少し待ってください")
            voice_input = streamlit_js_eval(js_expressions="""
                new Promise((resolve) => {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if (!SpeechRecognition) { resolve(''); return; }
                    const recognition = new SpeechRecognition();
                    recognition.lang = 'ja-JP';
                    recognition.interimResults = false;
                    recognition.maxAlternatives = 1;
                    recognition.onresult = (e) => resolve(e.results[0][0].transcript);
                    recognition.onerror = () => resolve('');
                    recognition.start();
                })
            """, want_output=True, key="voice_recognition")
            if voice_input is not None:
                st.session_state.listen_mode = False

        text_input = st.chat_input(f"{name}に話しかける...")

        user_input = None
        if voice_input and isinstance(voice_input, str) and voice_input.strip():
            user_input = voice_input.strip()
            st.toast(f"🎤 {user_input}")
        elif text_input:
            user_input = text_input

        if user_input:
            st.session_state.messages.append({"role": "user", "content": user_input})
            with st.chat_message("user"):
                st.write(user_input)

            system_prompt = build_system_prompt(config)
            with st.chat_message("assistant"):
                with st.spinner(""):
                    response = client.messages.create(
                        model="claude-haiku-4-5-20251001",
                        max_tokens=512,
                        system=system_prompt,
                        messages=st.session_state.messages,
                    )
                    reply = response.content[0].text
                    st.write(reply)

            st.session_state.messages.append({"role": "assistant", "content": reply})
            save_history(st.session_state.messages)

        # 下部ボタン
        if st.session_state.messages:
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("📔 今日の日記をつくる", use_container_width=True, type="primary"):
                    with st.spinner("日記を書いています…"):
                        prompt = build_diary_prompt(st.session_state.messages, config)
                        res = client.messages.create(
                            model="claude-haiku-4-5-20251001",
                            max_tokens=512,
                            messages=[{"role": "user", "content": prompt}],
                        )
                        diary_text = res.content[0].text
                        save_diary(today_str, diary_text)
                    st.success("日記をつけました！「📔 日記」タブで読めます。")
            with col_b:
                if st.button("会話をリセット", use_container_width=True):
                    st.session_state.messages = []
                    clear_history()
                    st.rerun()

    # ==============================
    # タブ②：日記一覧
    # ==============================
    with tab_diary:
        st.title("📔 日記")
        diaries = load_diaries()

        if not diaries:
            st.caption("まだ日記がありません。話した後に「今日の日記をつくる」を押してください。")
        else:
            for d in sorted(diaries.keys(), reverse=True):
                with st.expander(d, expanded=(d == today_str)):
                    st.markdown(diaries[d])
