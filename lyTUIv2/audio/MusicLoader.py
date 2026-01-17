import os
from mutagen.id3 import ID3
from models.tracks import Track
from services.get_metadata import get_metadata

class MusicLoader():

    def __init__(self):
        self.musics : list[Track] = []
        self.music : Track = None
    
    def load_music_from_dir(self, folder : str):
        SUPPORTED = (".mp3", ".m4a", ".wav", ".flac", ".ogg")
        id = 0
        for file in sorted(os.listdir(folder)):
        
            if file.lower().endswith(SUPPORTED) :
                path = os.path.join(folder, file)
                meta = get_metadata(path=path)
                self.music = Track(id,
                                   path,
                                   meta["title"],
                                   meta["album"],
                                   meta["artist"],
                                   meta["cover"]
                )

                self.musics.append(self.music)
                id += 1
        print(self.musics)


    
