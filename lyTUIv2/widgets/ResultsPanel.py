from textual.containers import Vertical
from textual.widgets import ListView, ListItem, Label, Static
from models.tracks import Track
from textual import on
from messages.MusicSelection import MusicSelection

class ResultsPanel(Vertical):

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
        
    

# ResultsPanel().show_results('all', [{'title': 'Un homme', 'artist': 'Jérémy Frerot', 'album': 'Un homme', 'year': 2025}])