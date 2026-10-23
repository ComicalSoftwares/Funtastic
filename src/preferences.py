from gi.repository import Adw, Gtk, GLib, Gio
import json
import os

CONFIG_DIR = os.path.join(GLib.get_user_config_dir(), 'funtastic')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')
AUTOSTART_DIR = os.path.join(GLib.get_user_config_dir(), 'autostart')
AUTOSTART_FILE = os.path.join(AUTOSTART_DIR, 'io.github.comicalsoftwares.funtastic.desktop')

DEFAULT_CONFIG = {
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

def set_autostart(enable: bool):
    """Safely requests background autostart via the XDG Desktop Portal."""
    def on_proxy_ready(source, result):
        try:
            proxy = Gio.DBusProxy.new_finish(result)
            options = {
                'reason': GLib.Variant('s', 'Show daily fun facts on login'),
                'autostart': GLib.Variant('b', enable),
                'commandline': GLib.Variant('as', ['flatpak', 'run', 'io.github.comicalsoftwares.funtastic'])
            }
            proxy.call(
                'RequestBackground',
                GLib.Variant('(sa{sv})', ('', options)),
                Gio.DBusCallFlags.NONE,
                -1,
                None,
                None,
                None
            )
        except Exception as e:
            print(f"Autostart portal error: {e}")

    Gio.DBusProxy.new_for_bus(
        Gio.BusType.SESSION,
        Gio.DBusProxyFlags.NONE,
        None,
        'org.freedesktop.portal.Desktop',
        '/org/freedesktop/portal/desktop',
        'org.freedesktop.portal.Background',
        None,
        on_proxy_ready
    )

def save_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)

    # Trigger the system portal to handle autostart safely
    set_autostart(config.get("startup", False))

class FuntasticPreferencesWindow(Adw.PreferencesWindow):
    __gtype_name__ = 'FuntasticPreferencesWindow'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_title("Preferences")
        self.config = load_config()

        page = Adw.PreferencesPage()
        self.add(page)

        general_group = Adw.PreferencesGroup(title="Automatic Startup")
        page.add(general_group)

        self.startup_row = Adw.SwitchRow(title="Start Funtastic once you log in")
        self.startup_row.set_active(self.config.get("startup", False))
        self.startup_row.connect("notify::active", self.on_startup_toggled)
        general_group.add(self.startup_row)

        storage_group = Adw.PreferencesGroup(title="Storage and network", description="Manage data usage and caching")
        page.add(storage_group)

        self.weekly_row = Adw.SwitchRow(title="Enable Weekly Fact Caching", subtitle="Recommended to keep ON.")
        self.weekly_row.set_active(self.config.get("weekly_download", True))
        self.weekly_row.connect("notify::active", self.on_weekly_toggled)
        storage_group.add(self.weekly_row)

        clear_cache_row = Adw.ActionRow(title="Clear Local Cache", subtitle="Delete cached history and fetch fresh facts")
        clear_button = Gtk.Button(label="Clear")
        clear_button.set_valign(Gtk.Align.CENTER)
        clear_button.add_css_class("destructive-action")
        clear_button.connect("clicked", self.on_clear_cache_clicked)
        clear_cache_row.add_suffix(clear_button)
        storage_group.add(clear_cache_row)

        reset_group = Adw.PreferencesGroup(title="Reset")
        page.add(reset_group)

        reset_row = Adw.ActionRow(title="Restore Defaults", subtitle="Reset all settings and preferences back to default values")
        reset_button = Gtk.Button(label="Reset Preferences")
        reset_button.set_valign(Gtk.Align.CENTER)
        reset_button.add_css_class("destructive-action")
        reset_button.connect("clicked", self.on_reset_clicked)
        reset_row.add_suffix(reset_button)
        reset_group.add(reset_row)

    def on_startup_toggled(self, row, *args):
        self.config["startup"] = row.get_active()
        save_config(self.config)

    def on_weekly_toggled(self, row, *args):
        self.config["weekly_download"] = row.get_active()
        save_config(self.config)

    def on_clear_cache_clicked(self, button):
        cache_file = os.path.join(os.path.expanduser('~'), '.local', 'share', 'funtastic', 'cache.json')
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
                button.set_label("Cleared!")
                button.set_sensitive(False)
            except Exception as e:
                print(f"Failed to clear cache: {e}")

    def on_reset_clicked(self, button):
        save_config(DEFAULT_CONFIG.copy())
        self.config = load_config()
        self.startup_row.set_active(self.config["startup"])
        self.weekly_row.set_active(self.config["weekly_download"])
        button.set_label("Reset Done!")
        button.set_sensitive(False)
