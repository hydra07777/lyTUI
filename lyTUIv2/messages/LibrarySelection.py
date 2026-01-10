from textual.message import Message

class LibrarySelection(Message):
    def __init__(self, id: str, value : str):
        self.id = id
        self.value = value
        super().__init__()