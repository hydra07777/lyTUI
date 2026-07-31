import random
from textual.containers import Vertical
from textual.widgets import Static, ProgressBar
from widgets.lyrics_view import LyricsView
from models.tracks import Track
from services.ansi_converter import convert_cover_ansi
from rich.text import Text


class MusicPanel(Vertical):

    DEFAULT_CSS = """
    /* Container Principal - Fond sombre type "Black Theme" */
MusicPanel {
    layout: vertical;
    background: #121212; /* Le fond très sombre de Spotify */
    color: #ffffff;
    padding: 1 2;
    height: 100%;
}

/* Zone de la pochette (Cover Art) */
#test {
    height: auto;
    content-align: center middle;
    margin-bottom: 1;
}

/* Barre de progression ASCII (style Debian: ---O---) */
#ascii_progress {
    height: auto;
    content-align: center middle;
    color: #1DB954;
    text-style: bold;
    margin-bottom: 1;
}

/* Titre de la musique (#tt) */
#tt {
    text-style: bold;
    content-align: center middle;
    color: #ffffff;
    height: auto;
    margin-bottom: 2;
    text-opacity: 90%;
}

/* Vue des paroles (Lyrics) 
   On lui donne height: 1fr pour qu'il prenne tout l'espace disponible 
   entre le titre et la barre de progression.
*/
LyricsView {
    height: 1fr; 
    background: #181818; /* Légèrement plus clair pour séparer */
    border: wide #121212;
    color: #b3b3b3; /* Gris clair pour le texte non actif */
    scrollbar-gutter: stable;
    border: round #2a2a2a;
    background: #181818;
    content-align: center middle;
        
    
    
}

/* Barre de progression */
ProgressBar {
    dock: bottom; /* On fixe la barre en bas */
    width: 100%;
    height: 1;
    margin-top: 1;
    margin-bottom: 1;
    padding: 0;
}

/* Stylisation spécifique de la barre Textual pour ressembler à Spotify */
ProgressBar > .bar--bar {
    color: #1DB954; /* Spotify Green */
    background: #404040; /* Gris foncé pour la partie vide */
}

ProgressBar > .bar--complete {
    color: #1DB954;
}

/* Temps écoulé */
#elapsed_time {
    dock: bottom;
    content-align: center middle;
    color: #b3b3b3;
    text-style: bold;
    height: 1;
    margin-bottom: 1;
}

/* Boutons / Contrôles (Le static "touche") */
MusicPanel > Static {
    color: #b3b3b3;
}
    """

    ASCII_PROGRESS_WIDTH = 34
    SCRAMBLE_ZONE = 5
    SCRAMBLE_CHARS = "!<>-_\\/[]{}~=+*^?#$%&01"

    def compose(self):
        self.lyrics = LyricsView()

        yield Static("No music selected", id="test")
        yield Static("", id="ascii_progress")
        yield Static("—", id="tt")

        yield ProgressBar(total=300, id="progress")
        yield Static("--:--", id="elapsed_time")

        yield self.lyrics

    def display_music_cover(self, music):
        pass

    def show_music_selected(self, track: Track):
        cover = convert_cover_ansi(track.cover_byte)
        text = Text.from_ansi(cover)

        self.lyrics.load_lyrics_from_path(track.path)
        self.query_one("#test").update(text)

    def update_ascii_progress(self, elapsed: float, duration: float):
        width = self.ASCII_PROGRESS_WIDTH

        if not duration or duration <= 0:
            ratio = 0.0
        else:
            ratio = max(0.0, min(1.0, elapsed / duration))

        cursor = int(ratio * (width - 1))
        scramble_end = min(width, cursor + 1 + self.SCRAMBLE_ZONE)

        elapsed_str = f"{int(elapsed) // 60:02}:{int(elapsed) % 60:02}"
        duration_str = f"{int(duration) // 60:02}:{int(duration) % 60:02}" if duration else "--:--"

        text = Text(f"{elapsed_str} [")
        for i in range(width):
            if i < cursor:
                text.append("-")
            elif i == cursor:
                text.append("O", style="bold white")
            elif i < scramble_end:
                text.append(random.choice(self.SCRAMBLE_CHARS), style="bold #ff5555")
            else:
                text.append("-")
        text.append(f"] {duration_str}")

        self.query_one("#ascii_progress").update(text)

    def reset_ascii_progress(self):
        self.query_one("#ascii_progress").update("")

    def update_elapsed_time(self, time: int):
        minutes = time // 60
        seconds = time % 60
        self.query_one("#elapsed_time").update(f"{minutes:02}:{seconds:02}")

    def update_progress_bar(self, elapsed_time: int):
        bar = self.query_one("#progress", ProgressBar)
        bar.progress = elapsed_time
        self.update_elapsed_time(elapsed_time)

    def on_refresh_lyrics(self, timestamps: float):
        self.lyrics.sync(timestamps)
