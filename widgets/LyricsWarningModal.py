from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical
from textual.widgets.option_list import Option


class LyricsWarningModal(ModalScreen):
    """Confirmation avant écriture de paroles non synchronisées."""

    def __init__(self, track_id: int, plain_lyrics: str, on_confirm):
        super().__init__()
        self.track_id = track_id
        self.plain_lyrics = plain_lyrics
        self.on_confirm = on_confirm

    def compose(self):
        with Vertical(id="modal_container"):
            yield Label("⚠️ Paroles non synchronisées", id="modal_title")
            yield Label(
                "Ces paroles n'ont pas de timestamps (pas de synchronisation). "
                "Les enregistrer quand même ?"
            )
            yield OptionList(
                Option("Confirmer", id="confirm"),
                Option("Annuler", id="cancel"),
                id="warning_actions_list",
            )

    def on_option_list_option_selected(self, event):
        if event.option.id == "confirm":
            self.on_confirm(self.track_id, self.plain_lyrics)
        self.dismiss()
