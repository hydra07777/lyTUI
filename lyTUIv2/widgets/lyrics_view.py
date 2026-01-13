from textual.widgets import Static

class LyricsView(Static) :
    def __init__(self):
        super().__init__("No lyrics")
        self.lines = []
        self.index = 0