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

from gi.repository import Gtk, Gio, Adw, GLib
from .window import FuntasticWindow
from .preferences import FuntasticPreferencesWindow, load_config

CONFIG_DIR = os.path.join(os.path.expanduser('~'), '.config', 'funtastic')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')


class FuntasticApplication(Adw.Application):
    def __init__(self):
        super().__init__(application_id='io.github.comicalsoftwares.funtastic',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS,
                         resource_base_path='/io/github/comicalsoftwares/funtastic')
        self.config = load_config()
        self.create_action('quit', lambda *_: self.quit(), ['<control>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

    def do_activate(self):
        win = self.props.active_window
        if not win:
            fact = self.get_daily_fact()
            win = FuntasticWindow(application=self, initial_fact=fact)
            win.present()

    def on_about_action(self, *args):
        about = Adw.AboutDialog(
            application_name='Funtastic !',
            application_icon='io.github.comicalsoftwares.funtastic',
            developer_name='Anir El Haddaj',
            version='1.0.0',
            translator_credits=_('translator-credits'),
            developers=['Anir El Haddaj'],
            copyright='MIT License\n\nCopyright (c) 2026 Anir El Haddaj (ComicalSoftwares)'
        )
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        self.config = load_config()
        prefs_win = FuntasticPreferencesWindow(transient_for=self.props.active_window)
        prefs_win.present()

    def create_action(self, name, callback, shortcuts=None):
        action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)

    def get_cache_path(self):
        app_dir = os.path.join(GLib.get_user_data_dir(), 'funtastic')
        os.makedirs(app_dir, exist_ok=True)
        return os.path.join(app_dir, 'cache.json')

    def fetch_wikipedia_fact(self):
        today = date.today()
        month = f"{today.month:02d}"
        day = f"{today.day:02d}"
        url = f"https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/{month}/{day}"
        req = urllib.request.Request(url, headers={'User-Agent': 'FuntasticApp/1.0'})
        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read().decode('utf-8'))
                events = data.get('events', [])
                bad_keywords = ['kill', 'dead', 'death', 'shot', 'shooting', 'murder', 'war', 'attack', 'crash', 'died', 'assassination', 'executed', 'battle', 'bomb', 'fatal', 'disaster', 'accident']

                for fact_item in events:
                    text = fact_item.get('text', '')
                    if not any(word in text.lower() for word in bad_keywords):
                        year = fact_item.get('year')
                        return f"In {year}, {text}" if (year and not text.startswith(str(year))) else text
        except Exception:
            pass
        return "Wikipedia's servers are down."

    def get_daily_fact(self):
        self.config = load_config()

        if not self.config.get("weekly_download", True):
            return self.fetch_wikipedia_fact()

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
