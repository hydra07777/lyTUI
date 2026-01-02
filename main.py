"""
lyTUI - A Terminal User Interface music player with synchronized lyrics.

This application provides a modern TUI for playing MP3 files with karaoke-style
lyrics display, inspired by btop's design.
"""

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, ProgressBar
from textual.reactive import reactive

from audio.player import AudioPlayer
from ui.playlist import Playlist
from ui.lyrics_view import LyricsView


def fmt(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m:02}:{s:02}"


class MusicApp(App):
    """
    Main application class for lyTUI music player.

    Handles the TUI layout, user interactions, and audio playback coordination.
    """

    BINDINGS = [
        ("space", "toggle", "Play/Pause"),
        ("q", "quit", "Quit"),
    ]

    CSS = """
    Screen {
        background: #000000;
        color: #ffffff;
    }

    #footer {
        color: #888888;
        text-align: center;
        border-top: solid #00ffff;
        background: #111111;
        padding: 0 1;
    }

    Horizontal {
        height: 100%;
    }

    Vertical {
        width: 2fr;
        border-left: solid #00ffff;
        padding: 1;
        background: #000000;
    }

    #title {
        color: #ffff00;
        text-align: center;
        border-bottom: solid #00ffff;
        margin-bottom: 1;
        background: #111111;
        padding: 0 1;
    }

    #time {
        text-align: center;
        color: #ffffff;
        background: #222222;
        padding: 0 1;
        margin: 1 0;
    }

    ProgressBar {
        margin: 1 0;
        height: 1;
    }

    ProgressBar > .progress-bar--bar {
        background: #00ff00;
    }

    ProgressBar > .progress-bar--background {
        background: #333333;
    }

    LyricsView {
        height: 10;
        border: solid #00ffff;
        padding: 1;
        background: #111111;
        margin-top: 1;
    }

    Playlist {
        width: 1fr;
        border-right: solid #00ffff;
        padding: 1;
        background: #000000;
    }

    #playlist-title {
        color: #ffff00;
        text-align: center;
        border-bottom: solid #00ffff;
        margin-bottom: 1;
        background: #111111;
        padding: 0 1;
    }

    ListView {
        height: 100%;
        border: none;
        background: transparent;
    }

    ListItem {
        color: #ffffff;
        padding: 0 1;
    }

    ListItem:hover {
        background: #ffff00;
        color: #000000;
    }

    ListItem.--highlight {
        background: #00ffff;
        color: #000000;
    }
    """

    playing = reactive(False)

    def compose(self) -> ComposeResult:
        self.player = AudioPlayer()
        self.playlist = Playlist()
        self.lyrics = LyricsView()

        yield Horizontal(
            Vertical(
                Static("🎵 Playlist", id="playlist-title"),
                self.playlist,
            ),
            Vertical(
                Static("🎵 Player", id="title"),
                Static("00:00", id="time"),
                ProgressBar(total=300, id="progress"),
                self.lyrics,
            ),
        )
        yield Static("[↑↓] Select  [Enter] Play  [Space] Pause  [Q] Quit", id="footer")

    def on_mount(self):
        # 📂 dossier music/
        self.playlist.load_folder("music")
        self.set_interval(0.3, self.refresh_ui)

    def on_list_view_selected(self, event):
        song = event.item.song
        path = f"music/{song}"

        # ▶️ Audio
        self.player.load(path)
        self.player.play()
        self.playing = True

        # 🎤 Lyrics depuis le MP3 (USLT)
        self.lyrics.load_from_mp3(path)

        # 📊 Progress bar
        bar = self.query_one("#progress", ProgressBar)
        bar.total = self.player.length
        bar.progress = 0

    def action_toggle(self):
        if self.playing:
            self.player.pause()
            self.playing = False
        else:
            self.player.resume()
            self.playing = True

    def refresh_ui(self):
        pos = self.player.position()

        self.query_one("#time", Static).update(fmt(pos))

        bar = self.query_one("#progress", ProgressBar)
        bar.progress = pos

        # ⏱️ sync lyrics
        self.lyrics.sync(pos)


if __name__ == "__main__":
    MusicApp().run()
