"""
Lyrics display widget with karaoke-style highlighting.
"""

import re
from textual.widgets import Static
from mutagen.id3 import ID3

class LyricsView(Static):
    """
    Widget for displaying synchronized lyrics with current line highlighting.

    Parses USLT tags from MP3 files and displays lyrics with karaoke effect.
    """

    def __init__(self):
        super().__init__("No lyrics")
        self.lines = []
        self.index = 0

    def load_from_mp3(self, path: str):
        self.lines = []
        self.index = 0

        try:
            audio = ID3(path)
            uslts = audio.getall("USLT")

            if not uslts:
                self.update("No lyrics")
                return

            # 👉 prendre celui qui contient des timestamps
            timed_lyrics = None
            for tag in uslts:
                if "[" in tag.text and ":" in tag.text:
                    timed_lyrics = tag.text
                    break

            if not timed_lyrics:
                self.update("Lyrics found, but not synchronized")
                return

            # Normalisation CRLF
            timed_lyrics = timed_lyrics.replace("\r", "\n")
            self._parse_lyrics(timed_lyrics)

        except Exception as e:
            self.update(f"No lyrics\n{e}")

    def _parse_lyrics(self, text: str):
        pattern = re.compile(r"\[(\d+):(\d+\.\d+)\]\s*(.*)")
        self.lines = []

        for line in text.split("\n"):
            match = pattern.match(line.strip())
            if match:
                minutes = int(match.group(1))
                seconds = float(match.group(2))
                timestamp = minutes * 60 + seconds
                lyric = match.group(3)
                self.lines.append((timestamp, lyric))

        if self.lines:
            self._update_display()
        else:
            self.update("No lyrics")

    def _update_display(self):
        # Afficher 2 lignes avant, la courante surlignée, et 1 ligne après
        start = max(0, self.index - 2)
        end = min(len(self.lines), self.index + 2)

        display_lines = []
        for i in range(start, end):
            lyric = self.lines[i][1]
            if i == self.index:
                # Surligner la ligne courante en jaune gras avec inversion des couleurs pour la rendre plus visible
                display_lines.append(f"[bold yellow reverse]{lyric}[/]")
            else:
                display_lines.append(lyric)

        self.update("\n".join(display_lines))

    def sync(self, current_time: float):
        if not self.lines:
            return

        while (
            self.index + 1 < len(self.lines)
            and current_time >= self.lines[self.index + 1][0]
        ):
            self.index += 1

        self._update_display()
