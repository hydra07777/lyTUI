from textual.message import Message
from models.tracks import Track

class MusicSelection(Message) :
    def __init__(self, music : Track):
        self.music = music
        super().__init__()