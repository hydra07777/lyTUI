from textual.containers import Vertical
from textual.widgets import Static, ProgressBar

class MusicPanel(Vertical):
    def compose(self):
        yield Static("no Music selected")
        yield ProgressBar(total= 300, id="progress")
        yield L
    def display_music_cover(self, music):
        pass