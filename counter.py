from textual.widgets import Static

class Counter(Static):
    def on_update(self, song, time):
        self.update(f'{song} - {time%60}')