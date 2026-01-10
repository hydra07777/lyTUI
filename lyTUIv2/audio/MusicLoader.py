import os
from mutagen.id3 import ID3

class MusicLoader():

    def __init__(self):
        self.musics = []
        self.music = {}
    
    def load_music_from_dir(self, folder : str):
         
        for file in sorted(os.listdir(folder)):
            if file.lower().endswith(".mp3") :
                music = ID3(os.path.join(folder, file))
                audio =  music.get('TIT2', 'Unknown').text[0]
                self.music = {
                    "title" : music.get('TIT2', 'Unknown').text[0],
                    "artist" : music.get('TPE2', 'Unknown').text[0],
                    "album" : music.get('TALB', 'Unknown').text[0],
                    "year" : 2025
                }

                self.musics.append(self.music)
        print(self.musics)


    
