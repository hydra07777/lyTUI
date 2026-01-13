from textual.message import Message

class MusicSelection(Message) :
    def __init__(self, music : dict):
        self.music = music
        super().__init__()