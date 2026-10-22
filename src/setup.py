from gi.repository import Adw, Gtk
from .config import load_config, save_config
import os

class SetupWindow(Adw.Window):
    __gtype_name__ = 'SetupWindow'

    def __init__(self, on_complete_callback, **kwargs):
        super().__init__(**kwargs)
        self.on_complete_callback = on_complete_callback
        self.set_title("Welcome to Funtastic!")

        self.set_default_size(480, 610)
        self.set_size_request(480, 610)
        self.set_resizable(False)
        self.set_modal(True)

        clamp = Adw.Clamp(maximum_size=420)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        box.set_margin_top(30)
        box.set_margin_bottom(30)
        box.set_margin_start(20)
        box.set_margin_end(20)

        status_page = Adw.StatusPage(title="Welcome to Funtastic!", description="Get fun-facts every single day.", icon_name="io.github.comicalsoftwares.funtastic")
        box.append(status_page)

        group = Adw.PreferencesGroup(title="Would you like to have Funtastic run at startup ?")
        box.append(group)

        self.startup_row = Adw.SwitchRow(title="Start Funtastic at system startup", subtitle="If toggled ON, Funtastic will start automatically everytime you log in.")
        group.add(self.startup_row)

        start_button = Gtk.Button(label="Let's Go !")
        start_button.add_css_class("suggested-action")
        start_button.add_css_class("pill")
        start_button.set_margin_top(10)
        start_button.connect("clicked", self.on_start_clicked)
        box.append(start_button)

        clamp.set_child(box)
        self.set_content(clamp)

    def on_start_clicked(self, button):
        config = load_config()
        config["startup"] = self.startup_row.get_active()
        save_config(config)
