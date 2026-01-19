class Track:
    def __init__(self, id: int, path : str, title : str, album: str, artist : str, cover_byte):
        self._id = id
        self.path = path
        self.title = title
        self.album = album
        self.artist = artist
        self.cover_byte = cover_byte
        self.cover_ansi = None