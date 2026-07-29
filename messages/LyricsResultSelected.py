from textual.message import Message


class LyricsResultSelected(Message):
    def __init__(self, track_id: int, synced_lyrics: str | None, plain_lyrics: str | None):
        self.track_id = track_id
        self.synced_lyrics = synced_lyrics
        self.plain_lyrics = plain_lyrics
        super().__init__()
