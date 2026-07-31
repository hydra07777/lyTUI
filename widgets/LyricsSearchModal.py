from textual.screen import ModalScreen
from textual.widgets import OptionList, Label
from textual.containers import Vertical
from textual.widgets.option_list import Option
from messages.LyricsResultSelected import LyricsResultSelected


class LyricsSearchModal(ModalScreen):
    BINDINGS = [
        ("escape", "dismiss", "Fermer"),
    ]

    def __init__(self, results: list[dict], track_id: int):
        super().__init__()
        self.results = results
        self.track_id = track_id

    def compose(self):
        with Vertical(id="modal_container"):
            yield Label("🔎 Résultats lrclib", id="modal_title")

            if not self.results:
                yield Label("Aucun résultat trouvé.")
                yield OptionList(Option("Fermer", id="close"), id="lyrics_results_list")
                return

            options = []
            for i, result in enumerate(self.results):
                artist = result.get("artistName") or "?"
                title = result.get("trackName") or "?"
                album = result.get("albumName") or "?"
                duration = result.get("duration")
                duration_str = f"{int(duration)}s" if duration else "?"
                sync_tag = "[synced]" if result.get("syncedLyrics") else "[plain only]"
                label = f"{artist} — {title} ({album}, {duration_str}) {sync_tag}"
                options.append(Option(label, id=str(i)))

            options.append(Option("Fermer", id="close"))
            yield OptionList(*options, id="lyrics_results_list")

    def on_option_list_option_selected(self, event):
        if event.option.id == "close":
            self.dismiss()
            return

        index = int(event.option.id)
        result = self.results[index]
        self.post_message(
            LyricsResultSelected(
                self.track_id,
                result.get("syncedLyrics") or None,
                result.get("plainLyrics") or None,
            )
        )
        self.dismiss()
