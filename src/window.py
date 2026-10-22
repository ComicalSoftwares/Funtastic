from gi.repository import Adw, Gtk, Gio, Gdk
import os

@Gtk.Template(resource_path='/io/github/comicalsoftwares/funtastic/window.ui')
class FuntasticWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'FuntasticWindow'
    title_label = Gtk.Template.Child()
    fact_label = Gtk.Template.Child()
    tomorrow = Gtk.Template.Child()

    def __init__(self, initial_fact=None, **kwargs):
        super().__init__(**kwargs)
        self.current_fact = initial_fact or "A wise man once said absolutely nothing."
        self.update_fact_display(self.current_fact)
        self.setup_save_button()

    def update_fact_display(self, fact_text=None):
        if fact_text:
            self.current_fact = fact_text
        markup_text = f"<i>“{self.current_fact}”</i>"
        if hasattr(self, 'fact_label') and self.fact_label:
            self.fact_label.set_label(markup_text)

    def setup_save_button(self):
        menu = Gio.Menu()
        menu.append("Copy to Clipboard", "win.copy-clipboard")
        menu.append("Save as Text File...", "win.save-file")

        popover = Gtk.PopoverMenu.new_from_model(menu)

        save_btn = Gtk.MenuButton(
            icon_name="document-save-symbolic",
            popover=popover,
            valign=Gtk.Align.CENTER,
            tooltip_text="Save or Copy Fact"
        )
        save_btn.add_css_class("flat")

        copy_action = Gio.SimpleAction.new("copy-clipboard", None)
        copy_action.connect("activate", lambda *_: self.copy_to_clipboard())
        self.add_action(copy_action)

        save_file_action = Gio.SimpleAction.new("save-file", None)
        save_file_action.connect("activate", lambda *_: self.save_as_file())
        self.add_action(save_file_action)
        def pack_into_header(widget):
            if isinstance(widget, (Adw.HeaderBar, Gtk.HeaderBar)):
                widget.pack_end(save_btn)
                return True
            child = widget.get_first_child()
            while child:
                if pack_into_header(child):
                    return True
                child = child.get_next_sibling()
            return False

        pack_into_header(self)

    def get_formatted_fact_with_source(self):
        return f"{self.current_fact}\n\nSource: Wikipedia (https://en.wikipedia.org)"

    def copy_to_clipboard(self):
        clipboard = self.get_display().get_clipboard()
        content = self.get_formatted_fact_with_source()
        clipboard.set(content)

    def save_as_file(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Save Fact")
        dialog.set_initial_name("funtastic_fact.txt")

        def on_save_finish(dialog, result):
            try:
                file = dialog.save_finish(result)
                if file:
                    path = file.get_path()
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(self.get_formatted_fact_with_source())
            except Exception as e:
                print(f"Error saving file: {e}")

        dialog.save(self, None, on_save_finish)
