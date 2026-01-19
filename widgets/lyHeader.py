from textual.widgets import Static

class LyHeader(Static):
    def on_update(self, title):
        self.update(f"{title}")
        