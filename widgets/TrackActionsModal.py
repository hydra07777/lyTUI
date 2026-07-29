from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical
from textual.widgets.option_list import Option
from messages.FetchLyricsRequested import FetchLyricsRequested


class TrackActionsModal(ModalScreen):
    def __init__(self, track_id: int):
        super().__init__()
        self.track_id = track_id

    def compose(self):
        with Vertical(id="modal_container"):
            yield Label("🎵 Actions", id="modal_title")
            yield OptionList(
                Option("Fetch the lyrics", id="fetch_lyrics"),
                id="track_actions_list",
            )

    def on_option_list_option_selected(self, event):
        if event.option.id == "fetch_lyrics":
            self.post_message(FetchLyricsRequested(self.track_id))
        self.dismiss()
