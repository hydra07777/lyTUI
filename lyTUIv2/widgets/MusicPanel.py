from textual.containers import Vertical
from textual.widgets import Static, ProgressBar
from widgets.lyrics_view import LyricsView

class MusicPanel(Vertical):
    def compose(self):
        yield Static("no Music selected")
        yield ProgressBar(total= 300, id="progress")
        yield Static("touche")
        yield LyricsView()

    def display_music_cover(self, music):
        pass