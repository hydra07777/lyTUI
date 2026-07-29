from textual.message import Message


class FetchLyricsRequested(Message):
    def __init__(self, track_id: int):
        self.track_id = track_id
        super().__init__()
