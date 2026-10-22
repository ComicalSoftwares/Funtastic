import json
import os

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'funtastic')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
AUTOSTART_DIR = os.path.join(os.path.expanduser('~'), '.config', 'autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'io.github.comicalsoftwares.funtastic.desktop')
SETUP_FLAG = os.path.join(os.path.expanduser('~'), '.local', 'share', 'funtastic', '.setup_done')

DEFAULT_CONFIG = {
    "setup_completed": False,
    "startup": False,
    "weekly_download": True
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass
    return DEFAULT_CONFIG.copy()

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2)
        update_autostart(config.get("startup", False))

        os.makedirs(os.path.dirname(SETUP_FLAG), exist_ok=True)
        if not os.path.exists(SETUP_FLAG):
            with open(SETUP_FLAG, 'w') as f:
                f.write("done")
    except Exception as e:
        print(f"Failed to save config: {e}")

def update_autostart(enable):
    os.makedirs(AUTOSTART_DIR, exist_ok=True)
    if enable:
        desktop_entry ="""[Desktop Entry]
Type=Application
Name=Funtastic !
Exec=flatpak run io.github.comicalsoftwares.funtastic
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
"""
        with open(AUTOSTART_FILE, 'w', encoding='utf-8') as f:
            f.write(desktop_entry)
    else:
        if os.path.exists(AUTOSTART_FILE):
            os.remove(AUTOSTART_FILE)

