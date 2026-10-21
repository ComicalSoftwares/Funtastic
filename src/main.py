import json
import os
import urllib.request
import urllib.error
from datetime import date, timedelta
import sys
import gi

from gettext import gettext as _

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw
from .window import FuntasticWindow
from .config import load_config, CONFIG_FILE


class FuntasticApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.comicalsoftwares.funtastic',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/io/github/comicalsoftwares/funtastic')
        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            fact = self.get_daily_fact()
            win = FuntasticWindow(application=self, initial_fact=fact)

            setup_flag = os.path.join(
                os.path.expanduser('~'), '.local', 'share', 'funtastic', '.setup_done'
            )

            from .config import CONFIG_FILE

            # Print debug info to terminal to check if the Setup will run or not.
            print(f"[Funtastic Debug] Config Path: {CONFIG_FILE}")
            print(f"[Funtastic Debug] Config Exists? {os.path.exists(CONFIG_FILE)}")
            print(f"[Funtastic Debug] Setup Flag Path: {setup_flag}")
            print(f"[Funtastic Debug] Setup Flag Exists? {os.path.exists(setup_flag)}")

            # In case there's no setup config/flag.. the setup assumes that this is a fresh install.
            if not os.path.exists(setup_flag) and not os.path.exists(CONFIG_FILE):
                print("[Funtastic Debug] Triggering Setup Window...")
                from .setup import SetupWindow
                setup_dialog = SetupWindow(
                    on_complete_callback=lambda: print("[Funtastic Debug] Setup Completed & Saved!"),
                    transient_for=win
                )
                win.present()
                setup_dialog.present()
                return
            else:
                print("[Funtastic Debug] Setup skipped (Config found).")

        config = load_config()
        if config.get("display_mode") == "notification":
            notification = Gio.Notification.new("Funtastic! Daily Fact")
            notification.set_body(win.current_fact)
            self.send_notification("daily-fact", notification)
        else:
            win.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(
            application_name='Funtastic !',
            application_icon='io.github.comicalsoftwares.funtastic',
            developer_name='Anir El Haddaj',
            version='1.0 alpha',
            translator_credits=_('translator-credits'),
            developers=['Anir El Haddaj'],
            copyright='© 2026 Anir El Haddaj (ComicalSoftwares)'
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        from .preferences import FuntasticPreferencesWindow
        prefs_win = FuntasticPreferencesWindow(transient_for=self.props.active_window)
        prefs_win.present()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def get_cache_path(self):
        app_dir = os.path.join(os.path.expanduser('~'), '.local', 'share', 'funtastic')
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'cache.json')

    def fetch_wikipedia_fact(self):
        today = date.today()
        month = f"{today.month:02d}"
        day = f"{today.day:02d}"
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        req = urllib.request.Request(url, headers={'User-Agent': 'FuntasticApp/1.0 (GNOME Desktop Application)'})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                events = data.get('events', [])

                bad_keywords = [ # I don't want tragic facts
                    'kill', 'dead', 'death', 'shot', 'shooting', 'murder',
                    'war', 'attack', 'crash', 'died', 'assassination', 'executed',
                    'battle', 'bomb', 'fatal', 'disaster', 'accident'
                ]

                config = load_config()
                raw_interests = config.get("interests", "")
                user_interests = [i.strip().lower() for i in raw_interests.split(",") if i.strip()]

                for fact_item in events:
                    text = fact_item.get('text', '')
                    text_lower = text.lower()

                    if any(word in text_lower for word in bad_keywords):
                        continue

                    year = fact_item.get('year')
                    formatted_text = f"In {year}, {text}" if (year and not text.startswith(str(year))) else text

                    if user_interests:
                        if any(interest in text_lower for interest in user_interests):
                            return formatted_text
                    else:
                        return formatted_text

                for fact_item in events:
                    text = fact_item.get('text', '')
                    if not any(word in text.lower() for word in bad_keywords):
                        year = fact_item.get('year')
                        return f"In {year}, {text}" if (year and not text.startswith(str(year))) else text

        except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
            pass

        return "Nothing. Because Wikipedia's servers are down for the moment."

    def get_daily_fact(self):
        cache_file = self.get_cache_path()
        today_str = str(date.today())
        fact_text = None
        cache_data = {}

        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cache_data = json.load(f)
                    if today_str in cache_data:
                        fact_text = cache_data[today_str]
            except Exception:
                pass

        if not fact_text:
            fact_text = self.fetch_wikipedia_fact()
            cache_data[today_str] = fact_text

            keys_to_keep = {str(date.today() - timedelta(days=i)) for i in range(7)}
            pruned_cache = {k: v for k, v in cache_data.items() if k in keys_to_keep}

            try:
                with open(cache_file, 'w', encoding='utf-8') as f:
                    json.dump(pruned_cache, f, ensure_ascii=False, indent=2)
            except Exception:
                pass

        return fact_text


def main(version):
    app = FuntasticApplication()
    return app.run(sys.argv)
