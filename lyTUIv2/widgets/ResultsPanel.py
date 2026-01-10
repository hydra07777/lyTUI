from textual.containers import Vertical
from textual.widgets import ListView, ListItem, Label, Static

class ResultsPanel(Vertical):

    def compose(self):
        yield Static('ici et m')

    def show_results(self, id: str, results):
        self.remove_children()
        label = Label(f"Résultats : {id}")
        lv = ListView(
            *[ListItem(Label(str(r["title"]))) for r in results]
        )
        self.mount(label)
        self.mount(lv)

        print(lv)

# ResultsPanel().show_results('all', [{'title': 'Un homme', 'artist': 'Jérémy Frerot', 'album': 'Un homme', 'year': 2025}])