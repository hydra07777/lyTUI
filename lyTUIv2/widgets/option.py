from textual.containers import Vertical
from textual.widgets import ListItem, ListView, Label
from messages.LibrarySelection import LibrarySelection
from textual import on

class Option(Vertical) :
    def compose(self):
        yield ListView(
            ListItem(Label('All musics'), id="all"),
            ListItem(Label('Artists'), id="artist"),
            ListItem(Label('Album'), id="album")
        )
    @on(ListView.Selected)
    def on_selected(self, event: ListView.Selected):
        value = event.item.query_one(Label).render
        id = event.item.id

        self.post_message(LibrarySelection(id,value))