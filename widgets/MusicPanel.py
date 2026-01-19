from textual.containers import Vertical, Horizontal
from textual.widgets import Static, ProgressBar
from widgets.lyrics_view import LyricsView
from models.tracks import Track
from services.ansi_converter import convert_cover_ansi
from rich.text import Text

class MusicPanel(Vertical):
    def compose(self):
        self.lyrics = LyricsView()
        yield Static("no Music selected", id="test")
        yield Static('hahah', id='tt')

        
        yield ProgressBar(total= 300, id="progress")
        yield Static('--:--', id="elapsed_time")
        yield Static("touche")
        yield self.lyrics

    def display_music_cover(self, music):
        pass

    def show_music_selected(self, track : Track) :
        cover = convert_cover_ansi(track.cover_byte)
        text = Text.from_ansi(cover)
        self.lyrics.load_lyrics_from_path(track.path)
        self.query_one("#test").update(text)

    def update_elapsed_time( self, time):
        minutes = time // 60
        seconds = time % 60
        self.query_one("#elapsed_time").update(f"{minutes:02}:{seconds:02}")
    
    def update_progress_bar(self, elapsed_time : int ):
        bar = self.query_one("#progress", ProgressBar)
        bar.progress = elapsed_time
        self.update_elapsed_time(elapsed_time)

    def on_refresh_lyrics(self, timestamps : float):
        self.lyrics.sync(timestamps)

        