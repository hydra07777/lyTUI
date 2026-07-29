from textual.message import Message


class TrackActionsRequested(Message):
    def __init__(self, track_id: int):
        self.track_id = track_id
        super().__init__()
