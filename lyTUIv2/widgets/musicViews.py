from textual.containers import Vertical
from textual.widgets import ListItem, ListView, Label, Static

class MusicView(Vertical):
    def compose(self):
          yield Static("No Category selected")
    def on_ui_refresh ( self, ListViem : ListItem):
        static = self.query_one(Static)
        self.remove(static)
        self.mount(ListViem)
