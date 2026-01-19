from textual.message import Message

class AudioDeviceSelected(Message):
    """Message envoyé quand un périphérique audio est choisi."""
    def __init__(self, device_id: int):
        self.device_id = device_id
        super().__init__()