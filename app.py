import os
import anthropic
import streamlit as st
from character import build_system_prompt
from storage import save_config, load_config, save_history, load_history, clear_history

st.set_page_config(page_title="話し相手", page_icon="💬", layout="centered")

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# --- キャラ設定読み込み ---
if "config" not in st.session_state:
    st.session_state.config = load_config()
if "messages" not in st.session_state:
    st.session_state.messages = load_history()

# --- ヒアリング画面 ---
if st.session_state.config is None:
    st.title("💬 話し相手をつくる")
    st.caption("5つの質問に答えると、あなただけの話し相手が生まれます。")

    with st.form("setup"):
        user_name = st.text_input("あなたの名前（呼ばれたい名前）", placeholder="さく")
        name = st.text_input("話し相手の名前", placeholder="ハルカ")
        relationship = st.selectbox("関係性", ["友人", "幼なじみ", "先輩", "後輩", "恋人", "メンター"])
        tone = st.selectbox("口調", ["タメ口・フレンドリー", "丁寧語・落ち着いた", "関西弁", "元気・テンション高め", "クール・寡黙"])
        personality = st.text_area("性格・特徴（自由に）", placeholder="例：聞き上手で穏やか。たまに毒舌だけど根は優しい。", height=80)
        topics = st.text_area("よく話す話題・共通の趣味", placeholder="例：競馬、株、音楽、日常のグチ", height=80)
        submitted = st.form_submit_button("話し相手をつくる", use_container_width=True, type="primary")

    if submitted:
        if not name or not user_name:
            st.warning("名前を入力してください。")
        else:
            config = {
                "user_name": user_name,
                "name": name,
                "relationship": relationship,
                "tone": tone,
                "personality": personality,
                "topics": topics,
            }
            save_config(config)
            st.session_state.config = config
            st.rerun()

# --- チャット画面 ---
else:
    config = st.session_state.config
    name = config["name"]

    col1, col2 = st.columns([4, 1])
    col1.title(f"💬 {name}")
    if col2.button("設定をリセット", use_container_width=True):
        st.session_state.config = None
        st.session_state.messages = []
        clear_history()
        import os
        if os.path.exists("character_config.json"):
            os.remove("character_config.json")
        st.rerun()

    # 履歴表示
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    # 入力
    user_input = st.chat_input(f"{name}に話しかける...")
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

    if st.session_state.messages:
        if st.button("会話をリセット", use_container_width=True):
            st.session_state.messages = []
            clear_history()
            st.rerun()
