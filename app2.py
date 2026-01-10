from textual.app import  App
from textual.widgets import Header, ListView, ListItem, Label, Static, Footer


class MyApp(App) :

    def compose(self) :
        yield Header()
        yield Static("lyTUI" \
        "" \
        "" \
        "", id="title")

        yield ListView(
            ListItem(Label("song 1"), id="song_1"),
            ListItem(Label("song 2"), id="song_2"),
            ListItem(Label("song 3"), id="song_3"),
            ListItem(Label("song 4"), id="song_4"),
        )

        yield Footer()

    def on_list_view_selected(self, event : ListView.Selected) :
        label = event.item.query_one(Label).render()
        self.current_song = label
        self.query_one("#title").update(label)

MyApp().run()