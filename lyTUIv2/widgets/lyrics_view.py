from textual.widgets import Static
from mutagen.id3 import ID3
import re

class LyricsView(Static) :
    def __init__(self):
        super().__init__("No lyrics")
        self.lines = []
        self.index = 0
    
    def load_lyrics_from_path(self, path : str):
        self.lines = []
        self.index = 0

        try:
            audio = ID3(path)
            uslts = audio.getall('USLT')

            if not uslts :
                return "no lyrics"
            
            timed_lyrics = None

            for tag in uslts:
                if "[" in tag.text and ":" in tag.text:
                    timed_lyrics = tag.text
                    break
            if not timed_lyrics:
                return "lyrics found, but not sync"
            
            ## ah ah ah ah

           
            timed_lyrics = timed_lyrics.replace("\r", "\n")
            self._parse_lyrics(timed_lyrics)
            
        except Exception as e:
            print(f"{e}")

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

    def _update_display( self):
        # Afficher 2 lignes avant, la courante surlignée, et 1 ligne après

        start = max(0, self.index-2)
        end = min(len(self.lines), self.index+2)
        print(f"{start}, {end}")

        display_lines = []
        for i in range(start, end):
            lyric = self.lines[i][1]
            if i == self.index:
                display_lines.append(f"[bold yellow reverse]{lyric}[/]")
            else :
                display_lines.append(lyric)
        self.update("\n".join(display_lines))
        print(display_lines)

    def sync(self, current_time: float):
        if not self.lines:
            return

    # Avancer tant que la prochaine ligne est dépassée
        while (
            self.index + 1 < len(self.lines)
            and current_time >= self.lines[self.index + 1][0]
        ):
            self.index += 1
            self._update_display()

    

LyricsView().load_lyrics_from_path("../Jérémy Frerot - Un homme.mp3")