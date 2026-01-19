from textual.message import Message


class MusicSelection(Message) :
    def __init__(self, id : int):
        self.id = id
        super().__init__()