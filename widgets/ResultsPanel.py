from textual.containers import Vertical
from textual.widgets import ListView, ListItem, Label, Static
from models.tracks import Track
from textual import on
from messages.MusicSelection import MusicSelection
from messages.TrackActionsRequested import TrackActionsRequested

class ResultsPanel(Vertical):

    BINDINGS = [
        ("o", "open_track_actions", "Actions"),
    ]

    def compose(self):
        yield Static('ici et m')

    def show_results(self, id: str, results : list[Track]):
        self.remove_children()
        label = Label(f"Résultats : {id}")
        lv = ListView(
            *[ListItem(Label(str(track.title)), name= f"{track._id}") for track in results]
        )
        self.mount(label)
        self.mount(lv)

    @on(ListView.Selected)
    def on_track_selected( self, event : ListView.Selected):
        id = int(event.item.name)

        self.post_message(MusicSelection(id))

    def action_open_track_actions(self):
        try:
            lv = self.query_one(ListView)
        except Exception:
            return

        item = lv.highlighted_child
        if item is None or item.name is None:
            return

        track_id = int(item.name)
        self.post_message(TrackActionsRequested(track_id))
        
    

