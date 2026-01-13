import os
from mutagen.id3 import ID3
from models.tracks import Track

class MusicLoader():

    def __init__(self):
        self.musics = []
        self.music : Track = ""
    
    def load_music_from_dir(self, folder : str):
         
        for file in sorted(os.listdir(folder)):
            if file.lower().endswith(".mp3") :
                music = ID3(os.path.join(folder, file))
                cover = music.get('APIC:')
                audio =  music.get('TIT2', 'Unknown').text[0]
                self.music = Track( os.path.join(folder, file),
                                   music.get('TIT2', 'Unknown').text[0],
                                   music.get('TALB', 'Unknown').text[0],
                                   music.get('TPE2', 'Unknown').text[0],
                                   cover.data if cover else None
                )

                self.musics.append(self.music)
        print(self.musics)


    
