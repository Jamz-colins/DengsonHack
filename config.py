import json
import os
from datetime import datetime

# Identitas Toolkit
APP_NAME = "DengsonHack"
AUTHOR = "Siro"
GITHUB = "https://github.com/Jamz-colins"
VERSION = "2.0.0"

# Palet Warna Catppuccin Mocha
THEME = {
    "mauve": "#cba6f7",
    "blue": "#89b4fa",
    "teal": "#94e2d5",
    "green": "#a6e3a1",
    "yellow": "#f9e2af",
    "peach": "#fab387",
    "red": "#f38ba8",
    "subtext": "#a6adc8",
    "surface": "#313244",
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USER_KEY_FILE = os.path.join(DATA_DIR, ".user_apikey.json")


def save_json_file(filename: str, payload: dict) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)
    filepath = os.path.join(DATA_DIR, filename)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=4, ensure_ascii=False)
    return filepath


def save_result(module_name: str, target: str, data: dict) -> str:
    safe_target = "".join(c if c.isalnum() else "_" for c in target)[:30]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{module_name}_{safe_target}_{timestamp}.json"

    payload = {
        "toolkit": APP_NAME,
        "author": AUTHOR,
        "version": VERSION,
        "module": module_name,
        "target": target,
        "timestamp": datetime.now().isoformat(),
        "data": data,
    }
    return save_json_file(filename, payload)


def get_saved_api_key(service: str) -> str:
    if not os.path.exists(USER_KEY_FILE):
        return ""
    try:
        with open(USER_KEY_FILE, "r", encoding="utf-8") as f:
            keys = json.load(f)
        return keys.get(service, "")
    except Exception:
        return ""


def set_saved_api_key(service: str, api_key: str) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    keys = {}
    if os.path.exists(USER_KEY_FILE):
        try:
            with open(USER_KEY_FILE, "r", encoding="utf-8") as f:
                keys = json.load(f)
        except Exception:
            keys = {}
    keys[service] = api_key
    with open(USER_KEY_FILE, "w", encoding="utf-8") as f:
        json.dump(keys, f, indent=4)
