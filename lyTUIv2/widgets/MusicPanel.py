from textual.containers import Vertical
from textual.widgets import Static, ProgressBar
from widgets.lyrics_view import LyricsView
from models.tracks import Track
from services.ansi_converter import convert_cover_ansi
from rich.text import Text

class MusicPanel(Vertical):
    def compose(self):
        yield Static("no Music selected", id="test")
        yield ProgressBar(total= 300, id="progress")
        yield Static("touche")
        yield LyricsView()

    def display_music_cover(self, music):
        pass

    def show_music_selected(self, track : Track) :
        cover = convert_cover_ansi(track.cover_byte)
        text = Text.from_ansi(cover)
        self.query_one("#test").update(text)