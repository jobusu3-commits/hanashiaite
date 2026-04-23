import json
import os

HISTORY_FILE = "history.json"
CONFIG_FILE = "character_config.json"
DIARY_FILE = "diary.json"
GREETED_FILE = "greeted_date.json"


def save_config(config: dict):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)


def load_config() -> dict | None:
    if not os.path.exists(CONFIG_FILE):
        return None
    with open(CONFIG_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_history(messages: list):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, encoding="utf-8") as f:
        return json.load(f)


def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE)


def save_diary(date_str: str, content: str):
    diaries = load_diaries()
    diaries[date_str] = content
    with open(DIARY_FILE, "w", encoding="utf-8") as f:
        json.dump(diaries, f, ensure_ascii=False, indent=2)


def load_diaries() -> dict:
    if not os.path.exists(DIARY_FILE):
        return {}
    with open(DIARY_FILE, encoding="utf-8") as f:
        return json.load(f)


def get_greeted_date() -> str | None:
    if not os.path.exists(GREETED_FILE):
        return None
    with open(GREETED_FILE, encoding="utf-8") as f:
        return json.load(f).get("date")


def set_greeted_date(date_str: str):
    with open(GREETED_FILE, "w", encoding="utf-8") as f:
        json.dump({"date": date_str}, f)
