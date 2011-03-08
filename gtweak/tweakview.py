from gi.repository import Gtk, Gdk

from gtweak.tweakmodel import TweakModel

class TweakView:
    def __init__(self, notebook, entry, tweak_box, model):
        self._notebook = notebook
        self._entry_manager = EntryManager(
            entry,
            self._on_search,
            self._on_search_cancel)

        self._model = model
        self._model.load_tweaks()

        self.treeview = Gtk.TreeView(model=model)        
        self.treeview.props.headers_visible = False
        self.treeview.append_column(
                Gtk.TreeViewColumn(
                        "Tweak", Gtk.CellRendererText(), text=TweakModel.COLUMN_NAME))
        self.treeview.get_selection().connect("changed", self._on_selection_changed)

        #add all tweaks
        map(lambda t: tweak_box.pack_start(t.widget, False, False, 0), self._model.tweaks)

    def show_tweaks(self, tweaks):
        map(Gtk.Widget.show_all, [t.widget for t in tweaks])

    def hide_tweaks(self, tweaks):
        map(Gtk.Widget.hide, [t.widget for t in tweaks])

    def show_only_tweaks(self, tweaks):
        for t in self._model.tweaks:
            if t in tweaks:
                t.widget.show_all()
            else:
                t.widget.hide()

    def select_none(self):
        self.treeview.get_selection().unselect_all()

    def _on_search(self, txt):
        tweaks = self._model.search_matches(txt)
        self.show_only_tweaks(tweaks)
        self.select_none()
        self._notebook.set_current_page(1)

    def _on_search_cancel(self):
        self._notebook.set_current_page(0)

    def _on_pre_selection_change(self):
        self._notebook.set_current_page(0)

    def _on_post_selection_change(self):
        self._notebook.set_current_page(1)

    def _on_selection_changed(self, selection):
        model, selected = selection.get_selected()
        if selected:
            self._on_pre_selection_change()
            
            #apparently iters do not persist over iteration, so use treepaths instead
            path_selected = model.get_path(selected)
            #hide other tweakgroups
            root = model.get_iter_first()
            while root:
                if model.get_path(root) != path_selected:
                    tweakgroup = model.get_value(root, model.COLUMN_TWEAK)
                    self.hide_tweaks(tweakgroup.tweaks)
                root = model.iter_next(root)
            #show selected
            tweakgroup = model.get_value(selected, model.COLUMN_TWEAK)
            self.show_tweaks(tweakgroup.tweaks)
            
            self._on_post_selection_change()
            
class EntryManager:

    SYMBOLIC = ""#"-symbolic"

    def __init__(self, search_entry, search_cb, search_cancel_cb):
        self._entry = search_entry
        self._search_cb = search_cb
        self._search_cancel_cb = search_cancel_cb
        self._entry.connect("changed", self._on_changed)
        self._entry.connect("key-press-event", self._on_key_press)
        self._entry.connect("icon-release", self._on_clear_icon_release)
        self._on_changed(self._entry)

    def _search(self):
        txt = self._entry.get_text()
        if txt:
            self._search_cb(txt)

    def _search_cancel(self):
        self._search_cancel_cb()
        self._entry.set_text("")
        
    def _on_changed(self, entry):
        if not self._entry.get_text():
            self._entry.set_properties(
                    secondary_icon_name="edit-find" + EntryManager.SYMBOLIC,
                    secondary_icon_activatable=False,
                    secondary_icon_sensitive=False)
        else:
            self._entry.set_properties(
                    secondary_icon_name="edit-clear" + EntryManager.SYMBOLIC,
                    secondary_icon_activatable=True,
                    secondary_icon_sensitive=True)
    
    def _on_key_press(self, entry, event):
        if event.keyval == Gdk.KEY_Return:
            self._search()
        elif event.keyval == Gdk.KEY_Escape:
            self._search_cancel()
    
    def _on_clear_icon_release(self, *args):
        self._search_cancel()
        
